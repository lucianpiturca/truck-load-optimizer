# ==========================================================
# axles.py
# Truck Load Optimizer
# Axle weight calculation
# ==========================================================


def get_pallet_centre_from_kingpin(

    truck,

    pallet

):

    """
    Pallet centre position measured from kingpin.

    Trailer front is behind the kingpin by
    trailer_front_offset.
    """

    return (

        pallet.y

        +

        pallet.draw_length / 2

        -

        truck.trailer_front_offset

    )



# ==========================================================
# CARGO CENTRE OF GRAVITY
# ==========================================================


def calculate_cargo_cg(

    truck,

    pallets

):


    if not pallets:

        return 0



    total_weight = sum(

        p.weight

        for p in pallets

    )


    if total_weight == 0:

        return 0



    moment = 0



    for pallet in pallets:


        position = get_pallet_centre_from_kingpin(

            truck,

            pallet

        )


        moment += (

            pallet.weight

            *

            position

        )



    return moment / total_weight



# ==========================================================
# TRAILER SUPPORT REACTIONS
# ==========================================================


def calculate_kingpin_and_bogie_load(

    truck,

    pallets

):

    """

    Trailer is treated as a beam:

    Kingpin support = 0m

    Bogie support = bogie_position


    """



    cargo_weight = sum(

        p.weight

        for p in pallets

    )


    if cargo_weight == 0:

        return 0, 0



    cg = calculate_cargo_cg(

        truck,

        pallets

    )



    bogie_distance = truck.bogie_position



    bogie_load = (

        cargo_weight

        *

        cg

        /

        bogie_distance

    )



    kingpin_load = (

        cargo_weight

        -

        bogie_load

    )



    # safety limits

    bogie_load = max(

        0,

        min(

            cargo_weight,

            bogie_load

        )

    )


    kingpin_load = (

        cargo_weight

        -

        bogie_load

    )


    return (

        kingpin_load,

        bogie_load

    )



# ==========================================================
# TRACTOR AXLES
# ==========================================================


def calculate_tractor_distribution(

    truck,

    kingpin_load

):

    """

    Kingpin load split between tractor axles.

    """



    wheelbase = truck.wheelbase



    kingpin_distance = truck.kingpin_offset



    front_load = (

        kingpin_load

        *

        (

            wheelbase

            -

            kingpin_distance

        )

        /

        wheelbase

    )


    drive_load = (

        kingpin_load

        -

        front_load

    )


    return (

        front_load,

        drive_load

    )



# ==========================================================
# TRAILER TRIDEM
# ==========================================================


def calculate_tridem_distribution(

    bogie_load

):

    """

    Equal tridem axle distribution.

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
# MAIN API
# ==========================================================


def calculate_axle_weights(

    truck,

    pallets

):


    kingpin, bogie = calculate_kingpin_and_bogie_load(

        truck,

        pallets

    )


    front, drive = calculate_tractor_distribution(

        truck,

        kingpin

    )


    tridem = calculate_tridem_distribution(

        bogie

    )



    axle_weights = [

        truck.empty_axles[0] + front,

        truck.empty_axles[1] + drive,

        truck.empty_axles[2] + tridem[0],

        truck.empty_axles[3] + tridem[1],

        truck.empty_axles[4] + tridem[2]

    ]



    report = {}



    for i, weight in enumerate(axle_weights):


        report[f"Axle {i+1}"] = {

            "weight": weight,

            "limit": truck.axle_limits[i]

        }



    report["total"] = sum(

        axle_weights

    )



    report["centre_of_gravity"] = calculate_cargo_cg(

        truck,

        pallets

    )



    return report