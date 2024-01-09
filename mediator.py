from __future__ import annotations

import abc
from typing import List, Union
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
        self._mediator = None

    def set_mediator(self, mediator: Mediator) -> None:
        self._mediator = mediator

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

    def notify(self, event: str) -> None:
        """Notify mediator about some event"""
        if isinstance(self._mediator, Mediator):
            self._mediator.notify(self, event)

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
    """Class for airplane"""

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
    """Class for helicopter"""

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
    def __init__(
        self,
        line_number: int,
        mediator: Mediator | None = None,
    ):
        self._line_number = line_number
        self._mediator = mediator
        self._aircraft = None

    def set_mediator(self, mediator: Mediator) -> None:
        self._mediator = mediator

    def get_line_number(self) -> int:
        return self._line_number

    def get_aircraft(self) -> Aircraft | None:
        return self._aircraft

    def set_aircraft(self, aircraft: Aircraft) -> None:
        self._aircraft = aircraft

    def unset_aircraft(self) -> None:
        self._aircraft = None
        if isinstance(self._mediator, Mediator):
            self._mediator.notify(self, "unset_aircraft")


class Garage:
    def __init__(
        self,
        number: int,
        mediator: Mediator | None = None,
    ):
        self._number = number
        self._mediator = mediator
        self._aircrafts = []

    def set_mediator(self, mediator: Mediator) -> None:
        self._mediator = mediator

    def get_number(self) -> int:
        return self._number

    def place(self, aircraft: Aircraft) -> bool:
        if aircraft.is_landed() is False:
            return False

        aircraft.move_to_garage()
        self._aircrafts.append(aircraft)
        if isinstance(self._mediator, Mediator):
            self._mediator.notify(self, "placed_aircraft")
        return True

    def get_placed_aircrafts(self) -> list[Aircraft]:
        return self._aircrafts


class Mediator:
    def __init__(self, airstrips: List[Airstrip], garages: List[Garage]):
        self._airstrips = airstrips
        self._garages = garages

    @staticmethod
    def display_free_airstrip(line_number):
        """Display mediator's message"""
        print(f"Медиатор: Полоса {line_number} освобождена.")

    @staticmethod
    def notify(sender: Union[Aircraft, Airstrip, Garage], event: str) -> None:
        """Notify method"""
        if isinstance(sender, Aircraft) and event == "landed":
            sender.display_aircraft_landing_message(sender.get_line_number())
        elif isinstance(sender, Aircraft) and event == "moved_to_garage":
            sender.display_aircraft_parked_message(sender.get_number())
        elif isinstance(sender, Airstrip) and event == "unset_aircraft":
            Mediator.display_free_airstrip(sender.get_line_number())

    def set_mediator_for_components(self) -> None:
        """Set mediator for each Aircraft"""
        for airstrip in self._airstrips + self._garages:
            airstrip.set_mediator(self)

    def request_land(self, aircraft: Aircraft) -> bool:
        """Request land for each Aircraft"""
        for airstrip in self._airstrips:
            if airstrip.get_aircraft() is not None:
                continue
            aircraft.display_aircraft_landing_message(airstrip.get_line_number())
            airstrip.set_aircraft(aircraft)
            aircraft.landed()
            aircraft.notify("landed")
            return True
        return False

    def request_move_to_garage(self, airstrip: Airstrip) -> None:
        """Request move to garage each Aircraft"""
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
        """Start mediator's work"""
        while any(not aircraft.is_moved_to_garage() for aircraft in aircrafts):
            for airstrip in self._airstrips:
                landed_aircraft = airstrip.get_aircraft()
                if landed_aircraft:
                    self.request_move_to_garage(airstrip)

            for aircraft in aircrafts:
                if not aircraft.is_landed():
                    self.request_land(aircraft)


def initialize_airport(airplane_count, helicopter_count, airstrip_count, garage_count):
    """Setup airport's unit"""
    airplane_in_air = [
        Airplane("airplane_" + uuid4().hex) for _ in range(airplane_count)
    ]
    helicopter_in_air = [
        Helicopter("helicopter_" + uuid4().hex) for _ in range(helicopter_count)
    ]
    airstrips = [Airstrip(i + 1) for i in range(airstrip_count)]
    garages = [Garage(i + 1) for i in range(garage_count)]
    mediator = Mediator(airstrips, garages)
    mediator.set_mediator_for_components()

    for aircraft in airplane_in_air:
        mediator.request_land(aircraft)

    for helicopter in helicopter_in_air:
        mediator.request_land(helicopter)

    mediator.run_traffic_control(helicopter_in_air)
    mediator.run_traffic_control(airplane_in_air)

    for garage in garages:
        print(
            f"В гараже №{garage.get_number()} летательных аппаратов: {len(garage.get_placed_aircrafts())}"
        )


AIRCRAFT_COUNT = 100
HELICOPTER_COUNT = 50
AIRSTRIP_COUNT = 9
GARAGE_COUNT = 10


def main():
    initialize_airport(AIRCRAFT_COUNT, HELICOPTER_COUNT, AIRSTRIP_COUNT, GARAGE_COUNT)


if __name__ == "__main__":
    main()
