"""
Module for Mediator pattern study

Python 3.10.4
pylint code rate 9.25/10
"""
from __future__ import annotations

import abc
from uuid import uuid4
from random import randint


class Aircraft:
    """The parent class for all flying objects"""

    def __init__(
        self,
        registration_number: str,
        is_landed: bool = False,
        is_moved_to_garage: bool = False,
    ):
        self._registration_number = registration_number
        self._is_landed = is_landed
        self._is_moved_to_garage = is_moved_to_garage

    def get_registration_number(self) -> str:
        """Getting aircraft registration number"""
        return self._registration_number

    def is_landed(self) -> bool:
        """Checking for aircraft landed status"""
        return self._is_landed

    def is_moved_to_garage(self) -> bool:
        """Checking that aircraft is placed in garage"""
        return self._is_moved_to_garage

    def landed(self) -> None:
        """Changing aircraft landed status"""
        self._is_landed = True

    def move_to_garage(self) -> None:
        """Changing aircraft garage status"""
        self._is_moved_to_garage = True

    @abc.abstractmethod
    def display_no_seats_message(self) -> None:
        """Displays a message indicating that the aircraft has no available seats for landing."""
        pass

    @abc.abstractmethod
    def display_aircraft_parked_message(self, garage_number) -> None:
        """Displays a message indicating that the aircraft has been successfully parked in a garage."""
        pass

    @abc.abstractmethod
    def display_aircraft_landing_message(self, airstrip_number) -> None:
        """Displays a message indicating that the aircraft is landing on a specific airstrip."""
        pass


class Airplane(Aircraft):
    """
    Class for airplane
    """

    def __init__(
        self,
        registration_number: str,
        is_landed: bool = False,
        is_moved_to_garage: bool = False,
    ):
        super().__init__(registration_number, is_landed, is_moved_to_garage)

    def display_no_seats_message(self) -> None:
        print(f"Самолету {self._registration_number} некуда сесть.")

    def display_aircraft_parked_message(self, garage_number) -> None:
        print(f"Самолет {self._registration_number} помещен в гараж {garage_number}")

    def display_aircraft_landing_message(self, airstrip_number) -> None:
        print(
            f"Самолет {self._registration_number} садится на полосу {airstrip_number}"
        )


class Helicopter(Aircraft):
    """
    Class for airplane
    """

    def __init__(
        self,
        registration_number: str,
        is_landed: bool = False,
        is_moved_to_garage: bool = False,
    ):
        super().__init__(registration_number, is_landed, is_moved_to_garage)

    def display_no_seats_message(self) -> None:
        print(f"Вертолету {self._registration_number} некуда сесть.")

    def display_aircraft_parked_message(self, garage_number) -> None:
        print(f"Вертолет {self._registration_number} помещен в гараж {garage_number}")

    def display_aircraft_landing_message(self, airstrip_number) -> None:
        print(
            f"Вертолет {self._registration_number} садится на полосу {airstrip_number}"
        )


class Airstrip:
    """
    Class for airstrip
    """

    def __init__(
        self,
        line_number: int,
        mediator: Mediator | None = None,
    ):
        self._line_number = line_number
        self._mediator = mediator
        self._aircraft = None

    def get_line_number(self) -> int:
        """Getting airstrip number"""
        return self._line_number

    def get_aircraft(self) -> Aircraft | None:
        """Getting aircraft that placed on this airstrip"""
        return self._aircraft

    def set_aircraft(self, aircraft: Aircraft) -> None:
        """Setting aircraft for placing on this airstrip"""
        self._aircraft = aircraft

    def unset_aircraft(self) -> None:
        """Unsetting aircraft for placing on this airstrip"""
        self._aircraft = None


class Garage:
    """
    Class for garage
    """

    def __init__(
        self,
        number: int,
        mediator: Mediator | None = None,
    ):
        self._number = number
        self._mediator = mediator
        self._aircrafts = []

    def get_number(self) -> int:
        """Getting garage number"""
        return self._number

    def place(self, aircraft: Aircraft) -> bool:
        """Placing aircraft inside garage"""
        if aircraft.is_landed() is False:
            return False

        aircraft.move_to_garage()
        self._aircrafts.append(aircraft)

        return True

    def get_placed_aircrafts(self) -> list[Aircraft]:
        """Gettiong aircrafts placed inside garage"""
        return self._aircrafts


class Mediator:
    def __init__(self, airstrips: list[Airstrip], garages: list[Garage]):
        self._airstrips = airstrips
        self._garages = garages

    def request_land(self, aircraft: Aircraft) -> bool:
        for airstrip in self._airstrips:
            if airstrip.get_aircraft() is not None:
                continue
            aircraft.display_aircraft_landing_message(airstrip.get_line_number())
            airstrip.set_aircraft(aircraft)
            aircraft.landed()
            return True
        return False

    def request_move_to_garage(self, airstrip: Airstrip) -> None:
        landed_aircraft = airstrip.get_aircraft()
        if landed_aircraft and randint(0, 9) == 0:
            current_garage = min(
                self._garages, key=lambda garage: len(garage.get_placed_aircrafts())
            )
            landed_aircraft.display_aircraft_parked_message(current_garage.get_number())
            current_garage.place(landed_aircraft)
            airstrip.unset_aircraft()
        else:
            landed_aircraft.display_no_seats_message()

    def run_traffic_control(self, aircrafts: list[Aircraft]) -> None:
        while any(not aircraft.is_moved_to_garage() for aircraft in aircrafts):
            for airstrip in self._airstrips:
                landed_aircraft = airstrip.get_aircraft()
                if landed_aircraft:
                    self.request_move_to_garage(airstrip)

            for aircraft in aircrafts:
                if not aircraft.is_landed():
                    self.request_land(aircraft)


AIRCRAFT_COUNT = 50
HELICOPTER_COUNT = 50
AIRSTRIP_COUNT = 9
GARAGE_COUNT = 6

airplane_in_air = [Airplane("airplane_" + uuid4().hex) for _ in range(AIRCRAFT_COUNT)]
helicopter_in_air = [
    Helicopter("helicopter_" + uuid4().hex) for _ in range(HELICOPTER_COUNT)
]

airstrips = [Airstrip(i + 1, mediator=None) for i in range(AIRSTRIP_COUNT)]
garages = [Garage(i + 1, mediator=None) for i in range(GARAGE_COUNT)]

mediator = Mediator(airstrips, garages)

for aircraft in airplane_in_air:
    mediator.request_land(aircraft)

for helicopter in helicopter_in_air:
    mediator.request_land(helicopter)

mediator.run_traffic_control(helicopter_in_air)
mediator.run_traffic_control(airplane_in_air)


for garage in garages:
    print(
        f"В гараже №{garage.get_number()} самолётов: {len(garage.get_placed_aircrafts())}"
    )
