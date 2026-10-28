"""Milestone 1.7 tests for YOUR module allan.py (Sprint 1, IMU data pipeline).

Put this file next to your allan.py and run:
    conda activate robotics-course
    python -m pytest test_allan.py -q

The estimator (fully overlapping Allan deviation), the units of tau, and
the helper functions are specified on the milestone 1.7 page. numpy only
(no scipy); every noise sequence is seeded, so results never change.
"""
import numpy as np
import pytest

from allan import allan_deviation, angle_random_walk, loglog_slope

FS = 100.0
N = 2 ** 16
SIGMA = 0.05  # deg/s, white rate noise


@pytest.fixture(scope="module")
def white():
    return SIGMA * np.random.default_rng(2024).standard_normal(N)


def test_white_noise_values(white):
    """white noise: ADEV(tau) = sigma / sqrt(m), so sigma at one sample and sigma/sqrt(10) at m = 10"""
    taus, adev = allan_deviation(white, FS, taus=[0.01, 0.1])
    np.testing.assert_allclose(taus, [0.01, 0.1])
    assert adev[0] == pytest.approx(SIGMA, rel=0.03)
    assert adev[1] == pytest.approx(SIGMA / np.sqrt(10), rel=0.05)


def test_white_noise_slope_is_minus_half(white):
    """white noise falls with slope -1/2 on a log-log plot"""
    taus, adev = allan_deviation(white, FS)
    keep = taus <= (N / 20) / FS
    assert loglog_slope(taus[keep], adev[keep]) == pytest.approx(-0.5, abs=0.05)


def test_random_walk_slope_is_plus_half():
    """a rate random walk (integrated white noise) rises with slope +1/2"""
    rng = np.random.default_rng(99)
    walk = np.cumsum(1e-3 * rng.standard_normal(N))
    taus, adev = allan_deviation(walk, FS, taus=[1.0, 2.0, 5.0, 10.0, 20.0, 50.0])
    assert loglog_slope(taus, adev) == pytest.approx(0.5, abs=0.1)


def test_exact_small_example_is_overlapping():
    """matches the overlapping formula by hand on [0, 0, 1, 1, 0, 0] (tau in seconds, not samples)"""
    taus, adev = allan_deviation([0, 0, 1, 1, 0, 0], fs=10.0, taus=[0.1, 0.2])
    np.testing.assert_allclose(taus, [0.1, 0.2])
    np.testing.assert_allclose(adev, [np.sqrt(0.2), np.sqrt(1 / 3)], rtol=1e-12)


def test_returned_taus_are_the_ones_actually_used():
    """a requested tau is rounded to a whole number of samples and the real tau is returned"""
    taus, _ = allan_deviation(np.arange(1000.0) % 7, FS, taus=[0.013, 0.5])
    np.testing.assert_allclose(taus, [0.01, 0.5])


def test_default_taus(white):
    """default taus start at one sample, increase strictly, and stop at half the record"""
    taus, adev = allan_deviation(white, FS)
    assert taus[0] == pytest.approx(1 / FS)
    assert np.all(np.diff(taus) > 0)
    assert taus[-1] <= (N // 2) / FS + 1e-12
    assert len(taus) >= 10 and len(adev) == len(taus)


def test_constant_bias_does_not_show_up():
    """a constant offset gives zero ADEV, and scaling the signal by c scales ADEV by |c|"""
    _, flat = allan_deviation(np.full(500, 3.7), FS, taus=[0.01, 0.1, 1.0])
    np.testing.assert_allclose(flat, 0.0, atol=1e-12)
    y = np.random.default_rng(5).standard_normal(4000)
    _, a1 = allan_deviation(y, FS, taus=[0.01, 0.1])
    _, a2 = allan_deviation(-3.0 * y + 10.0, FS, taus=[0.01, 0.1])
    np.testing.assert_allclose(a2, 3.0 * a1, rtol=1e-9)


def test_bad_input_raises():
    """raises ValueError for too few samples, fs <= 0, 2-D data, or an impossible tau"""
    with pytest.raises(ValueError):
        allan_deviation([1.0, 2.0], FS)
    with pytest.raises(ValueError):
        allan_deviation(np.zeros(100), 0.0)
    with pytest.raises(ValueError):
        allan_deviation(np.zeros((50, 3)), FS)
    with pytest.raises(ValueError):
        allan_deviation(np.zeros(100), FS, taus=[0.6])


def test_angle_random_walk_from_white_noise(white):
    """angle random walk is the ADEV read at tau = 1 s: sigma / sqrt(fs) deg/sqrt(s)"""
    taus, adev = allan_deviation(white, FS)
    arw = angle_random_walk(taus, adev)
    assert arw == pytest.approx(SIGMA / np.sqrt(FS), rel=0.05)
    assert arw * 60 == pytest.approx(0.3, rel=0.05)  # in deg/sqrt(h)


def test_angle_random_walk_needs_tau_of_one_second():
    """raises ValueError when the curve does not include tau = 1 s"""
    with pytest.raises(ValueError):
        angle_random_walk([0.01, 0.1, 0.5], [1.0, 0.5, 0.2])


def test_loglog_slope_exact_and_bad_input():
    """fits the slope of log10(adev) vs log10(tau) and rejects zeros (log of 0)"""
    t = np.array([0.1, 1.0, 10.0, 100.0])
    assert loglog_slope(t, 2.0 * t ** -0.5) == pytest.approx(-0.5)
    assert loglog_slope(t, 0.3 * t ** 1.0) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        loglog_slope([0.1, 1.0], [0.0, 1.0])
