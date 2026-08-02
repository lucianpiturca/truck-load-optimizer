# ==========================================================
# truck.py
# Truck Load Optimizer
#
# Single source of truth for vehicle geometry
# ==========================================================


from dataclasses import dataclass
from typing import List



# ==========================================================
# TRUCK MODEL
# ==========================================================


@dataclass
class Truck:


    name: str


    # ------------------------------------------------------
    # Internal trailer dimensions
    # ------------------------------------------------------

    trailer_length: float

    trailer_width: float

    trailer_height: float



    # ------------------------------------------------------
    # Legal limits
    # ------------------------------------------------------

    legal_gross: float



    # ------------------------------------------------------
    # Axles
    #
    # Order:
    # 1 - steer axle
    # 2 - drive axle
    # 3 - trailer axle 1
    # 4 - trailer axle 2
    # 5 - trailer axle 3
    # ------------------------------------------------------

    empty_axles: List[float]

    axle_limits: List[float]



    # ------------------------------------------------------
    # Vehicle geometry
    # ------------------------------------------------------

    wheelbase: float

    kingpin_offset: float

    bogie_position: float

    trailer_front_offset: float



    colour: str = "#f2f2f2"



    # ======================================================
    # Compatibility aliases
    # ======================================================


    @property
    def internal_length(self):

        return self.trailer_length



    @property
    def internal_width(self):

        return self.trailer_width



    @property
    def internal_height(self):

        return self.trailer_height



    @property
    def max_cargo_height(self):

        return self.trailer_height



    # ======================================================
    # Geometry helpers
    # ======================================================


    @property
    def kingpin_to_front(self):

        """
        Distance:
        kingpin -> trailer front bulkhead
        """

        return self.trailer_front_offset



    @property
    def kingpin_to_bogie(self):

        """
        Distance:
        kingpin -> centre of tridem bogie
        """

        return self.bogie_position



    @property
    def rear_overhang(self):

        """
        Distance:
        bogie centre -> rear doors

        """

        return (

            self.trailer_length

            -

            self.bogie_position

            -

            self.trailer_front_offset

        )



# ==========================================================
# CURTAINSIDER
# ==========================================================


CURTAINSIDER = Truck(


    name="Curtainsider",



    # Internal floor:
    # industry usable length
    trailer_length=13.62,

    trailer_width=2.48,

    trailer_height=2.70,



    legal_gross=40000,



    # Empty truck with fuel

    empty_axles=[

        5200,

        2800,

        2670,

        2670,

        2670

    ],



    axle_limits=[

        10000,

        11500,

        8000,

        8000,

        8000

    ],



    # European articulated geometry

    wheelbase=3.60,


    # kingpin position relative to tractor

    kingpin_offset=0.90,


    # kingpin -> tridem centre

    bogie_position=7.60,


    # kingpin -> front bulkhead

    trailer_front_offset=1.60,



    colour="#f2f2f2"

)



# ==========================================================
# FRIGO
# ==========================================================


FRIGO = Truck(


    name="Frigo",



    trailer_length=13.41,

    trailer_width=2.45,


    # 20cm reserved for refrigeration system

    trailer_height=2.40,



    legal_gross=40000,



    # Empty truck with fuel

    empty_axles=[

        5400,

        3800,

        2940,

        2940,

        2940

    ],



    axle_limits=[

        10000,

        11500,

        8000,

        8000,

        8000

    ],



    wheelbase=3.60,


    kingpin_offset=0.90,


    bogie_position=7.60,


    trailer_front_offset=1.60,



    colour="#e8f4ff"

)



# ==========================================================
# AVAILABLE TRUCKS
# ==========================================================


TRUCKS = {

    "Curtainsider": CURTAINSIDER,

    "Frigo": FRIGO

}