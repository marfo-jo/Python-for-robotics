**About 25 minutes, plus 15 minutes trying it.** Just enough numpy and Matplotlib to load a CSV log and make plots you'd put in a README: stacked time series, a log-log plot, and a live plot. Module S lesson S.8 covers Matplotlib in depth later.

All the examples below use a **practice log** you generate yourself, so you can try everything without hardware. It's a fake heater test: temperature and current at 50 Hz, with the heater switching on at t = 5 s.

## Step 0: make a practice log

Save this as `make_practice_log.py` in a scratch folder (not in your project repo) and run it:

```python
import numpy as np

# Make a fake log to practice on: 20 s at 50 Hz, a heater switching on at t = 5 s.
rng = np.random.default_rng(0)
t_ms = np.arange(0, 20000, 20)
temp_c = 21 + 4 * (1 - np.exp(-np.clip(t_ms - 5000, 0, None) / 4000)) + 0.05 * rng.standard_normal(t_ms.size)
current_a = np.where(t_ms >= 5000, 1.2, 0.0) + 0.02 * rng.standard_normal(t_ms.size)
np.savetxt("heater_log.csv", np.column_stack([t_ms, temp_c, current_a]),
           delimiter=",", header="t_ms,temp_c,current_a", comments="", fmt=["%d", "%.3f", "%.3f"])
print(open("heater_log.csv").read().splitlines()[:3])
```

Output:

```
['t_ms,temp_c,current_a', '0,21.006,0.024', '20,20.993,0.006']
```

## Step 1: load a CSV into numpy

```python
import numpy as np

data = np.loadtxt("heater_log.csv", delimiter=",", skiprows=1)
print(data.shape)
t_s = (data[:, 0] - data[0, 0]) / 1000.0
temp_c = data[:, 1]
print(t_s[:3], round(float(temp_c.mean()), 2))
```

Output:

```
(1000, 3)
[0.   0.02 0.04] 23.21
```

- `np.loadtxt` reads a numeric table into a 2-D array: one row per sample, one column per field. `skiprows=1` skips the header row. (If your file has a column that isn't a number, `loadtxt` raises `ValueError`; use `usecols=(...)` to pick only numeric columns.)
- `data[:, 0]` means "every row, column 0": a whole column as a 1-D array.
- **Time in seconds from the start**: subtract the first timestamp, divide by 1000. Plotting raw `t_ms` gives you an x-axis that starts at some arbitrary number like 123450.
- Math on a column applies to every element at once (no loop). That's why your `raw_to_g` from milestone 1.3 must work on arrays.

## Step 2: stacked time series

The standard figure for a sensor log: one subplot per physical quantity, sharing the time axis.

```python
import matplotlib.pyplot as plt
import numpy as np

data = np.loadtxt("heater_log.csv", delimiter=",", skiprows=1)
t_s = (data[:, 0] - data[0, 0]) / 1000.0

fig, (ax_temp, ax_cur) = plt.subplots(2, 1, sharex=True, figsize=(8, 5), layout="constrained")
ax_temp.plot(t_s, data[:, 1], label="heater temperature")
ax_temp.set_ylabel("temperature (°C)")
ax_temp.legend()
ax_temp.grid(True)
ax_cur.plot(t_s, data[:, 2], color="tab:orange", label="heater current")
ax_cur.set_ylabel("current (A)")
ax_cur.set_xlabel("time (s)")
ax_cur.legend()
ax_cur.grid(True)
fig.suptitle("heater_log.csv")
fig.savefig("heater_log.png", dpi=150)
print("saved heater_log.png")
```

What each piece does:

| Call | Why |
|---|---|
| `plt.subplots(2, 1, sharex=True)` | two rows, one column; zooming one subplot zooms the other in time |
| `layout="constrained"` | stops labels from overlapping |
| `set_ylabel("temperature (°C)")` | **every axis gets a quantity and a unit**: a plot without units isn't evidence |
| `label=...` then `legend()` | names each line; essential once a subplot has 3 lines (x, y, z) |
| `fig.savefig(..., dpi=150)` | writes a PNG you can put in a README; save *before* `plt.show()` |

To see the window as well, add `plt.show()` at the end. In VS Code, run the file with the Run button or `python file.py` in the terminal: a window opens and the script waits until you close it.

## Step 3: a log-log plot

Allan deviation (milestone 1.7) is always plotted on log-log axes, because each noise type is a straight line with its own slope there.

```python
import matplotlib.pyplot as plt
import numpy as np

tau = np.logspace(-2, 3, 50)
sigma = 0.005 / np.sqrt(tau) + 0.0004 * np.sqrt(tau / 1000)

fig, ax = plt.subplots(layout="constrained")
ax.loglog(tau, sigma, "o-", markersize=3, label="example curve")
ax.loglog(tau, 0.005 / np.sqrt(tau), "--", label="slope -1/2 reference")
ax.set_xlabel("averaging time τ (s)")
ax.set_ylabel("deviation (°/s)")
ax.grid(True, which="both")
ax.legend()
fig.savefig("loglog.png", dpi=150)
print("saved loglog.png")
```

`np.logspace(-2, 3, 50)` makes 50 points evenly spaced on a log scale from 10^-2 to 10^3. `grid(True, which="both")` draws the minor grid lines too, which you need to read values off a log axis.

## Step 4: a live plot

For a live plot (milestone 1.6), the pattern is: keep the last few seconds of data in fixed-length buffers, and let Matplotlib call an update function about 25 times per second. Each update reads **everything new**, then redraws **once**.

```python
from collections import deque

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

rng = np.random.default_rng(1)
times = deque(maxlen=250)     # the last 5 s at 50 Hz
values = deque(maxlen=250)
state = {"t": 0.0}

fig, ax = plt.subplots()
(line,) = ax.plot([], [], label="fake sensor")
ax.set_ylim(-2, 2)
ax.set_xlabel("time (s)")
ax.set_ylabel("value")
ax.legend(loc="upper left")


def read_new_samples():
    """Stand-in for 'read everything waiting on the serial port'. Returns about 2 samples."""
    out = []
    for _ in range(2):
        state["t"] += 0.02
        out.append((state["t"], np.sin(state["t"]) + 0.1 * rng.standard_normal()))
    return out


def update(frame):
    for t, v in read_new_samples():
        times.append(t)
        values.append(v)
    line.set_data(times, values)
    ax.set_xlim(times[0], max(times[0] + 5, times[-1]))
    return (line,)


anim = FuncAnimation(fig, update, interval=40, cache_frame_data=False)
plt.show()
```

The ideas to carry into your own live plot:

- `deque(maxlen=250)` is a ring buffer: appending to a full one silently drops the oldest item. Memory stays constant no matter how long you run.
- `ax.plot([], [])` creates the line **once**; each update only changes its data with `set_data`. Calling `ax.plot` again in every update creates thousands of lines and slows to a crawl.
- `interval=40` asks for an update every 40 ms (25 per second). Your screen doesn't need 100 updates per second, and drawing is slow. Data comes in at 100 Hz; drawing happens at 25 Hz; the buffer between them absorbs the difference.
- Keep a reference to the animation (`anim = ...`). Without it, Python garbage-collects the animation and nothing moves.
- In your real version, `read_new_samples` reads `port.in_waiting` bytes (or at least 1 with a short timeout), feeds them to your parser, and returns the new samples.

## Common beginner mistakes

- No units on the axes. Every reviewer notices.
- Plotting against the sample index instead of time. A dropped sample then shifts everything after it.
- `plt.show()` before `savefig`: on some setups the saved file is blank, because the figure was closed when you closed the window.
- Re-creating the whole figure in every live update.
- Loading a 3-hour CSV with a Python loop and `csv.reader`. Use `np.loadtxt`; it's much faster.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ValueError: could not convert string to float` in `loadtxt` | The header row wasn't skipped, or a column isn't numeric | `skiprows=1`; `usecols=(...)`. |
| The window never appears | Running in a non-GUI context, or `MPLBACKEND=Agg` is set | Run from a normal terminal; unset `MPLBACKEND`. |
| Saved PNG is blank | `savefig` called after `show` | Save first. |
| Live plot freezes, then jumps | Update too slow, or reading only one sample per update | Read everything waiting; update 20 to 25 times per second. |
| Live plot shows nothing | Axis limits don't include the data | Set `ylim` to your signal range; update `xlim` as time moves. |
| Labels overlap | Default layout | `layout="constrained"`. |
