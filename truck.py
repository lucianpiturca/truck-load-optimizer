from dataclasses import dataclass


@dataclass(frozen=True)
class Truck:
    """
    Standard European articulated vehicle (tractor + semi-trailer)
    """

    # Display
    name: str
    colour: str

    # Internal loading dimensions (metres)
    internal_length: float
    internal_width: float
    internal_height: float

    # Maximum permitted cargo height
    max_cargo_height: float

    # Legal gross vehicle weight (kg)
    legal_gross_weight: float

    # Empty axle weights (tractor with fuel + empty trailer)
    # [Steer, Drive, Trailer1, Trailer2, Trailer3]
    empty_axles: list[float]

    # Legal axle limits
    axle_limits: list[float]

    # ------------------------------------------------------------------
    # Standard European trailer geometry
    # ------------------------------------------------------------------

    # Front bulkhead -> kingpin
    kingpin_to_front: float

    # Kingpin -> centre of tridem bogie
    kingpin_to_bogie: float

    # Centre of bogie -> rear doors
    bogie_to_rear: float

    # Tractor wheelbase
    wheelbase: float

    # ------------------------------------------------------------------
    # Calculated properties
    # ------------------------------------------------------------------

    @property
    def trailer_length(self):
        return self.internal_length

    @property
    def trailer_width(self):
        return self.internal_width

    @property
    def trailer_height(self):
        return self.internal_height

    @property
    def total_empty_weight(self):
        return sum(self.empty_axles)

    @property
    def payload_capacity(self):
        return self.legal_gross_weight - self.total_empty_weight

    @property
    def bogie_position_from_front(self):
        """
        Distance from front bulkhead to centre of tridem.
        """
        return self.kingpin_to_front + self.kingpin_to_bogie

    @property
    def rear_position(self):
        return self.internal_length


# ==========================================================
# STANDARD EUROPEAN CURTAINSIDER
# ==========================================================

CURTAINSIDER = Truck(

    name="Curtainsider",

    colour="#efefef",

    internal_length=13.62,
    internal_width=2.48,
    internal_height=2.70,

    max_cargo_height=2.70,

    legal_gross_weight=40000,

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

    kingpin_to_front=1.60,
    kingpin_to_bogie=7.60,
    bogie_to_rear=4.42,

    wheelbase=3.60
)


# ==========================================================
# STANDARD EUROPEAN REFRIGERATED TRAILER
# ==========================================================

FRIGO = Truck(

    name="Refrigerated",

    colour="#dceeff",

    internal_length=13.41,
    internal_width=2.45,
    internal_height=2.60,

    # 20 cm reserved for evaporator and air circulation
    max_cargo_height=2.40,

    legal_gross_weight=40000,

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

    kingpin_to_front=1.60,
    kingpin_to_bogie=7.60,
    bogie_to_rear=4.21,

    wheelbase=3.60
)


TRUCKS = {
    CURTAINSIDER.name: CURTAINSIDER,
    FRIGO.name: FRIGO
}