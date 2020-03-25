import ppb
import ppb.assets
import ppb.sprites

from pygame import Surface, draw

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
            x_hat = x.normalize()
            v = other.velocity - self.velocity
            # x and v are their position and velocity relative to us
            v_normal = x_hat * v
            if v_normal >= 0:
                # they're moving away from us
                continue
            # see https://en.wikipedia.org/wiki/Elastic_collision#Equations
            total_mass = self.mass + other.mass
            self_vf_normal = 2 * other.mass / total_mass * v_normal
            vf_normal = (other.mass - self.mass) / total_mass * v_normal

            self.velocity = self.velocity + self_vf_normal * x_hat
            other.velocity = other.velocity + (vf_normal - v_normal) * x_hat



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
        ]:
            b = Ball(image=ppb.assets.Circle(230, 20, 20))
            for (k, v) in d.items():
                setattr(b, k, v)
            self.add(b)
