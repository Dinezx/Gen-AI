from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class AppMode(str, Enum):
    GENERATE_FORMULA = "generate_formula"
    FIX_POWERAPPS_ERROR = "fix_powerapps_error"


class ProviderName(str, Enum):
    OLLAMA = "ollama"
    OPENAI = "openai"


class PowerAppsField(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    type: Literal[
        "text",
        "number",
        "date",
        "dropdown",
        "checkbox",
        "email",
        "phone",
        "multiline",
    ]


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=5, max_length=4000)
    mode: AppMode
    provider: ProviderName | None = None
    context: dict[str, Any] | None = None


class GenerateResponse(BaseModel):
    fields: list[PowerAppsField] = Field(default_factory=list)
    formula: str = ""
    explanation: str | None = None


class HealthResponse(BaseModel):
    status: str
    default_provider: ProviderName | str
    supported_modes: list[AppMode]
