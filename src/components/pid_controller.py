import logging
from src.components.models.pid_gains import PidGains
from src.components.models.pid_cool_factor import PidCoolFactor

class PidContoller:

    def __init__(self, dt, gains30: PidGains, gains80: PidGains, coolfactor: PidCoolFactor, tm_lag):
        self.logger = logging.getLogger(__name__)
        self.dt = dt
        self.max = 1.0
        self.min = 0.0
        self.gains30 = gains30
        self.gains80 = gains80
        self.coolfactor = coolfactor
        self.integ = 0
        self.last_error = 0
        self.last_output = 0
        self.tm_lag = tm_lag # Prevents rapid jumps in the output
        self.filtered_d = 0.0
        self.err = 0


    def calculate(self, set, act):
        '''
        First calculate P & D
        Then the conditional integration (I)
        Then limits the output
        '''
        kp = self.linear_interpolate_value(act, self.gains30.kp, self.gains80.kp)
        ki = self.linear_interpolate_value(act, self.gains30.ki, self.gains80.ki)
        kd = self.linear_interpolate_value(act, self.gains30.kd, self.gains80.kd)

        error = set - act
        
        P = kp * error

        # Conditianl integration (prevents windup)
        if not (self.last_output >= 1.0 and error > 0 or self.last_output <= 0.0 and error < 0): 
            # Reduces self.integ in the right speed
            cooling_factor = self.parabolic_interpolate_value(act, self.coolfactor.factor30, self.coolfactor.factor50, self.coolfactor.factor80) if error < self.coolfactor.threshold else 1

            self.integ += error * self.dt * cooling_factor
        I = ki * self.integ

        # Low-pass Filter calculates how quickly the temperature error changes
        alpha = self.dt / (self.tm_lag + self.dt) # Determines how quickly the filtered value follows the raw D-term
        raw_d = kd * (error - self.err) / self.dt
        self.filtered_d += alpha * (raw_d - self.filtered_d)
        D = self.filtered_d
        raw_output = P + I + D
        self.last_output = raw_output

        output = max(self.min, min(raw_output, self.max))

        self.last_error = error
        return output, True

    def linear_interpolate_value(self, temperature: float, value30: float, value80: float):
        '''
        For Gain Scheduling (different gains at different temperatures)
        '''
        m = (temperature - 30) / 50.0
        return value30 + m * (value80 - value30)

    def parabolic_interpolate_value(self, temperature: float, value30:float, value50: float, value80: float):
        '''
        For Cooling Factor (add more precise cooling)
        ''' 
        return (
            value30 * (temperature - 50) * (temperature - 80) / 1000
            - value50 * (temperature -30) * (temperature - 80) / 600
            + value80 * (temperature -30) * (temperature - 50) / 1500)
