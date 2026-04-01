from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx

from app.core.config import get_settings
from app.schemas import AppMode, GenerateRequest, GenerateResponse, HealthResponse
from app.services.llm_service import LLMService
from app.services.prompt_builder import SYSTEM_MESSAGE, build_user_prompt
from app.services.providers import build_provider

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        default_provider=settings.default_provider,
        supported_modes=[AppMode.GENERATE_FORMULA, AppMode.FIX_POWERAPPS_ERROR],
    )


@app.post(f"{settings.api_prefix}/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest) -> GenerateResponse:
    provider_name = request.provider.value if request.provider else settings.default_provider

    try:
        provider = build_provider(provider_name=provider_name, settings=settings)
        service = LLMService(provider)

        messages = [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {
                "role": "user",
                "content": build_user_prompt(request.mode, request.prompt, request.context),
            },
        ]

        return await service.generate_structured(messages)

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"LLM provider error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {exc}") from exc
