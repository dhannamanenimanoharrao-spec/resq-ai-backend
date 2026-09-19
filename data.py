from models import Ambulance, Emergency, Hospital


ambulances = [
    Ambulance(
        id="AMB-001",
        name="Ambulance 01",
        latitude=17.4435,
        longitude=78.3772,
        status="available",
        ambulance_type="advanced",
    ),
    Ambulance(
        id="AMB-002",
        name="Ambulance 02",
        latitude=17.4650,
        longitude=78.3560,
        status="available",
        ambulance_type="basic",
    ),
    Ambulance(
        id="AMB-003",
        name="Ambulance 03",
        latitude=17.4200,
        longitude=78.4500,
        status="available",
        ambulance_type="advanced",
    ),
    Ambulance(
        id="AMB-004",
        name="Ambulance 04",
        latitude=17.3900,
        longitude=78.4700,
        status="busy",
        ambulance_type="basic",
    ),
]


hospitals = [
    Hospital(
        id="HOS-001",
        name="Hospital Alpha",
        latitude=17.4420,
        longitude=78.3900,
        available_beds=24,
        emergency_capable=True,
    ),
    Hospital(
        id="HOS-002",
        name="Hospital Beta",
        latitude=17.4300,
        longitude=78.4100,
        available_beds=12,
        emergency_capable=True,
    ),
    Hospital(
        id="HOS-003",
        name="Hospital Gamma",
        latitude=17.4050,
        longitude=78.4500,
        available_beds=31,
        emergency_capable=True,
    ),
]


emergencies: list[Emergency] = []