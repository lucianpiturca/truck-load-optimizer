# ==========================================================
# axles.py
# Truck Load Optimizer
#
# Axle load calculation engine
# ==========================================================


from dataclasses import dataclass
from typing import List

from cargo import Pallet
from truck import Truck



# ==========================================================
# RESULT OBJECT
# ==========================================================


@dataclass
class AxleReport:


    axle_weights: List[float]


    total_weight: float


    cargo_weight: float


    centre_of_gravity: float



    legal: bool



    overweight_axles: List[int]



# ==========================================================
# TRAILER POSITION MODEL
# ==========================================================


def cargo_position(
    pallet: Pallet
):

    """
    Returns pallet centre position
    from trailer front.

    y is measured from front bulkhead.
    """


    return (

        pallet.y

        +

        pallet.draw_length / 2

    )



# ==========================================================
# WEIGHT DISTRIBUTION MODEL
# ==========================================================


def calculate_cargo_distribution(
    truck: Truck,
    pallets: List[Pallet]
):

    """
    Calculates how cargo weight reaches axles.

    The model uses:

    - tractor front/drive group
    - trailer tridem position

    Cargo in front of bogie transfers load forward.
    Cargo behind bogie transfers load rearward.
    """



    cargo_axles = [

        0.0,

        0.0,

        0.0,

        0.0,

        0.0

    ]



    bogie = truck.bogie_position



    total_cargo = 0



    weighted_position = 0



    for pallet in pallets:


        if not pallet.loaded:

            continue



        weight = pallet.weight



        position = cargo_position(

            pallet

        )


        total_cargo += weight



        weighted_position += (

            weight

            *

            position

        )



        # --------------------------------------------------
        # Simplified articulated vehicle load transfer
        #
        # Front of bogie:
        # affects drive axle group
        #
        # Rear of bogie:
        # affects trailer axles
        # --------------------------------------------------


        distance = position - bogie



        if distance < 0:


            # Cargo forward of bogie

            transfer = min(

                abs(distance) / bogie,

                1

            )


            cargo_axles[1] += (

                weight

                *

                0.45

                *

                transfer

            )


            trailer_share = (

                weight

                *

                (

                    1 -

                    0.45 * transfer

                )

            )



        else:


            # Cargo behind bogie

            transfer = min(

                distance /

                (

                    truck.trailer_length

                    -

                    bogie

                ),

                1

            )


            trailer_share = (

                weight

                *

                0.70

                *

                transfer

            )


            cargo_axles[1] += (

                weight

                -

                trailer_share

            )



        # distribute trailer load

        cargo_axles[2] += (

            trailer_share * 0.34

        )


        cargo_axles[3] += (

            trailer_share * 0.33

        )


        cargo_axles[4] += (

            trailer_share * 0.33

        )



    if total_cargo > 0:


        centre = (

            weighted_position

            /

            total_cargo

        )

    else:

        centre = 0



    return (

        cargo_axles,

        total_cargo,

        centre

    )



# ==========================================================
# MAIN AXLE CALCULATION
# ==========================================================


def calculate_axle_weights(

    truck: Truck,

    pallets: List[Pallet]

):


    cargo_axles, cargo_weight, cg = calculate_cargo_distribution(

        truck,

        pallets

    )



    axle_weights = []



    for empty, cargo in zip(

        truck.empty_axles,

        cargo_axles

    ):


        axle_weights.append(

            empty + cargo

        )



    total = sum(

        axle_weights

    )



    return AxleReport(

        axle_weights=axle_weights,

        total_weight=total,

        cargo_weight=cargo_weight,

        centre_of_gravity=cg,

        legal=True,

        overweight_axles=[]

    )



# ==========================================================
# LEGAL CHECK
# ==========================================================


def check_axle_legality(

    truck: Truck,

    report: AxleReport

):


    overweight = []



    for index, weight in enumerate(

        report.axle_weights

    ):


        if weight > truck.axle_limits[index]:


            overweight.append(

                index + 1

            )



    legal = (

        len(overweight) == 0

        and

        report.total_weight <= truck.legal_gross

    )



    report.legal = legal

    report.overweight_axles = overweight



    return report