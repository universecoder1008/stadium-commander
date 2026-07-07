import random

from models.stadium_input import (
    StadiumInput,
    GateData,
    TransportData,
    ParkingData,
    MetroData,
    BusData
)


class StadiumSimulator:

    def generate(self):

        gates = []

        for i in range(1, 5):

            gates.append(
                GateData(
                    gate=f"Gate {i}",
                    occupancy=random.randint(20, 98),
                    queue_minutes=random.randint(1, 30),
                    entry_rate=random.randint(20, 220)
                )
            )

        transport = TransportData(

            parking=ParkingData(
                occupancy=random.randint(20, 100),
                available_spots=random.randint(0, 600)
            ),

            metro=MetroData(
                next_arrival_minutes=random.randint(1, 8),
                expected_passengers=random.randint(500, 3500)
            ),

            bus=BusData(
                delay_minutes=random.randint(0, 20)
            )
        )

        return StadiumInput(

            current_time="17:40",

            match_phase="Pre-Match",

            gates=gates,

            transport=transport
        )