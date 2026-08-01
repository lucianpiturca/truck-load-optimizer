# axles.py

from dataclasses import dataclass



@dataclass
class AxleReport:

    axles: list

    total_weight: float



# ==========================================================
# European 4x2 tractor + 3 axle semi-trailer model
# ==========================================================

TRACTOR_TARE_FRONT = 6000     # kg on steering axle
TRACTOR_TARE_REAR = 5000      # kg on drive axle

TRAILER_TARE_TOTAL = 7000     # kg

TRAILER_AXLE_SHARE = [
    0.33,
    0.33,
    0.34
]


# distances from kingpin (metres)

DRIVE_AXLE_POSITION = -3.0

TRAILER_AXLE_POSITIONS = [
    9.8,
    11.0,
    12.2
]



def calculate_axle_weights(

    truck,

    pallets

):


    #
    # Start with empty vehicle
    #

    axle_weights = [

        float(TRACTOR_TARE_FRONT),

        float(TRACTOR_TARE_REAR),

        float(TRAILER_TARE_TOTAL * 0.33),

        float(TRAILER_TARE_TOTAL * 0.33),

        float(TRAILER_TARE_TOTAL * 0.34)

    ]



    #
    # Add pallet loads
    #

    for pallet in pallets:


        if not getattr(

            pallet,

            "loaded",

            True

        ):

            continue



        weight = pallet.weight



        #
        # pallet centre position
        #

        pallet_position = (

            pallet.y

            +

            pallet.length / 2

        )



        #
        # load split
        #
        # Front of trailer:
        # more tractor load
        #
        # Rear:
        # more trailer load
        #


        if pallet_position <= 4:


            tractor_share = 0.35


        elif pallet_position <= 8:


            tractor_share = 0.20


        else:


            tractor_share = 0.10



        trailer_share = 1 - tractor_share



        #
        # Tractor distribution
        #

        axle_weights[0] += (

            weight

            *

            tractor_share

            *

            0.35

        )


        axle_weights[1] += (

            weight

            *

            tractor_share

            *

            0.65

        )



        #
        # Trailer axle group
        #

        trailer_weight = (

            weight

            *

            trailer_share

        )


        for i, share in enumerate(

            TRAILER_AXLE_SHARE

        ):


            axle_weights[i+2] += (

                trailer_weight

                *

                share

            )



    total = sum(axle_weights)



    return AxleReport(

        axles=[

            round(x,0)

            for x in axle_weights

        ],

        total_weight=round(

            total,

            0

        )

    )