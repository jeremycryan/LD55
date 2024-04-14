import math
import time

import pygame

from combatant import Frog, BigFrog, Lizard, Seeker, Unicorn, Beekeeper, TYPES
import constants as c
import random

from combatant_collection import CombatantCollection
from image_manager import ImageManager
from panel import Panel
from primitives import Pose


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


class ShopFrame(Frame):
    def load(self):
        self.background = ImageManager.load("images/shop_background.png")
        self.sign = ImageManager.load("images/shop_sign.png")
        self.teams = ImageManager.load("images/team_names.png")

        self.cauldron = ImageManager.load_copy("images/cauldron.png")
        self.cost_font = pygame.font.Font("fonts/SpicySushi.ttf", 60)


        self.panels = [
            Panel(Frog, Pose((500, 650))),
            Panel(Seeker, Pose((c.WINDOW_WIDTH//2, 650))),
            Panel(Beekeeper, Pose((c.WINDOW_WIDTH - 500, 650))),
            Panel(BigFrog, Pose((500, 900))),
            Panel(Lizard, Pose((c.WINDOW_WIDTH//2, 900))),
            Panel(Unicorn, Pose((c.WINDOW_WIDTH - 500, 900))),
        ]

        self.money = {0: 100, 1:100}
        self.summons = {0: {}, 1:{}}

    def update(self, dt, events):
        for panel in self.panels:
            panel.update(dt, events)

        for event in events:
            if event.type == "Twitch":
                self.process_twitch_message(event.message)

    def draw(self, surface, offset=(0, 0)):
        surface.blit(self.background, offset)
        surface.blit(self.teams, (offset[0], offset[1] + math.sin(time.time()*4.5)*4))
        surface.blit(self.sign, (c.WINDOW_WIDTH//2 - self.sign.get_width()//2 + offset[0], offset[1]))
        for panel in self.panels:
            panel.draw(surface, offset)

        cost_surf = self.cost_font.render(f"{self.money[0]}", True, (80, 60, 100))
        cauldron_surf = self.cauldron.copy()
        cauldron_surf.blit(cost_surf,
            (cauldron_surf.get_width()//2 - cost_surf.get_width()//2,
            cauldron_surf.get_height()//2 - cost_surf.get_height()//2 + 15))
        cost_surf = self.cost_font.render(f"{self.money[0]}", True, (255, 255, 255))
        cauldron_surf.blit(cost_surf,
            (cauldron_surf.get_width()//2 - cost_surf.get_width()//2,
            cauldron_surf.get_height()//2 - cost_surf.get_height()//2 + 10))

        x, y = (120 - self.cauldron.get_width()//2, 120 - self.cauldron.get_height()//2)
        surface.blit(cauldron_surf, (x+offset[0], y+offset[1]))

        cost_surf = self.cost_font.render(f"{self.money[1]}", True, (80, 60, 100))
        cauldron_surf = self.cauldron.copy()
        cauldron_surf.blit(cost_surf,
            (cauldron_surf.get_width()//2 - cost_surf.get_width()//2,
            cauldron_surf.get_height()//2 - cost_surf.get_height()//2 + 15))
        cost_surf = self.cost_font.render(f"{self.money[1]}", True, (255, 255, 255))
        cauldron_surf.blit(cost_surf,
            (cauldron_surf.get_width()//2 - cost_surf.get_width()//2,
            cauldron_surf.get_height()//2 - cost_surf.get_height()//2 + 10))

        x, y = (c.WINDOW_WIDTH - 120 - self.cauldron.get_width()//2, 120 - self.cauldron.get_height()//2)
        surface.blit(cauldron_surf, (x+offset[0], y+offset[1]))



    def process_twitch_message(self, message):
        text = message.text.lower()
        if not text or text[0] != "!":
            return
        text = text[1:]
        split = text.split()
        if not split:
            return

        if split[0] == "join" and len(split) == 2:
            if split[1] == "yellow":
                if message.user not in self.game.teams[0]:
                    self.game.teams[0].append(message.user)
                    if message.user in self.game.teams[1]:
                        self.game.teams[1].remove(message.user)
            if split[1] == "blue":
                if message.user not in self.game.teams[1]:
                    self.game.teams[1].append(message.user)
                    if message.user in self.game.teams[0]:
                        self.game.teams[0].remove(message.user)

        if message.user not in self.game.teams[0] and message.user not in self.game.teams[1]:
            return  # ignore people who haven't joined a team

        if split[0] == "buy" and len(split) in (2, 3):
            creature_type = None
            for creature in TYPES:
                if creature.NAME.lower() == split[1]:
                    creature_type = creature
            if not creature_type:
                return
            if len(split) == 2:
                quantity = 1
            else:
                try:
                    quantity = int(split[2])
                except:
                    return
            self.buy_creatures(message.user, creature_type, quantity)

    def buy_creatures(self, user, creature_type, quantity):
        if quantity == 0:
            return
        if user in self.game.teams[0]:
            team = 0
        else:
            team = 1
        for _ in range(quantity):
            if self.money[team] < creature_type.COST:
                return
            self.money[team] -= creature_type.COST
            summon_dict = self.summons[team]
            if creature_type not in summon_dict:
                summon_dict[creature_type] = 0
            summon_dict[creature_type] += 1