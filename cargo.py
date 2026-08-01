from dataclasses import dataclass
from typing import List


@dataclass
class CargoItem:
    """
    Cargo entered by the user.

    One CargoItem may represent multiple identical pallets.
    """

    description: str

    quantity: int

    width: float      # metres
    length: float     # metres
    height: float     # metres

    weight: float     # kg

    allow_rotation: bool = True


@dataclass
class Pallet:
    """
    Individual pallet generated from a CargoItem.
    """

    id: int

    description: str

    width: float

    length: float

    height: float

    weight: float

    allow_rotation: bool

    rotated: bool = False

    x: float = 0.0

    y: float = 0.0

    loaded: bool = False

    reject_reason: str = ""


def expand_manifest(cargo: List[CargoItem]) -> List[Pallet]:
    """
    Converts the cargo list into individual pallets.
    """

    pallets = []

    pallet_id = 1

    for item in cargo:

        for _ in range(item.quantity):

            pallets.append(

                Pallet(

                    id=pallet_id,

                    description=item.description,

                    width=item.width,

                    length=item.length,

                    height=item.height,

                    weight=item.weight,

                    allow_rotation=item.allow_rotation

                )

            )

            pallet_id += 1

    return pallets