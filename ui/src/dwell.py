
class Dwell:
    
    def __init__(self, tar_temp: float, tar_time:float, alarm: bool):
        self.tar_temp = tar_temp 
        self.tar_time = tar_time 
        self.rest_time = tar_time
        self.alarm = alarm

    def getName(self, index: int, dwell_amount: int):
        if (index == 0):
            return "Einmaischen"
        if (index == (dwell_amount -1)):
            return "Ausmaischen"
        # TODO: Give all the Dwell Names and a effitient way to find the correct one. Else the name ist Rast
        return "Rast"

    def toggleAlarm(self):
        self.alarm = not self.alarm