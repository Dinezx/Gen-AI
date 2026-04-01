import json

from app.schemas import GenerateResponse
from app.services.providers import LLMProvider


class LLMService:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def generate_structured(self, messages: list[dict[str, str]]) -> GenerateResponse:
        raw_text = await self.provider.generate(messages)
        payload = self._parse_json(raw_text)
        try:
            return GenerateResponse.model_validate(payload)
        except Exception as exc:
            raise ValueError(f"JSON schema validation failed: {exc}") from exc

    def _parse_json(self, raw_text: str) -> dict:
        # Try direct parse first.
        try:
            parsed = json.loads(raw_text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        # Fallback: extract first balanced JSON object from mixed text.
        candidate = self._extract_first_json_object(raw_text)
        if not candidate:
            raise ValueError("Model response did not include a valid JSON object")

        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON received from model: {exc}") from exc

        if not isinstance(parsed, dict):
            raise ValueError("Model JSON must be a top-level object")

        return parsed

    @staticmethod
    def _extract_first_json_object(text: str) -> str | None:
        start = text.find("{")
        if start < 0:
            return None

        depth = 0
        in_string = False
        escaped = False

        for index in range(start, len(text)):
            ch = text[index]

            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue

            if ch == '"':
                in_string = True
                continue

            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : index + 1]

        return None
