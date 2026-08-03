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


    # Usable internal trailer dimensions (metres)

    trailer_length: float

    trailer_width: float

    # Maximum internal cargo height (metres)

    trailer_height: float

    # Overall external trailer length (metres).  This is reference data;
    # packing must use trailer_length above.

    external_trailer_length: float



    # Maximum combination weight

    legal_gross: float



    # Maximum axle weights kg

    axle_limits: list



    # Empty axle weights kg

    empty_axles: list



    # Tractor geometry

    # Steer axle -> drive axle

    wheelbase: float



    # Drive axle -> fifth wheel (metres).  A fifth wheel 0.60 m ahead of
    # the drive axle on a 3.60 m wheelbase gives a 1/6 steer, 5/6 drive
    # static transfer of kingpin load.

    kingpin_to_drive_axle: float



    # Trailer geometry

    # Kingpin -> centre of tridem group

    bogie_position: float



    # Kingpin -> trailer front

    trailer_front_offset: float

    # Verified centre of gravity of a uniformly distributed payload,
    # measured behind the kingpin.  This is reference data for validating
    # the vehicle profile; individual pallet CGs are calculated directly.

    uniform_payload_cg: float

    @property
    def kingpin_to_rear_bulkhead(self):

        return self.trailer_length - self.trailer_front_offset

    @property
    def kingpin_steer_fraction(self):

        return self.kingpin_to_drive_axle / self.wheelbase



# ==========================================================
# CURTAINSIDER
# Empty weight with fuel = 16,000 kg
# ==========================================================


CURTAINSIDER = Truck(

    name="Curtainsider",


    # Confirmed usable internal loading length.
    trailer_length=13.55,

    trailer_width=2.45,

    trailer_height=2.68,

    external_trailer_length=13.62,


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


    kingpin_to_drive_axle=0.60,


    bogie_position=7.70,


    trailer_front_offset=1.60,

    uniform_payload_cg=5.20

)



# ==========================================================
# FRIGO
# Empty weight with fuel = 18,000 kg
# ==========================================================


FRIGO = Truck(

    name="Frigo",


    trailer_length=13.31,

    trailer_width=2.45,

    trailer_height=2.45,

    external_trailer_length=13.68,


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


    kingpin_to_drive_axle=0.60,


    bogie_position=7.70,


    trailer_front_offset=1.68,

    uniform_payload_cg=5.02

)



# ==========================================================
# AVAILABLE TRUCKS
# ==========================================================


TRUCKS = {

    "Curtainsider": CURTAINSIDER,

    "Frigo": FRIGO

}
