from dataclasses import dataclass
from typing import List


# ==========================================================
# CARGO ITEM (User input)
# ==========================================================

@dataclass
class CargoItem:
    """
    One line entered by the user.

    Example:
        10 pallets
        120 x 80
        1200 kg each
    """

    description: str

    quantity: int

    length: float      # metres
    width: float       # metres
    height: float      # metres

    weight: float      # kg per pallet

    allow_rotation: bool = True

    def validate(self, truck=None):

        errors = []

        if self.quantity <= 0:
            errors.append("Quantity must be greater than zero.")

        if self.length <= 0:
            errors.append("Length must be greater than zero.")

        if self.width <= 0:
            errors.append("Width must be greater than zero.")

        if self.height <= 0:
            errors.append("Height must be greater than zero.")

        if self.weight <= 0:
            errors.append("Weight must be greater than zero.")

        if truck is not None:

            if self.height > truck.max_cargo_height:

                errors.append(
                    f"Height ({self.height:.2f} m) exceeds "
                    f"{truck.name} maximum cargo height "
                    f"({truck.max_cargo_height:.2f} m)."
                )

            if (
                self.length > truck.internal_length
                and
                self.width > truck.internal_length
            ):

                errors.append(
                    "Pallet is longer than trailer."
                )

            if (
                self.width > truck.internal_width
                and
                self.length > truck.internal_width
            ):

                errors.append(
                    "Pallet is wider than trailer."
                )

        return errors


# ==========================================================
# INDIVIDUAL PALLET
# ==========================================================

@dataclass
class Pallet:
    """
    One physical pallet.
    """

    id: int

    description: str

    length: float
    width: float
    height: float

    weight: float

    allow_rotation: bool = True

    # Placement
    x: float = 0.0
    y: float = 0.0

    rotated: bool = False

    loaded: bool = False

    # Optional optimizer metadata
    score: float = 0.0

    reason_not_loaded: str = ""

    @property
    def draw_width(self):

        return self.length if self.rotated else self.width

    @property
    def draw_length(self):

        return self.width if self.rotated else self.length

    @property
    def centre_x(self):

        return self.x + self.draw_width / 2

    @property
    def centre_y(self):

        return self.y + self.draw_length / 2

    @property
    def area(self):

        return self.length * self.width

    @property
    def volume(self):

        return self.length * self.width * self.height

    def rotate(self):

        if self.allow_rotation:

            self.rotated = not self.rotated


# ==========================================================
# EXPAND USER CARGO INTO INDIVIDUAL PALLETS
# ==========================================================

def expand_cargo(cargo: List[CargoItem]) -> List[Pallet]:

    pallets = []

    pallet_id = 1

    for item in cargo:

        for _ in range(item.quantity):

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