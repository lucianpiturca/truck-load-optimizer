# axles.py

from dataclasses import dataclass
from typing import List

from cargo import Pallet
from truck import Truck



# ==========================================================
# RESULT STRUCTURES
# ==========================================================

@dataclass
class AxleResult:

    axle_number: int

    weight: float

    limit: float

    overloaded: bool



@dataclass
class AxleReport:

    axles: List[AxleResult]

    total_weight: float

    legal_total: bool

    centre_of_gravity: float



    @property
    def legal_axles(self):

        return all(

            not axle.overloaded

            for axle in self.axles

        )



# ==========================================================
# AXLE CALCULATION
# ==========================================================


def calculate_axle_weights(

    truck: Truck,

    pallets: List[Pallet]

):

    """
    Calculate final axle weights.

    European semi-trailer model:

    Tractor:
        Axle 1 steering
        Axle 2 drive

    Trailer:
        Axles 3-4-5 bogie


    Cargo position affects:
        - kingpin load
        - trailer bogie load

    """



    # Start with empty truck

    axle_weights = list(

        truck.empty_axles

    )



    total_cargo_weight = sum(

        pallet.weight

        for pallet in pallets

        if pallet.loaded

    )



    trailer_load = 0

    kingpin_load = 0



    weighted_position = 0



    # ------------------------------------------------------
    # Cargo distribution
    # ------------------------------------------------------


    for pallet in pallets:


        if not pallet.loaded:

            continue



        weight = pallet.weight



        # pallet centre position
        # measured from trailer front

        pallet_position = (

            pallet.y

            +

            pallet.length / 2

        )



        weighted_position += (

            pallet_position

            *

            weight

        )



        # convert to distance from kingpin

        distance_from_kingpin = (

            pallet_position

            -

            truck.trailer_front_offset

        )



        if distance_from_kingpin < 0:

            distance_from_kingpin = 0



        if distance_from_kingpin > truck.trailer_length:

            distance_from_kingpin = truck.trailer_length



        # --------------------------------------------------
        # Load transfer model
        #
        # Front pallets:
        # more kingpin
        #
        # Rear pallets:
        # more trailer axles
        # --------------------------------------------------


        kingpin_ratio = (

            0.55

            -

            (

                distance_from_kingpin

                /

                truck.trailer_length

            )

            *

            0.20

        )



        kingpin_ratio = max(

            0.35,

            min(

                0.55,

                kingpin_ratio

            )

        )



        kingpin_load += (

            weight

            *

            kingpin_ratio

        )



        trailer_load += (

            weight

            *

            (

                1

                -

                kingpin_ratio

            )

        )



    # ------------------------------------------------------
    # Tractor distribution
    # ------------------------------------------------------

    axle_weights[0] += (

        kingpin_load

        *

        0.10

    )


    axle_weights[1] += (

        kingpin_load

        *

        0.90

    )



    # ------------------------------------------------------
    # Trailer bogie
    # ------------------------------------------------------

    axle_weights[2] += trailer_load / 3

    axle_weights[3] += trailer_load / 3

    axle_weights[4] += trailer_load / 3



    # ------------------------------------------------------
    # Centre of gravity
    # ------------------------------------------------------

    if total_cargo_weight > 0:

        centre_of_gravity = (

            weighted_position

            /

            total_cargo_weight

        )

    else:

        centre_of_gravity = 0



    return AxleReport(

        axles=[

            AxleResult(

                axle_number=i+1,

                weight=round(

                    axle_weights[i],

                    1

                ),

                limit=truck.axle_limits[i],

                overloaded=(

                    axle_weights[i]

                    >

                    truck.axle_limits[i]

                )

            )

            for i in range(5)

        ],

        total_weight=round(

            sum(axle_weights),

            1

        ),

        legal_total=(

            sum(axle_weights)

            <=

            truck.legal_gross

        ),

        centre_of_gravity=round(

            centre_of_gravity,

            2

        )

    )



# ==========================================================
# HELPER FUNCTIONS
# ==========================================================


def is_legal(report: AxleReport):

    return (

        report.legal_axles

        and

        report.legal_total

    )



def axle_score(report: AxleReport):

    """

    Score used later by optimizer.

    Higher = better.

    """

    score = 100



    for axle in report.axles:

        usage = (

            axle.weight

            /

            axle.limit

        )



        if usage > 1:

            score -= (

                usage - 1

            ) * 200



        else:

            # reward balanced loading

            score -= abs(

                0.75 - usage

            ) * 10



    if not report.legal_total:

        score -= 200



    return round(

        score,

        2

    )