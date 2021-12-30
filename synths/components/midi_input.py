import pygame.midi as pgm
## This class is used to catch midi input from the keyboard. It uses the pygame.midi library.

class Midi_Input:
    def __init__(self, is_for_control=False):
        pgm.init()
        self._device_id = pgm.get_default_input_id() 
        self._input = pgm.Input(self._device_id)
        self._note = 0
        self._velocity = 0
        self._parameter = 0
        self._value = 0
        self._is_for_control = is_for_control

    def read_note(self):
        input = self._input.read(1)
        if input != []:
            (status, note, velocity, _) = input[0][0]
            if status == 144 or status == 128:
                self._note = pgm.midi_to_frequency(note)
                self._velocity = velocity
                print(self._note)
            else:
                self._velocity = 0
                self._note = 0
        else:
            self._velocity = 0
            self._note = 0 

    def read_control(self):
        input = self._input.read(1)
        if input != []:
            (status, parameter, value, _) = input[0][0]
            if status == 176:
                self._parameter = parameter
                self._value = value
                print(self._value)
            else:
                self._parameter= 0
                self._value = 0
        else:
            self._parameter = 0
            self._value = 0 