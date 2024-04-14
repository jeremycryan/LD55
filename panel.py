import math
import time

import pygame

from image_manager import ImageManager


class Panel:

    def __init__(self, enemy_class, position):
        self.position = position
        self.back_surf = ImageManager.load("images/shop_panel.png")
        self.name_font = pygame.font.Font("fonts/SEBASTIAN_INFORMAL.otf", 50)
        self.body_font = pygame.font.Font("fonts/SEBASTIAN_INFORMAL.otf", 30)
        self.cost_font = pygame.font.Font("fonts/SpicySushi.ttf", 60)
        self.unit_surf = ImageManager.load(enemy_class.IDLE_SPRITE)
        if (self.unit_surf.get_width() > 200):
            self.unit_surf = pygame.transform.scale(self.unit_surf, (200, 200))

        self.name_surf = self.name_font.render(enemy_class.NAME, True, (59, 112, 85))
        self.body_surfs = [self.body_font.render(substring, True, (39, 112, 85)) for substring in enemy_class.DESCRIPTION.split("\n")]
        self.cauldron_surf = ImageManager.load_copy("images/cauldron.png")

        cost_surf = self.cost_font.render(f"{enemy_class.COST}", True, (80, 60, 100))
        self.cauldron_surf.blit(cost_surf,
            (self.cauldron_surf.get_width()//2 - cost_surf.get_width()//2,
            self.cauldron_surf.get_height()//2 - cost_surf.get_height()//2 + 15))
        cost_surf = self.cost_font.render(f"{enemy_class.COST}", True, (255, 255, 255))
        self.cauldron_surf.blit(cost_surf,
            (self.cauldron_surf.get_width()//2 - cost_surf.get_width()//2,
            self.cauldron_surf.get_height()//2 - cost_surf.get_height()//2 + 10))


    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):

        xadd = math.sin(self.position.x/300 + time.time() *3) * 5
        yadd = math.cos(self.position.x/200 + self.position.y/300 + time.time() * 4) * 5

        x = self.position.x + offset[0] + xadd
        y = self.position.y + offset[1] + yadd
        surface.blit(self.back_surf, (x - self.back_surf.get_width()//2, y - self.back_surf.get_height()//2))
        surface.blit(self.unit_surf, (x - 85 - self.unit_surf.get_width()//2, y - self.unit_surf.get_height()//2))
        surface.blit(self.name_surf, (x + 20, y - self.back_surf.get_height()//2 + 60))
        surface.blit(self.cauldron_surf, (x - self.back_surf.get_width()//2 - 20, y - self.back_surf.get_height()//2 - 20))

        for surf in self.body_surfs:
            surface.blit(surf, (x + 20, y - self.back_surf.get_height() // 2 + 120))
            y += 25