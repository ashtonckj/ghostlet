"""Ghost motion and state logic. Pure Python (no Qt) so it is cheap and easy to test.

Coordinates are screen pixels of the ghost's centre. States:
  idle     - just appeared, fades in and bobs in place
  floating - drifts gently around its home spot
  sleeping - dozes after floating for a while
  fleeing  - user came back: dart away from the cursor and fade out

The first ghost stays near the cursor; any others roam the screen.
Props (pumpkins, graves) rest along the bottom of the screen while ghosts are out, and
more appear the longer you are away. When the ghosts flee, they carry the props off.
"""
import math

IDLE, FLOATING, SLEEPING, FLEEING = "idle", "floating", "sleeping", "fleeing"
STATES = (IDLE, FLOATING, SLEEPING, FLEEING)

FADE_IN = 1.0  # seconds
IDLE_TIME = 3.0  # seconds hovering before drifting
SLEEP_AFTER = 120.0  # seconds of floating before dozing off
FLEE_TIME = 0.8  # seconds to run off and vanish
FLEE_SPEED = 300.0  # pixels per second at the start of fleeing
ANIM_FPS = 4  # frame rate for multi-frame artwork
FOLLOW = 3.0  # how fast the ghost eases toward its target (per second)
GRAB_TIME = 0.3  # seconds for a fleeing ghost to snatch its prop
ROAM_DRIFT = 5.0  # roaming ghosts drift this many times wider than the cursor companion
START_PROPS = 3
PROP_EVERY = 30.0  # seconds between extra props
MAX_PROPS = 12
RARE_ODDS = 10  # art with "rare" in its name is this many times less likely


class Ghost:
    def __init__(self, cx, cy, rng, drift=1.0, variant="default"):
        self.variant = variant  # art folder name; the app picks the frames
        angle = rng.uniform(0, math.tau)
        dist = rng.uniform(50, 120)
        self.home_x = cx + math.cos(angle) * dist
        self.home_y = cy + math.sin(angle) * dist
        self.x, self.y = self.home_x, self.home_y
        self.rx = rng.uniform(30, 70) * drift  # drift radius
        self.ry = rng.uniform(15, 35) * drift
        self.phase = rng.uniform(0, math.tau)
        self.vx = self.vy = 0.0
        self.alpha = 0.0
        self.facing_left = False
        self.state = IDLE
        self.state_time = 0.0
        self.time = 0.0

    def _set_state(self, state):
        self.state = state
        self.state_time = 0.0

    def flee(self, cx, cy):
        if self.state == FLEEING:
            return
        dx, dy = self.x - cx, self.y - cy
        d = math.hypot(dx, dy) or 1.0
        self.vx, self.vy = dx / d * FLEE_SPEED, dy / d * FLEE_SPEED
        self._set_state(FLEEING)

    @property
    def gone(self):
        return self.state == FLEEING and self.state_time >= FLEE_TIME

    def frame(self, count):
        return int(self.time * ANIM_FPS) % count

    def update(self, dt):
        self.time += dt
        self.state_time += dt
        t = self.time

        if self.state == FLEEING:
            boost = 1 + 3 * dt  # speed up as it runs
            self.vx *= boost
            self.vy *= boost
            self.x += self.vx * dt
            self.y += self.vy * dt
            self.alpha = max(0.0, 1 - self.state_time / FLEE_TIME)
            self.facing_left = self.vx < 0
            return

        self.alpha = min(1.0, self.alpha + dt / FADE_IN)
        if self.state == IDLE and self.state_time >= IDLE_TIME:
            self._set_state(FLOATING)
        elif self.state == FLOATING and self.state_time >= SLEEP_AFTER:
            self.home_x, self.home_y = self.x, self.y  # fall asleep where it is
            self._set_state(SLEEPING)

        if self.state == SLEEPING:
            tx, ty = self.home_x, self.home_y + 2 * math.sin(t)
        else:
            amp = min(1.0, self.state_time / 2) if self.state == FLOATING else 0.0
            tx = self.home_x + self.rx * amp * math.sin(0.5 * t + self.phase)
            ty = self.home_y + self.ry * amp * math.sin(0.8 * t + self.phase) + 4 * math.sin(2 * t)

        if abs(tx - self.x) > 0.5:
            self.facing_left = tx < self.x
        k = min(1.0, dt * FOLLOW)  # ease toward target so state changes never jump
        self.x += (tx - self.x) * k
        self.y += (ty - self.y) * k


class Prop:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.rest_x, self.rest_y = x, y
        self.x, self.y = x, y
        self.alpha = 0.0
        self.carrier = None
        self.hang = 0.0  # pixels below the carrier's centre
        self.carry_time = 0.0

    def grab(self, ghost, hang):
        if self.carrier is None:
            self.carrier, self.hang = ghost, hang

    @property
    def gone(self):
        return self.carrier is not None and self.carrier.gone

    def update(self, dt):
        """Call after the carrier ghost has been updated this frame."""
        g = self.carrier
        if g is None:
            self.alpha = min(1.0, self.alpha + dt / FADE_IN)
            return
        self.carry_time += dt
        k = min(1.0, self.carry_time / GRAB_TIME)  # zip up to the ghost, then hang on
        self.x = self.rest_x + (g.x - self.rest_x) * k
        self.y = self.rest_y + (g.y + self.hang - self.rest_y) * k
        self.alpha = min(self.alpha, g.alpha)


def prop_spots(left, right, count, rng):
    """Spread count x positions evenly across [left, right], with a little jitter."""
    slot = (right - left) / count
    return [left + slot * (i + rng.uniform(0.25, 0.75)) for i in range(count)]


def props_due(elapsed):
    """How many props should be out after this many seconds of haunting."""
    return min(MAX_PROPS, START_PROPS + int(elapsed // PROP_EVERY))


def pick_weighted(rng, names):
    """Pick a random art name; names containing "rare" are RARE_ODDS times less likely."""
    weights = [1 if "rare" in n.lower() else RARE_ODDS for n in names]
    return rng.choices(names, weights=weights)[0]
