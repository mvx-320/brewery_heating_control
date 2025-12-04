#!/usr/bin/python3
# ------------------------------------------------------------------------------
# Python 3.4.3
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# includes
# ------------------------------------------------------------------------------
import os
import sys


# ------------------------------------------------------------------------------
class myPID:
    dt = 0.0
    max = 0.0
    min = 0.0
    kp = 0.0
    kd = 0.0
    ki = 0.0
    err = 0.0
    integ = 0.0

    def __init__(self, dt, max_w, min_w, kp, ki, kd):
        self.dt = dt
        self.max = max_w
        self.min = min_w
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.hysterese = 0
        self.h_value = 0.2

    def calculate(self, set, act):
        tolerance = act * -0.008571428571428572 + 1.1857142857142857
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

            output_proz = P + I + D;
            output_watt = (output_proz *35)
            
            #print(f'\t\tP:{P:>4.4f} + I:{I:>4.4f} + D:{D:>4.4f} = {output_proz:>4.4f}; integ: {self.integ:>8.4f}')
            
            if output_watt > self.max:
                output_watt = self.max
            elif output_watt < self.min:
                output_watt = self.min

            self.err = error;
            
            
            return output_watt, True


# ------------------------------------------------------------------------------
def main():
    pid = myPID(0.1, 100, -100, 0.1, 0.01, 0.5)

    val = 20;
    for i in range(100):
        inc = pid.run(0, val)
        print('val:', '{:7.3f}'.format(val), ' inc:', '{:7.3f}'.format(inc))
        val += inc


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
# ------------------------------------------------------------------------------
