# ==========================================================
# cargo.py
# Truck Load Optimizer
#
# Cargo definitions and pallet objects
# ==========================================================


from dataclasses import dataclass, field
from typing import List
import copy



# ==========================================================
# CARGO INPUT OBJECT
# ==========================================================


@dataclass
class CargoItem:

    """
    User entered cargo.

    Example:

    Description:
        Paper rolls

    Quantity:
        10

    Size:
        1.20 x 0.80 x 1.50 m

    Weight:
        1000 kg
    """


    description: str

    quantity: int


    length: float

    width: float

    height: float


    weight: float


    allow_rotation: bool = True



    def validate(self, truck):

        errors = []


        if self.length <= 0:

            errors.append(
                "Length must be positive"
            )


        if self.width <= 0:

            errors.append(
                "Width must be positive"
            )


        if self.height <= 0:

            errors.append(
                "Height must be positive"
            )


        if self.weight <= 0:

            errors.append(
                "Weight must be positive"
            )


        # physical check

        # Height is profile-specific because refrigerated trailers have a
        # lower usable internal clearance than curtainsiders.
        trailer_height = getattr(truck, "trailer_height", None)

        fits_normal = (

            self.length <= truck.trailer_length
            and
            self.width <= truck.trailer_width
            and
            (
                trailer_height is None
                or self.height <= trailer_height
            )

        )


        fits_rotated = (

            self.width <= truck.trailer_length
            and
            self.length <= truck.trailer_width
            and
            (
                trailer_height is None
                or self.height <= trailer_height
            )

        )


        if not fits_normal and not fits_rotated:

            errors.append(

                "Cargo dimensions exceed trailer"

            )


        return errors



# ==========================================================
# PALLET OBJECT
# ==========================================================


@dataclass
class Pallet:


    id: int


    description: str


    length: float

    width: float

    height: float


    weight: float


    allow_rotation: bool = True



    # ------------------------------------------------------
    # Loading status
    # ------------------------------------------------------

    loaded: bool = False


    rotated: bool = False



    # position inside trailer

    x: float = 0.0

    y: float = 0.0



    # reason if rejected

    reason_not_loaded: str = ""



    # ======================================================
    # Geometry helpers
    # ======================================================


    @property
    def area(self):

        return (

            self.length

            *

            self.width

        )



    @property
    def draw_length(self):

        if self.rotated:

            return self.width

        return self.length



    @property
    def draw_width(self):

        if self.rotated:

            return self.length

        return self.width



    @property
    def centre_y(self):

        return (

            self.y

            +

            self.draw_length / 2

        )



    @property
    def centre_x(self):

        return (

            self.x

            +

            self.draw_width / 2

        )



    # ======================================================
    # Rotation
    # ======================================================


    def rotate(self):

        if self.allow_rotation:

            self.rotated = not self.rotated



    def clone(self):

        return copy.deepcopy(self)



# ==========================================================
# CREATE PALLETS FROM CARGO
# ==========================================================


def expand_cargo(
    cargo_items: List[CargoItem]
):


    pallets = []


    pallet_id = 1



    for item in cargo_items:


        for number in range(

            item.quantity

        ):


            pallets.append(

                Pallet(

                    id=pallet_id,

                    description=item.description,

                    length=item.length,

                    width=item.width,

                    height=item.height,

                    weight=item.weight,

                    allow_rotation=item.allow_rotation

                )

            )


            pallet_id += 1



    return pallets



# ==========================================================
# UTILITY FUNCTIONS
# ==========================================================


def total_weight(
    pallets: List[Pallet]
):

    return sum(

        p.weight

        for p in pallets

    )



def loaded_weight(
    pallets: List[Pallet]
):

    return sum(

        p.weight

        for p in pallets

        if p.loaded

    )



def clone_pallets(
    pallets: List[Pallet]
):

    return [

        p.clone()

        for p in pallets

    ]
