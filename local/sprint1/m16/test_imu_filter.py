"""Milestone 1.6 tests for YOUR module imu_filter.py (Sprint 1, IMU data pipeline).

Put this file next to your imu_filter.py and run:
    conda activate robotics-course
    python -m pytest test_imu_filter.py -q

Function names, angle conventions (degrees), and the filter equation are
specified on the milestone 1.6 page. numpy only; all noise is seeded.
"""
import math

import numpy as np
import pytest

from imu_filter import accel_angles, complementary_step, estimate_gyro_bias, run_complementary

FS = 100.0
DT = 1.0 / FS


def test_bias_of_one_axis_is_the_mean():
    """estimates the bias of a still gyro as the mean of its samples"""
    rng = np.random.default_rng(0)
    samples = 0.8 + 0.05 * rng.standard_normal(2000)
    assert float(estimate_gyro_bias(samples)) == pytest.approx(float(np.mean(samples)))
    assert float(estimate_gyro_bias([1.0, 2.0, 3.0])) == pytest.approx(2.0)


def test_bias_of_three_axes():
    """an (N, 3) array gives one bias per axis (x, y, z)"""
    data = np.array([[1.0, -2.0, 0.5], [3.0, -4.0, 0.5]])
    np.testing.assert_allclose(estimate_gyro_bias(data), [2.0, -3.0, 0.5])


def test_bias_rejects_empty_input():
    """raises ValueError when there are no samples to average"""
    with pytest.raises(ValueError):
        estimate_gyro_bias([])


def test_accel_angles_level_and_tilted():
    """returns (roll, pitch) in degrees from gravity: level is (0, 0)"""
    assert accel_angles(0.0, 0.0, 1.0) == pytest.approx((0.0, 0.0), abs=1e-9)
    r30 = math.radians(30)
    assert accel_angles(0.0, math.sin(r30), math.cos(r30)) == pytest.approx((30.0, 0.0), abs=1e-9)
    p20 = math.radians(20)
    assert accel_angles(-math.sin(p20), 0.0, math.cos(p20)) == pytest.approx((0.0, 20.0), abs=1e-9)


def test_accel_angles_edge_cases():
    """works on its side (az = 0) and does not depend on the magnitude of g"""
    assert accel_angles(0.0, 1.0, 0.0)[0] == pytest.approx(90.0)
    assert accel_angles(0.0, -2.0, 2.0)[0] == pytest.approx(-45.0)
    assert accel_angles(-0.5, 0.0, 0.0)[1] == pytest.approx(90.0)


def test_step_exact_value():
    """blends: alpha * (previous + rate * dt) + (1 - alpha) * accel angle"""
    assert complementary_step(10.0, 5.0, 0.0, 0.01, alpha=0.98) == pytest.approx(9.849)
    assert complementary_step(0.0, 0.0, 10.0, 0.01) == pytest.approx(0.2)


def test_step_alpha_limits():
    """alpha = 1 is pure gyro integration, alpha = 0 is pure accelerometer"""
    assert complementary_step(3.0, 100.0, -50.0, 0.02, alpha=1.0) == pytest.approx(5.0)
    assert complementary_step(3.0, 100.0, -50.0, 0.02, alpha=0.0) == pytest.approx(-50.0)


def test_step_rejects_bad_parameters():
    """raises ValueError for dt <= 0 or alpha outside [0, 1]"""
    for dt, alpha in [(0.0, 0.98), (-0.01, 0.98), (0.01, 1.5), (0.01, -0.1)]:
        with pytest.raises(ValueError):
            complementary_step(0.0, 0.0, 0.0, dt, alpha)


def test_run_output_shape_and_start():
    """returns one estimate per sample, starting from the first accel angle unless angle0 is given"""
    gyro = np.zeros(5)
    acc = np.full(5, 12.0)
    out = run_complementary(gyro, acc, DT)
    assert len(out) == 5
    np.testing.assert_allclose(out, 12.0)
    out2 = run_complementary(gyro, acc, DT, alpha=0.5, angle0=0.0)
    assert out2[0] == pytest.approx(6.0)


def test_run_rejects_mismatched_lengths():
    """raises ValueError when the gyro and accel series have different lengths"""
    with pytest.raises(ValueError):
        run_complementary(np.zeros(10), np.zeros(9), DT)


def test_filter_bounds_gyro_bias_drift():
    """a 1 deg/s gyro bias drifts 60 deg in a minute by integration; the filter stays within 1 deg"""
    rng = np.random.default_rng(7)
    n = int(60 * FS)
    gyro = 1.0 + 0.05 * rng.standard_normal(n)
    acc = 5.0 + 0.5 * rng.standard_normal(n)
    out = run_complementary(gyro, acc, DT, alpha=0.98)
    integrated = 5.0 + np.cumsum(gyro) * DT
    assert abs(integrated[-1] - 5.0) > 50
    assert abs(np.mean(out[-1000:]) - 5.0) < 1.0
    corrected = run_complementary(gyro - estimate_gyro_bias(gyro), acc, DT, alpha=0.98)
    assert abs(np.mean(corrected[-1000:]) - 5.0) < 0.2


def test_filter_beats_noisy_accelerometer_in_motion():
    """during a 2 Hz +-20 deg swing the filter is far less noisy than the accel angle"""
    rng = np.random.default_rng(11)
    t = np.arange(0, 10, DT)
    truth = 20.0 * np.sin(2 * np.pi * 2.0 * t)
    rate = 20.0 * 2 * np.pi * 2.0 * np.cos(2 * np.pi * 2.0 * (t + DT / 2))
    gyro = rate + 0.2 * rng.standard_normal(t.size)
    acc = truth + 3.0 * rng.standard_normal(t.size)
    out = run_complementary(gyro, acc, DT, alpha=0.98, angle0=0.0)
    truth_next = 20.0 * np.sin(2 * np.pi * 2.0 * (t + DT))
    rms_filter = np.sqrt(np.mean((out[100:] - truth_next[100:]) ** 2))
    rms_accel = np.sqrt(np.mean((acc[100:] - truth[100:]) ** 2))
    assert rms_filter < 0.5 * rms_accel
