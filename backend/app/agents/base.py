"""Base agent runner that handles Claude API calls with tool use and retry logic."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import anthropic
from pydantic import BaseModel, ValidationError

from app.config import get_settings
from app.schemas.task import AgentType, StreamEvent, StreamEventType

logger = logging.getLogger(__name__)


class AgentRunner:
    """Runs a single agent: sends messages to Claude, handles tool calls, validates output."""

    def __init__(
        self,
        agent_type: AgentType,
        system_prompt: str,
        tools: list[dict],
        tool_dispatch: dict[str, Any],
        output_model: type[BaseModel],
        client: anthropic.AsyncAnthropic | None = None,
    ):
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.tools = tools
        self.tool_dispatch = tool_dispatch
        self.output_model = output_model
        settings = get_settings()
        self.client = client or anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.model_name
        self.max_retries = settings.max_retries

    async def run(
        self,
        user_message: str,
        subtask_id: str,
    ) -> AsyncIterator[StreamEvent | BaseModel]:
        """Execute the agent with tool-use loop and schema validation retries.

        Yields StreamEvent objects for progress, and finally yields the validated output model.
        """
        messages: list[dict] = [{"role": "user", "content": user_message}]

        yield StreamEvent(
            event=StreamEventType.AGENT_START,
            agent=self.agent_type,
            data=f"Starting {self.agent_type.value} agent",
            subtask_id=subtask_id,
        )

        for attempt in range(1, self.max_retries + 1):
            try:
                async for event in self._tool_loop(messages, subtask_id):
                    if isinstance(event, StreamEvent):
                        yield event
                        if event.event == StreamEventType.AGENT_COMPLETE:
                            parsed = self._parse_output(event.data)
                            yield parsed
                            return
                break  # Should not reach here, but safety exit
            except (ValidationError, json.JSONDecodeError) as e:
                logger.warning(
                    "Schema validation failed for %s (attempt %d/%d): %s",
                    self.agent_type.value,
                    attempt,
                    self.max_retries,
                    e,
                )
                if attempt == self.max_retries:
                    yield StreamEvent(
                        event=StreamEventType.ERROR,
                        agent=self.agent_type,
                        data=f"Schema validation failed after {self.max_retries} retries: {e}",
                        subtask_id=subtask_id,
                    )
                    raise
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"Your output did not match the required schema. Error:\n{e}\n\n"
                            "Please fix your response and return ONLY the corrected JSON."
                        ),
                    }
                )
                yield StreamEvent(
                    event=StreamEventType.AGENT_PROGRESS,
                    agent=self.agent_type,
                    data=f"Retrying due to validation error (attempt {attempt}/{self.max_retries})",
                    subtask_id=subtask_id,
                )

    def _parse_output(self, text: str) -> BaseModel:
        """Extract JSON from agent response text and validate against output model."""
        json_str = text
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0].strip()
        elif "{" in text:
            start = text.index("{")
            end = text.rindex("}") + 1
            json_str = text[start:end]

        data = json.loads(json_str)
        return self.output_model.model_validate(data)

    async def _tool_loop(
        self,
        messages: list[dict],
        subtask_id: str,
    ) -> AsyncIterator[StreamEvent]:
        """Run the tool-use loop until the model produces a final text response."""
        while True:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages,
            )

            text_parts = []
            tool_use_blocks = []

            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_use_blocks.append(block)

            if tool_use_blocks:
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for tool_block in tool_use_blocks:
                    yield StreamEvent(
                        event=StreamEventType.TOOL_CALL,
                        agent=self.agent_type,
                        data=f"Calling tool: {tool_block.name}",
                        subtask_id=subtask_id,
                    )

                    if tool_block.name in self.tool_dispatch:
                        result = self.tool_dispatch[tool_block.name](tool_block.input)
                    else:
                        result = json.dumps({"error": f"Unknown tool: {tool_block.name}"})

                    yield StreamEvent(
                        event=StreamEventType.TOOL_RESULT,
                        agent=self.agent_type,
                        data=f"Tool {tool_block.name} completed",
                        subtask_id=subtask_id,
                    )

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_block.id,
                            "content": result,
                        }
                    )

                messages.append({"role": "user", "content": tool_results})

                if text_parts:
                    yield StreamEvent(
                        event=StreamEventType.AGENT_PROGRESS,
                        agent=self.agent_type,
                        data="\n".join(text_parts),
                        subtask_id=subtask_id,
                    )
                continue

            # No tool calls — final text response
            final_text = "\n".join(text_parts)
            yield StreamEvent(
                event=StreamEventType.AGENT_COMPLETE,
                agent=self.agent_type,
                data=final_text,
                subtask_id=subtask_id,
            )
            return
