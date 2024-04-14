import math
import time

import pygame

from image_manager import ImageManager
import constants as c

class Panel:

    def __init__(self, enemy_class, position):
        self.position = position
        self.back_surf = ImageManager.load("images/shop_panel.png")
        self.name_font = pygame.font.Font("fonts/SEBASTIAN_INFORMAL.otf", int(50*c.SCALE))
        self.body_font = pygame.font.Font("fonts/SEBASTIAN_INFORMAL.otf", int(30*c.SCALE))
        self.cost_font = pygame.font.Font("fonts/SpicySushi.ttf", int(60*c.SCALE))
        self.unit_surf = ImageManager.load(enemy_class.IDLE_SPRITE)
        if (self.unit_surf.get_width() > 200*c.SCALE):
            self.unit_surf = pygame.transform.scale(self.unit_surf, (int(200*c.SCALE), int(200*c.SCALE)))

        self.name_surf = self.name_font.render(enemy_class.NAME, True, (59, 112, 85))
        self.body_surfs = [self.body_font.render(substring, True, (39, 112, 85)) for substring in enemy_class.DESCRIPTION.split("\n")]
        self.cauldron_surf = ImageManager.load_copy("images/cauldron.png")

        cost_surf = self.cost_font.render(f"{enemy_class.COST}", True, (80, 60, 100))
        self.cauldron_surf.blit(cost_surf,
            (self.cauldron_surf.get_width()//2 - cost_surf.get_width()//2,
            self.cauldron_surf.get_height()//2 - cost_surf.get_height()//2 + 15*c.SCALE))
        cost_surf = self.cost_font.render(f"{enemy_class.COST}", True, (255, 255, 255))
        self.cauldron_surf.blit(cost_surf,
            (self.cauldron_surf.get_width()//2 - cost_surf.get_width()//2,
            self.cauldron_surf.get_height()//2 - cost_surf.get_height()//2 + 10*c.SCALE))

        self.master_surf = pygame.Surface((self.back_surf.get_width() + 50*c.SCALE, self.back_surf.get_height()+50*c.SCALE)).convert_alpha() # .back_surf.copy()
        self.master_surf.fill((0, 0, 0, 0))
        x = self.master_surf.get_width()//2
        y = self.master_surf.get_height()//2
        self.master_surf.blit(self.back_surf, (x - self.back_surf.get_width()//2, y - self.back_surf.get_height()//2))
        self.master_surf.blit(self.unit_surf, (x - 85*c.SCALE - self.unit_surf.get_width()//2, y - self.unit_surf.get_height()//2))
        self.master_surf.blit(self.name_surf, (x + 20*c.SCALE, y - self.back_surf.get_height()//2 + 50*c.SCALE))
        self.master_surf.blit(self.cauldron_surf, (x - self.back_surf.get_width()//2 - 20*c.SCALE, y - self.back_surf.get_height()//2 - 20*c.SCALE))
        for surf in self.body_surfs:
            self.master_surf.blit(surf, (x + 20*c.SCALE, y - self.back_surf.get_height() // 2 + 110*c.SCALE))
            y += 25


    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):

        xadd = math.sin(self.position.x/300 + time.time() *3) * 5
        yadd = math.cos(self.position.x/200 + self.position.y/300 + time.time() * 4) * 5

        x = self.position.x + offset[0] + xadd
        y = self.position.y + offset[1] + yadd
        surface.blit(self.master_surf, (x - self.master_surf.get_width()//2, y - self.master_surf.get_height()//2))
        # surface.blit(self.back_surf, (x - self.back_surf.get_width()//2, y - self.back_surf.get_height()//2))
        # surface.blit(self.unit_surf, (x - 85 - self.unit_surf.get_width()//2, y - self.unit_surf.get_height()//2))
        # surface.blit(self.name_surf, (x + 20, y - self.back_surf.get_height()//2 + 60))
        # surface.blit(self.cauldron_surf, (x - self.back_surf.get_width()//2 - 20, y - self.back_surf.get_height()//2 - 20))

