# ==========================================================
# axles.py
# Truck Load Optimizer
# Axle load calculation
# ==========================================================


from typing import List



# ==========================================================
# BASIC HELPERS
# ==========================================================


def pallet_position(pallet):

    """
    Returns pallet centre position in metres
    from trailer front.

    """

    return (

        pallet.y

        +

        pallet.draw_length / 2

    )



def trailer_to_bogie_distance(truck):

    """
    Distance from trailer front
    to centre of tridem bogie.

    """

    return truck.bogie_position



# ==========================================================
# CARGO MOMENT
# ==========================================================


def cargo_moment(

    pallets

):

    """

    Total cargo moment around trailer front.

    """

    moment = 0


    weight = 0


    for pallet in pallets:


        pos = pallet_position(

            pallet

        )


        moment += (

            pallet.weight

            *

            pos

        )


        weight += pallet.weight


    return weight, moment



# ==========================================================
# TRAILER BOGIE LOAD
# ==========================================================


def calculate_trailer_bogie_load(

    truck,

    pallets

):

    """

    Calculates how much cargo weight
    reaches the trailer bogie.

    """

    total_weight, moment = cargo_moment(

        pallets

    )


    if total_weight == 0:

        return 0



    cg = moment / total_weight



    bogie = truck.bogie_position



    # Simple supported beam model:
    #
    # front support = kingpin
    # rear support = bogie centre
    #

    bogie_share = (

        total_weight

        *

        cg

        /

        bogie

    )


    return min(

        total_weight,

        max(

            0,

            bogie_share

        )

    )



# ==========================================================
# KINGPIN LOAD
# ==========================================================


def calculate_kingpin_load(

    truck,

    pallets

):


    total_weight, moment = cargo_moment(

        pallets

    )


    if total_weight == 0:

        return 0



    bogie_load = calculate_trailer_bogie_load(

        truck,

        pallets

    )


    kingpin = (

        total_weight

        -

        bogie_load

    )


    return max(

        0,

        kingpin

    )



# ==========================================================
# TRACTOR AXLES
# ==========================================================


def calculate_tractor_axles(

    truck,

    kingpin_load

):

    """

    Splits kingpin load between:

    axle 1

    axle 2


    Based on European 4x2 tractor geometry.

    """



    wheelbase = truck.wheelbase



    distance_from_front_axle = (

        truck.kingpin_offset

    )


    front_share = (

        kingpin_load

        *

        (

            wheelbase

            -

            distance_from_front_axle

        )

        /

        wheelbase

    )


    drive_share = (

        kingpin_load

        -

        front_share

    )


    return (

        front_share,

        drive_share

    )



# ==========================================================
# TRAILER AXLES
# ==========================================================


def calculate_trailer_axles(

    truck,

    bogie_load

):

    """

    Splits tridem bogie load equally.

    """

    each = (

        bogie_load / 3

    )


    return [

        each,

        each,

        each

    ]



# ==========================================================
# MAIN FUNCTION
# ==========================================================


def calculate_axle_weights(

    truck,

    pallets

):


    cargo_weight, _ = cargo_moment(

        pallets

    )


    kingpin = calculate_kingpin_load(

        truck,

        pallets

    )


    bogie = calculate_trailer_bogie_load(

        truck,

        pallets

    )



    tractor_front, tractor_drive = calculate_tractor_axles(

        truck,

        kingpin

    )


    trailer_axles = calculate_trailer_axles(

        truck,

        bogie

    )



    empty = truck.empty_axles



    axle_values = [

        empty[0] + tractor_front,

        empty[1] + tractor_drive,

        empty[2] + trailer_axles[0],

        empty[3] + trailer_axles[1],

        empty[4] + trailer_axles[2]

    ]



    report = {}



    for i, value in enumerate(axle_values):


        report[f"Axle {i+1}"] = {

            "weight": value,

            "limit": truck.axle_limits[i]

        }



    total = sum(

        axle_values

    )



    report["total"] = total



    if cargo_weight:

        report["centre_of_gravity"] = (

            cargo_moment(pallets)[1]

            /

            cargo_weight

        )

    else:

        report["centre_of_gravity"] = 0



    return report