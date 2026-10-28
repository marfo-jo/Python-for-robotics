"""Milestone 1.4 tests for YOUR module imu_packet.py (Sprint 1, IMU data pipeline).

Put this file next to your imu_packet.py and run:
    conda activate robotics-course
    python -m pytest test_imu_packet.py -q

The frame format, checksum, and the PacketParser rules (resync, drop and
corrupt counters) are specified on the milestone 1.4 page. Standard library
and numpy only. Every "random" stream is seeded, so results never change.
"""
import random

import pytest

from imu_packet import FRAME_LEN, SYNC, PacketParser, build_frame, checksum, parse_frame


def make_frames(n, start_seq=0, t0=1000):
    """n valid frames, 10 ms apart, with payloads that never contain 0xA5."""
    frames = []
    for k in range(n):
        seq = (start_seq + k) % 256
        values = (100 + k, -200 - k, 16000, -1500, 3 * k, -7, 42)
        frames.append(build_frame(seq, t0 + 10 * k, values))
    return frames


def test_checksum_known_values():
    """8-bit Fletcher: ck_a is the running sum, ck_b the sum of the running sums"""
    assert checksum(b"") == (0, 0)
    assert checksum(b"\x01\x02\x03") == (6, 10)
    assert checksum(b"\xff\xff") == (254, 253)


def test_checksum_catches_swapped_bytes():
    """detects two bytes arriving in the wrong order (a plain sum or XOR cannot)"""
    assert checksum(b"\x01\x02") != checksum(b"\x02\x01")
    assert checksum(b"\x10\x00\x20") != checksum(b"\x20\x00\x10")


def test_build_frame_exact_layout():
    """lays out sync, seq, little-endian t_ms, 7 little-endian int16s, ck_a, ck_b (23 bytes)"""
    frame = build_frame(7, 0x01020304, (1, -1, 256, 0, 0, 0, -32768))
    assert FRAME_LEN == 23 and len(frame) == 23
    assert SYNC == b"\xa5\x5a"
    assert frame[:7] == b"\xa5\x5a\x07\x04\x03\x02\x01"
    assert frame[7:21] == b"\x01\x00\xff\xff\x00\x01\x00\x00\x00\x00\x00\x00\x00\x80"
    assert tuple(frame[21:]) == checksum(frame[2:21])


def test_build_frame_rejects_bad_input():
    """raises ValueError for the wrong number of values or out-of-range fields"""
    with pytest.raises(ValueError):
        build_frame(0, 0, (1, 2, 3, 4, 5, 6))
    with pytest.raises(ValueError):
        build_frame(256, 0, (0,) * 7)
    with pytest.raises(ValueError):
        build_frame(0, -1, (0,) * 7)
    with pytest.raises(ValueError):
        build_frame(0, 0, (0, 0, 0, 40000, 0, 0, 0))


def test_parse_frame_round_trip():
    """parse_frame(build_frame(...)) gives back (seq, t_ms, values)"""
    values = (16384, -16384, 32767, -32768, 0, 131, -1)
    assert parse_frame(build_frame(255, 4294967295, values)) == (255, 4294967295, values)


def test_parse_frame_rejects_damage():
    """returns None for a wrong length, a bad sync, a flipped payload bit, or a bad checksum"""
    good = build_frame(3, 500, (1, 2, 3, 4, 5, 6, 7))
    assert parse_frame(good[:-1]) is None
    assert parse_frame(good + b"\x00") is None
    assert parse_frame(b"\xa5\x00" + good[2:]) is None
    flipped = bytearray(good)
    flipped[10] ^= 0x04
    assert parse_frame(bytes(flipped)) is None
    bad_ck = bytearray(good)
    bad_ck[22] ^= 0xFF
    assert parse_frame(bytes(bad_ck)) is None


def test_parser_clean_stream():
    """a clean stream in one chunk gives every sample in order with all counters at zero"""
    frames = make_frames(50)
    p = PacketParser()
    samples = p.feed(b"".join(frames))
    assert [s[0] for s in samples] == list(range(50))
    assert samples[3] == (3, 1030, (103, -203, 16000, -1500, 9, -7, 42))
    assert (p.good, p.corrupt, p.dropped, p.skipped_bytes) == (50, 0, 0, 0)


def test_parser_handles_any_chunking():
    """frames split across feed() calls (1 byte, or random sizes) parse the same"""
    stream = b"".join(make_frames(20))
    p1 = PacketParser()
    one_by_one = []
    for i in range(len(stream)):
        one_by_one += p1.feed(stream[i:i + 1])
    rng = random.Random(1234)
    p2 = PacketParser()
    chunked, i = [], 0
    while i < len(stream):
        n = rng.randint(1, 40)
        chunked += p2.feed(stream[i:i + n])
        i += n
    assert len(one_by_one) == 20 and one_by_one == chunked
    assert p1.good == p2.good == 20


def test_parser_skips_startup_garbage():
    """skips junk before the first sync (opening the port mid-frame) and counts the bytes"""
    junk = bytes([0x00, 0x13, 0x5A, 0xFF, 0x42, 0x10, 0x7E])
    p = PacketParser()
    samples = p.feed(junk + b"".join(make_frames(5)))
    assert len(samples) == 5
    assert p.skipped_bytes == len(junk)
    assert p.corrupt == 0


def test_parser_counts_corrupt_frame_and_keeps_neighbors():
    """fault injection: one flipped bit costs exactly one frame (corrupt=1, dropped=1)"""
    frames = make_frames(10)
    bad = bytearray(frames[4])
    bad[12] ^= 0x01
    frames[4] = bytes(bad)
    p = PacketParser()
    samples = p.feed(b"".join(frames))
    assert [s[0] for s in samples] == [0, 1, 2, 3, 5, 6, 7, 8, 9]
    assert (p.good, p.corrupt, p.dropped) == (9, 1, 1)


def test_parser_resyncs_after_truncated_frame():
    """fault injection: a frame cut short must not swallow the good frame right after it"""
    frames = make_frames(6)
    stream = b"".join(frames[:2]) + frames[2][:10] + b"".join(frames[3:])
    p = PacketParser()
    samples = p.feed(stream)
    assert [s[0] for s in samples] == [0, 1, 3, 4, 5]
    assert p.corrupt == 1
    assert p.dropped == 1
    assert p.skipped_bytes == 10


def test_parser_sequence_wraps_without_false_drops():
    """seq 254, 255, 0, 1 is not a drop, but 254 then 1 is 2 dropped frames"""
    p = PacketParser()
    p.feed(b"".join(make_frames(4, start_seq=254)))
    assert (p.good, p.dropped) == (4, 0)
    q = PacketParser()
    q.feed(build_frame(254, 0, (0,) * 7) + build_frame(1, 30, (0,) * 7))
    assert q.dropped == 2


def test_parser_false_sync_inside_payload():
    """a payload that happens to contain A5 5A (int16 23205) never confuses the parser"""
    values = (23205, 23205, 0, 0, 0, 23205, 0)
    frames = [build_frame(k, 10 * k, values) for k in range(8)]
    damaged = bytearray(frames[1])
    damaged[2] ^= 0x01
    frames[1] = bytes(damaged)
    p = PacketParser()
    samples = p.feed(b"\x00\x01" + b"".join(frames))
    assert [s[0] for s in samples] == [0, 2, 3, 4, 5, 6, 7]
    assert all(s[2] == values for s in samples)
    assert p.corrupt >= 1 and p.dropped == 1


def test_parser_random_noise_bursts():
    """fault injection: seeded random byte corruption never crashes and loses only damaged frames"""
    rng = random.Random(42)
    frames = make_frames(200)
    damaged = set(rng.sample(range(1, 199), 15))
    stream = bytearray()
    for k, f in enumerate(frames):
        f = bytearray(f)
        if k in damaged:
            f[rng.randrange(2, FRAME_LEN)] ^= 1 << rng.randrange(8)
        stream += f
    p = PacketParser()
    samples = p.feed(bytes(stream))
    assert [s[0] for s in samples] == [k for k in range(200) if k not in damaged]
    assert p.dropped == 15 and p.corrupt >= 15


def test_parser_rejects_text():
    """feed() raises TypeError when given a str instead of bytes"""
    with pytest.raises(TypeError):
        PacketParser().feed("A55A")
