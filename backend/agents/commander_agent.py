"""Commander Agent for Stadium Commander.

This module coordinates with the Gemini API to reason over aggregated situation reports
and return unified operational decisions.
"""

import os
import json
import logging
from typing import Any
from pathlib import Path
from google import genai

from models.situation_report import CombinedSituationReport
from models.commander_schema import CommanderResponse

logger = logging.getLogger("stadium_commander.agent")


class CommanderAgent:
    """Agent responsible for reasoning over situation reports using Gemini."""

    def __init__(self, client: Any = None, system_prompt: str = None):
        """Initializes the CommanderAgent with injected or default dependencies.

        Args:
            client: Optional injected Google GenAI client instance.
            system_prompt: Optional injected system prompt string.
        """
        if client is not None:
            self.client = client
        else:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY environment variable is missing. AI reasoning client set to None.")
                self.client = None
            else:
                try:
                    self.client = genai.Client(api_key=api_key)
                except Exception as e:
                    logger.error("Failed to initialize genai.Client inside CommanderAgent: %s", str(e))
                    self.client = None

        if system_prompt is not None:
            self.system_prompt = system_prompt
        else:
            # Fallback to local prompt loading
            prompt_path = Path("prompts") / "commander_prompt.txt"
            try:
                with open(prompt_path, "r", encoding="utf-8") as file:
                    self.system_prompt = file.read()
            except Exception as e:
                logger.warning("Failed to load local prompts/commander_prompt.txt: %s. Using default prompt.", str(e))
                self.system_prompt = "You are Stadium Commander."

    def analyze(self, report: CombinedSituationReport) -> CommanderResponse:
        """Runs the Gemini reasoning process over the CombinedSituationReport.

        Args:
            report: The aggregated CombinedSituationReport object.

        Returns:
            A validated CommanderResponse object containing priorities and actions.
        """
        if not self.client:
            logger.warning("AI reasoning client is offline. Returning fallback response directly.")
            return CommanderResponse(
                priority="WARNING",
                top_risk="AI reasoning temporarily unavailable",
                summary="Deterministic analyzers completed successfully. AI recommendations are temporarily unavailable.",
                actions=[
                    "Review analyzer outputs manually.",
                    "Retry AI reasoning later."
                ],
                estimated_impact="Operations continue using deterministic analyzer outputs.",
                confidence=0.75
            )

        serialized = report.model_dump_json(indent=2)
        prompt = f"{self.system_prompt}\n\nCOMBINED SITUATION REPORT:\n{serialized}"

        for attempt in range(2):
            try:
                logger.info("Calling Gemini API to reason on report. Attempt %d.", attempt + 1)
                
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                raw_text = response.text
                if not raw_text:
                    raise ValueError("Received empty response from Gemini API.")

                # Clean and parse JSON
                clean_text = self._clean_json_response(raw_text)
                parsed_json = json.loads(clean_text)
                
                # Validate response schema
                return CommanderResponse(**parsed_json)
            except Exception as e:
                logger.exception("Failed to analyze situation report on attempt %d: %s", attempt + 1, str(e))
                if attempt == 1:
                    logger.warning("Gemini AI reasoning failed after retries. Returning fallback CommanderResponse.", exc_info=True)
                    return CommanderResponse(
                        priority="WARNING",
                        top_risk="AI reasoning temporarily unavailable",
                        summary="Deterministic analyzers completed successfully. AI recommendations are temporarily unavailable.",
                        actions=[
                            "Review analyzer outputs manually.",
                            "Retry AI reasoning later."
                        ],
                        estimated_impact="Operations continue using deterministic analyzer outputs.",
                        confidence=0.75
                    )

    def _clean_json_response(self, text: str) -> str:
        """Cleans potential markdown wrapping codeblocks from Gemini text response."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()