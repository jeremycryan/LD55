from combatant import Frog, BigFrog, Lizard, Seeker, Unicorn, Beekeeper
import constants as c
import random

from combatant_collection import CombatantCollection


class Frame:
    def __init__(self, game):
        self.game = game
        self.done = False

    def load(self):
        pass

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))

    def next_frame(self):
        return Frame(self.game)


class ArenaFrame(Frame):
    def load(self):
        self.combatants = CombatantCollection()
        #self.combatants.add_multiple([Frog(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5, random.random()*c.WINDOW_HEIGHT), tribe=0) for _ in range(10)])
        self.combatants.add_multiple([Frog(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5 + c.WINDOW_WIDTH//2, random.random()*c.WINDOW_HEIGHT), tribe=1) for _ in range(5)])
        self.combatants.add_multiple([Seeker(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5, random.random()*c.WINDOW_HEIGHT), tribe=0) for _ in range(3)])
        self.combatants.add_multiple([Unicorn(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5, random.random()*c.WINDOW_HEIGHT), tribe=0) for _ in range(1)])
        self.combatants.add_multiple([BigFrog(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5, random.random()*c.WINDOW_HEIGHT), tribe=0) for _ in range(2)])
        self.combatants.add_multiple([Lizard(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5 + c.WINDOW_WIDTH//2, random.random()*c.WINDOW_HEIGHT), tribe=1) for _ in range(3)])
        self.combatants.add_multiple([Beekeeper(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5 + c.WINDOW_WIDTH//2, random.random()*c.WINDOW_HEIGHT), tribe=1) for _ in range(3)])

    def update(self, dt, events):
        self.combatants.update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        surface.fill((128, 190, 128))
        self.combatants.draw(surface, offset)
