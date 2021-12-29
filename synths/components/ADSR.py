from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import math
import numpy as np
import pyaudio

class ADSR:

    def __init__(self, a=0.02, d=1, s=0.7, r=0.5):
        self._a = a
        self._d = d
        self._s = s
        self._r = r
        self._is_realising = False

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

    @r.setter
    def r(self, value):
        self._r = value


    def evaluate(self, i, n, l):
        if not self._is_realising:
            if i<self._a*n:
                return i/(self._a*n)
            elif i<self._a*n + self._d*n:
                return (i-self._a*n)/(self._d*n)*(self._s-1)/self._d+1
            else:
                return self._s
        else:
            #if i<self._a*n + self._d*n + l*n + self._r*n:
            return max(0, i/(self._r*n)*(-self._s/self._r) + self._s)
        #else:
            #return 0

    def show(self, l, n):

        x = [i for i in range(int(self._a*n + self._d*n + l*n + self._r*n))]

        y = [i/(self._a*n) for i in range(int(self._a*n))]+ [i/(self._d*n)*(self._s-1)/self._d+1 for i in range(int(self._d*n))] + [self._s for _ in range(int(l*n))] + [i/(self._r*n)*(-self._s/self._r) + self._s for i in range(int(self._r*n))]

        plt.plot(x, y)
        plt.show()

