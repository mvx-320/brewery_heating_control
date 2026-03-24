from src.components.models.dwell_name import DwellName

class DwellNameService:
    # TODO: Safe the Dwell Names and their min and max, temp and time as a "static" variable
    # TODO: Should be stored in a JSON
    dwell_names: list[DwellName] = [
        DwellName("Gummirast", 35.0, 40.0, 15.0, 30.0),
        DwellName("Weizenrast", 40.0, 48.0, 15.0, 15.0),
        DwellName("Maltoserast", 30.0, 45.0, 30.0, 60.0),
        DwellName("Eiweißrast", 50.0, 58.0, 10.0, 20.0),
        DwellName("Maltoserast", 60.0, 68.0, 30.0, 90.0),
        DwellName("Verzuckerungsrast", 70.0, 75.0, 15.0, 45.0)
    ]

    def getDwellName(self, temp: float, time: float) -> str:
        for dwell_name in self.dwell_names:
            if (dwell_name.min_temp <= temp <= dwell_name.max_temp) and (dwell_name.min_time <= time <= dwell_name.max_time):
                return dwell_name.name
        return "Rast"