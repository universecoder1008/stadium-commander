from pathlib import Path

from services.gemini_service import generate


class CommanderAgent:

    def __init__(self):

        prompt_path = Path("prompts") / "commander_prompt.txt"

        with open(prompt_path, "r", encoding="utf-8") as file:
            self.system_prompt = file.read()

    def run(self, analyzer_report: str):

        prompt = f"""
{self.system_prompt}

ANALYZER REPORTS

{analyzer_report}
"""

        return generate(prompt)