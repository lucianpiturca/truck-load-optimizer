def calculate_axle_loads(truck, pallets):
    """
    Calculates approximate axle loads.

    Uses:
    - empty axle weights from truck.py
    - pallet position inside trailer
    - trailer length distribution

    x position:
        0 = front of trailer
        trailer_length = rear doors
    """


    # Start with empty truck

    axle_loads = [

        float(x)

        for x in truck.empty_axles

    ]


    if not pallets:
        return axle_loads



    trailer_length = truck.trailer_length



    total_cargo = sum(

        pallet["weight"]

        for pallet in pallets

    )


    for pallet in pallets:


        weight = pallet["weight"]


        # pallet center position

        center = (

            pallet["x"]

            +

            pallet["length"] / 2

        )


        position_ratio = (

            center

            /

            trailer_length

        )


        if position_ratio < 0:

            position_ratio = 0


        if position_ratio > 1:

            position_ratio = 1



        #
        # Distribution model:
        #
        # Front of trailer affects tractor axles more
        # Rear affects trailer axles more
        #


        tractor_share = (

            1 - position_ratio

        )


        trailer_share = position_ratio



        tractor_load = (

            weight

            *

            tractor_share

        )


        trailer_load = (

            weight

            *

            trailer_share

        )



        # Split tractor load

        axle_loads[0] += (

            tractor_load * 0.45

        )


        axle_loads[1] += (

            tractor_load * 0.55

        )



        # Split trailer bogie

        axle_loads[2] += (

            trailer_load * 0.34

        )


        axle_loads[3] += (

            trailer_load * 0.33

        )


        axle_loads[4] += (

            trailer_load * 0.33

        )



    return axle_loads





def check_axles(truck, axle_loads):

    """
    Returns legal status for each axle.
    """


    results = []


    for load, limit in zip(

        axle_loads,

        truck.axle_limits

    ):

        results.append({

            "weight": load,

            "limit": limit,

            "legal": load <= limit

        })


    return results





def calculate_gross_weight(axle_loads):

    return sum(axle_loads)