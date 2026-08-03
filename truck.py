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


    # Trailer dimensions (metres)

    trailer_length: float

    trailer_width: float



    # Maximum combination weight

    legal_gross: float



    # Maximum axle weights kg

    axle_limits: list



    # Empty axle weights kg

    empty_axles: list



    # Tractor geometry

    # Steer axle -> drive axle

    wheelbase: float



    # Drive axle -> fifth wheel

    kingpin_to_drive_axle: float



    # Trailer geometry

    # Kingpin -> centre of tridem group

    bogie_position: float



    # Kingpin -> trailer front

    trailer_front_offset: float



# ==========================================================
# CURTAINSIDER
# Empty weight with fuel = 16,000 kg
# ==========================================================


CURTAINSIDER = Truck(

    name="Curtainsider",


    trailer_length=13.55,

    trailer_width=2.45,


    legal_gross=40000,


    axle_limits=[

        10000,   # Axle 1 steer

        11500,   # Axle 2 drive

        8000,    # Axle 3 trailer

        8000,    # Axle 4 trailer

        8000     # Axle 5 trailer

    ],



    empty_axles=[

        5190,    # Axle 1 steer

        2800,    # Axle 2 drive

        2670,    # Axle 3

        2670,    # Axle 4

        2670     # Axle 5

    ],



    wheelbase=3.60,


    kingpin_to_drive_axle=0.90,


    bogie_position=7.60,


    trailer_front_offset=1.60

)



# ==========================================================
# FRIGO
# Empty weight with fuel = 18,000 kg
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

        5380,    # Axle 1 steer

        3800,    # Axle 2 drive

        2940,    # Axle 3

        2940,    # Axle 4

        2940     # Axle 5

    ],



    wheelbase=3.60,


    kingpin_to_drive_axle=0.90,


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