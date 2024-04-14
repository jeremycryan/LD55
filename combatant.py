import math

import pygame

from particle import SparkParticle, Poof
from pyracy.sprite_tools import Sprite, Animation
from image_manager import ImageManager
from primitives import Pose
import random
import constants as c


class Combatant:
    NAME = "Combatant"
    DESCRIPTION = "Remains mysterious"
    COST = 999
    FRICTION = 0.3
    RADIUS = 40
    ACCELERATION = 400
    MAX_SPEED = 150
    BOUNCE_SPEED = 4
    JUMP_HEIGHT = 1.2 # multiplied by radius
    HIT_POINTS = 10
    BASE_DAMAGE = 5
    BASE_RANGE = 5
    ATTACK_SPEED = 1.0
    IDLE_SPRITE = "images/frog_nice.png"
    STRETCH_INTENSITY = 0.8
    WALK_ANGLE = 20
    TARGETABLE = True
    COLLIDABLE = True
    TARGETS_MULTIPLE = False
    TARGET_DISTANCE_MIN = 0
    TARGET_DISTANCE_MAX = 0
    TARGET_ANGLE_SPREAD = 30
    MASS = 100
    START_SLOW = True

    def __init__(self, combatant_collection, position, tribe=0):
        self.particles = []
        self.sprite = self.load_sprite()
        self.position = Pose(position)
        self.animation_offset = Pose((0, 0))
        self.velocity = Pose((0, 0))
        self.destroyed = False
        self.age = 0

        self.hit_points = self.HIT_POINTS

        self.target_position = self.position.copy()
        self.tribe = tribe

        if self.BOUNCE_SPEED > 0:
            self.step_period = random.random() * math.pi * 2
        else:
            self.step_period = math.pi/4
        self.previous_step_period = self.step_period

        self.since_blink = 999
        self.previous_position = self.position.copy()

        self.combatant_collection = combatant_collection
        self.target_enemy = None

        self.since_last_attack = 999

        self.target_angle_to_enemy = 0
        self.target_distance_to_enemy = 0

        self.nearby_combatants = []

    def blink(self):
        self.since_blink = 0
        if self.RADIUS < 100:
            for i in range(5):
                self.particles.append(SparkParticle(position=self.position.get_position(), scale_factor=self.RADIUS/25*0.5))

    def deal_damage_to(self, other):
        other.take_damage(self.BASE_DAMAGE)

    def take_damage(self, amt):
        self.hit_points -= amt
        if self.hit_points<=0:
            self.die()
        self.blink()

    def load_sprite(self):
        sprite = Sprite()
        idle = Animation(ImageManager.load(self.IDLE_SPRITE))
        sprite.add_animation({
            "Idle": idle
        }, loop=True)
        sprite.start_animation("Idle")
        return sprite

    def draw_shadow(self, surface, offset=(0, 0)):
        mult = abs(self.animation_offset.y)/self.RADIUS * 0.5 + 1
        shadow = pygame.Surface((self.RADIUS * 2/mult, self.RADIUS/mult))
        shadow.fill((255, 0, 0))
        shadow.set_colorkey((255, 0, 0))
        shadow.set_alpha(50)
        pygame.draw.ellipse(shadow, (0, 0, 0), shadow.get_rect())
        x = offset[0] + self.position.x - shadow.get_width()//2
        y = offset[0] + self.position.y + self.RADIUS*0.8 - shadow.get_height()*0.5
        surface.blit(shadow, (x, y))

    def draw(self, surface, offset=(0, 0)):
        image = self.sprite.get_image()
        image = pygame.transform.rotate(image, self.animation_offset.angle)
        blink_factor = max(0.3 - self.since_blink * 2, 0)
        image = self.squish_image(image, -(math.cos(2*self.step_period))*0.25*self.STRETCH_INTENSITY*self.get_animation_intensity() +1 - blink_factor)
        mask = pygame.mask.from_surface(image)
        if self.since_blink < 0.1:
            image = self.get_blink_image(mask)
        x = offset[0] + self.position.x - image.get_width()//2 + self.animation_offset.x
        y = offset[1] + self.position.y - image.get_height()//2 + self.animation_offset.y

        for particle in self.particles:
            if particle.layer != 0:
                continue
            particle.draw(surface, offset=offset)

        if (not self.destroyed or self.since_blink < 0.1):
            self.draw_shadow(surface, offset)  # TODO separate draw function for shadows
            self.draw_outline(surface, mask, (x, y))
            surface.blit(image, (x, y))
            # if c.DEBUG:
            #     pygame.draw.line(surface, (70, 70, 70), self.position.get_position(), self.target_position.get_position())

        for particle in self.particles:
            if particle.layer != 1:
                continue
            particle.draw(surface, offset=offset)

    def get_blink_image(self, mask):
        return mask.to_surface(unsetcolor=(0, 0, 0, 0))

    @staticmethod
    def squish_image(image, amt):
        width_factor = amt
        height_factor = 1/amt
        return pygame.transform.scale(image, (image.get_width()*width_factor, image.get_height()*height_factor))

    def update(self, dt, events):
        self.nearby_combatants = self.combatant_collection.get_nearby_combatants(self.position)

        self.age += dt
        self.since_last_attack += dt
        self.since_blink += dt

        if not self.destroyed:
            self.update_target_position()
            self.update_position(dt, events)
            self.update_velocity(dt, events)
            self.update_animation(dt, events)

        threshold = 1.5
        if self.age < threshold and self.START_SLOW:
            self.velocity *= self.age/threshold

        for particle in self.particles[:]:
            particle.update(dt, events)
            if particle.destroyed:
                self.particles.remove(particle)

    def update_target_position(self):
        enemies = [i for i in self.nearby_combatants if i.tribe != self.tribe and i.TARGETABLE]
        if self.target_enemy == None or self.target_enemy.destroyed:
            if not enemies:
                self.target_enemy = None
                if (self.target_position - self.position).magnitude() < self.RADIUS*2:
                    self.target_position = Pose((random.random() * (c.ARENA_WIDTH - 400) + 200, random.random() * (c.ARENA_HEIGHT - 400) + 200))
                return
            self.set_target_enemy(enemies[0])

        if enemies and (enemies[0].position - self.position).magnitude() < self.TARGET_DISTANCE_MIN:
            if enemies[0] != self.target_enemy:
                self.set_target_enemy(enemies[0])

        self.target_position = self.target_enemy.position
        angle = self.target_angle_to_enemy * math.pi/180
        diff = Pose((math.cos(angle), math.sin(angle)))
        if isinstance(self, Lizard):
            a = 3
            pass
        self.target_position += diff * self.target_distance_to_enemy

        self.check_attack(enemies)

    def set_target_enemy(self, enemy):
        if not enemy.TARGETABLE:
            return
        self.target_enemy = enemy
        angle_from_enemy_to_self = math.atan2(self.position.y - enemy.position.y, self.position.x - enemy.position.x)
        self.target_angle_to_enemy = angle_from_enemy_to_self + self.TARGET_ANGLE_SPREAD*2*(random.random() - 0.5)
        self.target_distance_to_enemy = random.random() * (self.TARGET_DISTANCE_MAX - self.TARGET_DISTANCE_MIN) + self.TARGET_DISTANCE_MIN

    def within_attack_range(self, other):
        return (other.position - self.position).magnitude() < other.RADIUS + self.RADIUS + self.BASE_RANGE

    def check_attack(self, enemies):
        if self.destroyed:
            return
        # if not enemies:
        #     raise Exception("Not supposed to happen")
        #     enemies = self.combatant_collection.get_nearby_combatants(self.position, tribe_to_exclude=self.tribe)
        #     enemies = [enemy for enemy in enemies if enemy.TARGETABLE]
        if (self.since_last_attack > (1/self.ATTACK_SPEED)):
            enemy_to_attack = None

            if not self.TARGETS_MULTIPLE:
                if self.target_enemy and self.within_attack_range(self.target_enemy):
                    enemy_to_attack = self.target_enemy
                elif enemies and self.within_attack_range(enemies[0]):
                    self.target_enemy = enemies[0]
                    enemy_to_attack = enemies[0]
                if not enemy_to_attack:
                    return
                self.attack(enemy_to_attack)
            else:
                attacked = False
                for enemy in enemies:
                    if self.within_attack_range(enemy):
                        self.attack(enemy)
                        attacked = True
                return attacked

    def attack(self, other):
        if self.destroyed or other.destroyed:
            return
        self.since_last_attack = random.random() * (1/self.ATTACK_SPEED) * 0.25
        self.deal_damage_to(other)

    def update_velocity(self, dt, events):
        if self.destroyed:
            return

        self.apply_friction(dt)
        self.check_collision(dt)
        self.apply_wall_avoidance(dt)

        diff = self.target_position - self.position
        normalized = diff.copy()
        normalized.scale_to(1)
        speed_in_direction = self.velocity.dot(normalized)
        over_speed_limit = speed_in_direction - self.MAX_SPEED
        if over_speed_limit<0:
            add_vector = normalized * self.ACCELERATION * dt
            if add_vector.dot(normalized) > -over_speed_limit:
                add_vector.scale_to(-over_speed_limit)
            self.velocity += add_vector

    def apply_wall_avoidance(self, dt):
        push_vector = Pose((0, 0))
        force = 5
        if (self.position.x < 200):
            push_vector += Pose((1, 0)) * force * (200 - self.position.x)
        if (self.position.x > c.ARENA_WIDTH - 200):
            push_vector += Pose((-1, 0)) * force * (200 - (c.ARENA_WIDTH - self.position.x))
        if (self.position.y < 200):
            push_vector += Pose((0, 1)) * force * (200 - self.position.y)
        if (self.position.y > c.ARENA_HEIGHT - 200):
            push_vector += Pose((0, -1)) * force * (200 - (c.ARENA_HEIGHT - self.position.y))
        self.velocity += push_vector*dt

    def check_collision(self, dt):
        if self.destroyed:
            return

        nearby_combatants = self.nearby_combatants
        for other in nearby_combatants:
            if other is self:
                continue
            diff = (other.position - self.position).magnitude()
            if (diff >= other.RADIUS + self.RADIUS):
                continue
            self.collide_with(other, dt)

    def collide_with(self, other, dt):
        if self.destroyed or other.destroyed or not other.COLLIDABLE:
            return

        direction = other.position - self.position
        direction.scale_to(1)
        x = (other.position - self.position).magnitude()
        x0 = other.RADIUS + self.RADIUS
        k = 200
        spring_vector = direction * (x - x0)*k
        self.velocity += spring_vector*dt*(100/self.MASS)

    def update_position(self, dt, events):
        self.previous_position = self.position.copy()
        self.position += self.velocity*dt
        if self.position.x < 0:
            self.position.x = 0
            self.take_damage(10)
        if self.position.y < 0:
            self.position.y = 0
            self.take_damage(10)
        if self.position.x > c.ARENA_WIDTH:
            self.position.x = c.ARENA_WIDTH
            self.take_damage(10)
        if self.position.y > c.ARENA_HEIGHT:
            self.position.y = c.ARENA_HEIGHT
            self.take_damage(10)
        self.combatant_collection.check_switched_buckets(self, self.previous_position)

    def apply_friction(self, dt):
        self.velocity *= self.FRICTION**dt


    def sort_value(self):
        return self.position.y + self.RADIUS

    def die(self):
        self.velocity.scale_to(0)
        self.blink()
        self.destroyed = True

        for i in range(20):
            self.particles.append(SparkParticle(position=self.position.get_position(), scale_factor=self.RADIUS/25))

    def is_friendly_toward(self, other):
        return other.tribe == self.tribe

    def update_animation(self, dt, events):
        self.sprite.update(dt, events)
        speed_factor = self.get_animation_intensity()
        self.step_period += dt * math.pi * self.BOUNCE_SPEED * speed_factor
        self.animation_offset.angle = math.sin(self.step_period) * self.WALK_ANGLE * speed_factor
        self.animation_offset.y = -abs(math.cos(self.step_period)) * self.RADIUS * self.JUMP_HEIGHT * speed_factor
        self.check_step()

    def get_animation_intensity(self):
        speed_factor = (self.velocity.magnitude()/self.MAX_SPEED)
        speed_factor = min(speed_factor, 1)
        speed_factor = max(speed_factor, 0.3)
        return speed_factor

    def check_step(self):
        if (self.step_period + math.pi/2) % math.pi < (self.previous_step_period + math.pi/2) % math.pi:
            self.step()
        self.previous_step_period = self.step_period

    def step(self):
        if self.destroyed:
            return
        for i in range(4):
            self.particles.append(Poof((self.position + Pose((0, self.RADIUS*0.8))).get_position(), scale=self.RADIUS/150))

    def draw_outline(self, surface, mask, position):
        points = mask.outline(5)
        points = tuple((x+position[0], y+position[1]) for (x, y) in points)
        width = 8
        for point in points:
            pygame.draw.circle(surface, c.TEAM_COLORS[self.tribe], point, width)
        pygame.draw.polygon(surface, c.TEAM_COLORS[self.tribe], points, width)

class Frog(Combatant):
    NAME = "Frog"
    DESCRIPTION = "A small but\nloyal soldier"
    COST = 3
    pass

class BigFrog(Combatant):
    IDLE_SPRITE = "images/bullfrog_nice.png"
    NAME = "Bullfrog"
    COST = 10
    DESCRIPTION = "Heavy, powerful,\nand full of rage"
    HIT_POINTS = 40
    BASE_DAMAGE = 8
    MAX_SPEED = 100
    RADIUS = 75
    STRETCH_INTENSITY = 0.5
    MASS = 300
    BOUNCE_SPEED = 4
    JUMP_HEIGHT = 0.8

class Lizard(Combatant):
    IDLE_SPRITE = "images/lizard_nice.png"
    NAME = "Lizard"
    COST = 12
    DESCRIPTION = "Throws rocks,\nthrives in chaos"
    HIT_POINTS = 10
    BASE_DAMAGE = 5
    MAX_SPEED = 120
    ACCELERATION = 600
    BASE_RANGE = 350
    TARGET_DISTANCE_MIN = 250
    TARGET_DISTANCE_MAX = 350
    ATTACK_SPEED = 0.25
    RADIUS = 50

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.since_last_attack -= random.random()


    def attack(self, other):
        if self.destroyed or other.destroyed:
            return
        self.since_last_attack = random.random() * (1/self.ATTACK_SPEED) * 0.25
        self.deal_damage_to(other)
        diff = other.position - self.position
        diff.scale_to(self.RADIUS)
        self.combatant_collection.add(Rock(self.combatant_collection, (self.position+diff).get_position(), self.tribe, other))

    def set_target_enemy(self, enemy):
        super().set_target_enemy(enemy)
        self.since_last_attack = random.random() * (1/self.ATTACK_SPEED)  # start cooldown when approaching new enemy


class Projectile(Combatant):
    NAME = "Projectile"
    COLLIDABLE = False
    TARGETABLE = False
    HIT_POINTS = 1
    START_SLOW = False

    def __init__(self, combatant_collection, position, tribe=0, projectile_target=None):
        super().__init__(combatant_collection, position, tribe)
        self.projectile_target = projectile_target
        self.velocity = self.projectile_target.position - self.position
        self.velocity.scale_to(self.MAX_SPEED)

    def update_velocity(self, dt, events):
        self.target_position = self.position.copy()
        return  # rock just flies

    def attack(self, other):
        super().attack(other)
        self.take_damage(1)

class Rock(Projectile):
    IDLE_SPRITE = "images/rock.png"
    NAME = "Rock"

    BASE_DAMAGE = 5
    MAX_SPEED = 1200
    ACCELERATION = 1000
    RADIUS = 40
    BOUNCE_SPEED = 0

class Seeker(Combatant):
    IDLE_SPRITE = "images/bun_nice.png"
    DESCRIPTION = "Very fast, but\nnot very smart"
    NAME = "Bunny"
    COST = 10

    MAX_SPEED = 400
    ACCELERATION = 1500
    RADIUS = 40
    ATTACK_SPEED = 1.5
    BASE_DAMAGE = 12
    BOUNCE_SPEED = 6
    STRETCH_INTENSITY = 1.0

class Unicorn(Combatant):
    IDLE_SPRITE = "images/unicorn_nice.png"
    NAME = "Unicorn"
    COST = 35
    DESCRIPTION = "A big lad with\nbig dreams"

    RADIUS = 120
    ATTACK_SPEED = 0.2
    BASE_DAMAGE = 25
    BOUNCE_SPEED = 3
    MAX_SPEED = 60
    JUMP_HEIGHT = 0.5
    STRETCH_INTENSITY = 0.25
    WALK_ANGLE = 10
    HIT_POINTS = 80
    MASS = 1000
    TARGETS_MULTIPLE = True

class Bee(Combatant):
    IDLE_SPRITE = "images/bee_nice.png"
    NAME = "Bee"

    RADIUS = 25
    BASE_DAMAGE = 1
    # BOUNCE_SPEED = 0
    # JUMP_HEIGHT = 0
    MAX_SPEED = 180
    HIT_POINTS = 1
    MASS = 20
    ACCELERATION = 1000
    FRICTION = 0.1
    ATTACK_SPEED = 0.6
    START_SLOW = False


class Beekeeper(Combatant):
    IDLE_SPRITE = "images/beekeeper_nice.png"
    NAME = "Bear"
    COST = 15
    DESCRIPTION = "Likes bees more\nthan people"

    TARGET_DISTANCE_MIN = 350
    TARGET_DISTANCE_MAX = 450

    BASE_DAMAGE = 1
    HIT_POINTS = 18
    RADIUS = 40

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.since_bee = random.random() * 1 + 0.5

    def update(self, dt, events):
        super().update(dt, events)
        if self.destroyed:
            return
        self.since_bee += dt
        if self.since_bee > 3.5:
            self.bee()

    def bee(self):
        self.combatant_collection.add(
            Bee(self.combatant_collection, (self.position + Pose((random.random()*60 - 30, random.random()*60 - 30))).get_position(), self.tribe))
        self.since_bee = random.random() - 0.5

TYPES = [
    Frog,
    BigFrog,
    Lizard,
    Beekeeper,
    Unicorn,
    Seeker,
]
