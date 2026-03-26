"""Tools available to the ResearchAgent."""

from __future__ import annotations

import json


def web_search(query: str) -> str:
    """Search the web for information on a topic.

    Args:
        query: The search query string.

    Returns:
        JSON string with search results.
    """
    return json.dumps(
        {
            "tool": "web_search",
            "query": query,
            "results": [
                {
                    "title": f"Result for: {query}",
                    "snippet": (
                        f"Comprehensive information about {query}. "
                        "This is a simulated search result that would be replaced "
                        "by a real search API in production."
                    ),
                    "url": f"https://example.com/search?q={query.replace(' ', '+')}",
                }
            ],
        }
    )


def summarize_document(text: str, max_length: int = 500) -> str:
    """Summarize a long document into key points.

    Args:
        text: The document text to summarize.
        max_length: Maximum length of summary.

    Returns:
        Summarized text.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "... [truncated]"


def fact_check(claim: str) -> str:
    """Verify a factual claim.

    Args:
        claim: The claim to verify.

    Returns:
        JSON string with verification result.
    """
    return json.dumps(
        {
            "tool": "fact_check",
            "claim": claim,
            "verdict": "plausible",
            "reasoning": (
                f"The claim '{claim}' has been evaluated. "
                "In production this would cross-reference authoritative sources."
            ),
        }
    )


RESEARCH_TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for information on a topic",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query"}},
            "required": ["query"],
        },
    },
    {
        "name": "summarize_document",
        "description": "Summarize a long document into key points",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Document text"},
                "max_length": {"type": "integer", "description": "Max summary length", "default": 500},
            },
            "required": ["text"],
        },
    },
    {
        "name": "fact_check",
        "description": "Verify a factual claim against known sources",
        "input_schema": {
            "type": "object",
            "properties": {"claim": {"type": "string", "description": "The claim to verify"}},
            "required": ["claim"],
        },
    },
]

TOOL_DISPATCH = {
    "web_search": lambda args: web_search(args["query"]),
    "summarize_document": lambda args: summarize_document(
        args["text"], args.get("max_length", 500)
    ),
    "fact_check": lambda args: fact_check(args["claim"]),
}
