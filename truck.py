from dataclasses import dataclass

@dataclass
class TruckProfile:

    name: str

    trailer_length: float
    trailer_width: float

    empty_axles: list

    axle_limits: list

    legal_gross: int


TRUCKS = {

    "Curtainsider": TruckProfile(

        name="Curtainsider",

        trailer_length=13.60,
        trailer_width=2.48,

        empty_axles=[
            5200,
            2800,
            2670,
            2670,
            2670
        ],

        axle_limits=[
            10000,
            11500,
            8000,
            8000,
            8000
        ],

        legal_gross=40000

    ),

    "Frigo": TruckProfile(

        name="Frigo",

        trailer_length=13.40,
        trailer_width=2.45,

        empty_axles=[
            5400,
            3800,
            2940,
            2940,
            2940
        ],

        axle_limits=[
            10000,
            11500,
            8000,
            8000,
            8000
        ],

        legal_gross=40000

    )

}