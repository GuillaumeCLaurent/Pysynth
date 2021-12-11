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

class ADSR:

    def __init__(self, a=1, d=1, s=0.7, r=1):
        self._a = a
        self._d = d
        self._s = s
        self._r = r

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

    @r.setter
    def r(self, value):
        self._r = value

    def evaluate(self, i, n, l):
        if i<self._a*n:
            return i/(self._a*n)
        elif i<self._a*n + self._d*n:
            return (i-self._a*n)/(self._d*n)*(self._s-1)/self._d+1
        elif i< self._a*n + self._d*n + l*n:
            return self._s
        elif i<self._a*n + self._d*n + l*n + self._r*n:
            return (i-(self._a*n + self._d*n + l*n))/(self._r*n)*(-self._s/self._r) + self._s
        else:
            return 0

    def show(self, l, n):

        x = [i for i in range(int(self._a*n + self._d*n + l*n + self._r*n))]

        y = [i/(self._a*n) for i in range(int(self._a*n))]+ [i/(self._d*n)*(self._s-1)/self._d+1 for i in range(int(self._d*n))] + [self._s for _ in range(int(l*n))] + [i/(self._r*n)*(-self._s/self._r) + self._s for i in range(int(self._r*n))]

        plt.plot(x, y)
        plt.show()


def play_note(osc, freq, l, buffer_size):
    stream = pyaudio.PyAudio().open(
        rate=44_100,
        channels=1,
        format=pyaudio.paInt16,
        output=True,
        frames_per_buffer=buffer_size
    )
    osc.freq = freq
    for i in range(int(l/buffer_size)):
            sample = np.array([int(osc.__next__()* 32767) for _ in range(buffer_size)])
            stream.write(sample.tobytes())
    stream.close()


class Synth:

    def __init__(self, n=3, wave_forms=[1, 1, 1], freq=[440, 440, 440], amps=[1, 1, 1], phases = [0, 0, 0], sample_rate=44_100, adsr=ADSR()):
        self._sample_rate = sample_rate
        self._wave_forms = wave_forms
        self._freq = freq
        self._amps = amps
        self._n = n
        self._i = 0
        self._oscilators = np.array([Oscillator(freq=freq[i], phase=phases[i], sample_rate=self._sample_rate, wave_form = wave_forms[i], amp = amps[i]) for i in range(n)])
        self._adsr = adsr
        self._stream = pyaudio.PyAudio().open(
    rate=self._sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    output=True,
    frames_per_buffer=128
)


    def update_adsr_a(self, value):
        self._adsr.a = value

    def update_adsr_d(self, value):
        self._adsr.d = value

    def update_adsr_s(self, value):
        self._adsr.s = value

    def update_adsr_r(self, value):
        self._adsr.r = value

    def __next__(self):
        s = 0
        for osc in self._oscilators:
            s = s + osc.__next__()
        val = self._adsr.evaluate(self._i, self._sample_rate, 1)
        self._i = self._i + 1
        return val*s/self._n


    def play_note(self, freq, l):
        #for osc in self._oscilators:
            #osc.freq = freq

        for i in range(l):
            sample = np.array([int(self.__next__()* 32767) for i in range(128)])
            self._stream.write(sample.tobytes())


    def show(self, n):
        x = [i for i in range(n*self._sample_rate)]
        y = [self.__next__() for i in range(n*self._sample_rate)]
        plt.plot(x, y, "r-")
        plt.show()




















