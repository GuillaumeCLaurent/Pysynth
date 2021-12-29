from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import math
import numpy as np
import pyaudio


class Oscillator:
    def __init__(self, freq=440, phase=0, amp=1, sample_rate=44_100, wave_range=(-1, 1), wave_form=1, threshold=0):

        self._freq = freq
        self._amp = amp
        self._phase = phase
        self._sample_rate = sample_rate
        self._wave_form = wave_form
        self._threshold = threshold
        self._wave_range = wave_range
        self._w = 2*math.pi*self._freq
        self._a = amp
        self._p = phase
        self._index = 0
        self._step = (2*math.pi*self.freq)/self._sample_rate


    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, value):
        self._freq = value
        self._step = (2*math.pi*self.freq)/self._sample_rate
        self._w = 2*math.pi*self._freq

    @property
    def amp(self):
        return self._amp

    @amp.setter
    def amp(self, value):
        self._amp = value

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, value):
        self._phase = value

    def __next__(self):

        val = math.sin(self._index + self._p)
        if self._wave_form == 2:
            if val > self._threshold:
                val = 1
            else:
                val = -1

        elif self._wave_form == 3:
            a = self._index + self._p
            val = (a/(self._w)-math.floor(a/(self._w)))
            val = (val-0.5)*2

        elif self._wave_form == 4:
            a = self._index + self._p
            b = math.floor(2*a/(self._w))
            val = (2*a/(self._w)-b)
            if b%2 == 1 :
                val = 1-val
            val = (val-0.5)*2
        self._index = self._index + self._step

        return val*self._amp


    def show(self, n):
        x = [i for i in range(n*self._sample_rate)]
        y = [self.__next__() for i in range(n*self._sample_rate)]
        plt.plot(x, y)
        plt.show()
