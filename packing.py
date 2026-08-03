# ==========================================================
# packing.py
# Truck Load Optimizer
#
# Advanced packing engine
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass, field

from typing import List, Tuple, Optional

import copy

import math



# ==========================================================
# CONSTANTS
# ==========================================================

EURO_LENGTH = 1.20
EURO_WIDTH = 0.80

UK_LENGTH = 1.20
UK_WIDTH = 1.00

WIDTH_TOLERANCE = 0.02
LENGTH_TOLERANCE = 0.02



# ==========================================================
# PLACED PALLET
# ==========================================================

@dataclass
class PlacedPallet:

    description: str

    length: float

    width: float

    height: float

    weight: float

    x: float

    y: float

    rotated: bool = False

    row: int = 0

    column: int = 0

    sequence: int = 0

    @property
    def draw_length(self):

        return self.width if self.rotated else self.length

    @property
    def draw_width(self):

        return self.length if self.rotated else self.width

    @property
    def centre(self):

        return (

            self.x + self.draw_width / 2,

            self.y + self.draw_length / 2

        )



# ==========================================================
# ROW
# ==========================================================

@dataclass
class Row:

    pallets: List[PlacedPallet] = field(default_factory=list)

    length: float = 0.0

    width_used: float = 0.0

    row_number: int = 0

    @property
    def pallet_count(self):

        return len(self.pallets)



# ==========================================================
# LAYOUT
# ==========================================================

@dataclass
class Layout:

    pallets: List[PlacedPallet]

    trailer_length: float

    trailer_width: float

    rows: List[Row]

    used_length: float

    free_length: float

    score: float = 0

    pattern_name: str = ""

    @property
    def pallet_count(self):

        return len(self.pallets)

    @property
    def total_weight(self):

        return sum(

            p.weight

            for p in self.pallets

        )



# ==========================================================
# PALLET TEMPLATE
# ==========================================================

@dataclass
class PalletTemplate:

    description: str

    length: float

    width: float

    height: float

    weight: float



# ==========================================================
# HELPERS
# ==========================================================

def clone_templates(cargo):

    pallets = []

    for item in cargo:

        for _ in range(item.quantity):

            pallets.append(

                PalletTemplate(

                    description=item.description,

                    length=item.length,

                    width=item.width,

                    height=item.height,

                    weight=item.weight

                )

            )

    return pallets



def is_europallet(pallet):

    return (

        abs(pallet.length - EURO_LENGTH)

        <= LENGTH_TOLERANCE

        and

        abs(pallet.width - EURO_WIDTH)

        <= WIDTH_TOLERANCE

    )



def is_uk_pallet(pallet):

    return (

        abs(pallet.length - UK_LENGTH)

        <= LENGTH_TOLERANCE

        and

        abs(pallet.width - UK_WIDTH)

        <= WIDTH_TOLERANCE

    )



def rotated_size(pallet, rotate):

    if rotate:

        return (

            pallet.width,

            pallet.length

        )

    return (

        pallet.length,

        pallet.width

    )



# ==========================================================
# ROW PATTERN
# ==========================================================

@dataclass
class RowPattern:

    name: str

    pallet_width: float

    pallet_length: float

    across: int

    rotate: bool

    priority: int



# ==========================================================
# PATTERN GENERATION
# ==========================================================

def generate_patterns(

    trailer_width,

    pallet

):

    patterns = []



    # ------------------------------------------------------
    # EURO PALLET
    # Industry preferred:
    #
    # 80 + 80 + 80
    #
    # Only if width allows.
    # ------------------------------------------------------

    if is_europallet(pallet):

        if trailer_width >= 2.40:

            patterns.append(

                RowPattern(

                    name="EURO-3",

                    pallet_width=0.80,

                    pallet_length=1.20,

                    across=3,

                    rotate=False,

                    priority=100

                )

            )



        patterns.append(

            RowPattern(

                name="EURO-2",

                pallet_width=1.20,

                pallet_length=0.80,

                across=2,

                rotate=True,

                priority=70

            )

        )



    # ------------------------------------------------------
    # UK pallet
    # ------------------------------------------------------

    elif is_uk_pallet(pallet):

        patterns.append(

            RowPattern(

                name="UK-2",

                pallet_width=1.20,

                pallet_length=1.00,

                across=2,

                rotate=False,

                priority=100

            )

        )



    # ------------------------------------------------------
    # Generic pallet
    # ------------------------------------------------------

    else:

        for rotate in (False, True):

            L, W = rotated_size(

                pallet,

                rotate

            )

            across = int(

                trailer_width // W

            )

            if across < 1:

                continue

            patterns.append(

                RowPattern(

                    name=f"GEN-{across}",

                    pallet_width=W,

                    pallet_length=L,

                    across=across,

                    rotate=rotate,

                    priority=across

                )

            )



    patterns.sort(

        key=lambda p: p.priority,

        reverse=True

    )



    return patterns


# ==========================================================
# ROW BUILDING
# ==========================================================

def build_row(

    templates: List[PalletTemplate],

    pattern: RowPattern,

    y_position: float,

    row_number: int

) -> Tuple[Optional[Row], List[PalletTemplate]]:

    """
    Builds one complete loading row.

    Returns:

        Row

        Remaining pallet templates
    """

    if len(templates) < pattern.across:

        return None, templates


    row = Row(

        row_number=row_number

    )


    remaining = copy.deepcopy(templates)


    x = 0.0


    for column in range(pattern.across):


        template = remaining.pop(0)


        placed = PlacedPallet(

            description=template.description,

            length=template.length,

            width=template.width,

            height=template.height,

            weight=template.weight,

            x=x,

            y=y_position,

            rotated=pattern.rotate,

            row=row_number,

            column=column + 1

        )


        row.pallets.append(

            placed

        )


        x += pattern.pallet_width


    row.length = pattern.pallet_length

    row.width_used = pattern.pallet_width * pattern.across


    return row, remaining



# ==========================================================
# BUILD COMPLETE LAYOUT
# ==========================================================

def build_layout(

    trailer_length: float,

    trailer_width: float,

    templates: List[PalletTemplate],

    pattern: RowPattern

) -> Layout:

    """
    Builds one candidate layout using a single row pattern.
    """

    remaining = copy.deepcopy(templates)

    rows = []

    pallets = []

    current_y = 0.0

    row_number = 1


    while True:


        if len(remaining) == 0:

            break


        if current_y + pattern.pallet_length > trailer_length + 0.0001:

            break


        row, remaining = build_row(

            remaining,

            pattern,

            current_y,

            row_number

        )


        if row is None:

            break


        rows.append(row)

        pallets.extend(row.pallets)


        current_y += row.length

        row_number += 1


    layout = Layout(

        pallets=pallets,

        trailer_length=trailer_length,

        trailer_width=trailer_width,

        rows=rows,

        used_length=current_y,

        free_length=max(

            0,

            trailer_length - current_y

        ),

        pattern_name=pattern.name

    )


    return layout



# ==========================================================
# SCORE LAYOUT
# ==========================================================

def score_layout(

    layout: Layout

):

    """
    Higher score = better layout.

    Priority:

    1. More pallets
    2. Less unused trailer length
    3. Preferred loading pattern
    """

    score = 0

    score += layout.pallet_count * 10000

    score += (layout.trailer_length - layout.free_length) * 100

    if layout.pattern_name == "EURO-3":

        score += 5000

    elif layout.pattern_name == "UK-2":

        score += 3000

    layout.score = score

    return layout



# ==========================================================
# GENERATE CANDIDATES
# ==========================================================

def generate_candidate_layouts(

    trailer_length: float,

    trailer_width: float,

    cargo

) -> List[Layout]:

    """
    Generate every possible packing layout.

    Optimizer.py will later evaluate them
    against axle weights.
    """

    templates = clone_templates(

        cargo

    )


    if not templates:

        return []


    reference = templates[0]


    patterns = generate_patterns(

        trailer_width,

        reference

    )


    layouts = []


    for pattern in patterns:


        layout = build_layout(

            trailer_length,

            trailer_width,

            templates,

            pattern

        )


        score_layout(

            layout

        )


        layouts.append(

            layout

        )


    layouts.sort(

        key=lambda l: l.score,

        reverse=True

    )


    return layouts


# ==========================================================
# ADVANCED ROW SEARCH
# ==========================================================


def build_mixed_layout(

    trailer_length: float,

    trailer_width: float,

    templates: List[PalletTemplate]

) -> Layout:

    """
    Builds a mixed-pattern layout.

    The loader always starts from the front bulkhead.
    Different rows may use different pallet patterns.
    """


    remaining = copy.deepcopy(templates)


    rows = []

    pallets = []


    current_y = 0.0

    row_number = 1



    while remaining:


        # Take the heaviest remaining pallet as reference

        reference = sorted(

            remaining,

            key=lambda p: p.weight,

            reverse=True

        )[0]


        patterns = generate_patterns(

            trailer_width,

            reference

        )


        best_row = None

        best_remaining = remaining

        best_pattern_score = -1



        for pattern in patterns:


            if (

                current_y

                + pattern.pallet_length

                > trailer_length + 0.001

            ):

                continue



            row, new_remaining = build_row(

                remaining,

                pattern,

                current_y,

                row_number

            )


            if row is None:

                continue



            row_score = (

                row.pallet_count * 1000

                + pattern.priority

            )



            if row_score > best_pattern_score:

                best_row = row

                best_remaining = new_remaining

                best_pattern_score = row_score



        if best_row is None:

            break



        rows.append(best_row)

        pallets.extend(best_row.pallets)



        remaining = best_remaining


        current_y += best_row.length

        row_number += 1



    layout = Layout(

        pallets=pallets,

        trailer_length=trailer_length,

        trailer_width=trailer_width,

        rows=rows,

        used_length=current_y,

        free_length=max(

            0,

            trailer_length-current_y

        ),

        pattern_name="MIXED"

    )


    return layout



# ==========================================================
# IMPROVE FINAL ROW
# ==========================================================


def fill_partial_row(

    layout: Layout,

    remaining: List[PalletTemplate],

    trailer_width: float

):

    """
    Try to use remaining floor space.

    Example:
    33rd Euro pallet after several 3-wide rows.
    """


    if not remaining:

        return layout



    last_y = layout.used_length


    reference = remaining[0]


    patterns = generate_patterns(

        trailer_width,

        reference

    )


    for pattern in patterns:


        if (

            last_y + pattern.pallet_length

            > layout.trailer_length

        ):

            continue



        row, unused = build_row(

            remaining,

            pattern,

            last_y,

            len(layout.rows)+1

        )


        if row:


            layout.rows.append(row)

            layout.pallets.extend(row.pallets)

            layout.used_length += row.length

            layout.free_length = (

                layout.trailer_length

                - layout.used_length

            )


            break



    return layout



# ==========================================================
# CREATE ALL CANDIDATES
# ==========================================================


def create_loading_candidates(

    truck,

    cargo

):

    """
    Main packing entry point.

    Returns several possible physical layouts.

    optimizer.py decides legality.
    """


    templates = clone_templates(

        cargo

    )


    if not templates:

        return []



    candidates = []



    # ------------------------------------------------------
    # Candidate 1:
    # Best mixed pattern
    # ------------------------------------------------------

    mixed = build_mixed_layout(

        truck.trailer_length,

        truck.trailer_width,

        templates

    )


    score_layout(

        mixed

    )


    candidates.append(

        mixed

    )



    # ------------------------------------------------------
    # Candidate 2:
    # Pure patterns
    # ------------------------------------------------------

    reference = templates[0]


    patterns = generate_patterns(

        truck.trailer_width,

        reference

    )



    for pattern in patterns:


        layout = build_layout(

            truck.trailer_length,

            truck.trailer_width,

            templates,

            pattern

        )


        score_layout(

            layout

        )


        candidates.append(layout)



    # Remove duplicates

    unique = []


    signatures = set()


    for layout in candidates:


        signature = tuple(

            (

                p.description,

                round(p.x,2),

                round(p.y,2),

                p.rotated

            )

            for p in layout.pallets

        )


        if signature not in signatures:

            signatures.add(signature)

            unique.append(layout)



    unique.sort(

        key=lambda x: (

            x.pallet_count,

            x.score

        ),

        reverse=True

    )


    return unique



# ==========================================================
# COMPATIBILITY FUNCTION
# ==========================================================


def pack_pallets(

    truck,

    cargo

):

    """
    Compatibility wrapper.

    optimizer.py can call this.

    Returns the best physical layouts.
    """


    return create_loading_candidates(

        truck,

        cargo

    )


# ==========================================================
# PHYSICAL VALIDATION
# ==========================================================


def pallet_inside_trailer(

    pallet: PlacedPallet,

    trailer_length: float,

    trailer_width: float

):

    """
    Check that pallet is physically inside trailer.
    """

    return (

        pallet.x >= -0.001

        and pallet.y >= -0.001

        and pallet.x + pallet.draw_width

        <= trailer_width + 0.001

        and pallet.y + pallet.draw_length

        <= trailer_length + 0.001

    )



def pallets_overlap(

    a: PlacedPallet,

    b: PlacedPallet

):

    """
    Rectangle collision check.
    """


    return not (

        a.x + a.draw_width <= b.x

        or b.x + b.draw_width <= a.x

        or a.y + a.draw_length <= b.y

        or b.y + b.draw_length <= a.y

    )



def validate_layout(

    layout: Layout

):

    """
    Verify physical correctness.
    """

    errors = []



    # Check boundaries

    for pallet in layout.pallets:


        if not pallet_inside_trailer(

            pallet,

            layout.trailer_length,

            layout.trailer_width

        ):


            errors.append(

                f"{pallet.description}: outside trailer"

            )



    # Check collisions

    pallets = layout.pallets


    for i in range(len(pallets)):

        for j in range(i+1, len(pallets)):


            if pallets_overlap(

                pallets[i],

                pallets[j]

            ):


                errors.append(

                    f"{pallets[i].description}: overlap"

                )



    return (

        len(errors) == 0,

        errors

    )



# ==========================================================
# LAYOUT UTILITIES
# ==========================================================


def get_layout_dimensions(

    layout: Layout

):

    """

    Returns used dimensions.

    Used by reports/drawing.
    """

    return {

        "length_used": layout.used_length,

        "length_free": layout.free_length,

        "pallets": layout.pallet_count,

        "weight": layout.total_weight

    }



def get_loaded_pallets(

    layout: Layout

):

    return layout.pallets



# ==========================================================
# OPTIMIZER COMPATIBILITY
# ==========================================================


def get_best_physical_layout(

    truck,

    cargo

):

    """
    Returns best physical layout only.

    Legal checks are done elsewhere.
    """

    candidates = create_loading_candidates(

        truck,

        cargo

    )


    if not candidates:

        return None



    valid = []


    for layout in candidates:


        ok, _ = validate_layout(

            layout

        )


        if ok:

            valid.append(layout)



    if not valid:

        return None



    valid.sort(

        key=lambda x: (

            x.pallet_count,

            x.score

        ),

        reverse=True

    )


    return valid[0]



# ==========================================================
# END OF PACKING ENGINE
# ==========================================================
