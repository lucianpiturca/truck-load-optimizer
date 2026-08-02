# packing.py

from dataclasses import dataclass, field
from typing import List, Tuple

from cargo import Pallet
from truck import Truck


# ==========================================================
# DATA STRUCTURES
# ==========================================================

@dataclass
class FreeSpace:
    """
    Empty rectangular area inside trailer.

    Coordinates:
        x = distance from trailer front (m)
        y = distance from left side (m)
    """

    x: float
    y: float

    length: float
    width: float


@dataclass
class Placement:
    pallet_id: int

    x: float
    y: float

    length: float
    width: float

    rotated: bool


@dataclass
class Layout:

    pallets: List[Pallet] = field(default_factory=list)

    rejected: List[Pallet] = field(default_factory=list)

    used_length: float = 0.0

    used_area: float = 0.0


    def add(self, pallet):

        self.pallets.append(pallet)

        pallet.loaded = True



    def reject(self, pallet, reason):

        pallet.loaded = False

        pallet.reason_not_loaded = reason

        self.rejected.append(pallet)



    @property
    def pallet_count(self):

        return len(self.pallets)



# ==========================================================
# GEOMETRY FUNCTIONS
# ==========================================================


def rectangle_inside(
    x,
    y,
    length,
    width,
    trailer_length,
    trailer_width
):

    return (

        x >= 0

        and y >= 0

        and x + length <= trailer_length

        and y + width <= trailer_width

    )



def overlap(
    x1,
    y1,
    l1,
    w1,

    x2,
    y2,
    l2,
    w2
):

    """
    Rectangle collision detection.
    """

    if x1 + l1 <= x2:
        return False

    if x2 + l2 <= x1:
        return False

    if y1 + w1 <= y2:
        return False

    if y2 + w2 <= y1:
        return False


    return True



def pallet_dimensions(
    pallet: Pallet
) -> List[Tuple[float,float,bool]]:


    result = []


    result.append(
        (
            pallet.length,
            pallet.width,
            False
        )
    )


    if pallet.allow_rotation:

        result.append(
            (
                pallet.width,
                pallet.length,
                True
            )
        )


    return result



# ==========================================================
# VALIDATION
# ==========================================================


def pallet_height_ok(
    pallet,
    truck
):

    return (
        pallet.height <= truck.max_cargo_height
    )



def pallet_can_fit_anywhere(
    pallet,
    truck
):

    for length,width,_ in pallet_dimensions(pallet):

        if (
            length <= truck.internal_length
            and
            width <= truck.internal_width
        ):

            return True


    return False



# ==========================================================
# COLLISION CHECK
# ==========================================================


def position_is_free(
    pallet,
    x,
    y,
    length,
    width,
    layout
):

    for existing in layout.pallets:


        if overlap(

            x,
            y,
            length,
            width,

            existing.x,
            existing.y,

            existing.draw_length,
            existing.draw_width

        ):

            return False



    return True

# ==========================================================
# FREE SPACE MANAGEMENT
# ==========================================================


def split_free_space(
    space: FreeSpace,
    x,
    y,
    length,
    width
):

    """
    After placing a pallet, split the remaining
    rectangle into smaller free rectangles.

    Guillotine split:
    - area behind pallet
    - area beside pallet
    """

    spaces = []


    # Remaining length behind pallet

    if space.length > length:

        spaces.append(

            FreeSpace(

                x=x + length,

                y=y,

                length=space.length - length,

                width=space.width

            )

        )


    # Remaining width beside pallet

    if space.width > width:

        spaces.append(

            FreeSpace(

                x=x,

                y=y + width,

                length=length,

                width=space.width - width

            )

        )


    return spaces



def clean_free_spaces(
    spaces: List[FreeSpace]
):

    """
    Remove invalid spaces.
    """

    result = []


    for s in spaces:

        if (
            s.length > 0.001
            and
            s.width > 0.001
        ):

            result.append(s)


    return result



# ==========================================================
# PLACEMENT SEARCH
# ==========================================================


def find_position(
    pallet: Pallet,
    truck: Truck,
    layout: Layout,
    free_spaces: List[FreeSpace]
):

    """
    Find the first valid position.

    This is intentionally simple.
    Optimizer will later generate
    and compare many layouts.
    """


    candidates = []


    for space in free_spaces:


        for length, width, rotated in pallet_dimensions(pallet):


            if (

                length <= space.length

                and

                width <= space.width

            ):


                candidates.append(

                    (

                        space,

                        length,

                        width,

                        rotated

                    )

                )



    if not candidates:

        return None



    # Prefer:
    # 1. longest side forward
    # 2. smallest remaining space

    candidates.sort(

        key=lambda c:

            (

                c[0].y,

                c[0].x,

                -(c[1]*c[2])

            )

    )


    return candidates[0]



# ==========================================================
# PLACE ONE PALLET
# ==========================================================


def place_pallet(
    pallet: Pallet,
    placement,
    layout: Layout,
    free_spaces
):


    space, length, width, rotated = placement


    pallet.x = space.x

    pallet.y = space.y

    pallet.rotated = rotated



    layout.add(pallet)



    free_spaces.remove(space)



    new_spaces = split_free_space(

        space,

        pallet.x,

        pallet.y,

        length,

        width

    )


    free_spaces.extend(new_spaces)



    free_spaces[:] = clean_free_spaces(

        free_spaces

    )



# ==========================================================
# SORTING HELPERS
# ==========================================================


def sort_pallets_for_loading(
    pallets: List[Pallet]
):

    """
    Initial loading priority.

    Larger/heavier pallets first.
    Optimizer will later replace this
    with scoring.
    """

    return sorted(

        pallets,

        key=lambda p:

            (

                -(p.weight),

                -(p.area)

            )

    )



# ==========================================================
# BASIC PACKING ENGINE
# ==========================================================


def pack_layout(
    truck: Truck,
    pallets: List[Pallet]
):


    layout = Layout()


    free_spaces = [

        FreeSpace(

            x=0,

            y=0,

            length=truck.internal_length,

            width=truck.internal_width

        )

    ]



    ordered = sort_pallets_for_loading(

        pallets

    )



    for pallet in ordered:



        if not pallet_height_ok(
            pallet,
            truck
        ):

            layout.reject(

                pallet,

                "Cargo height exceeds trailer limit"

            )

            continue



        if not pallet_can_fit_anywhere(
            pallet,
            truck
        ):

            layout.reject(

                pallet,

                "Pallet dimensions exceed trailer dimensions"

            )

            continue



        placement = find_position(

            pallet,

            truck,

            layout,

            free_spaces

        )



        if placement is None:


            layout.reject(

                pallet,

                "Could not fit physically"

            )


        else:


            place_pallet(

                pallet,

                placement,

                layout,

                free_spaces

            )



    return layout

# ==========================================================
# LAYOUT STATISTICS
# ==========================================================


def calculate_layout_statistics(
    layout: Layout
):

    if not layout.pallets:

        layout.used_length = 0
        layout.used_area = 0

        return layout


    layout.used_length = max(

        p.y + p.draw_length

        for p in layout.pallets

    )


    layout.used_area = sum(

        p.area

        for p in layout.pallets

    )


    return layout



def floor_utilisation(
    layout: Layout,
    truck: Truck
):

    if truck.internal_length <= 0:
        return 0


    trailer_area = (

        truck.internal_length

        *

        truck.internal_width

    )


    return (

        layout.used_area

        /

        trailer_area

        *

        100

    )



# ==========================================================
# LAYOUT VALIDATION
# ==========================================================


def validate_layout(
    layout: Layout,
    truck: Truck
):

    errors = []


    for pallet in layout.pallets:


        if not pallet_height_ok(
            pallet,
            truck
        ):

            errors.append(

                f"{pallet.description}: "
                "height exceeds limit"

            )


        if not rectangle_inside(

            pallet.x,

            pallet.y,

            pallet.draw_length,

            pallet.draw_width,

            truck.internal_length,

            truck.internal_width

        ):

            errors.append(

                f"{pallet.description}: "
                "outside trailer"

            )



    return errors



# ==========================================================
# COPY / CLONE SUPPORT
# Used later by optimizer
# ==========================================================


def clone_layout(
    layout: Layout
):

    import copy


    return copy.deepcopy(layout)



# ==========================================================
# RESET PALLET STATUS
# ==========================================================


def reset_pallets(
    pallets
):

    for pallet in pallets:

        pallet.loaded = False

        pallet.x = 0

        pallet.y = 0

        pallet.rotated = False

        pallet.reason_not_loaded = ""



# ==========================================================
# PUBLIC API
# ==========================================================


def pack_pallets(
    truck: Truck,
    pallets
):

    """
    Main packing entry point.

    Input:
        truck object
        list[Pallet]

    Output:
        Layout object
    """


    reset_pallets(
        pallets
    )


    layout = pack_layout(

        truck,

        pallets

    )


    calculate_layout_statistics(

        layout

    )


    return layout
