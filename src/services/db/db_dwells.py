from src.components.models.dwell import Dwell


class DbDwells:
    
    dwell_array: list[Dwell] = [ 
        Dwell(30.0, None, True),    # Einmaischen: keine Zeit, nur Temperatur
        Dwell(30.0, 1200, False),  # 20 min = 1200 s
        Dwell(40.0, 1200, False),
        Dwell(60.0, 1200, True),
        Dwell(60.0, 1200, False),
        Dwell(60.0, None, False),   # Ausmaischen: keine Zeit, nur Temperatur
    ]

    # Tolerance to start the dwell timer
    temp_tolerance = 0.5