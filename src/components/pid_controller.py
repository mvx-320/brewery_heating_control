import sys, os, logging

from src.db_service.db_pid_values import PidValueService

class PidContoller:
    dt = PidValueService.dt # global

    def __init__(self, kp, ki, kd):
        self.logger = logging.getLogger(__name__)
        self.max = 1.0
        self.min = 0.0
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.hysterese = 0
        self.h_value = 0.2
        self.integ = 0
        self.err = 0

    def calculate(self, set, act):
        tolerance = act * -0.008571428571428572 + 1.1857142857142857 # act = 20 -> 1; act = 80 -> 0.5
        if (act < set - tolerance + self.hysterese):
            self.hysterese = self.h_value
            return self.max, False
        elif (act > set + tolerance/2 - self.hysterese):
            self.hysterese = self.h_value
            return self.min, False
        else:
            self.hysterese = 0
            error = set - act;

            P = self.kp * error;
            
            if act < set:
                self.integ += error * self.dt
            else:
                self.integ = 30
            I = self.ki * self.integ;

            D = self.kd * (error - self.err) / self.dt;

            output = P + I + D; # 0.0 - 1.0
            
            #self.logger.info(f'\t\tP:{P:>4.4f} + I:{I:>4.4f} + D:{D:>4.4f} = {output_proz:>4.4f}; integ: {self.integ:>8.4f}')
            
            if output > self.max:
                output = self.max
            elif output < self.min:
                output = self.min

            self.err = error;
            
            
            return output, True

