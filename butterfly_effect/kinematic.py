import ppb
import ppb.assets
import ppb.sprites

from pygame import Surface, draw

def elastic_collision(x_hat, v, m1, m2, internal=False):
    '''
    Compute the result of an elastic collision between an initally stationary object "O1" located at the origin,
    and another moving object "O2".

    Args:
        x_hat: Normal vector to the line that O2 reflects off of in the collision.
            For the case of two circles, this is the normalized position vector of O2.
            Must be a unit vector.
        v: Initial velocity vector of O2.
        m1: Mass of O1.  Can be infinite, in which case dv1 is always 0.
        m2: Mass of O2.
        internal: Whether to allow "internal" collisions, where O2 is initially moving away from O1.
            If false, then the result of an internal collision is (0, 0).

    Returns:
        Tuple (dv1, dv2), where dvi is the difference between
            the final velocity of Oi and the initial velocity of Oi.
    '''
    v_normal = x_hat * v
    if v_normal >= 0:
        # internal collision
        if not internal:
            return (ppb.Vector(0, 0), ppb.Vector(0, 0))

    # see https://en.wikipedia.org/wiki/Elastic_collision#Equations
    total_mass = m1 + m2
    dv1_normal = 2 * m2 / total_mass * v_normal
    dv2_normal = (-1 if m1 == float('inf') else (m2 - m1) / total_mass) * v_normal
    dv1 = dv1_normal * x_hat
    dv2 = (dv2_normal - v_normal) * x_hat
    return (dv1, dv2)


class Ball(ppb.sprites.RenderableMixin, ppb.sprites.RotatableMixin, ppb.sprites.BaseSprite):
    velocity = ppb.Vector(0, 0)
    mass = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_update(self, update_event: ppb.events.Update, signal):
        self.position += self.velocity * update_event.time_delta

        for other in update_event.scene.get(kind=Ball):
            if self is other:
                continue
            x = other.position - self.position
            if x.length > (self.size + other.size) / 2:
                # not touching
                continue
            if not x:
                # coincident; no way to collide reasonably
                continue
            v = other.velocity - self.velocity
            # x and v are their position and velocity relative to us
            x_hat = x.normalize()

            (dv1, dv2) = elastic_collision(x_hat, v, self.mass, other.mass)
            self.velocity += dv1
            other.velocity += dv2


class Wall(ppb.Sprite):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def collision_vector(self, b):
        '''Calculate the collision vector between this wall and a ball;
        or None if they aren't colliding.'''
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
        return None

    def on_update(self, update_event: ppb.events.Update, signal):
        for ball in update_event.scene.get(kind=Ball):
            x_hat = self.collision_vector(ball)
            if not x_hat:
                continue
            (_, dv2) = elastic_collision(x_hat, ball.velocity, float('inf'), ball.mass)
            ball.velocity += dv2


class Scene(ppb.BaseScene):
    background_color = 56, 143, 61

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for d in [
                {'size': 0.5, 'position': ppb.Vector(-2, 0), 'velocity': ppb.Vector(3, 0)},
                {'size': 1, 'mass': 4},
                {'size': 0.5, 'position': ppb.Vector(3, 0.1)},
                {'size': 0.5, 'position': ppb.Vector(4, -0.5)},
                {'size': 0.5, 'position': ppb.Vector(5, -1)},
                {'size': 0.5, 'position': ppb.Vector(-5, -3), 'velocity': ppb.Vector(1, 0)},
                {'size': 0.5, 'position': ppb.Vector(-2, -2.6), 'velocity': ppb.Vector(1, 0)},
                {'size': 0.5, 'position': ppb.Vector(-1, -2.7), 'velocity': ppb.Vector(1, 0)},
                {'size': 0.5, 'position': ppb.Vector(0, -2.8), 'velocity': ppb.Vector(1, 0)},
                {'size': 0.5, 'position': ppb.Vector(1, -2.95), 'velocity': ppb.Vector(2, 0)},
                {'size': 0.5, 'position': ppb.Vector(2, -2.94), 'velocity': ppb.Vector(3, 0)},
        ]:
            b = Ball(image=ppb.assets.Circle(230, 20, 20))
            for (k, v) in d.items():
                setattr(b, k, v)
            self.add(b)

        for d in [
                {'rotation': 20, 'position': ppb.Vector(-3, 0)},
                {'rotation': 45, 'position': ppb.Vector(0, 2.85)},
                {'rotation': 45, 'position': ppb.Vector(6, -3), 'size': 2},
        ]:
            b = Wall(image=ppb.assets.Square(170, 53, 232))
            for (k, v) in d.items():
                setattr(b, k, v)
            self.add(b)
