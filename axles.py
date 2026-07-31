def calculate_axle_loads(truck, pallets):
    """
    European 6x2 tractor + 3 axle semi-trailer model.

    Assumptions:
    Tractor:
        Axle 1 -> steering axle
        Axle 2 -> drive axle

    Trailer:
        Axle 3-5 -> tri-axle bogie


    Geometry assumptions:

    Tractor:
        Axle1 to Axle2 = 3.6 m
        Axle2 to Kingpin = 0.9 m


    Trailer:
        Kingpin to axle group center = 7.5 m

    """



    # -----------------------------
    # Empty vehicle weights
    # -----------------------------

    axle1 = truck.empty_axles[0]

    axle2 = truck.empty_axles[1]

    axle3 = truck.empty_axles[2]

    axle4 = truck.empty_axles[3]

    axle5 = truck.empty_axles[4]



    # -----------------------------
    # Accumulated loads
    # -----------------------------

    kingpin_load = 0

    trailer_load = 0



    for pallet in pallets:


        weight = pallet.get(
            "weight",
            0
        )


        # pallet centre position
        pallet_center = (

            pallet.get("x", 0)

            +

            pallet.get("length", 0) / 2

        )



        # metres from trailer front

        distance_from_front = pallet_center



        #
        # Semi trailer:
        #
        # Front of trailer near kingpin
        # Rear near axle group
        #


        trailer_length = 13.6


        # simplified load split

        trailer_share = (

            distance_from_front

            /

            trailer_length

        )


        trailer_share = max(

            0,

            min(

                1,

                trailer_share

            )

        )


        kingpin_part = (

            weight

            *

            (1 - trailer_share)

            *

            0.45

        )


        bogie_part = (

            weight

            -

            kingpin_part

        )


        kingpin_load += kingpin_part

        trailer_load += bogie_part



    # -----------------------------
    # Tractor load distribution
    # -----------------------------

    #
    # Kingpin sits behind drive axle.
    #
    # Most kingpin load goes to drive axle.
    # Small part transfers to steering axle.
    #


    axle1 += kingpin_load * 0.15

    axle2 += kingpin_load * 0.85



    # -----------------------------
    # Trailer axle distribution
    # -----------------------------


    axle3 += trailer_load / 3

    axle4 += trailer_load / 3

    axle5 += trailer_load / 3



    return [

        axle1,

        axle2,

        axle3,

        axle4,

        axle5

    ]





def check_axles(truck, axle_loads):


    limits = [

        10000,

        11500,

        8000,

        8000,

        8000

    ]


    results = []


    for i, weight in enumerate(axle_loads):


        results.append(

            {

                "axle":

                    i + 1,


                "weight":

                    weight,


                "limit":

                    limits[i],


                "legal":

                    weight <= limits[i]

            }

        )


    return results





def calculate_gross_weight(axle_loads):


    return sum(

        axle_loads

    )