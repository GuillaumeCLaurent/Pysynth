from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import math
import numpy as np
import pyaudio

# This class is defining the oscilator object, used to create a wave form played by the synth.
# The oscilitar is an iterable object. the next method is call whenever the next value of the waveform is needed
class Oscillator:
    def __init__(self, freq=440, phase=0, amp=1, sample_rate=44_100, wave_range=(-1, 1), waveform=1, threshold=0):
        self._freq = freq #Wave form frequency
        self._amp = amp #Wave form amplitude 
        self._phase = phase #Wave form phase
        self._sample_rate = sample_rate #Synth and oscilator sampling rate
        self._waveform = waveform #Shape of the waveform (1: sin, 2: square)
        self._threshold = threshold #Threshold for the Square wave
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
        # The next method returns the next value of the waveform
        val = math.sin(self._index + self._p)
        if self._waveform == 2:
            if val > self._threshold:
                val = 1
            else:
                val = -1

        elif self._waveform == 3:
            a = self._index + self._p
            val = (a/(self._w)-math.floor(a/(self._w)))
            val = (val-0.5)*2

        elif self._waveform == 4:
            a = self._index + self._p
            b = math.floor(2*a/(self._w))
            val = (2*a/(self._w)-b)
            if b%2 == 1 :
                val = 1-val
            val = (val-0.5)*2
        self._index = (self._index + self._step)%self._w

        return val*self._amp


    def show(self, n):
        x = [i for i in range(n*self._sample_rate)]
        y = [self.__next__() for i in range(n*self._sample_rate)]
        plt.plot(x, y)
        plt.show()
