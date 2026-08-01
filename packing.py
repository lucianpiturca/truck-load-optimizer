# packing.py

from dataclasses import dataclass, field



@dataclass
class Pallet:

    id: int

    description: str

    width: float

    length: float

    height: float

    weight: float

    allow_rotation: bool = True

    x: float = 0

    y: float = 0

    rotated: bool = False

    loaded: bool = True


@dataclass
class LayoutResult:

    pallets: list = field(default_factory=list)

    rejected: list = field(default_factory=list)



def possible_orientations(pallet):

    orientations = [

        (
            pallet.width,
            pallet.length,
            False
        )

    ]


    if pallet.allow_rotation and pallet.width != pallet.length:

        orientations.append(

            (
                pallet.length,
                pallet.width,
                True
            )

        )


    return orientations



def can_place(

    x,

    y,

    width,

    length,

    placed,

    trailer_width,

    trailer_length

):


    # trailer limits

    if x + width > trailer_width:

        return False


    if y + length > trailer_length:

        return False



    # collision check

    for p in placed:


        if not (

            x + width <= p.x

            or

            p.x + p.width <= x

            or

            y + length <= p.y

            or

            p.y + p.length <= y

        ):

            return False


    return True



def pack_pallets(

    truck,

    pallets,

    pattern="three"

):


    placed = []

    rejected = []



    # ==================================================
    # determine row width preference
    # ==================================================

    if pattern == "three":

        # search narrow side first

        orientations_order = [

            "narrow"

        ]


    else:

        orientations_order = [

            "wide"

        ]



    current_y = 0



    row_height = None



    for pallet in pallets:


        fitted = False



        for width, length, rotated in possible_orientations(pallet):


            # pattern preference

            if pattern == "three":

                # prefer 80 cm side across

                if width > length:

                    continue


            elif pattern == "two":

                # prefer 120 cm side across

                if width < length:

                    continue



            x_positions = []


            # left to right search

            x = 0


            while x <= truck.trailer_width - width:


                x_positions.append(x)

                x += 0.01



            # front to back search

            for y in [

                round(i * 0.01,2)

                for i in range(

                    int(truck.trailer_length*100)+1

                )

            ]:


                for x in x_positions:


                    if can_place(

                        x,

                        y,

                        width,

                        length,

                        placed,

                        truck.trailer_width,

                        truck.trailer_length

                    ):


                        new_pallet = Pallet(

                            id=pallet.id,

                            description=pallet.description,

                            width=width,

                            length=length,

                            height=pallet.height,

                            weight=pallet.weight,

                            allow_rotation=pallet.allow_rotation,

                            x=x,

                            y=y,

                            rotated=rotated

                        )


                        placed.append(

                            new_pallet

                        )


                        fitted = True


                        break



                if fitted:

                    break



            if fitted:

                break



        if not fitted:


            rejected.append(

                {

                    "description":

                    pallet.description,

                    "id":

                    pallet.id,

                    "reason":

                    "Could not fit physically"

                }

            )



    return LayoutResult(

        pallets=placed,

        rejected=rejected

    )