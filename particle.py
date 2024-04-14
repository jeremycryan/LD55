from image_manager import ImageManager
from primitives import Pose
import random
import math
import pygame
import constants as c
from pyracy.sprite_tools import Sprite, Animation


class Particle:

    def __init__(self, position=(0, 0), velocity=(0, 0), duration=1):
        self.position = Pose(position)
        self.velocity = Pose(velocity)
        self.destroyed = False
        self.duration = duration
        self.age = 0
        self.layer = 1

    def get_scale(self):
        return 1

    def update(self, dt, events):
        if self.destroyed:
            return
        self.position += self.velocity * dt
        if self.age > self.duration:
            self.destroy()
        self.age += dt

    def draw(self, surf, offset=(0, 0)):
        if self.destroyed:
            return

    def through(self):
        return min(0.999, self.age/self.duration)

    def destroy(self):
        self.destroyed = True

class SparkParticle(Particle):
    img = None

    def __init__(self, position, velocity=None, duration=0.2, scale_factor=1):
        if velocity is None:
            velocity = Pose((random.random() - 0.5, random.random() - 0.5))
        self.angle = velocity.get_angle_of_position()*180/math.pi
        self.angle_pos = velocity
        self.angle_pos.scale_to(1)
        super().__init__(position, velocity=velocity.get_position(),duration=duration)
        self.velocity = velocity * random.random()**2 * 1000 * ((scale_factor+1)/2)
        self.first = False
        if SparkParticle.img==None:
            self.first = True
            SparkParticle.img=ImageManager.load("images/death_particle.png")
        self.scale_factor = scale_factor

    def update(self, dt, events):
        super().update(dt, events)

    def get_scale(self):
        return (1 - self.through())*self.scale_factor

    def draw(self, surface, offset=(0, 0)):
        if self.destroyed:
            return

        surf = SparkParticle.img
        surf = pygame.transform.rotate(surf, self.angle)
        surf = pygame.transform.scale(surf, (surf.get_width()*self.get_scale(), surf.get_height()*self.get_scale()))
        pos = self.position + Pose(offset) - Pose((surf.get_width()//2, surf.get_height()//2)) + self.angle_pos*15
        surface.blit(surf, pos.get_position())

class Poof(Particle):
    def __init__(self, position=(0, 0), duration = 0.4, scale=1, speed = 1.0):
        scale = math.sqrt(scale)
        velocity_angle = random.random()*360
        velocity_magnitude = (random.random()*200 + 250)*scale
        velocity = Pose((velocity_magnitude, 0))
        velocity.rotate_position(velocity_angle)
        super().__init__(position=position, velocity=velocity.get_position(), duration=duration)
        velocity.y *= 0.5
        self.velocity *= speed
        self.poof = ImageManager.load("images/poof.png")
        self.angle = random.random()*360
        self.spin = random.random()*60 - 30
        self.layer = 0
        self.scale = scale

    def update(self, dt, events):
        super().update(dt, events)
        self.velocity.x *= 0.001**dt
        self.velocity.y *= 0.001**dt
        self.angle += self.spin*dt

    def draw(self, surface, offset=(0, 0)):
        if self.destroyed:
            return
        x = self.position.x + offset[0]
        y = self.position.y + offset[1]
        if x < -100 or x > c.WINDOW_WIDTH + 100:
            return
        if y < -100 or y > c.WINDOW_HEIGHT + 100:
            return

        scale = (2 - 2*self.through()) * self.scale
        surf = pygame.transform.scale(self.poof, (self.poof.get_width()*scale, self.poof.get_height()*scale))
        surf = pygame.transform.rotate(surf, self.angle)
        x -= surf.get_width()//2
        y -= surf.get_height()//2

        a = 80*(1 - self.through()**1.5)
        surf.set_alpha(a)

        surface.blit(surf, (x, y))