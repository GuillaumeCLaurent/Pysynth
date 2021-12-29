import matplotlib.pyplot as plt
import math
import numpy as np
import pyaudio
import threading
from components.ADSR import ADSR
from components.oscillator import Oscillator
from components.midi_input import Midi_Input

## This class defines the polysynth object. It can play one note at a time. It has a midi input, as much oscilators as needed, an adsr envelope
# For now it can only play notes and parameters cannot be modified while playing because it is running on only one thread. 

class PolySynth:

    def __init__(self, n=3, waveforms=[1, 1, 1], freq_coef=[1, 1, 1], amps=[0.03, 0.03, 0.03], phases = [0, 0, 0], sample_rate=44_100, adsr=ADSR()):
        self._sample_rate = sample_rate
        self._n = n
        self._waveforms = waveforms
        self._freq_coef = freq_coef
        self._amps = amps
        self._oscilators_rack = np.array([np.array([Oscillator(freq_coef[i], phases[i], amps[i], self._sample_rate, waveforms[i], 0) for i in range(self._n)]) for _ in range(10)])
        self.init_oscilators(waveforms, freq_coef, amps, phases, sample_rate)
        self._note = 0
        self._is_playing = False
        self._i = 0
        self._oscilators = np.array([Oscillator(freq=freq_coef[i]*440, phase=phases[i], sample_rate=self._sample_rate, waveform = waveforms[i], amp = amps[i]) for i in range(n)])
        self._freqs = np.zeros(10)
        self._adsr = adsr
        self._midi_input = Midi_Input()
        self._stream = pyaudio.PyAudio().open(
        rate=self._sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        output=True,
        frames_per_buffer=128)

    def init_oscilators(self, waveforms, freq_coef, amps, phases, sample_rate):
        self._oscilators_rack = np.array([np.array([Oscillator(freq_coef[i], phases[i], amps[i], self._sample_rate, waveforms[i], 0) for i in range(self._n)]) for _ in range(10)])


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
        for rack in self._oscilators_rack:
            for osc in rack:
                s = s + osc.__next__()
        #val = self._adsr.evaluate(self._i, self._sample_rate)
        self._i = self._i + 1
        return max(-1, min(1, s/self._n))

    def show(self, n):
        x = [i for i in range(n*self._sample_rate)]
        y = [self.__next__() for _ in range(n*self._sample_rate)]
        plt.plot(x, y, "r-")
        plt.show()

    def update_oscilators_rack(self, index, freq, playing):
        self._freqs[index] = freq
        for osc in self._oscilators_rack[index]:
            osc.freq = freq
            osc.is_on = playing


    def loop(self):
        self._midi_input.read_note()
        freq, velocity = self._midi_input._note, self._midi_input._velocity

        if freq >100:
            res = np.where(self._freqs == freq)[0]
            
            if len(res) == 0:
                t = np.where(self._freqs == 0)[0]
                
                if len(t) != 0:
                    self.update_oscilators_rack(t[0], freq, True)
            
            else:
                if velocity == 0:
                    self.update_oscilators_rack(res[0], 0, False)
                    
        sample = np.array([int(self.__next__()*32767) for i in range(128)])
        self._stream.write(sample.tobytes())

            

    def main(self):
        while True:
            self.loop()


if __name__=="__main__":
    # n=3, waveforms=[1, 1, 1], freq_coef=[1, 1, 1], amps=[1, 1, 1], phases = [0, 0, 0], sample_rate=44_100, adsr=ADSR()
    adsr = ADSR(a=0, d=0.5)
    piano = {'n':4,  'waveforms':[1, 1, 1, 1], 'freq_coef':[1, 2, 3, 4], 'amps':[0.25*0.05, 1*0.05, 0.125*0.05, 0.025*0.05], 'phases':[0, 0, 0, 0], 'adsr': adsr }
    test = {'n':1,  'waveforms':[1], 'freq_coef':[1], 'amps':[0.03], 'phases':[0], 'adsr': adsr }
    #synth = PolySynth()#**test)
    synth = PolySynth(**piano)
    synth.show(1)
    synth.main()