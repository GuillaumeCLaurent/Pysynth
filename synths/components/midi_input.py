import pygame.midi as pgm
## This class is used to catch midi input from the keyboard. It uses the pygame.midi library.

class Midi_Input:
    def __init__(self):
        pgm.init()
        self._device_id = pgm.get_default_input_id() 
        self._input = pgm.Input(self._device_id)
        self._note = 0
        self._velocity = 0

    def read_note(self):
        input = self._input.read(1)
        if input != []:
            (status, note, velocity, _) = input[0][0]
            if status == 144 or status == 128:
                self._note = pgm.midi_to_frequency(note)
                self._velocity = velocity
            else:
                self._velocity = 0
                self._note = 0
        else:
            self._velocity = 0
            self._note = 0 