# ==========================================================
# packing.py
# Truck Load Optimizer
#
# Loading engine.
#
# Cargo is loaded row by row across the trailer width, starting from the
# front bulkhead -- the same way a forklift operator actually loads a
# trailer. Same-footprint pallets are grouped into "lanes" before any row
# is built, so a row's spacing always matches the pallets placed in it.
# Leftover width in a row is filled with other lanes where it fits
# ("broken stowage"), and several construction heuristics plus row-order
# variants are generated so optimizer.py has a rich set of physically
# valid layouts to check against axle limits.
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass, field

from typing import List, Tuple, Optional, Dict

import copy


# ==========================================================
# CONSTANTS
# ==========================================================

EURO_LENGTH = 1.20
EURO_WIDTH = 0.80

UK_LENGTH = 1.20
UK_WIDTH = 1.00

WIDTH_TOLERANCE = 0.02
LENGTH_TOLERANCE = 0.02

# A load must not be placed flush against both the front bulkhead and rear
# doors. This prevents a theoretical arrangement that has no practical
# loading clearance.
END_CLEARANCE = 0.02

# Safety caps so candidate generation stays fast on large manifests.
MAX_FILL_PASSES = 6
MAX_CANDIDATES = 40


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

    # Per-cargo-type sequence number, retained from the user manifest.
    unit_number: int = 0

    @property
    def draw_length(self):
        return self.width if self.rotated else self.length

    @property
    def draw_width(self):
        return self.length if self.rotated else self.width

    @property
    def centre(self):
        return (self.x + self.draw_width / 2, self.y + self.draw_length / 2)


# ==========================================================
# ROW
# ==========================================================

@dataclass
class Row:

    pallets: List[PlacedPallet] = field(default_factory=list)
    length: float = 0.0
    width_used: float = 0.0
    row_number: int = 0

    # True if this row must stay immediately after whichever row precedes
    # it and can never be reordered away from it -- used for the
    # alternating stability pattern, where a centred single row is only
    # ever valid directly behind its supporting pair row.
    locked_after_previous: bool = False

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
        return sum(p.weight for p in self.pallets)


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

    # Per-cargo-type sequence number, retained from the user manifest.
    unit_number: int = 0

    allow_rotation: bool = True


# ==========================================================
# HELPERS
# ==========================================================

def clone_templates(cargo):

    pallets = []
    unit_numbers = {}

    for item in cargo:
        for _ in range(item.quantity):

            unit_numbers[item.description] = unit_numbers.get(item.description, 0) + 1

            pallets.append(
                PalletTemplate(
                    description=item.description,
                    length=item.length,
                    width=item.width,
                    height=item.height,
                    weight=item.weight,
                    unit_number=unit_numbers[item.description],
                    allow_rotation=getattr(item, "allow_rotation", True),
                )
            )

    return pallets


def is_europallet(pallet):
    return (
        abs(pallet.length - EURO_LENGTH) <= LENGTH_TOLERANCE
        and abs(pallet.width - EURO_WIDTH) <= WIDTH_TOLERANCE
    )


def is_uk_pallet(pallet):
    return (
        abs(pallet.length - UK_LENGTH) <= LENGTH_TOLERANCE
        and abs(pallet.width - UK_WIDTH) <= WIDTH_TOLERANCE
    )


def rotated_size(pallet, rotate):
    if rotate:
        return (pallet.width, pallet.length)
    return (pallet.length, pallet.width)


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

def generate_patterns(trailer_width, pallet, allow_rotation=True):
    """Return the row patterns available for one pallet footprint.

    Always includes a last-resort single-pallet ("across=1") pattern so a
    lone leftover unit can still be placed even when no multi-across
    pattern fits it -- the earlier engine could silently strand pallets
    like this.
    """

    patterns = []

    # ------------------------------------------------------
    # EURO PALLET -- industry preferred 3-across, fallback 2-across
    # ------------------------------------------------------
    if is_europallet(pallet):

        if trailer_width >= 2.40:
            patterns.append(
                RowPattern(name="EURO-3", pallet_width=0.80, pallet_length=1.20, across=3, rotate=False, priority=100)
            )

        patterns.append(
            RowPattern(name="EURO-2", pallet_width=1.20, pallet_length=0.80, across=2, rotate=True, priority=70)
        )

    # ------------------------------------------------------
    # UK pallet
    # ------------------------------------------------------
    elif is_uk_pallet(pallet):

        patterns.append(
            RowPattern(name="UK-2", pallet_width=1.00, pallet_length=1.20, across=2, rotate=False, priority=100)
        )

    # ------------------------------------------------------
    # Generic pallet
    # ------------------------------------------------------
    else:

        for rotate in (False, True):
            L, W = rotated_size(pallet, rotate)
            across = int(trailer_width // W)
            if across < 1:
                continue
            patterns.append(
                RowPattern(name=f"GEN-{across}", pallet_width=W, pallet_length=L, across=across, rotate=rotate, priority=across)
            )

    if not allow_rotation:
        patterns = [p for p in patterns if not p.rotate]

    if not any(p.across == 1 for p in patterns):
        orientations = (False, True) if allow_rotation else (False,)
        for rotate in orientations:
            L, W = rotated_size(pallet, rotate)
            if W <= trailer_width + WIDTH_TOLERANCE:
                patterns.append(
                    RowPattern(name="SINGLE", pallet_width=W, pallet_length=L, across=1, rotate=rotate, priority=1)
                )
                break

    patterns.sort(key=lambda p: p.priority, reverse=True)

    return patterns


# ==========================================================
# LANES -- group same-footprint pallets so a row is always
# built from pallets that actually match its pattern
# ==========================================================

def lane_key(template):
    return (round(template.length, 2), round(template.width, 2))


def group_into_lanes(templates) -> Dict[Tuple[float, float], List[PalletTemplate]]:
    """Group pallets sharing an identical (length, width) footprint.

    Pallets from different cargo lines that happen to share a footprint
    are combined into one lane, so they can pack the same row -- this is
    what lets the engine build dense mixed-cargo rows instead of only
    ever handling a single cargo type reliably.
    """
    lanes: Dict[Tuple[float, float], List[PalletTemplate]] = {}
    for template in templates:
        key = lane_key(template)
        lanes.setdefault(key, []).append(copy.deepcopy(template))
    return lanes


def lane_patterns(trailer_width, lane_templates):
    reference = lane_templates[0]
    return generate_patterns(trailer_width, reference, reference.allow_rotation)


# ==========================================================
# ROW BUILDING
# ==========================================================

def build_row_from_lane(
    lane_templates: List[PalletTemplate],
    pattern: RowPattern,
    y_position: float,
    row_number: int,
) -> Tuple[Optional[Row], List[PalletTemplate]]:
    """Build one row using only pallets from a single, matching lane."""

    if len(lane_templates) < pattern.across:
        return None, lane_templates

    row = Row(row_number=row_number)
    remaining = list(lane_templates)
    x = 0.0

    for column in range(pattern.across):
        template = remaining.pop(0)
        row.pallets.append(
            PlacedPallet(
                description=template.description,
                length=template.length,
                width=template.width,
                height=template.height,
                weight=template.weight,
                x=x,
                y=y_position,
                rotated=pattern.rotate,
                row=row_number,
                column=column + 1,
                unit_number=template.unit_number,
            )
        )
        x += pattern.pallet_width

    row.length = pattern.pallet_length
    row.width_used = pattern.pallet_width * pattern.across

    return row, remaining


def fill_row_gap(row, lanes, trailer_width, y_position, row_number, max_length):
    """Fill leftover width in a row with pallets from other lanes.

    Real loaders do this constantly ("broken stowage") -- a narrower box
    goes beside a euro-pallet row rather than leaving the gap empty.
    """

    for _ in range(MAX_FILL_PASSES):

        gap_width = trailer_width - row.width_used
        if gap_width <= WIDTH_TOLERANCE:
            break

        best = None

        for key, lane_templates in lanes.items():
            if not lane_templates:
                continue

            reference = lane_templates[0]
            orientations = (False, True) if reference.allow_rotation else (False,)

            for rotate in orientations:
                L, W = rotated_size(reference, rotate)
                if W <= gap_width + WIDTH_TOLERANCE and L <= max_length + LENGTH_TOLERANCE:
                    count = min(len(lane_templates), max(1, int((gap_width + WIDTH_TOLERANCE) // W)))
                    area = count * W * L
                    if best is None or area > best[4]:
                        best = (key, rotate, W, L, area, count)

        if best is None:
            break

        key, rotate, W, L, _, count = best
        lane_templates = lanes[key]
        x_start = row.width_used

        for i in range(count):
            template = lane_templates.pop(0)
            row.pallets.append(
                PlacedPallet(
                    description=template.description,
                    length=template.length,
                    width=template.width,
                    height=template.height,
                    weight=template.weight,
                    x=x_start + i * W,
                    y=y_position,
                    rotated=rotate,
                    row=row_number,
                    column=len(row.pallets) + 1,
                    unit_number=template.unit_number,
                )
            )

        row.width_used += count * W
        row.length = max(row.length, L)

    return row


# ==========================================================
# CONSTRUCTION HEURISTICS
# ==========================================================

def heuristic_score(heuristic, lane_templates, patterns, lane_order_index):
    """Score a lane's priority for being loaded next, for one heuristic."""

    best = patterns[0]

    if heuristic == "weight":
        return max(t.weight for t in lane_templates)
    if heuristic == "quantity":
        return len(lane_templates)
    if heuristic == "footprint":
        return best.across * best.pallet_width * best.pallet_length
    if heuristic == "preferred":
        return best.priority
    if heuristic == "insertion":
        return -lane_order_index

    return 0


def continue_greedy_fill(trailer_length, trailer_width, lanes, rows, pallets, current_y, row_number, heuristic):
    """Keep filling remaining trailer length from whatever lanes still
    have cargo, using the given heuristic. Shared by the plain
    construction heuristics and by the alternating stability pattern
    once it has finished (or can't continue) with its primary lane."""

    lane_order = {key: index for index, key in enumerate(lanes.keys())}

    while True:

        remaining_length = trailer_length - END_CLEARANCE - current_y
        if remaining_length <= 0:
            break

        candidates = []
        for key, lane_templates in lanes.items():
            if not lane_templates:
                continue
            patterns = [p for p in lane_patterns(trailer_width, lane_templates) if p.pallet_length <= remaining_length + LENGTH_TOLERANCE]
            if not patterns:
                continue
            score = heuristic_score(heuristic, lane_templates, patterns, lane_order.get(key, 0))
            candidates.append((score, key, patterns))

        if not candidates:
            break

        candidates.sort(key=lambda c: c[0], reverse=True)

        placed = False
        for _, key, patterns in candidates:
            for pattern in patterns:
                row, leftover = build_row_from_lane(lanes[key], pattern, current_y, row_number)
                if row is None:
                    continue

                lanes[key] = leftover
                row = fill_row_gap(row, lanes, trailer_width, current_y, row_number, remaining_length)

                rows.append(row)
                pallets.extend(row.pallets)
                current_y += row.length
                row_number += 1
                placed = True
                break
            if placed:
                break

        if not placed:
            break

    return rows, pallets, current_y, row_number


def build_layout_greedy(trailer_length, trailer_width, templates, heuristic, pattern_label) -> Layout:
    """Greedily build a full layout, choosing the next row's lane by
    the given heuristic and filling leftover width from other lanes."""

    lanes = group_into_lanes(templates)
    rows, pallets, current_y, row_number = continue_greedy_fill(
        trailer_length, trailer_width, lanes, [], [], 0.0, 1, heuristic
    )

    return Layout(
        pallets=pallets,
        trailer_length=trailer_length,
        trailer_width=trailer_width,
        rows=rows,
        used_length=current_y,
        free_length=max(0.0, trailer_length - current_y),
        pattern_name=pattern_label,
    )


# ==========================================================
# STABILITY LOADING PATTERN -- alternating pair / centred-single
#
# Used by real loaders for heavy cargo: a dense 3-across (or 2-across
# every row) block concentrates a lot of weight into a short stretch of
# trailer near the bulkhead, which can overload the front axle group
# long before the trailer is full. Alternating a 2-across row with a
# single pallet centred on the width spreads the same pallet count over
# roughly double the trailer length, cutting the weight-per-metre and
# letting far more of the load actually qualify as legal.
#
# The bulkhead row is always a pair (so the load has something solid to
# brace against), and a single row is never placed without a pair row
# immediately ahead of it -- two singles in a row would leave the second
# one unsupported.
# ==========================================================

def build_pair_row(lane_templates, trailer_width, y_position, row_number):
    """Two pallets side by side, centred on the trailer width."""

    if len(lane_templates) < 2:
        return None, lane_templates

    reference = lane_templates[0]
    orientations = (False, True) if reference.allow_rotation else (False,)

    for rotate in orientations:
        L, W = rotated_size(reference, rotate)
        if 2 * W <= trailer_width + WIDTH_TOLERANCE:
            remaining = list(lane_templates)
            row = Row(row_number=row_number)
            x_start = max(0.0, (trailer_width - 2 * W) / 2)
            for column in range(2):
                template = remaining.pop(0)
                row.pallets.append(
                    PlacedPallet(
                        description=template.description,
                        length=template.length,
                        width=template.width,
                        height=template.height,
                        weight=template.weight,
                        x=x_start + column * W,
                        y=y_position,
                        rotated=rotate,
                        row=row_number,
                        column=column + 1,
                        unit_number=template.unit_number,
                    )
                )
            row.length = L
            row.width_used = 2 * W
            return row, remaining

    return None, lane_templates


def build_centered_single_row(lane_templates, trailer_width, y_position, row_number):
    """One pallet, centred on the trailer width -- the stable
    single-pallet row used between pair rows for heavy loads."""

    if not lane_templates:
        return None, lane_templates

    reference = lane_templates[0]
    orientations = (False, True) if reference.allow_rotation else (False,)

    for rotate in orientations:
        L, W = rotated_size(reference, rotate)
        if W <= trailer_width + WIDTH_TOLERANCE:
            remaining = list(lane_templates)
            template = remaining.pop(0)
            x = max(0.0, (trailer_width - W) / 2)
            row = Row(row_number=row_number)
            row.pallets.append(
                PlacedPallet(
                    description=template.description,
                    length=template.length,
                    width=template.width,
                    height=template.height,
                    weight=template.weight,
                    x=x,
                    y=y_position,
                    rotated=rotate,
                    row=row_number,
                    column=1,
                    unit_number=template.unit_number,
                )
            )
            row.length = L
            row.width_used = W
            return row, remaining

    return None, lane_templates


def choose_alternating_lane(lanes, trailer_width):
    """Pick the lane to run the pair/single stability pattern on: the
    lane with a valid 2-across pattern and the greatest total weight,
    since this technique exists specifically to spread heavy total
    cargo weight over more of the trailer length."""

    best_key = None
    best_weight = -1.0

    for key, lane_templates in lanes.items():
        if not lane_templates:
            continue

        reference = lane_templates[0]
        orientations = (False, True) if reference.allow_rotation else (False,)
        eligible = any(2 * rotated_size(reference, rotate)[1] <= trailer_width + WIDTH_TOLERANCE for rotate in orientations)
        if not eligible:
            continue

        total_weight = sum(t.weight for t in lane_templates)
        if total_weight > best_weight:
            best_weight = total_weight
            best_key = key

    return best_key


def build_alternating_layout(trailer_length, trailer_width, templates, pattern_label) -> Layout:
    """Build a layout using the pair/centred-single stability pattern
    for the heaviest eligible lane, then fill any remaining trailer
    length with whatever cargo is left over."""

    lanes = group_into_lanes(templates)
    alt_key = choose_alternating_lane(lanes, trailer_width)

    rows = []
    pallets = []
    current_y = 0.0
    row_number = 1

    if alt_key is not None:

        lane = lanes[alt_key]
        expect_pair = True  # the bulkhead row must always be a pair

        while lane:

            remaining_length = trailer_length - END_CLEARANCE - current_y
            if remaining_length <= 0:
                break

            if expect_pair:
                row, leftover = build_pair_row(lane, trailer_width, current_y, row_number)
            else:
                row, leftover = build_centered_single_row(lane, trailer_width, current_y, row_number)
                if row is not None:
                    row.locked_after_previous = True

            if row is None or row.length > remaining_length + LENGTH_TOLERANCE:
                # Can't place the next row in the sequence (out of pallets
                # for a pair, or out of room) -- stop the pattern here
                # rather than ever placing a single without a pair ahead
                # of it.
                break

            lane = leftover
            rows.append(row)
            pallets.extend(row.pallets)
            current_y += row.length
            row_number += 1
            expect_pair = not expect_pair

        lanes[alt_key] = lane

    rows, pallets, current_y, row_number = continue_greedy_fill(
        trailer_length, trailer_width, lanes, rows, pallets, current_y, row_number, heuristic="weight"
    )

    return Layout(
        pallets=pallets,
        trailer_length=trailer_length,
        trailer_width=trailer_width,
        rows=rows,
        used_length=current_y,
        free_length=max(0.0, trailer_length - current_y),
        pattern_name=pattern_label,
    )


# ==========================================================
# ROW-ORDER SEARCH -- re-sequence rows along the trailer length
# to search for axle-legal centre-of-gravity placements without
# re-packing anything.
# ==========================================================

def row_weight(row):
    return sum(p.weight for p in row.pallets)


def build_blocks(rows: List[Row]) -> List[List[Row]]:
    """Chunk rows into blocks that must stay together and in order.

    A row with locked_after_previous=True (a stability-pattern single)
    is folded into the block started by the pair row before it. Every
    other row starts its own block and can be freely reordered.
    """
    blocks: List[List[Row]] = []
    for row in rows:
        if row.locked_after_previous and blocks:
            blocks[-1].append(row)
        else:
            blocks.append([row])
    return blocks


def block_weight(block: List[Row]) -> float:
    return sum(row_weight(row) for row in block)


def balanced_block_order(blocks):
    """Lightest blocks at both ends, heaviest blocks toward the middle."""

    ascending = sorted(blocks, key=block_weight)
    n = len(ascending)
    result: List[Optional[List[Row]]] = [None] * n
    lo, hi = 0, n - 1
    place_low = True

    for item in ascending:
        if place_low:
            result[lo] = item
            lo += 1
        else:
            result[hi] = item
            hi -= 1
        place_low = not place_low

    return result


def permute_layout(layout: Layout, order_name: str) -> Optional[Layout]:
    """Return a copy of layout with its rows re-sequenced along the
    trailer length, to search for a centre-of-gravity placement that
    clears axle limits. Rows are moved as locked blocks (see
    build_blocks) so a stability-pattern single row can never end up
    without its supporting pair row directly ahead of it."""

    if len(layout.rows) < 2:
        return None

    new_layout = copy.deepcopy(layout)
    blocks = build_blocks(new_layout.rows)

    if len(blocks) < 2:
        return None

    if order_name == "front-loaded":
        blocks = sorted(blocks, key=block_weight, reverse=True)
    elif order_name == "rear-loaded":
        blocks = sorted(blocks, key=block_weight)
    elif order_name == "balanced":
        blocks = balanced_block_order(blocks)
    else:
        return None

    rows = [row for block in blocks for row in block]

    current_y = 0.0
    for index, row in enumerate(rows, start=1):
        row.row_number = index
        for pallet in row.pallets:
            pallet.y = current_y
            pallet.row = index
        current_y += row.length

    new_layout.rows = rows
    new_layout.pallets = [p for row in rows for p in row.pallets]
    new_layout.used_length = current_y
    new_layout.free_length = max(0.0, new_layout.trailer_length - current_y)
    new_layout.pattern_name = f"{layout.pattern_name} \u00b7 {order_name.replace('-', ' ').title()}"

    return new_layout


# ==========================================================
# SCORE LAYOUT
# ==========================================================

def score_layout(layout: Layout) -> Layout:
    """Higher score = better layout.

    Priority: more pallets, then less unused trailer length, then denser
    floor-space utilisation.
    """

    score = 0
    score += layout.pallet_count * 10000
    score += (layout.trailer_length - layout.free_length) * 100

    if layout.pallets:
        floor_area = layout.trailer_length * layout.trailer_width
        used_area = sum(p.draw_length * p.draw_width for p in layout.pallets)
        if floor_area > 0:
            score += (used_area / floor_area) * 4000

    layout.score = score
    return layout


# ==========================================================
# CREATE ALL CANDIDATES
# ==========================================================

HEURISTICS = [
    ("weight", "Weight-first"),
    ("quantity", "Quantity-first"),
    ("footprint", "Density-first"),
    ("preferred", "Standard pattern"),
    ("insertion", "Manifest order"),
]

ROW_ORDERS = ("front-loaded", "rear-loaded", "balanced")


def create_loading_candidates(truck, cargo) -> List[Layout]:
    """Main packing entry point.

    Builds several physically valid layouts using different construction
    heuristics, then generates row-order variants of each for
    optimizer.py to check against axle limits. optimizer.py decides
    legality; this only decides what's physically possible.
    """

    templates = clone_templates(cargo)

    if not templates:
        return []

    base_layouts = []
    for heuristic, label in HEURISTICS:
        layout = build_layout_greedy(truck.trailer_length, truck.trailer_width, templates, heuristic, label)
        if layout.pallets:
            score_layout(layout)
            base_layouts.append(layout)

    alt_layout = build_alternating_layout(
        truck.trailer_length, truck.trailer_width, templates, "Stability spread (2+1)"
    )
    if alt_layout.pallets:
        score_layout(alt_layout)
        base_layouts.append(alt_layout)

    all_layouts = list(base_layouts)
    for layout in base_layouts:
        for order_name in ROW_ORDERS:
            permuted = permute_layout(layout, order_name)
            if permuted is not None:
                score_layout(permuted)
                all_layouts.append(permuted)

    # Remove duplicates (identical physical placement)
    unique = []
    signatures = set()

    for layout in all_layouts:
        signature = tuple(
            (p.description, round(p.x, 2), round(p.y, 2), p.rotated)
            for p in layout.pallets
        )
        if signature not in signatures:
            signatures.add(signature)
            unique.append(layout)

    unique.sort(key=lambda x: (x.pallet_count, x.score), reverse=True)

    return unique[:MAX_CANDIDATES]


# ==========================================================
# COMPATIBILITY FUNCTION
# ==========================================================

def pack_pallets(truck, cargo):
    """Compatibility wrapper. Returns the best physical layouts."""
    return create_loading_candidates(truck, cargo)


# ==========================================================
# PHYSICAL VALIDATION
# ==========================================================

def pallet_inside_trailer(pallet: PlacedPallet, trailer_length: float, trailer_width: float):
    """Check that pallet is physically inside trailer."""
    return (
        pallet.x >= -0.001
        and pallet.y >= -0.001
        and pallet.x + pallet.draw_width <= trailer_width + 0.001
        and pallet.y + pallet.draw_length <= trailer_length + 0.001
    )


def pallets_overlap(a: PlacedPallet, b: PlacedPallet):
    """Rectangle collision check."""
    return not (
        a.x + a.draw_width <= b.x
        or b.x + b.draw_width <= a.x
        or a.y + a.draw_length <= b.y
        or b.y + b.draw_length <= a.y
    )


def validate_layout(layout: Layout):
    """Verify physical correctness."""

    errors = []

    for pallet in layout.pallets:
        if not pallet_inside_trailer(pallet, layout.trailer_length, layout.trailer_width):
            errors.append(f"{pallet.description}: outside trailer")

    pallets = layout.pallets

    for i in range(len(pallets)):
        for j in range(i + 1, len(pallets)):
            if pallets_overlap(pallets[i], pallets[j]):
                errors.append(f"{pallets[i].description}: overlap")

    return (len(errors) == 0, errors)


# ==========================================================
# LAYOUT UTILITIES
# ==========================================================

def get_layout_dimensions(layout: Layout):
    """Returns used dimensions. Used by reports/drawing."""
    return {
        "length_used": layout.used_length,
        "length_free": layout.free_length,
        "pallets": layout.pallet_count,
        "weight": layout.total_weight,
    }


def get_loaded_pallets(layout: Layout):
    return layout.pallets


# ==========================================================
# OPTIMIZER COMPATIBILITY
# ==========================================================

def get_best_physical_layout(truck, cargo):
    """Returns best physical layout only. Legal checks are done elsewhere."""

    candidates = create_loading_candidates(truck, cargo)

    if not candidates:
        return None

    valid = []
    for layout in candidates:
        ok, _ = validate_layout(layout)
        if ok:
            valid.append(layout)

    if not valid:
        return None

    valid.sort(key=lambda x: (x.pallet_count, x.score), reverse=True)

    return valid[0]


# ==========================================================
# END OF PACKING ENGINE
# ==========================================================
