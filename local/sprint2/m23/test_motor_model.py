"""Milestone 2.3 tests for YOUR module motor_model.py (Sprint 2, DC motor test rig).

Put this file next to your motor_model.py and run:
    conda activate robotics-course
    python -m pytest test_motor_model.py -q

The model, the fitting method, and the exact (zero-order-hold) simulation
update are specified on the milestone 2.3 page. numpy only (no scipy); all
noise is seeded, so results never change.
"""
import numpy as np
import pytest

from motor_model import fit_first_order, r_squared, simulate_first_order

K_TRUE = 300.0     # rad/s per unit duty
TAU_TRUE = 0.12    # s
FS = 200.0


def step_log(u=0.5, t0=0.5, t_end=2.0, noise=0.0, seed=0):
    """A synthetic step test: motor at rest until t0, then duty u."""
    t = np.arange(0.0, t_end, 1.0 / FS)
    w = np.where(t >= t0, K_TRUE * u * (1.0 - np.exp(-(t - t0) / TAU_TRUE)), 0.0)
    rng = np.random.default_rng(seed)
    return t, w + noise * abs(K_TRUE * u) * rng.standard_normal(t.size)


def test_fit_noiseless_step():
    """recovers K and tau from a clean step that starts at t = 0"""
    t, w = step_log(t0=0.0)
    K, tau = fit_first_order(t, w, 0.5)
    assert K == pytest.approx(K_TRUE, rel=0.01)
    assert tau == pytest.approx(TAU_TRUE, rel=0.01)


def test_fit_uses_step_time_as_origin():
    """with 0.5 s of rest before the step, time must be measured from t0 (not from the log start)"""
    t, w = step_log(t0=0.5, noise=0.01, seed=1)
    K, tau = fit_first_order(t, w, 0.5, t0=0.5)
    assert K == pytest.approx(K_TRUE, rel=0.02)
    assert tau == pytest.approx(TAU_TRUE, rel=0.05)


def test_fit_noisy_step_k_from_steady_state():
    """K comes from the averaged steady state, not the noisy peak sample"""
    t, w = step_log(u=0.8, t0=0.0, noise=0.02, seed=2)
    K, tau = fit_first_order(t, w, 0.8)
    assert K == pytest.approx(K_TRUE, rel=0.02)
    assert tau == pytest.approx(TAU_TRUE, rel=0.08)


def test_fit_reverse_direction():
    """a negative duty step (motor reversing) gives the same positive K and tau"""
    t, w = step_log(u=-0.6, t0=0.0, noise=0.01, seed=3)
    K, tau = fit_first_order(t, w, -0.6)
    assert K == pytest.approx(K_TRUE, rel=0.02)
    assert tau == pytest.approx(TAU_TRUE, rel=0.05)


def test_fit_rejects_bad_input():
    """raises ValueError for mismatched lengths, u = 0, or timestamps that go backwards"""
    t, w = step_log(t0=0.0)
    with pytest.raises(ValueError):
        fit_first_order(t, w[:-1], 0.5)
    with pytest.raises(ValueError):
        fit_first_order(t, w, 0.0)
    t_bad = t.copy()
    t_bad[50] = t_bad[49]
    with pytest.raises(ValueError):
        fit_first_order(t_bad, w, 0.5)


def test_fit_rejects_stalled_motor():
    """fault injection: a duty inside the deadband (speed is only noise) raises ValueError"""
    t = np.arange(0.0, 2.0, 1.0 / FS)
    w = 0.5 * np.random.default_rng(4).standard_normal(t.size)
    with pytest.raises(ValueError):
        fit_first_order(t, w, 0.05)


def test_simulate_matches_analytic_step():
    """the exact update reproduces K*u*(1 - exp(-t/tau)) to numerical precision"""
    t = np.arange(0.0, 1.0, 0.005)
    w = simulate_first_order(t, 0.5, K_TRUE, TAU_TRUE)
    np.testing.assert_allclose(w, K_TRUE * 0.5 * (1 - np.exp(-t / TAU_TRUE)), rtol=1e-9, atol=1e-9)


def test_simulate_stable_with_large_time_step():
    """stays stable and never overshoots even when dt > 2*tau (forward Euler blows up here)"""
    t = np.arange(0.0, 5.0, 0.5)
    w = simulate_first_order(t, 1.0, 10.0, 0.1)
    assert np.all(w <= 10.0 + 1e-9)
    assert np.all(np.diff(w) >= -1e-9)
    assert w[-1] == pytest.approx(10.0, rel=1e-6)


def test_simulate_input_array_and_initial_speed():
    """u can be an array held between samples, and omega0 sets the starting speed"""
    t = np.arange(0.0, 2.0, 0.01)
    u = np.where(t < 1.0, 0.0, 0.4)
    w = simulate_first_order(t, u, K_TRUE, TAU_TRUE, omega0=50.0)
    assert w[0] == pytest.approx(50.0)
    i1 = int(np.argmin(np.abs(t - 1.0)))
    assert w[i1] == pytest.approx(50.0 * np.exp(-1.0 / TAU_TRUE), abs=1e-6)
    assert w[-1] == pytest.approx(K_TRUE * 0.4 * (1 - np.exp(-(t[-1] - 1.0) / TAU_TRUE)), rel=1e-6)


def test_simulate_uneven_timestamps():
    """handles jittery logged timestamps (uneven dt) exactly"""
    rng = np.random.default_rng(5)
    t = np.cumsum(rng.uniform(0.004, 0.016, 150))
    t -= t[0]
    w = simulate_first_order(t, 0.5, K_TRUE, TAU_TRUE)
    np.testing.assert_allclose(w, K_TRUE * 0.5 * (1 - np.exp(-t / TAU_TRUE)), rtol=1e-9, atol=1e-9)


def test_simulate_rejects_bad_input():
    """raises ValueError for tau <= 0 or a u array of the wrong length"""
    t = np.arange(0.0, 1.0, 0.01)
    with pytest.raises(ValueError):
        simulate_first_order(t, 0.5, K_TRUE, 0.0)
    with pytest.raises(ValueError):
        simulate_first_order(t, np.ones(10), K_TRUE, TAU_TRUE)


def test_r_squared():
    """R^2 is 1 for a perfect model, 0 for predicting the mean, and rejects mismatched arrays"""
    m = np.array([1.0, 2.0, 3.0, 4.0])
    assert r_squared(m, m) == pytest.approx(1.0)
    assert r_squared(m, np.full(4, m.mean())) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        r_squared(m, m[:3])


def test_fit_then_simulate_round_trip():
    """fit a noisy log, simulate the fitted model, and get R^2 above 0.99"""
    t, w = step_log(u=0.7, t0=0.3, noise=0.01, seed=6)
    K, tau = fit_first_order(t, w, 0.7, t0=0.3)
    u = np.where(t >= 0.3, 0.7, 0.0)
    pred = simulate_first_order(t, u, K, tau)
    assert r_squared(w, pred) > 0.99
