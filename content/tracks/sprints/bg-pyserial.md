**About 20 minutes, plus 10 minutes trying it.** Just enough pyserial for Sprint 1 milestone 1.3. Module S lesson S.2 covers it in depth later.

## What pyserial is

`pyserial` is the Python library that opens a serial port (on Windows, a `COM` port; on Linux, `/dev/ttyACM0` or `/dev/ttyUSB0`) and lets you read and write **bytes**. The Uno's USB connection shows up as a serial port, so everything your firmware sends with `Serial.print` or `Serial.write` arrives through pyserial.

It's already installed in the course env (version 3.5). The package is called `pyserial`, but you import it as `serial`:

```powershell
conda activate robotics-course
python -c "import serial; print(serial.__version__)"
```

If that prints `ModuleNotFoundError`, you're not in the conda env (see the troubleshooting table).

## Step 1: find the port

```powershell
python -m serial.tools.list_ports -v
```

prints every port with a description, for example:

```
COM3
    desc: Arduino Uno (COM3)
    hwid: USB VID:PID=2341:0043 SER=...
```

`2341` is Arduino's USB vendor ID. A clone Uno with a CH340 USB chip shows `1A86:7523` and a description like `USB-SERIAL CH340`. The COM number can change when you plug into a different USB socket, so check it rather than memorizing it.

## Step 2: open it, the right way

```python
import serial

with serial.Serial("COM3", 115200, timeout=1.0) as port:
    ...   # use the port here; it's closed automatically when the block ends
```

The three arguments that matter:

| Argument | Meaning | Get it wrong and... |
|---|---|---|
| port name | `"COM3"` on Windows | `FileNotFoundError` inside a `SerialException` |
| baud rate | must match `Serial.begin(...)` in the firmware | you receive garbage bytes, or nothing that decodes |
| `timeout` | seconds to wait in a read before giving up | `None` waits **forever** (your script hangs if the board stops); `0` never waits |

Use a `with` block. If your script crashes without closing the port, Windows keeps it locked until the Python process exits, and the next upload from the Arduino IDE fails with "port busy."

**One owner at a time.** On Windows only one program can have a COM port open. If the Arduino Serial Monitor is open, pyserial gets `PermissionError(13, 'Access is denied.')`. Close the monitor first, and close your script before uploading new firmware.

### Opening the port resets the Uno

When pyserial opens the port, it toggles the **DTR** line, and the Uno's board design turns that into a reset. So right after you open it:

1. there's about 1.5 to 2 seconds of silence while the bootloader runs, then
2. your sketch's `setup()` runs and its startup lines arrive, and
3. anything that was in the input buffer from before is stale.

Handle it: wait about 2 s after opening, then call `port.reset_input_buffer()` to throw away anything stale. (Your firmware's startup `#` lines arrive after the reset, so you may want to wait for the header line instead of sleeping a fixed time. That's a design choice for your logger.)

## Step 3: read

| Call | Returns | Use it for |
|---|---|---|
| `port.readline()` | `bytes` up to and **including** `b"\n"`, or whatever arrived before the timeout | text protocols (1.2 and 1.3) |
| `port.read(n)` | up to `n` bytes (fewer if the timeout expires) | binary protocols (1.4) |
| `port.in_waiting` | number of bytes already received and waiting | reading "everything available" without blocking |
| `port.reset_input_buffer()` | nothing | throwing away stale data |

Everything you read is **`bytes`**, not `str`. A line from your firmware looks like `b'123450,312,-88,16290,-1544,-21,13,-6\r\n'`: note the `b` prefix and the `\r\n` that `Serial.println` adds.

### Try it with no hardware: the loopback port

pyserial has a built-in fake port, `loop://`, where everything you write comes straight back. It's perfect for learning, and for tests. Run this:

```python
import serial

with serial.serial_for_url("loop://", baudrate=115200, timeout=0.5) as port:
    port.write(b"# hello from a fake device\r\n")
    port.write(b"21.5,OK\r\n")
    port.write(b"half a li")          # no newline: like a line cut off by the timeout
    for _ in range(3):
        raw = port.readline()
        print(repr(raw))
    print(repr(port.readline()))
```

Output:

```
b'# hello from a fake device\r\n'
b'21.5,OK\r\n'
b'half a li'
b''
```

Read that output carefully, because it shows the three things a reader must handle:

1. a complete line ends with `b"\r\n"`,
2. a **partial** line (no newline) comes back when the timeout expires, and
3. an **empty** `b''` means "the timeout expired and nothing arrived."

## Step 4: bytes to text

```python
raw = b"21.5,OK\r\n"
text = raw.decode("ascii").strip()
print(repr(text))          # '21.5,OK'
print(text.split(","))     # ['21.5', 'OK']
```

`decode` turns bytes into a `str`; `strip` removes the `\r\n`. At the **wrong baud rate**, the bytes you receive aren't valid text, and `decode("ascii")` raises `UnicodeDecodeError`. On a live link that's normal, not exceptional: catch it (or pass `errors="replace"`) and count the line as bad. Never let one noisy line crash a logger.

## Step 5: write

```python
port.write(b"PWM 120\n")           # bytes
port.write("PWM 120\n".encode())   # the same, built from a str
```

`write` only accepts bytes. You'll use this in Sprint 2 to send commands to the motor rig.

## Common beginner mistakes

- `timeout=None` (the default!), then wondering why the script hangs forever when the board is unplugged.
- Comparing `raw == "OK"`: `bytes` never equals `str`. Decode first, or compare with `b"OK"`.
- Forgetting the reset on open, and parsing the half-line that was in the buffer as real data.
- Keeping the Serial Monitor open while running the script (or vice versa).
- Using `readline()` on a binary stream (milestone 1.4): `0x0A` is just a byte value in binary data, not the end of anything.
- Opening and closing the port inside the loop. Every open resets the Uno.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `SerialException: could not open port 'COM3': PermissionError(13, 'Access is denied.')` | Port open in another program (Serial Monitor, another script, a crashed script still running) | Close it. In Task Manager, end stray `python.exe` processes. |
| `could not open port 'COM3': FileNotFoundError` | Wrong COM number, or the board is unplugged | `python -m serial.tools.list_ports -v` |
| `ModuleNotFoundError: No module named 'serial'` | Not in the conda env, or VS Code is using another Python | `conda activate robotics-course`; in VS Code, Ctrl+Shift+P > "Python: Select Interpreter". |
| `AttributeError: module 'serial' has no attribute 'Serial'` | The wrong package called `serial` is installed, or your own file is named `serial.py` | Rename your file. Check `python -m pip show pyserial`. |
| Reads return `b''` forever | Firmware not sending, wrong port, or the board is stuck in reset | Check with the Serial Monitor (then close it). |
| Garbage bytes, `UnicodeDecodeError` | Baud mismatch | Match `Serial.begin(...)`. |
| Data stops after a few minutes | Your script falls behind and the OS buffer overflows, or the laptop slept | Read faster (don't print every line); change power settings. |
