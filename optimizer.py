# optimizer.py

from dataclasses import dataclass

from packing import (
    Pallet,
    LayoutResult,
    pack_pallets
)

from axles import calculate_axle_weights



@dataclass
class OptimizationResult:

    best: tuple | None = None

    second_best: tuple | None = None

    rejected: list = None



def expand_cargo(cargo):

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



def stability_score(layout):

    rows = {}


    for pallet in layout.pallets:

        y = round(pallet.y, 1)

        rows[y] = rows.get(y, 0) + 1


    score = 0


    for count in rows.values():

        if count == 3:

            score += 100

        elif count == 2:

            score += 50


    return score



def calculate_score(layout):

    return (

        len(layout.pallets) * 10000

        +

        stability_score(layout)

    )



def is_legal(

    truck,

    layout

):


    axle_report = calculate_axle_weights(

        truck,

        layout.pallets

    )


    if axle_report.total_weight > truck.legal_gross:

        return False, axle_report


    for axle, limit in zip(

        axle_report.axles,

        truck.axle_limits

    ):

        if axle > limit:

            return False, axle_report


    return True, axle_report



def optimize_load(

    truck,

    cargo

):


    pallets = expand_cargo(cargo)


    candidates = []

    rejected = []



    # Prefer 3-wide layout first

    patterns = [

        "three",

        "two"

    ]



    for pattern in patterns:


        layout = pack_pallets(

            truck,

            pallets,

            pattern=pattern

        )


        if layout is None:

            continue



        legal, axle_report = is_legal(

            truck,

            layout

        )


        if legal:


            candidates.append(

                {

                    "score":

                    calculate_score(layout),

                    "layout":

                    layout,

                    "axles":

                    axle_report

                }

            )


        else:


            rejected.append(

                {

                    "description":

                    "Cargo",

                    "reason":

                    "Axle or gross weight exceeded"

                }

            )



        for item in layout.rejected:

            rejected.append(item)



    if not candidates:


        return OptimizationResult(

            best=None,

            second_best=None,

            rejected=rejected

        )



    candidates.sort(

        key=lambda x:x["score"],

        reverse=True

    )



    best = candidates[0]


    second = (

        candidates[1]

        if len(candidates) > 1

        else None

    )



    return OptimizationResult(

        best=(

            best["layout"],

            best["axles"]

        ),

        second_best=(

            second["layout"],

            second["axles"]

        )

        if second else None,

        rejected=rejected

    )