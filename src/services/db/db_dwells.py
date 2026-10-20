from src.components.models.dwell import Dwell


class DbDwells:
    
    dwell_array: list[Dwell] = [ # TODO: Eventuell komplett in eine lokale Datenbank verschieben
        Dwell(30.0, None, True),    # Einmaischen: keine Zeit, nur Temperatur
        Dwell(30.0, 12000, False),  # 20 min = 12000 ds
        Dwell(40.0, 12000, False),
        Dwell(60.0, 12000, True),
        Dwell(60.0, 12000, False),
        Dwell(60.0, None, False),   # Ausmaischen: keine Zeit
    ]
