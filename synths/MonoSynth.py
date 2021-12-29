from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import math
import numpy as np
import pyaudio
import threading
from components.ADSR import ADSR
from components.oscillator import Oscillator
from components.midi_input import Midi_Input

class Midi_input_Thread(threading.Thread):
    def __init__(self, midi_input):
        self._midi_input = midi_input
    
    def run(self):
        self._midi_input.read_note()

class MonoSynth:

    def __init__(self, n=3, wave_forms=[1, 1, 1], freq_coef=[1, 1, 1], amps=[1, 1, 1], phases = [0, 0, 0], sample_rate=44_100, adsr=ADSR()):
        self._sample_rate = sample_rate
        self._wave_forms = wave_forms
        self._freq_coef = freq_coef
        self._amps = amps
        self._note = 0
        self._is_playing = False
        self._n = n
        self._i = 0
        self._oscilators = np.array([Oscillator(freq=freq_coef[i]*440, phase=phases[i], sample_rate=self._sample_rate, wave_form = wave_forms[i], amp = amps[i]) for i in range(n)])
        self._adsr = adsr
        self._midi_input = Midi_Input()
        self._stream = pyaudio.PyAudio().open(
        rate=self._sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        output=True,
        frames_per_buffer=128)

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
        val = self._adsr.evaluate(self._i, self._sample_rate, 0.1)
        self._i = self._i + 1
        return val*s/self._n


    def play_note(self, freq, l):
        for i, osc in enumerate(self._oscilators):
            osc.freq = self._freq_coef[i]*freq

        for i in range(l):
            sample = np.array([int(self.__next__()* 32767) for i in range(128)])
            self._stream.write(sample.tobytes())


    def show(self, n):
        x = [i for i in range(n*self._sample_rate)]
        y = [self.__next__() for i in range(n*self._sample_rate)]
        plt.plot(x, y, "r-")
        plt.show()

    def loop(self):
        self._midi_input.read_note()
        freq, velocity = self._midi_input._note, self._midi_input._velocity

        if freq!= 0:
            print(freq)
            if velocity != 0:
                self._i = 0
                self._is_playing = True
                self._adsr.is_realising = False
                if freq != self._note:
                    
                    self._note = freq
                    for i, osc in enumerate(self._oscilators):
                        osc.freq = self._freq_coef[i]*self._note
            else:
                self._i = 0
                self._is_playing = False
                self._adsr.is_realising = True
                      
        sample = np.array([int(self.__next__()*32767) for i in range(128)])
        self._stream.write(sample.tobytes())

            

    def main(self):
        while True:
            self.loop()


# n=3, wave_forms=[1, 1, 1], freq_coef=[1, 1, 1], amps=[1, 1, 1], phases = [0, 0, 0], sample_rate=44_100, adsr=ADSR()
adsr = ADSR(a=0, d=0.5)
piano = {'n':4,  'wave_forms':[1, 1, 1, 1], 'freq_coef':[1, 2, 3, 4], 'amps':[0.25, 1, 0.125, 0.025], 'phases':[0.1, 0, 0, 0], 'adsr': adsr }
#synth = MonoSynth(n=4, wave_forms=[1, 1, 1, 1], freq_coef=[1, 2, 3, 4], amps=[0.25, 1, 0.125, 0.025], phases = [0, 0, 0, 0])
synth = MonoSynth(**piano)
synth.main()



 









