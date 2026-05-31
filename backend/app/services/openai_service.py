import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from openai import OpenAI

from ..core.config import settings


class OpenAIService:
    def __init__(self) -> None:
        api_key = settings.openai_api_key or None
        self.client = OpenAI(api_key=api_key)
        self.response_model = settings.openai_response_model
        self.tts_model = settings.openai_tts_model
        self.stt_model = settings.openai_stt_model

    def transcribe_audio(self, audio_path: str) -> str:
        with open(audio_path, "rb") as audio_file:
            response = self.client.audio.transcriptions.create(
                model=self.stt_model,
                file=audio_file,
            )

        return self._extract_response_text(response)

    def generate_tts(self, script_text: str, voice: str = "alloy") -> bytes:
        response = self.client.audio.speech.create(
            model=self.tts_model,
            voice=voice,
            input=script_text,
            response_format="mp3",
        )
        if hasattr(response, "content"):
            return response.content
        return bytes(response.parse(to=bytes))

    def analyze_candidate_response(self, candidate_text: str, question_text: str, job_title: str, previous_answers: dict[str, str]) -> dict[str, Any]:
        prompt = self._build_analysis_prompt(candidate_text, question_text, job_title, previous_answers)
        response = self.client.chat.completions.create(
            model=self.response_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        response_text = self._extract_response_text(response)
        return self._parse_json_response(response_text)

    def summarize_report(self, details: dict[str, Any]) -> dict[str, str]:
        prompt = self._build_report_prompt(details)
        response = self.client.chat.completions.create(
            model=self.response_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        response_text = self._extract_response_text(response)
        return self._parse_json_response(response_text)

    def _build_analysis_prompt(self, candidate_text: str, question_text: str, job_title: str, previous_answers: dict[str, str]) -> str:
        return (
            "You are an AI recruitment screening assistant. "
            "Analyze the candidate's answer and identify updates to candidate profile fields, sentiment, enthusiasm, clarification needs, follow-up question, "
            "and any indicators of interest or risk. Return valid JSON only. "
            "The JSON keys should be: candidate_updates, sentiment, enthusiasm, clarity, follow_up, interest_reasoning. "
            "The candidate_updates object can include name, education, skills, experience, current_role, expected_salary, notice_period, preferred_location, availability, job_change_intent, or any extra field. "
            f"Job title: {job_title}. Question asked: {question_text}. Candidate answer: {candidate_text}. "
            f"Previous answers: {json.dumps(previous_answers)}. "
        )
    
    def _build_report_prompt(self, details: dict[str, Any]) -> str:
        summary = json.dumps(details, indent=2)
        return (
            "You are a recruiting analyst. Generate a JSON report summary for the conversation. "
            "Return keys: summary, interest_category, interest_score, recommendation, key_observations, risk_factors. "
            f"Input details: {summary}. "
        )

    def _response_text(self, response: Any) -> str:
        if hasattr(response, "choices") and response.choices:
            return response.choices[0].message.content or ""
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text
        if hasattr(response, "text") and response.text:
            return response.text
        if hasattr(response, "output"):
            parts = []
            for item in response.output:
                if hasattr(item, "text") and item.text:
                    parts.append(item.text)
                elif isinstance(item, str):
                    parts.append(item)
            return "\n".join(parts)
        if hasattr(response, "content") and isinstance(response.content, bytes):
            return response.content.decode("utf-8", errors="ignore")
        return ""

    def _extract_response_text(self, response: Any) -> str:
        text = self._response_text(response)
        return text.strip()

    def _parse_json_response(self, text: str) -> dict[str, Any]:
        sanitized = self._sanitize_json_block(text)
        try:
            return json.loads(sanitized)
        except json.JSONDecodeError:
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                return {"candidate_updates": {}, "sentiment": "neutral", "enthusiasm": 3, "clarity": "unclear", "follow_up": None, "interest_reasoning": text}

    def _sanitize_json_block(self, text: str) -> str:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        return match.group(0) if match else text

    def save_audio_to_temp(self, audio_bytes: bytes, suffix: str = ".mp3") -> str:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(audio_bytes)
            return temp_file.name
