import constants as c
from primitives import Pose


class CombatantCollection:
    GRANULARITY = 150

    def __init__(self):
        self.combatants = []
        self.buckets = {}
        x = 0
        while x < c.ARENA_WIDTH:
            x += self.GRANULARITY
            y = 0
            while y < c.ARENA_HEIGHT:
                y += self.GRANULARITY
                self.buckets[(x, y)] = CombatantCollection.Bucket()

    def pose_to_bucket_key(self, pose):
        x = int(pose.x//self.GRANULARITY*self.GRANULARITY + self.GRANULARITY)
        y = int(pose.y//self.GRANULARITY*self.GRANULARITY + self.GRANULARITY)
        return x, y

    def pose_to_bucket(self, pose):
        x, y = self.pose_to_bucket_key(pose)
        if (x, y) not in self.buckets:
            return None
        return self.buckets[(x, y)]

    def add(self, combatant):
        self.combatants += [combatant]
        bucket = self.pose_to_bucket(combatant.position)
        bucket.add(combatant)

    def check_switched_buckets(self, combatant, old_pose):
        new_pose = combatant.position
        if self.pose_to_bucket(old_pose) != self.pose_to_bucket(new_pose):
            if self.pose_to_bucket(old_pose):
                self.pose_to_bucket(old_pose).remove(combatant)
            if self.pose_to_bucket(new_pose):
                self.pose_to_bucket(new_pose).add(combatant)

    def add_multiple(self, enumerable):
        for combatant in enumerable:
            self.add(combatant)

    def get_nearby_combatants(self, pose, tribe_to_exclude=None):
        combatants = set()
        for xoffset in (-2*self.GRANULARITY, self.GRANULARITY, 0, self.GRANULARITY, 2*self.GRANULARITY):
            for yoffset in (-2*self.GRANULARITY, self.GRANULARITY, 0, self.GRANULARITY, 2*self.GRANULARITY):
                bucket = self.pose_to_bucket(pose + Pose((xoffset, yoffset)))
                if bucket == None:
                    continue
                combatants = combatants.union(bucket.combatants)
        combatants_list = [combatant for combatant in combatants if combatant.tribe != tribe_to_exclude and not combatant.destroyed]
        combatants_list.sort(key=lambda x: (x.position - pose).magnitude())
        return combatants_list

    def __iter__(self):
        for combatant in self.combatants:
            yield combatant

    def sort(self, key):
        self.combatants.sort(key=key)

    def update(self, dt, events):
        for combatant in self.combatants[:]:
            combatant.update(dt, events)
            if combatant.destroyed and not len(combatant.particles):
                self.combatants.remove(combatant)

    def draw(self, surface, offset=(0, 0)):
        self.combatants.sort(key=lambda x: x.sort_value())
        for combatant in self.combatants:
            combatant.draw(surface, offset)

    class Bucket():
        def __init__(self):
            self.combatants = set()

        def add(self, combatant):
            self.combatants.add(combatant)

        def remove(self, combatant):
            self.combatants.remove(combatant)

        def __repr__(self):
            return f"{len(self.combatants)}"