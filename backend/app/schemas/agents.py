from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.task import AgentType, SubTask


class ResearchInput(BaseModel):
    query: str = Field(..., description="The research question to investigate")
    context: str = Field(default="", description="Additional context from prior subtasks")
    depth: str = Field(default="standard", description="Research depth: quick, standard, deep")


class ResearchOutput(BaseModel):
    summary: str = Field(..., description="Concise research summary")
    key_findings: list[str] = Field(default_factory=list, description="Bullet-point findings")
    sources: list[str] = Field(default_factory=list, description="Sources or references cited")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0-1")


class CodeGenInput(BaseModel):
    specification: str = Field(..., description="What code to generate")
    language: str = Field(default="python", description="Target programming language")
    context: str = Field(default="", description="Additional context from prior subtasks")


class CodeGenOutput(BaseModel):
    code: str = Field(..., description="Generated source code")
    language: str = Field(..., description="Programming language used")
    explanation: str = Field(default="", description="Explanation of the code")
    dependencies: list[str] = Field(default_factory=list, description="Required packages")


class DataAnalysisInput(BaseModel):
    question: str = Field(..., description="The analytical question")
    data_description: str = Field(default="", description="Description of data to analyze")
    context: str = Field(default="", description="Additional context from prior subtasks")


class DataAnalysisOutput(BaseModel):
    analysis: str = Field(..., description="Detailed analysis text")
    methodology: str = Field(default="", description="Methodology used")
    conclusions: list[str] = Field(default_factory=list, description="Key conclusions")
    visualizations: list[str] = Field(
        default_factory=list, description="Descriptions of suggested visualizations"
    )


class OrchestratorPlan(BaseModel):
    reasoning: str = Field(..., description="Why the task was decomposed this way")
    subtasks: list[SubTask] = Field(..., description="Ordered list of subtasks to execute")
