from ppb import Vector, Sprite, BaseScene
from ppb.assets import Circle, Square
from ppb.sprites import RenderableMixin, RotatableMixin, BaseSprite
from ppb.systemslib import System

import itertools
from math import sqrt

class CollisionSystem(System):
    @staticmethod
    def elastic_collision(x_hat, v, m1, m2, internal=False):
        '''
        Compute the result of an elastic collision between an initally stationary object "O1" located at the origin,
        and another moving object "O2".

        If both m1 and m2 are infinite, then they do not interact at all.

        Args:
            x_hat: Normal vector to the line that O2 reflects off of in the collision.
                For the case of two circles, this is the normalized position vector of O2.
                Must be a unit vector.
            v: Initial velocity vector of O2.
            m1: Mass of O1.  Can be infinite, in which case dv1 is always 0.
            m2: Mass of O2.  Can be infinite, in which case dv2 is always 0.
            internal: Whether to allow "internal" collisions, where O2 is initially moving away from O1.
                If false, then the result of an internal collision is (0, 0).

        Returns:
            Tuple (dv1, dv2), where dvi is the difference between
                the final velocity of Oi and the initial velocity of Oi.
        '''
        if m1 == float('inf') and m2 == float('inf'):
            # two infinite-mass objects; forbid interaction
            return (Vector(0, 0), Vector(0, 0))

        v_normal = x_hat * v
        if v_normal >= 0:
            # internal collision
            if not internal:
                return (Vector(0, 0), Vector(0, 0))

        if m1 == float('inf'):
            # object bouncing off a wall
            return (Vector(0, 0), -2 * v_normal * x_hat)
        if m2 == float('inf'):
            # imagine a ping-pong paddle
            return (2 * v_normal * x_hat, Vector(0, 0))

        # see https://en.wikipedia.org/wiki/Elastic_collision#Equations
        total_mass = m1 + m2
        dv1_normal = 2 * m2 / total_mass * v_normal
        dv2_normal = (m2 - m1) / total_mass * v_normal
        dv1 = dv1_normal * x_hat
        dv2 = (dv2_normal - v_normal) * x_hat
        return (dv1, dv2)

    @staticmethod
    def collision_vector(o1, o2):
        x_hat = o1.collision_vector(o2)
        if x_hat is not NotImplemented:
            return x_hat
        neg_x_hat = o2.collision_vector(o1)
        if neg_x_hat is not NotImplemented:
            return -neg_x_hat
        return Vector(0, 0)

    def on_update(self, update_event, signal):
        collidables = update_event.scene.get(kind=CollidableMixin)
        for (o1, o2) in itertools.combinations(collidables, 2):
            x_hat = self.collision_vector(o1, o2)
            if not x_hat:
                continue
            (dv1, dv2) = self.elastic_collision(x_hat, o2.velocity - o1.velocity, o1.mass, o2.mass)
            o1.velocity += dv1
            o2.velocity += dv2


class CollidableMixin:
    velocity = Vector(0, 0)
    mass = 1

    def collision_vector(self, other):
        '''
        Determine the collision vector between this and another collidable object.

        Returns:
            Normal vector to the line of reflection in the collision
            between self and other;
            or 0 if there is no collision;
            or NotImplemented if the result is unknown.
        '''
        return NotImplemented


class Ball(RenderableMixin, RotatableMixin, BaseSprite, CollidableMixin):
    size = 0.5
    image = Circle(230, 20, 20)

    def collision_vector(self, other):
        if isinstance(other, Ball):
            x = other.position - self.position
            if x.length > (self.size + other.size) / 2:
                # not touching
                return Vector(0, 0)
            if not x:
                # coincident; no way to collide reasonably
                return x
            return x.normalize()
        return NotImplemented

    def on_update(self, update_event, signal):
        self.position += self.velocity * update_event.time_delta


class Splitter(Ball):
    split_angle = 10
    image = Circle(20, 230, 20)

    def on_update(self, update_event, signal):
        super().on_update(update_event, signal)
        if self.mass * self.velocity.length >= 1:
            update_event.scene.add(Splitter(
                position=self.position,
                size=self.size / sqrt(2),
                mass=self.mass / 2,
                velocity=self.velocity.rotate(self.split_angle),
            ))
            update_event.scene.add(Splitter(
                position=self.position,
                size=self.size / sqrt(2),
                mass=self.mass / 2,
                velocity=self.velocity.rotate(-self.split_angle),
            ))
            update_event.scene.remove(self)



class Wall(Sprite, CollidableMixin):
    mass = float('inf')
    image = Square(170, 53, 232)

    def collision_vector(self, other):
        if isinstance(other, Ball):
            return self.collision_with_ball(other)
        return NotImplemented

    def collision_with_ball(self, b):
        '''Calculate the collision vector between this wall and a ball;
        or 0 if they aren't colliding.'''
        position_rotated = (b.position - self.position).rotate(-self.rotation) + self.position
        for (c1, c2) in [
                    (self.left.bottom, self.left.top),
                    (self.bottom.left, self.bottom.right),
                    (self.right.bottom, self.right.top),
                    (self.top.left, self.top.right),
                ]:
            # side collision
            x = position_rotated - c1
            c = c2 - c1
            c_hat = c.normalize()
            e = x * c_hat
            n = x - e * c_hat
            if 0 <= e <= c.length and n.length <= b.size / 2:
                return n.normalize().rotate(self.rotation)
        for c in [self.left.top, self.right.top,
                  self.left.bottom, self.right.bottom]:
            # corner collision
            n = position_rotated - c
            if n.length <= b.size / 2:
                return n.normalize().rotate(self.rotation)
        return Vector(0, 0)


class Scene(BaseScene):
    background_color = 56, 143, 61

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for x in [
                Ball(position=Vector(-2, 0), velocity=Vector(8, 0)),
                Ball(size=1, mass=4),
                Ball(position=Vector(4, -0.5)),
                Ball(position=Vector(5, -1)),
                Ball(position=Vector(-5, -3), velocity=Vector(1, 0)),
                Ball(position=Vector(-2, -2.6), velocity=Vector(1, 0)),
                Ball(position=Vector(-1, -2.7), velocity=Vector(1, 0)),
                Ball(position=Vector(0, -2.8), velocity=Vector(1, 0)),
                Ball(position=Vector(1, -2.95), velocity=Vector(2, 0)),
                Ball(position=Vector(2, -2.94), velocity=Vector(3, 0)),

                Wall(rotation=20, position=Vector(-3, 0)),
                Wall(rotation=45, position=Vector(0, 2.85)),
                Wall(rotation=45, position=Vector(6, -3), size=2),

                Splitter(position=Vector(3, 0.1)),
        ]:
            self.add(x)
