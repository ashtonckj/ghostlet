import math
import random

from ghostlet.ghost import (
    FLEE_TIME,
    FLEEING,
    FLOATING,
    IDLE,
    IDLE_TIME,
    SLEEP_AFTER,
    SLEEPING,
    Ghost,
)


def run(g, seconds, dt=1 / 30):
    for _ in range(int(seconds / dt)):
        g.update(dt)


def make(cx=500, cy=400, seed=1):
    return Ghost(cx, cy, random.Random(seed))


def test_spawns_near_cursor_and_fades_in():
    g = make()
    assert 50 <= math.hypot(g.x - 500, g.y - 400) <= 120
    assert g.state == IDLE and g.alpha == 0
    run(g, 1.1)
    assert g.alpha == 1.0


def test_state_progression():
    g = make()
    run(g, IDLE_TIME + 0.1)
    assert g.state == FLOATING
    run(g, SLEEP_AFTER)
    assert g.state == SLEEPING


def test_floating_stays_near_home():
    g = make()
    run(g, 60)
    assert abs(g.x - g.home_x) <= g.rx + 1
    assert abs(g.y - g.home_y) <= g.ry + 5


def test_flees_away_from_cursor_and_disappears():
    g = make()
    run(g, 5)
    cx, cy = g.x - 10, g.y  # cursor just left of the ghost
    g.flee(cx, cy)
    assert g.state == FLEEING
    start = math.hypot(g.x - cx, g.y - cy)
    run(g, FLEE_TIME / 2)
    assert math.hypot(g.x - cx, g.y - cy) > start
    assert not g.facing_left and 0 < g.alpha < 1
    run(g, FLEE_TIME)
    assert g.gone and g.alpha == 0


def test_flee_is_idempotent_and_handles_cursor_on_ghost():
    g = make()
    g.flee(g.x, g.y)  # zero distance must not divide by zero
    v = (g.vx, g.vy)
    g.flee(0, 0)
    assert (g.vx, g.vy) == v


def test_frame_index_wraps():
    g = make()
    run(g, 10)
    assert 0 <= g.frame(3) < 3
    assert g.frame(1) == 0
