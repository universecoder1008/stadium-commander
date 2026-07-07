import json

from analyzers.crowd_analyzer import CrowdAnalyzer
from agents.commander_agent import CommanderAgent

from models.commander_schema import CommanderResponse
from models.stadium_input import StadiumInput


class StadiumOrchestrator:

    def __init__(self):
        self.crowd_analyzer = CrowdAnalyzer()
        self.commander_agent = CommanderAgent()

    def process(self, stadium_data: StadiumInput):

        # Analyze crowd using Python
        crowd_result = self.crowd_analyzer.analyze(stadium_data)

        # Build combined report
        combined_report = {
            "crowd": crowd_result.model_dump()
        }

        # Ask Gemini Commander
        commander_raw = self.commander_agent.run(
            json.dumps(combined_report, indent=2)
        )

        commander_result = CommanderResponse(
            **json.loads(commander_raw)
        )

        return commander_result