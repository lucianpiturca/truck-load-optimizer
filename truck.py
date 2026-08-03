# ==========================================================
# truck.py
# Truck Load Optimizer
# Vehicle definitions
# ==========================================================


from dataclasses import dataclass



# ==========================================================
# TRUCK MODEL
# ==========================================================


@dataclass
class Truck:


    name: str


    # Trailer dimensions

    trailer_length: float

    trailer_width: float



    # Legal limits

    legal_gross: float


    axle_limits: list



    # Empty axle weights

    empty_axles: list



    # Geometry

    wheelbase: float


    kingpin_to_drive_axle: float


    bogie_position: float


    trailer_front_offset: float



# ==========================================================
# STANDARD EUROPEAN CURTAINSIDER
# ==========================================================


CURTAINSIDER = Truck(


    name="Curtainsider",



    # 13.6m semi trailer

    trailer_length=13.60,


    trailer_width=2.45,



    # Typical EU combination

    legal_gross=40000,



    # 5 axle combination

    axle_limits=[

        10000,   # Steer axle

        11500,   # Drive axle

        8000,    # Trailer axle 1

        8000,    # Trailer axle 2

        8000     # Trailer axle 3

    ],



    # Empty vehicle axle weights

    # tractor + empty trailer

    empty_axles=[

        5200,

        2800,

        2670,

        2670,

        2670

    ],



    # Tractor geometry

    # Front axle -> drive axle

    wheelbase=3.60,



    # Drive axle -> fifth wheel

    kingpin_to_drive_axle=0.90,



    # Trailer kingpin -> tridem centre

    bogie_position=7.60,



    # Kingpin is ahead of trailer floor

    trailer_front_offset=1.60

)



# ==========================================================
# OPTIONAL OTHER TRUCKS
# ==========================================================


FRIGO = Truck(


    name="Frigo",


    trailer_length=13.60,


    trailer_width=2.45,


    legal_gross=40000,


    axle_limits=[

        10000,

        11500,

        8000,

        8000,

        8000

    ],


    empty_axles=[

        5300,

        2900,

        2750,

        2750,

        2750

    ],


    wheelbase=3.70,


    kingpin_to_drive_axle=0.95,


    bogie_position=7.60,


    trailer_front_offset=1.60

)



# ==========================================================
# AVAILABLE TRUCKS
# ==========================================================


TRUCKS = {


    "Curtainsider": CURTAINSIDER,


    "Frigo": FRIGO

}