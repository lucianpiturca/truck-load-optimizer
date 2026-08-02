# axles.py
# Truck Load Optimizer 2.0
#
# Static axle load calculation
# Based on European articulated vehicle geometry


from dataclasses import dataclass
from typing import List

from cargo import Pallet
from truck import Truck



# ==========================================================
# RESULT OBJECTS
# ==========================================================


@dataclass
class AxleReport:

    axle_weights: List[float]

    total_weight: float

    cargo_weight: float

    centre_of_gravity: float



    @property
    def overweight(self):

        return [
            i
            for i, weight in enumerate(self.axle_weights)
            if weight > 0
        ]



# ==========================================================
# PALLET POSITION
# ==========================================================


def pallet_centre_position(
    pallet: Pallet
):
    """
    Returns pallet centre position
    measured from trailer front.

    x-axis:
        0 = front bulkhead
        trailer_length = rear doors
    """


    return (
        pallet.y
        +
        pallet.draw_length / 2
    )



# ==========================================================
# CENTRE OF GRAVITY
# ==========================================================


def calculate_centre_of_gravity(
    pallets: List[Pallet]
):

    total_weight = 0

    moment = 0


    for pallet in pallets:

        if not pallet.loaded:
            continue


        position = pallet_centre_position(
            pallet
        )


        total_weight += pallet.weight


        moment += (
            pallet.weight
            *
            position
        )


    if total_weight == 0:

        return 0


    return (
        moment
        /
        total_weight
    )



# ==========================================================
# TRAILER BOGIE LOAD
# ==========================================================


def calculate_bogie_load(
    truck: Truck,
    pallets: List[Pallet]
):
    """
    Calculates total reaction on trailer bogie.

    Simplified beam:

    Kingpin ---------------- Bogie

       distance = kingpin_to_bogie


    Cargo creates moment around kingpin.
    """


    cargo_on_trailer = 0

    moment = 0



    for pallet in pallets:

        if not pallet.loaded:
            continue


        cargo_on_trailer += pallet.weight


        distance_from_kingpin = (

            pallet_centre_position(pallet)

            -

            truck.kingpin_to_front

        )


        moment += (

            pallet.weight

            *

            distance_from_kingpin

        )



    if cargo_on_trailer == 0:

        return 0



    bogie_load = (

        moment

        /

        truck.kingpin_to_bogie

    )


    return bogie_load



# ==========================================================
# TRACTOR SPLIT
# ==========================================================


def split_tractor_load(
    truck: Truck,
    kingpin_load: float
):
    """
    Splits kingpin load between:
    
    axle 1 (steer)
    axle 2 (drive)

    using tractor wheelbase.

    This is a simplified static split.
    """


    wheelbase = truck.wheelbase


    if wheelbase <= 0:

        return (
            0,
            kingpin_load
        )


    # approximate fifth-wheel position

    fifth_wheel_position = 3.60



    drive_share = (

        fifth_wheel_position

        /

        wheelbase

    )


    drive = (

        kingpin_load

        *

        drive_share

    )


    steer = (

        kingpin_load

        -

        drive

    )


    return (
        steer,
        drive
    )



# ==========================================================
# TRAILER AXLE SPLIT
# ==========================================================


def split_trailer_axles(
    bogie_load: float
):

    """
    Equal tridem distribution.

    Future improvement:
    allow axle spacing geometry.
    """


    each = bogie_load / 3


    return [

        each,
        each,
        each

    ]



# ==========================================================
# MAIN CALCULATION
# ==========================================================


def calculate_axle_weights(
    truck: Truck,
    pallets: List[Pallet]
):


    kingpin_cargo = 0


    bogie_cargo = calculate_bogie_load(
        truck,
        pallets
    )


    total_cargo = sum(

        pallet.weight

        for pallet in pallets

        if pallet.loaded

    )



    kingpin_cargo = (

        total_cargo

        -

        bogie_cargo

    )



    steer_addition, drive_addition = split_tractor_load(

        truck,

        kingpin_cargo

    )



    trailer_additions = split_trailer_axles(

        bogie_cargo

    )



    axle_weights = [

        truck.empty_axles[0]
        +
        steer_addition,


        truck.empty_axles[1]
        +
        drive_addition,


        truck.empty_axles[2]
        +
        trailer_additions[0],


        truck.empty_axles[3]
        +
        trailer_additions[1],


        truck.empty_axles[4]
        +
        trailer_additions[2]

    ]



    return AxleReport(

        axle_weights=axle_weights,

        total_weight=sum(axle_weights),

        cargo_weight=total_cargo,

        centre_of_gravity=calculate_centre_of_gravity(

            pallets

        )

    )



# ==========================================================
# LEGAL CHECK
# ==========================================================


def check_axles_legal(
    truck: Truck,
    report: AxleReport
):


    results = []


    for weight, limit in zip(

        report.axle_weights,

        truck.axle_limits

    ):

        results.append(

            weight <= limit

        )


    gross_ok = (

        report.total_weight
        <=
        truck.legal_gross_weight

    )


    return (

        all(results)

        and

        gross_ok

    )