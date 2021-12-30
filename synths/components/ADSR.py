import matplotlib.pyplot as plt
import math
import numpy as np
import pyaudio

## This class define the ADSR envelope object. It is used to adjust the amplitude of the signal through time to mimic reak instruments and give movement.
# This concept is very well explained here : https://www.wikiaudio.org/adsr-envelope/

class ADSR:

    def __init__(self, a=0.02, d=1, s=0.7, r=0.5):
        self._a = a #a is for attack, correponding to the time taken by the signal to reach its maximum amplitude.
        self._d = d #d is for decay
        self._s = s #s is for sustain
        self._r = r #r is for release
        self._i = 0
        self._is_realising = False #This boolean is used to track when the note is off and the signal is released.

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, value):
        self._a = value

    @property
    def d(self):
        return self._d

    @d.setter
    def d(self, value):
        self._d = value

    @property
    def s(self):
        return self._s

    @s.setter
    def s(self, value):
        self._s = value

    @property
    def r(self):
        return self._r
    
    @property
    def is_realising(self):
        return self._is_realising

    @is_realising.setter
    def is_realising(self, value):
        self._is_realising = value
        self._i = 0

    @r.setter
    def r(self, value):
        self._r = value

    def copy(self):
        new = ADSR(a=self._a, d=self._d, s=self._s, r=self._r)
        return new

    def evaluate(self, n):
        # This method evaluate the amplitude value at a given time (i, int) with a given sampling rate (n)
        i = self._i
        self._i = self._i + 1
        if not self._is_realising: 
            if i<self._a*n:
                #Attack
                return i/(self._a*n)
            elif i<self._a*n + self._d*n:
                #Decay
                return (i-self._a*n)/(self._d*n)*(self._s-1)/self._d+1
            else:
                #Sustain
                return self._s
        else:
            #Release
            return max(0, i/(self._r*n)*(-self._s/self._r) + self._s)
        
        

    def show(self, l, n):
        # This method show the envelope with matplotlib.
        x = [i for i in range(int(self._a*n + self._d*n + l*n + self._r*n))]

        y = [i/(self._a*n) for i in range(int(self._a*n))]+ [i/(self._d*n)*(self._s-1)/self._d+1 for i in range(int(self._d*n))] + [self._s for _ in range(int(l*n))] + [i/(self._r*n)*(-self._s/self._r) + self._s for i in range(int(self._r*n))]

        plt.plot(x, y)
        plt.show()