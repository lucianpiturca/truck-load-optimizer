from dataclasses import dataclass


@dataclass
class Truck:
    """
    European articulated truck (tractor + semi-trailer)
    """

    name: str

    trailer_length: float      # metres
    trailer_width: float       # metres
    trailer_height: float      # metres

    legal_gross: int           # kg

    empty_axles: list          # kg on axles 1-5

    axle_limits: list          # kg on axles 1-5

    wheelbase: float           # tractor axle1 -> axle2 (m)

    kingpin_offset: float      # axle2 -> kingpin (m)

    bogie_position: float      # kingpin -> trailer bogie centre (m)

    trailer_front_offset: float  # trailer front -> kingpin (m)

    colour: str = "#d9d9d9"

    @property
    def empty_weight(self):
        return sum(self.empty_axles)

    @property
    def payload_capacity(self):
        return self.legal_gross - self.empty_weight


CURTAINSIDER = Truck(

    name="Curtainsider",

    trailer_length=13.60,
    trailer_width=2.48,
    trailer_height=2.70,

    legal_gross=40000,

    # Axles 1-5
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

    # Standard European 4x2 tractor geometry
    wheelbase=3.60,
    kingpin_offset=0.90,

    # Kingpin -> centre of trailer bogie
    bogie_position=7.50,

    # Trailer front -> kingpin
    trailer_front_offset=1.80,

    colour="#f2f2f2"
)


FRIGO = Truck(

    name="Frigo",

    trailer_length=13.40,
    trailer_width=2.45,
    trailer_height=2.60,

    legal_gross=40000,

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

    wheelbase=3.60,
    kingpin_offset=0.90,
    bogie_position=7.50,
    trailer_front_offset=1.80,

    colour="#d8eefc"
)


TRUCKS = {
    CURTAINSIDER.name: CURTAINSIDER,
    FRIGO.name: FRIGO
}