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



def generate_orientations(pallet):


    result = []


    result.append(

        (
            pallet.width,

            pallet.length

        )

    )


    if pallet.allow_rotation and pallet.width != pallet.length:


        result.append(

            (

                pallet.length,

                pallet.width

            )

        )


    return result



def total_weight(layout):


    return sum(

        p.weight

        for p in layout.pallets

    )



def legal_solution(

    truck,

    layout

):


    axle = calculate_axle_weights(

        truck,

        layout

    )


    if axle.total_weight > truck.legal_gross:

        return False, axle


    for value, limit in zip(

        axle.axles,

        truck.axle_limits

    ):


        if value > limit:

            return False, axle


    return True, axle



def stability_score(layout):


    score = 0


    # reward compact rows

    rows = {}


    for pallet in layout.pallets:


        key = round(

            pallet.y,

            2

        )


        rows[key] = rows.get(

            key,

            0

        ) + 1



    for count in rows.values():


        if count == 3:

            score += 100


        elif count == 2:

            score += 50



    return score



def solution_score(

    layout,

    stability

):


    return (

        len(layout.pallets) * 10000

        +

        stability

    )



def optimize_load(

    truck,

    cargo

):


    pallets = expand_cargo(cargo)



    candidates = []

    rejected = []



    #
    # Try normal packing first
    #

    patterns = [

        "three",

        "two"

    ]



    for pattern in patterns:


        for pallet in pallets:


            pallet.orientations = generate_orientations(

                pallet

            )



        layout = pack_pallets(

            truck,

            pallets,

            pattern=pattern

        )



        if layout is None:

            continue



        legal, axle = legal_solution(

            truck,

            layout

        )


        if legal:


            candidates.append(

                (

                    solution_score(

                        layout,

                        stability_score(layout)

                    ),

                    layout,

                    axle

                )

            )


        else:


            for pallet in pallets:


                rejected.append(

                    {

                        "description":

                        pallet.description,

                        "reason":

                        "Axle or gross weight exceeded"

                    }

                )



    if not candidates:


        return OptimizationResult(

            best=None,

            second_best=None,

            rejected=rejected

        )



    candidates.sort(

        key=lambda x:x[0],

        reverse=True

    )



    best = candidates[0]


    second = None


    if len(candidates) > 1:

        second = candidates[1]



    return OptimizationResult(

        best=(

            best[1],

            best[2]

        ),

        second_best=(

            second[1],

            second[2]

        )

        if second else None,

        rejected=rejected

    )