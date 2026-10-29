import math
import random

from ghostlet.ghost import (
    FLEE_TIME,
    FLEEING,
    FLOATING,
    GRAB_TIME,
    IDLE,
    IDLE_TIME,
    MAX_PROPS,
    PROP_EVERY,
    RARE_ODDS,
    SLEEP_AFTER,
    SLEEPING,
    Ghost,
    Prop,
    pick_weighted,
    prop_spots,
    props_due,
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


def test_prop_spots_spread_inside_bounds():
    xs = prop_spots(100, 1100, 5, random.Random(3))
    assert len(xs) == 5 and xs == sorted(xs)
    assert all(100 <= x <= 1100 for x in xs)
    assert min(b - a for a, b in zip(xs, xs[1:])) > 0


def test_prop_rests_then_is_carried_away_with_ghost():
    g = make()
    p = Prop("pumpkin", 300, 1000)
    for _ in range(40):
        g.update(1 / 30)
        p.update(1 / 30)
    assert (p.x, p.y) == (300, 1000) and p.alpha == 1.0 and not p.gone

    g.flee(g.x - 10, g.y)
    p.grab(g, 20)
    p.grab(make(), 99)  # a second grab must not steal it
    t = 0.0
    while t < GRAB_TIME + 0.05:
        g.update(1 / 30)
        p.update(1 / 30)
        t += 1 / 30
    assert p.carrier is g
    assert math.isclose(p.x, g.x) and math.isclose(p.y, g.y + 20)
    assert p.alpha <= g.alpha
    while not g.gone:
        g.update(1 / 30)
        p.update(1 / 30)
    assert p.gone and p.alpha == 0


def test_props_grow_over_time_up_to_the_cap():
    assert props_due(0) == 3
    assert props_due(PROP_EVERY - 0.1) == 3
    assert props_due(PROP_EVERY) == 4
    assert props_due(10_000) == MAX_PROPS


def test_rare_art_is_picked_less_often():
    rng = random.Random(7)
    names = ["pumpkin", "pumpkin_gold_rare"]
    picks = [pick_weighted(rng, names) for _ in range(5500)]
    rare = picks.count("pumpkin_gold_rare")
    assert 250 < rare < 750  # expected 500 with RARE_ODDS == 10
    assert RARE_ODDS == 10
    assert pick_weighted(rng, ["only"]) == "only"


def test_roaming_ghost_drifts_wider_and_keeps_its_variant():
    g = Ghost(0, 0, random.Random(1), drift=5, variant="gold_rare")
    near = make(seed=1)
    assert g.rx == near.rx * 5 and g.variant == "gold_rare"
    assert near.variant == "default"
