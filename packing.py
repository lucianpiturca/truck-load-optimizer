# ==========================================================
# packing.py
# Truck Load Optimizer
#
# Advanced physical packing engine
#
# Part 1/3
# ==========================================================


from dataclasses import dataclass, field
from typing import List, Tuple
import copy
import math


from cargo import Pallet
from truck import Truck



# ==========================================================
# BASIC GEOMETRY OBJECTS
# ==========================================================


@dataclass
class Rectangle:

    x: float

    y: float

    length: float

    width: float



    @property
    def right(self):

        return self.x + self.width



    @property
    def rear(self):

        return self.y + self.length



# ==========================================================
# PALLET PLACEMENT RESULT
# ==========================================================


@dataclass
class PalletPosition:


    pallet: Pallet


    x: float

    y: float


    rotated: bool



    @property
    def length(self):

        if self.rotated:

            return self.pallet.width

        return self.pallet.length



    @property
    def width(self):

        if self.rotated:

            return self.pallet.length

        return self.pallet.width



    @property
    def area(self):

        return (

            self.length

            *

            self.width

        )



    @property
    def centre_length(self):

        return (

            self.y

            +

            self.length / 2

        )



    @property
    def centre_width(self):

        return (

            self.x

            +

            self.width / 2

        )



# ==========================================================
# ROW STRUCTURE
# ==========================================================


@dataclass
class LoadingRow:


    start_position: float


    pallets: List[PalletPosition] = field(

        default_factory=list

    )



    @property
    def length_used(self):

        if not self.pallets:

            return 0


        return max(

            p.length

            for p in self.pallets

        )



    @property
    def width_used(self):

        return sum(

            p.width

            for p in self.pallets

        )



    @property
    def weight(self):

        return sum(

            p.pallet.weight

            for p in self.pallets

        )



# ==========================================================
# COMPLETE LAYOUT
# ==========================================================


@dataclass
class Layout:


    pallets: List[Pallet] = field(

        default_factory=list

    )


    rows: List[LoadingRow] = field(

        default_factory=list

    )


    used_length: float = 0.0


    used_area: float = 0.0


    score: float = 0.0



    @property
    def pallet_count(self):

        return len(

            self.pallets

        )



    def clone(self):

        return copy.deepcopy(

            self

        )



# ==========================================================
# PACKING CANDIDATE
# ==========================================================


@dataclass
class PackingCandidate:


    layout: Layout


    reason: str = ""



    score: float = 0.0



# ==========================================================
# DIMENSION HELPERS
# ==========================================================


def possible_orientations(
    pallet: Pallet
):

    """
    Returns possible pallet orientations.

    Original first.
    Rotated second.

    Duplicate rotations are removed.
    """


    options = []


    options.append(

        (

            pallet.length,

            pallet.width,

            False

        )

    )


    if pallet.allow_rotation:


        if (

            pallet.width != pallet.length

        ):


            options.append(

                (

                    pallet.width,

                    pallet.length,

                    True

                )

            )



    return options



# ==========================================================
# TRAILER BOUNDARY CHECK
# ==========================================================


def inside_trailer(
    pallet_position: PalletPosition,
    truck: Truck
):


    return (

        pallet_position.x >= 0

        and

        pallet_position.y >= 0

        and

        pallet_position.x +

        pallet_position.width

        <=

        truck.trailer_width


        and


        pallet_position.y +

        pallet_position.length

        <=

        truck.trailer_length

    )



# ==========================================================
# COLLISION CHECK
# ==========================================================


def rectangles_overlap(
    a: Rectangle,
    b: Rectangle
):


    return not (

        a.right <= b.x

        or

        b.right <= a.x

        or

        a.rear <= b.y

        or

        b.rear <= a.y

    )



def pallet_overlap(
    new_position: PalletPosition,
    existing: List[PalletPosition]
):


    new_rect = Rectangle(

        new_position.x,

        new_position.y,

        new_position.length,

        new_position.width

    )



    for item in existing:


        old_rect = Rectangle(

            item.x,

            item.y,

            item.length,

            item.width

        )


        if rectangles_overlap(

            new_rect,

            old_rect

        ):

            return True



    return False



# ==========================================================
# POSITION CREATION
# ==========================================================


def create_position(

    pallet: Pallet,

    x: float,

    y: float,

    rotated: bool

):


    return PalletPosition(

        pallet=pallet,

        x=x,

        y=y,

        rotated=rotated

    )


# ==========================================================
# EURO PALLET PATTERN LOGIC
# Part 2/3
# ==========================================================



EURO_LENGTH = 1.20

EURO_WIDTH = 0.80



def is_euro_pallet(
    pallet: Pallet
):

    """
    Detect standard EUR pallet.

    Accepted:
    120x80
    80x120

    Small tolerance included.
    """


    tolerance = 0.02


    return (

        (

            abs(pallet.length - EURO_LENGTH)
            < tolerance

            and

            abs(pallet.width - EURO_WIDTH)
            < tolerance

        )

        or

        (

            abs(pallet.width - EURO_LENGTH)
            < tolerance

            and

            abs(pallet.length - EURO_WIDTH)
            < tolerance

        )

    )



# ==========================================================
# PATTERN GENERATION
# ==========================================================


def generate_width_patterns(
    truck: Truck,
    pallet: Pallet
):

    """
    Returns preferred width arrangements.

    For euro pallets:

        3-wide:
        80 + 80 + 80

        2-wide:
        120 + 120


    For other pallets:
        calculate possible counts.
    """


    patterns = []



    if is_euro_pallet(pallet):


        # 3 wide euro pallets

        patterns.append(

            {

                "count": 3,

                "orientation": "turned",

                "width_used": 2.40,

                "priority": 100

            }

        )



        # 2 wide euro pallets

        patterns.append(

            {

                "count": 2,

                "orientation": "normal",

                "width_used": 2.40,

                "priority": 80

            }

        )



    else:


        for length, width, rotated in possible_orientations(

            pallet

        ):


            count = int(

                truck.trailer_width

                /

                width

            )


            if count > 0:


                patterns.append(

                    {

                        "count": count,

                        "orientation":

                            rotated,

                        "width_used":

                            count * width,

                        "priority":

                            count * 10

                    }

                )



    return sorted(

        patterns,

        key=lambda x:

        x["priority"],

        reverse=True

    )



# ==========================================================
# PLACE ONE PALLET
# ==========================================================


def find_position(

    truck: Truck,

    pallet: Pallet,

    existing: List[PalletPosition],

    start_y: float

):


    """
    Searches a position.

    Front to back.

    Left to right.

    """


    step = 0.01



    for rotated_length, rotated_width, rotated in possible_orientations(

        pallet

    ):



        y = start_y



        while y + rotated_length <= truck.trailer_length:



            x = 0



            while x + rotated_width <= truck.trailer_width:



                position = create_position(

                    pallet,

                    x,

                    y,

                    rotated

                )



                if inside_trailer(

                    position,

                    truck

                ) and not pallet_overlap(

                    position,

                    existing

                ):


                    return position



                x += step



            y += step



    return None



# ==========================================================
# BUILD ROW
# ==========================================================


def build_row(

    truck: Truck,

    pallets: List[Pallet],

    start_y: float

):


    row = LoadingRow(

        start_position=start_y

    )



    positions = []



    x = 0



    row_length = 0



    for pallet in pallets:



        position = find_position(

            truck,

            pallet,

            positions,

            start_y

        )



        if position is None:

            break



        position.x = x



        position.y = start_y



        positions.append(

            position

        )


        pallet.loaded = True

        pallet.x = position.x

        pallet.y = position.y

        pallet.rotated = position.rotated



        row_length = max(

            row_length,

            position.length

        )



        x += position.width



    row.pallets = positions



    return row, row_length



# ==========================================================
# PATTERN ROW CREATOR
# ==========================================================


def create_pattern_rows(

    truck: Truck,

    pallets: List[Pallet]

):


    rows = []


    remaining = list(

        pallets

    )


    current_y = 0



    while remaining:



        row_pallets = []



        width_used = 0



        reference = remaining[0]



        patterns = generate_width_patterns(

            truck,

            reference

        )



        pattern = patterns[0]



        count = pattern["count"]



        for pallet in remaining[:count]:

            row_pallets.append(

                pallet

            )



        row, length = build_row(

            truck,

            row_pallets,

            current_y

        )



        if not row.pallets:

            break



        rows.append(

            row

        )



        for pallet in row_pallets:

            if pallet in remaining:

                remaining.remove(

                    pallet

                )



        current_y += length



        if current_y >= truck.trailer_length:

            break



    return rows



# ==========================================================
# APPLY ROWS TO LAYOUT
# ==========================================================


def rows_to_layout(

    rows: List[LoadingRow]

):


    pallets = []



    used_length = 0

    used_area = 0



    for row in rows:


        for position in row.pallets:


            pallets.append(

                position.pallet

            )


            used_length = max(

                used_length,

                position.y + position.length

            )


            used_area += position.area



    return Layout(

        pallets=pallets,

        rows=rows,

        used_length=used_length,

        used_area=used_area

    )

# ==========================================================
# LAYOUT SCORING
# Part 3/3
# ==========================================================



def calculate_used_length(
    layout: Layout
):

    if not layout.pallets:

        return 0


    return max(

        p.y + p.draw_length

        for p in layout.pallets

    )



def calculate_used_area(
    layout: Layout
):


    return sum(

        p.area

        for p in layout.pallets

    )



# ==========================================================
# GAP ANALYSIS
# ==========================================================


def calculate_side_gap_penalty(
    truck: Truck,
    rows: List[LoadingRow]
):


    penalty = 0



    for row in rows:


        used = row.width_used


        gap = (

            truck.trailer_width

            -

            used

        )


        # large side gaps are undesirable

        if gap > 0.20:

            penalty += gap * 10



    return penalty



# ==========================================================
# STABILITY SCORE
# ==========================================================


def stability_score(
    layout: Layout
):

    """
    Rewards:

    - full width usage
    - fewer gaps
    - balanced rows


    This is not axle calculation.
    Axles are handled later.
    """


    score = 0



    for row in layout.rows:


        width = row.width_used


        if width >= 2.35:

            score += 20


        elif width >= 2.00:

            score += 10



        else:

            score -= 10



    return score



# ==========================================================
# COMPLETE LAYOUT SCORE
# ==========================================================


def score_layout(
    truck: Truck,
    layout: Layout
):


    score = 0



    # more pallets is better

    score += layout.pallet_count * 100



    # better floor usage

    trailer_area = (

        truck.trailer_length

        *

        truck.trailer_width

    )


    if trailer_area > 0:


        utilisation = (

            layout.used_area

            /

            trailer_area

        )

        score += utilisation * 100



    # stability

    score += stability_score(

        layout

    )



    # punish gaps

    score -= calculate_side_gap_penalty(

        truck,

        layout.rows

    )



    # prefer shorter unused rear space

    score -= (

        truck.trailer_length

        -

        layout.used_length

    )



    return score



# ==========================================================
# GENERATE CANDIDATES
# ==========================================================


def generate_candidates(

    truck: Truck,

    pallets: List[Pallet]

):


    candidates = []



    # ------------------------------------------------------
    # Candidate 1
    # Preferred patterns
    # ------------------------------------------------------

    ordered = sorted(

        pallets,

        key=lambda p:

        (

            -p.weight,

            -p.area

        )

    )


    rows = create_pattern_rows(

        truck,

        ordered

    )


    layout = rows_to_layout(

        rows

    )


    layout.score = score_layout(

        truck,

        layout

    )


    candidates.append(

        PackingCandidate(

            layout=layout,

            score=layout.score,

            reason="Preferred stability pattern"

        )

    )



    # ------------------------------------------------------
    # Candidate 2
    # Rotation alternative
    # ------------------------------------------------------

    rotated = []


    for pallet in ordered:


        copy_pallet = pallet.clone()


        if copy_pallet.allow_rotation:

            copy_pallet.rotate()



        rotated.append(

            copy_pallet

        )



    rows = create_pattern_rows(

        truck,

        rotated

    )


    layout = rows_to_layout(

        rows

    )


    layout.score = score_layout(

        truck,

        layout

    )


    candidates.append(

        PackingCandidate(

            layout=layout,

            score=layout.score,

            reason="Rotation alternative"

        )

    )



    return sorted(

        candidates,

        key=lambda c:

        c.score,

        reverse=True

    )



# ==========================================================
# PUBLIC API
# ==========================================================


def pack_pallets(

    truck: Truck,

    pallets: List[Pallet]

):


    """
    Main packing entry point.

    Returns best physical layout.
    """


    candidates = generate_candidates(

        truck,

        pallets

    )


    if not candidates:


        return Layout()



    best = candidates[0].layout



    return best



# ==========================================================
# ALTERNATIVE SOLUTIONS
# ==========================================================


def get_alternative_layouts(

    truck: Truck,

    pallets: List[Pallet]

):


    candidates = generate_candidates(

        truck,

        pallets

    )


    return [

        c.layout

        for c in candidates

    ]