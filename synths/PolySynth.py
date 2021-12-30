import matplotlib.pyplot as plt
import math
import numpy as np
import pyaudio
import threading
from components.ADSR import ADSR
from components.oscillator import Oscillator
from components.midi_input import Midi_Input
import time

## This class defines the polysynth object. It can play one note at a time. It has a midi input, as much oscilators as needed, an adsr envelope
# For now it can only play notes and parameters cannot be modified while playing because it is running on only one thread. 

class PolySynth:

    def __init__(self, n=3, m=10, waveforms=[1, 1, 1], freq_coef=[1, 1, 1], amps=[0.03, 0.03, 0.03], phases = [0, 0, 0], sample_rate=44_100, adsr=ADSR()):
        self._sample_rate = sample_rate
        self._n = n
        self._m = m
        self._waveforms = waveforms
        self._freq_coef = freq_coef
        self._amps = amps
        self._oscilators_rack = np.array([np.array([Oscillator(freq_coef[i], phases[i], amps[i], self._sample_rate, waveforms[i], 0) for i in range(self._n)]) for _ in range(m)])
        self._note = 0
        self._is_playing = False
        self._i = 0
        self._freqs = np.zeros(m)
        self._adsrs = [adsr.copy() for _ in range(m)]
        self._midi_input = Midi_Input()
        self._stream = pyaudio.PyAudio().open(
        rate=self._sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        output=True,
        frames_per_buffer=128)
        self._input_thread = threading.Thread(target=self.input_loop, daemon=True)

    def update_adsr_a(self, value):
        for adsr in self._adsrs:
            adsr.a = value

    def update_adsr_d(self, value):
        for adsr in self._adsrs:
            adsr.d = value

    def update_adsr_s(self, value):
        for adsr in self._adsrs:
            adsr.s = value

    def update_adsr_r(self, value):
        for adsr in self._adsrs:
            adsr.r = value

    def __next__(self):
        s = 0
        for i, rack in enumerate(self._oscilators_rack):
            subs = 0
            for osc in rack:
                subs = subs + osc.__next__()
            val = self._adsrs[i].evaluate(self._sample_rate)
            s = s+subs*val
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
        self._adsrs[index].is_realising = not playing


    def input_loop(self):
        while True:
            self._midi_input.read_note()
            freq, velocity = self._midi_input._note, self._midi_input._velocity

            if freq >10:
                res = np.where(self._freqs == freq)[0]
                
                if len(res) == 0:
                    t = np.where(self._freqs == 0)[0]
                    
                    if len(t) != 0:
                        self.update_oscilators_rack(t[0], freq, True)
                        
                
                else:
                    if velocity == 0:
                        self.update_oscilators_rack(res[0], 0, False)
                        


    def sound_loop(self):    
        while True:    
            #print(self._freqs)
            #time.sleep(0.5)
            sample = np.array([int(self.__next__()*32767) for i in range(128)])
            self._stream.write(sample.tobytes())
            

            

    def main(self):
        self._input_thread.start()
        #self._sound_thread.start()
        self.sound_loop()
        


if __name__=="__main__":
    # n=3, waveforms=[1, 1, 1], freq_coef=[1, 1, 1], amps=[1, 1, 1], phases = [0, 0, 0], sample_rate=44_100, adsr=ADSR()
    adsr = ADSR(a=0.2, d=0.5, s=0.8, r = 0.8)
    piano = {'n':4,  'waveforms':[1, 1, 1, 1], 'freq_coef':[1, 2, 3, 4], 'amps':[0.25*0.05, 1*0.05, 0.125*0.05, 0.025*0.05], 'phases':[0, 0, 0, 0], 'adsr': adsr }
    test = {'n':1,  'waveforms':[1], 'freq_coef':[1], 'amps':[0.1], 'phases':[0], 'adsr': adsr }
    #synth = PolySynth()#**test)
    synth = PolySynth(**test)
    #synth.show(1)
    synth.main()
    time.sleep(10)
    print("done")