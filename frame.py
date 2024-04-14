import math
import time

import pygame

from combatant import Frog, BigFrog, Lizard, Seeker, Unicorn, Beekeeper, TYPES, Combatant, Hedgehog, Dragon
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
    def __init__(self, game, summons):
        super().__init__(game)
        self.summons = summons
        self.age = 0
        self.time_remaining = 4
        self.complete = False


        self.since_toast = 999
        self.toast_surf = None




    def load(self):
        self.combatants = CombatantCollection()
        for team in [0, 1]:
            summon_dict = self.summons[team]
            for unit in summon_dict:
                for _ in range(summon_dict[unit]):
                    if team == 0:
                        position = (random.random()*c.WINDOW_WIDTH*0.4 + c.WINDOW_WIDTH*0.1, random.random()*c.WINDOW_HEIGHT*0.8 + c.WINDOW_HEIGHT*0.1)
                    else:
                        position = (random.random()*c.WINDOW_WIDTH*0.4 + c.WINDOW_WIDTH*0.6, random.random()*c.WINDOW_HEIGHT*0.8 + c.WINDOW_HEIGHT*0.1)
                    self.combatants.add_multiple([unit(self.combatants, position, tribe=team)])
        self.edge = ImageManager.load("images/transition_edge.png")
        self.edge_flipped = pygame.transform.rotate(self.edge, 180)
        self.backdrop = ImageManager.load("images/backdrop.png").convert()
        self.toast_font = pygame.font.Font("fonts/SpicySushi.ttf", 80)
        self.toast("START")
        self.toast_color = (41, 49, 76)

        # self.combatants.add_multiple([Frog(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5, random.random()*c.WINDOW_HEIGHT), tribe=0) for _ in range(10)])
        # self.combatants.add_multiple([Frog(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5 + c.WINDOW_WIDTH//2, random.random()*c.WINDOW_HEIGHT), tribe=1) for _ in range(5)])
        # self.combatants.add_multiple([Seeker(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5, random.random()*c.WINDOW_HEIGHT), tribe=0) for _ in range(3)])
        # self.combatants.add_multiple([Unicorn(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5, random.random()*c.WINDOW_HEIGHT), tribe=0) for _ in range(1)])
        # self.combatants.add_multiple([BigFrog(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5, random.random()*c.WINDOW_HEIGHT), tribe=0) for _ in range(2)])
        # self.combatants.add_multiple([Lizard(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5 + c.WINDOW_WIDTH//2, random.random()*c.WINDOW_HEIGHT), tribe=1) for _ in range(3)])
        # self.combatants.add_multiple([Beekeeper(self.combatants, (random.random()*c.WINDOW_WIDTH*0.5 + c.WINDOW_WIDTH//2, random.random()*c.WINDOW_HEIGHT), tribe=1) for _ in range(3)])

    def update(self, dt, events):
        self.since_toast += dt
        self.age += dt
        if self.complete:
            self.time_remaining -= dt
        self.combatants.update(dt, events)
        if not len([c for c in self.combatants if c.tribe == 0 and not c.destroyed]):
            self.win(1)
        elif not len([c for c in self.combatants if c.tribe == 1 and not c.destroyed]):
            self.win(0)
        if self.time_remaining < -1:
            self.done = True

    def win(self, tribe):
        if self.complete:
            return
        winner = "YELLOW" if tribe==0 else "BLUE"
        color = (176, 138, 0) if tribe == 0 else (87, 104, 164)
        self.toast(f"{winner} TEAM WINS!", color, delay=1.5)
        self.complete = True

    def draw(self, surface, offset=(0, 0)):
        # surface.fill((128, 190, 128))
        surface.blit(self.backdrop, offset)
        self.combatants.draw(surface, offset)

        threshold = 0.5
        if self.age < threshold + 1:
            through = 1 - self.age/threshold
            if through > 1:
                through = 1
            y = c.WINDOW_HEIGHT - through * (c.WINDOW_HEIGHT + self.edge.get_height())
            x = 0
            surface.blit(self.edge_flipped, (x, y - self.edge_flipped.get_height()))
            pygame.draw.rect(surface, (41, 49, 76), pygame.Rect(0, y, c.WINDOW_WIDTH, c.WINDOW_HEIGHT - y + 5))

        threshold = 0.5
        if self.time_remaining < threshold:
            through = 1 - self.time_remaining/threshold
            if through > 1:
                through = 1
            y = -self.edge.get_height() + through * (c.WINDOW_HEIGHT + self.edge.get_height())
            x = 0
            surface.blit(self.edge, (x, y))
            pygame.draw.rect(surface, (41, 49, 76), pygame.Rect(0, 0, c.WINDOW_WIDTH, y))

        self.draw_toast(surface, offset)

    def next_frame(self):
        return ShopFrame(self.game)

    def toast(self, text, color = (41, 49, 76), delay = 0):
        self.toast_color = color
        self.since_toast = -delay
        self.toast_surf = self.toast_font.render(text, True, (255, 255, 255))

    def draw_toast(self, surface, offset=(0, 0)):
        phase_1 = 0.3
        phase_2 = 1.3
        phase_3 = 1.6
        max_height = 110
        if self.since_toast > phase_3 or self.since_toast<=0:
            return
        if self.since_toast<phase_1:
            height = max(self.since_toast/phase_1 * max_height, 1)
        elif self.since_toast < phase_2:
            height = max_height
        else:
            height = max((phase_3 - self.since_toast)/(phase_3 - phase_2) * max_height, 1)
        pygame.draw.rect(surface, self.toast_color, pygame.Rect(0, c.WINDOW_HEIGHT//2 - height//2, c.WINDOW_WIDTH, height))
        self.toast_surf.set_alpha(255 * height/max_height)
        surface.blit(self.toast_surf, (c.WINDOW_WIDTH//2 - self.toast_surf.get_width()//2, c.WINDOW_HEIGHT//2 - self.toast_surf.get_height()//2 + 15*c.SCALE))

class ShopFrame(Frame):
    def next_frame(self):
        return ArenaFrame(self.game, self.summons)

    def load(self):
        self.game.restart_stream()

        self.background = ImageManager.load("images/shop_background_2.png").convert()
        self.teams = ImageManager.load("images/team_names.png")

        self.cauldron = ImageManager.load_copy("images/cauldron.png")
        self.cost_font = pygame.font.Font("fonts/SpicySushi.ttf", int(60*c.SCALE))

        self.time_font = pygame.font.Font("fonts/SpicySushi.ttf", int(73*c.SCALE))

        self.time_remaining = 90

        self.preview_units_left = []
        self.preview_units_right = []
        self.preview_units_left_age = []
        self.preview_units_right_age = []

        nudge = 230
        self.panels = [
            Panel(Frog, Pose((500*c.SCALE-nudge*c.SCALE, 650*c.SCALE))),
            Panel(Seeker, Pose((c.WINDOW_WIDTH//2-nudge*c.SCALE, 650*c.SCALE))),
            Panel(Beekeeper, Pose((c.WINDOW_WIDTH//2 +nudge*c.SCALE, 650*c.SCALE))),
            Panel(BigFrog, Pose((500*c.SCALE-nudge*c.SCALE, 900*c.SCALE))),
            Panel(Hedgehog, Pose((c.WINDOW_WIDTH//2-nudge*c.SCALE, 900*c.SCALE))),
            Panel(Unicorn, Pose((c.WINDOW_WIDTH//2 + nudge*c.SCALE, 900*c.SCALE))),
            Panel(Dragon, Pose((c.WINDOW_WIDTH - 500*c.SCALE+nudge*c.SCALE, 900*c.SCALE))),
            Panel(Lizard, Pose((c.WINDOW_WIDTH - 500 * c.SCALE + nudge * c.SCALE, 650 * c.SCALE))),
        ]


        self.money = {0: 100, 1:100}
        self.summons = {0: {}, 1:{}}

        self.clock = ImageManager.load("images/clock.png")

        self.edge = ImageManager.load("images/transition_edge.png")
        self.edge_flipped = pygame.transform.rotate(self.edge, 180)
        self.age = 0

        self.game.teams[0].append("jarm")
        self.game.teams[1].append("ppab")



    def update(self, dt, events):
        self.age += dt

        if self.time_remaining > 5 and self.money[0] < 5 and self.money[1] < 5:
            self.time_remaining = 5

        if self.time_remaining < 5 and self.money[0] == 100:
            for i in range(20):
                unit = random.choice([Frog, BigFrog, Lizard, Beekeeper, Unicorn, Seeker, Hedgehog, Dragon])
                self.buy_creatures("jarm", unit, 1)
        if self.time_remaining < 5 and self.money[1] == 100:
            for i in range(20):
                unit = random.choice([Frog, BigFrog, Lizard, Beekeeper, Unicorn, Seeker, Hedgehog, Dragon])
                self.buy_creatures("ppab", unit, 1)

        for panel in self.panels:
            panel.update(dt, events)

        for event in events:
            if event.type == "Twitch":
                self.process_twitch_message(event.message)

        self.time_remaining -= dt
        if self.time_remaining <= -1.5:
            self.done = True

        for i in range(len(self.preview_units_left_age)):
            self.preview_units_left_age[i] += dt
        for i in range(len(self.preview_units_right_age)):
            self.preview_units_right_age[i] += dt



    def draw_clock(self, surface, offset=(0, 0)):
        surface.blit(self.clock, (c.WINDOW_WIDTH//2 - self.clock.get_width()//2, c.WINDOW_HEIGHT - self.clock.get_height()))

        time_left = int(self.time_remaining)
        scale = (self.time_remaining%1)**4*0.5 + 1

        color = (87, 103, 127)
        if (time_left < 10):
            color = (255, 0, 114)
        text = self.time_font.render(f"{time_left}", True, color)
        text = pygame.transform.scale(text, (text.get_width()*scale, text.get_height()*scale))
        surface.blit(text, (c.WINDOW_WIDTH//2 - text.get_width()//2, c.WINDOW_HEIGHT - 30*c.SCALE - text.get_height()//2))

        pass

    def draw(self, surface, offset=(0, 0)):
        surface.blit(self.background, offset)

        self.draw_ui(surface, offset=(0, 0))
        self.draw_money(surface, offset)
        self.draw_previews(surface, offset)
        self.draw_clock(surface, offset)
        self.draw_wipe(surface, offset)

    def draw_ui(self, surface, offset=(0, 0)):
        for panel in self.panels:
            panel.draw(surface, offset)
        surface.blit(self.teams, (offset[0], offset[1] + math.sin(time.time()*4.5)*4))
        # surface.blit(self.sign, (c.WINDOW_WIDTH//2 - self.sign.get_width()//2 + offset[0], offset[1]))

    def draw_money(self, surface, offset=(0, 0)):
        cost_surf = self.cost_font.render(f"{self.money[0]}", True, (80, 60, 100))
        cauldron_surf = self.cauldron.copy()
        cauldron_surf.blit(cost_surf,
                           (cauldron_surf.get_width() // 2 - cost_surf.get_width() // 2,
                            cauldron_surf.get_height() // 2 - cost_surf.get_height() // 2 + 15*c.SCALE))
        cost_surf = self.cost_font.render(f"{self.money[0]}", True, (255, 255, 255))
        cauldron_surf.blit(cost_surf,
                           (cauldron_surf.get_width() // 2 - cost_surf.get_width() // 2,
                            cauldron_surf.get_height() // 2 - cost_surf.get_height() // 2 + 10*c.SCALE))

        x, y = (120*c.SCALE - self.cauldron.get_width() // 2, 120*c.SCALE - self.cauldron.get_height() // 2)
        surface.blit(cauldron_surf, (x + offset[0], y + offset[1]))

        cost_surf = self.cost_font.render(f"{self.money[1]}", True, (80, 60, 100))
        cauldron_surf = self.cauldron.copy()
        cauldron_surf.blit(cost_surf,
                           (cauldron_surf.get_width() // 2 - cost_surf.get_width() // 2,
                            cauldron_surf.get_height() // 2 - cost_surf.get_height() // 2 + 15*c.SCALE))
        cost_surf = self.cost_font.render(f"{self.money[1]}", True, (255, 255, 255))
        cauldron_surf.blit(cost_surf,
                           (cauldron_surf.get_width() // 2 - cost_surf.get_width() // 2,
                            cauldron_surf.get_height() // 2 - cost_surf.get_height() // 2 + 10*c.SCALE))

        x, y = (c.WINDOW_WIDTH - 120*c.SCALE - self.cauldron.get_width() // 2, 120*c.SCALE - self.cauldron.get_height() // 2)
        surface.blit(cauldron_surf, (x + offset[0], y + offset[1]))

    def draw_wipe(self, surface, offset=(0, 0)):
        threshold = 0.5
        if self.age < threshold + 1:
            through = 1 - self.age/threshold
            if through > 1:
                through = 1
            y = c.WINDOW_HEIGHT - through * (c.WINDOW_HEIGHT + self.edge.get_height())
            x = 0
            surface.blit(self.edge_flipped, (x, y - self.edge_flipped.get_height()))
            pygame.draw.rect(surface, (41, 49, 76), pygame.Rect(0, y, c.WINDOW_WIDTH, c.WINDOW_HEIGHT + 3 - y))

        threshold = 0.5
        if self.time_remaining < threshold:
            through = 1 - self.time_remaining/threshold
            if through > 1:
                through = 1
            y = -self.edge.get_height() + through * (c.WINDOW_HEIGHT + self.edge.get_height())
            x = 0
            surface.blit(self.edge, (x, y))
            pygame.draw.rect(surface, (41, 49, 76), pygame.Rect(0, 0, c.WINDOW_WIDTH, y))

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
            self.add_preview_unit(team, creature_type)

    def add_preview_unit(self, team, creature):
        if team == 0:
            use_list = self.preview_units_left
            age_list = self.preview_units_left_age
        else:
            use_list = self.preview_units_right
            age_list = self.preview_units_right_age
        use_list.append(creature)
        if not age_list:
            age_list.append(0)
            return
        age_list.append(min(0, age_list[-1] - 0.25))

    def draw_previews(self, surface, offset=(0, 0)):
        center = 400*c.SCALE + offset[0], 480*c.SCALE + offset[1]
        out_small = 30*c.SCALE
        out_medium = 60*c.SCALE
        out_large = 100*c.SCALE

        spawn_time = 1

        for i, (creature, age) in enumerate([(j, k) for (j, k) in list(zip(self.preview_units_left, self.preview_units_left_age))[::-1] if j.RADIUS > 100]):
            i = len([j for j in self.preview_units_left[::-1] if j.RADIUS > 100]) - i - 1
            y = center[1] - 40*c.SCALE
            distance_from_center = out_large * (i+1)//2
            direction = 1 if i%2 else -1
            x = center[0] + direction*distance_from_center
            surf = ImageManager.load(creature.IDLE_SPRITE)

            squish = max(min(age*3, math.sin(time.time()*2*creature.BOUNCE_SPEED + i)*0.1 + 1), 0.01)
            surf = Combatant.squish_image(surf, squish)
            if (age < spawn_time and age > 0):
                mask = pygame.mask.from_surface(surf)
                lighten = mask.to_surface(unsetcolor=(0, 0, 0), setcolor=(255, 255, 255))
                lighten.set_colorkey((0, 0, 0))
                lighten.set_alpha(255 - age*255)
                surf.blit(lighten, (0, 0))

            surface.blit(surf, (x - surf.get_width()//2, y - surf.get_height()))

        for i, (creature, age) in enumerate([(j, k) for (j, k) in list(zip(self.preview_units_left, self.preview_units_left_age))[::-1] if j.RADIUS <= 100 and j.RADIUS > 50]):
            i = len([j for j in self.preview_units_left[::-1] if j.RADIUS <= 100 and j.RADIUS > 50]) - i - 1
            y = center[1] - 20
            distance_from_center = out_medium * (i+1)//2
            direction = 1 if i%2 else -1
            x = center[0] + direction*distance_from_center
            surf = ImageManager.load(creature.IDLE_SPRITE)
            squish = max(min(age*3, math.sin(time.time()*2*creature.BOUNCE_SPEED + i)*0.1 + 1), 0.01)
            surf = Combatant.squish_image(surf, squish)
            if (age < spawn_time and age > 0):
                mask = pygame.mask.from_surface(surf)
                lighten = mask.to_surface(unsetcolor=(0, 0, 0), setcolor=(255, 255, 255))
                lighten.set_colorkey((0, 0, 0))
                lighten.set_alpha(255 - age*255)
                surf.blit(lighten, (0, 0))
            surface.blit(surf, (x - surf.get_width()//2, y - surf.get_height()))

        for i, (creature, age) in enumerate([(j, k) for (j, k) in list(zip(self.preview_units_left, self.preview_units_left_age))[::-1] if j.RADIUS <= 50]):
            row = 0
            i = len([j for j in self.preview_units_left if j.RADIUS <= 50]) - i - 1
            if i > 20:
                row = 1
                i = i%20
            y = center[1] - row*30*c.SCALE
            distance_from_center = out_small * (i+1)//2
            direction = 1 if i%2 else -1
            x = center[0] + direction*distance_from_center
            surf = ImageManager.load(creature.IDLE_SPRITE)
            squish = max(min(age*3, math.sin(time.time()*2*creature.BOUNCE_SPEED + i)*0.1 + 1), 0.01)
            surf = Combatant.squish_image(surf, squish)
            if (age < spawn_time and age > 0):
                mask = pygame.mask.from_surface(surf)
                lighten = mask.to_surface(unsetcolor=(0, 0, 0), setcolor=(255, 255, 255))
                lighten.set_colorkey((0, 0, 0))
                lighten.set_alpha(255 - age*255)
                surf.blit(lighten, (0, 0))
            surface.blit(surf, (x - surf.get_width()//2, y - surf.get_height()))

        center = c.WINDOW_WIDTH - 400*c.SCALE + offset[0], 480*c.SCALE + offset[1]

        for i, (creature, age) in enumerate([(j, k) for (j, k) in list(zip(self.preview_units_right, self.preview_units_right_age))[::-1] if j.RADIUS > 100]):
            i = len([j for j in self.preview_units_right[::-1] if j.RADIUS > 100]) - i - 1
            y = center[1] - 40*c.SCALE
            distance_from_center = out_large * (i+1)//2
            direction = 1 if i%2 else -1
            x = center[0] + direction*distance_from_center
            surf = ImageManager.load(creature.IDLE_SPRITE)

            squish = max(min(age*3, math.sin(time.time()*2*creature.BOUNCE_SPEED + i)*0.1 + 1), 0.01)
            surf = Combatant.squish_image(surf, squish)
            if (age < spawn_time and age > 0):
                mask = pygame.mask.from_surface(surf)
                lighten = mask.to_surface(unsetcolor=(0, 0, 0), setcolor=(255, 255, 255))
                lighten.set_colorkey((0, 0, 0))
                lighten.set_alpha(255 - age*255)
                surf.blit(lighten, (0, 0))

            surface.blit(surf, (x - surf.get_width()//2, y - surf.get_height()))

        for i, (creature, age) in enumerate([(j, k) for (j, k) in list(zip(self.preview_units_right, self.preview_units_right_age))[::-1] if j.RADIUS <= 100 and j.RADIUS > 50]):
            i = len([j for j in self.preview_units_right[::-1] if j.RADIUS <= 100 and j.RADIUS > 50]) - i - 1
            y = center[1] - 20*c.SCALE
            distance_from_center = out_medium * (i+1)//2
            direction = 1 if i%2 else -1
            x = center[0] + direction*distance_from_center
            surf = ImageManager.load(creature.IDLE_SPRITE)
            squish = max(min(age*3, math.sin(time.time()*2*creature.BOUNCE_SPEED + i)*0.1 + 1), 0.01)
            surf = Combatant.squish_image(surf, squish)
            if (age < spawn_time and age > 0):
                mask = pygame.mask.from_surface(surf)
                lighten = mask.to_surface(unsetcolor=(0, 0, 0), setcolor=(255, 255, 255))
                lighten.set_colorkey((0, 0, 0))
                lighten.set_alpha(255 - age*255)
                surf.blit(lighten, (0, 0))
            surface.blit(surf, (x - surf.get_width()//2, y - surf.get_height()))

        for i, (creature, age) in enumerate([(j, k) for (j, k) in list(zip(self.preview_units_right, self.preview_units_right_age))[::-1] if j.RADIUS <= 50]):
            row = 0
            i = len([j for j in self.preview_units_right if j.RADIUS <= 50]) - i - 1
            if i > 20:
                row = 1
                i = i%20
            y = center[1] - row*30*c.SCALE
            distance_from_center = out_small * (i+1)//2
            direction = 1 if i%2 else -1
            x = center[0] + direction*distance_from_center
            surf = ImageManager.load(creature.IDLE_SPRITE)
            squish = max(min(age*3, math.sin(time.time()*2*creature.BOUNCE_SPEED + i)*0.1 + 1), 0.01)
            surf = Combatant.squish_image(surf, squish)
            if (age < spawn_time and age > 0):
                mask = pygame.mask.from_surface(surf)
                lighten = mask.to_surface(unsetcolor=(0, 0, 0), setcolor=(255, 255, 255))
                lighten.set_colorkey((0, 0, 0))
                lighten.set_alpha(255 - age*255)
                surf.blit(lighten, (0, 0))
            surface.blit(surf, (x - surf.get_width()//2, y - surf.get_height()))




