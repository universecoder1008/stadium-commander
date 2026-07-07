from simulator.stadium_simulator import StadiumSimulator
from orchestrator.stadium_orchestrator import StadiumOrchestrator

simulator = StadiumSimulator()

stadium = simulator.generate()

orchestrator = StadiumOrchestrator()

result = orchestrator.process(stadium)

print(result)