# packing.py

from dataclasses import dataclass
from typing import List, Optional

from cargo import Pallet
from truck import Truck


# ==========================================================
# FREE SPACE
# ==========================================================

@dataclass
class FreeRectangle:
    """
    Empty rectangular area inside trailer floor.

    Coordinates:
    x = across trailer width
    y = trailer length direction
    """

    x: float
    y: float

    width: float
    length: float


    @property
    def area(self):
        return self.width * self.length



# ==========================================================
# PALLET PLACEMENT OPTION
# ==========================================================

@dataclass
class Placement:

    rectangle: FreeRectangle

    width: float

    length: float

    rotated: bool

    score: float



# ==========================================================
# COMPLETE LAYOUT RESULT
# ==========================================================

@dataclass
class LayoutResult:

    pallets: List[Pallet]

    used_length: float

    free_length: float

    utilisation: float

    score: float = 0



# ==========================================================
# PACKING ENGINE
# ==========================================================

class PackingEngine:


    def __init__(self, truck: Truck):

        self.truck = truck

        self.reset()



    # ------------------------------------------------------

    def reset(self):

        """
        Start with entire trailer floor available.
        """

        self.free_spaces = [

            FreeRectangle(

                x=0,

                y=0,

                width=self.truck.trailer_width,

                length=self.truck.trailer_length

            )

        ]


        self.loaded_pallets = []



    # ------------------------------------------------------

    def can_place(
        self,
        rectangle,
        width,
        length
    ):

        return (

            width <= rectangle.width

            and

            length <= rectangle.length

        )



    # ------------------------------------------------------

    def find_best_position(
        self,
        pallet: Pallet
    ) -> Optional[Placement]:

        """
        Search every available rectangle.

        Try:

        1. normal pallet orientation

        2. rotated orientation

        Select lowest wasted space.
        """


        best = None



        for space in self.free_spaces:



            # -----------------------------
            # Normal orientation
            # -----------------------------

            if self.can_place(

                space,

                pallet.width,

                pallet.length

            ):


                waste = (

                    space.area

                    -

                    pallet.width * pallet.length

                )


                candidate = Placement(

                    rectangle=space,

                    width=pallet.width,

                    length=pallet.length,

                    rotated=False,

                    score=waste

                )


                if (

                    best is None

                    or

                    candidate.score < best.score

                ):

                    best = candidate



            # -----------------------------
            # Rotated orientation
            # -----------------------------

            if pallet.allow_rotation:


                if self.can_place(

                    space,

                    pallet.length,

                    pallet.width

                ):


                    waste = (

                        space.area

                        -

                        pallet.width * pallet.length

                    )


                    candidate = Placement(

                        rectangle=space,

                        width=pallet.length,

                        length=pallet.width,

                        rotated=True,

                        score=waste

                    )


                    if (

                        best is None

                        or

                        candidate.score < best.score

                    ):

                        best = candidate



        return best



    # ------------------------------------------------------

    def split_space(
        self,
        used_space: FreeRectangle,
        pallet_width,
        pallet_length
    ):

        """
        Split remaining area after pallet placement.
        """


        self.free_spaces.remove(
            used_space
        )


        # Space to the right

        right_width = (

            used_space.width

            -

            pallet_width

        )


        if right_width > 0:


            self.free_spaces.append(

                FreeRectangle(

                    x=

                    used_space.x + pallet_width,

                    y=

                    used_space.y,

                    width=

                    right_width,

                    length=

                    pallet_length

                )

            )



        # Space behind pallet

        back_length = (

            used_space.length

            -

            pallet_length

        )


        if back_length > 0:


            self.free_spaces.append(

                FreeRectangle(

                    x=

                    used_space.x,

                    y=

                    used_space.y + pallet_length,

                    width=

                    used_space.width,

                    length=

                    back_length

                )

            )



    # ------------------------------------------------------

    def place_pallet(
        self,
        pallet: Pallet
    ):


        placement = self.find_best_position(
            pallet
        )


        if placement is None:

            return False



        if placement.rotated:

            pallet.width, pallet.length = (

                pallet.length,

                pallet.width

            )


            pallet.rotated = True



        pallet.x = placement.rectangle.x

        pallet.y = placement.rectangle.y

        pallet.loaded = True



        self.loaded_pallets.append(
            pallet
        )


        self.split_space(

            placement.rectangle,

            placement.width,

            placement.length

        )


        return True



    # ------------------------------------------------------

    def get_used_length(self):


        if not self.loaded_pallets:

            return 0



        return max(

            pallet.y + pallet.length

            for pallet in self.loaded_pallets

        )



    # ------------------------------------------------------

    def get_result(self):


        used = self.get_used_length()


        return LayoutResult(

            pallets=self.loaded_pallets,

            used_length=used,

            free_length=max(

                0,

                self.truck.trailer_length - used

            ),

            utilisation=sum(

                p.width * p.length

                for p in self.loaded_pallets

            )

            /

            (

                self.truck.trailer_width

                *

                self.truck.trailer_length

            )

        )



# ==========================================================
# PUBLIC FUNCTION
# ==========================================================


def pack_pallets(

    truck: Truck,

    pallets: List[Pallet]

):


    engine = PackingEngine(
        truck
    )


    for pallet in pallets:

        engine.place_pallet(
            pallet
        )


    return engine.get_result()