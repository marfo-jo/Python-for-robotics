### The same job, on a real robot

Everything you just built (strip, validate the checksum, split, convert ddmm.mmmm, skip bad lines) is exactly what a ROS 2 GPS driver does. On a robot you rarely write that driver yourself: you run the standard one, and it **publishes** each good fix as a `sensor_msgs/msg/NavSatFix` message on the `/fix` topic. Every other node (localization, logging, a map display) just **subscribes** to `/fix` and never touches NMEA text again.

Think of it like a PLC input card: the card does the signal conditioning and debouncing once, and the ladder logic just reads a clean bit. The driver is the input card, and `/fix` is the clean bit.

```
GPS receiver --UART/USB--> nmea_serial_driver --/fix (NavSatFix)--> your node
   ($GPGGA...*54)           (checksum, parse,                       (logs lat/lon,
                             ddmm -> degrees)                         status)
```

Do this in your **Ubuntu 22.04 VM with ROS 2 Humble**. Every command below goes in a VM terminal. Run `source /opt/ros/humble/setup.bash` first in every new terminal (or add it to `~/.bashrc` once).

### (a) Install and run the standard driver

```bash
sudo apt update
sudo apt install ros-humble-nmea-navsat-driver
```

If you have a USB GPS (any u-blox or similar puck), plug it in and pass it through to the VM (VirtualBox: *Devices → USB*; VMware: *VM → Removable Devices*). Then find its port and give yourself permission to use serial ports:

```bash
ls /dev/ttyUSB* /dev/ttyACM*          # usually /dev/ttyUSB0 or /dev/ttyACM0
sudo usermod -aG dialout $USER        # then log out and back in (once)
```

Run the driver, setting the port and baud rate as ROS **parameters**:

```bash
ros2 run nmea_navsat_driver nmea_serial_driver --ros-args -p port:=/dev/ttyUSB0 -p baud:=9600
```

The driver's default baud is 4800 (the old NMEA standard), but most modern receivers ship at 9600. Wrong baud looks exactly like it did on your Arduino serial monitor: garbage, or nothing. Here, it shows up as checksum warnings or a silent `/fix` topic.

Check it in a second terminal:

```bash
ros2 topic list                # you should see /fix (plus /vel and /time_reference)
ros2 topic echo /fix           # one message per fix
ros2 topic hz /fix             # about 1 Hz for most receivers
```

Two things you'll recognize from this module, inside the driver's own Python source (`nmea_navsat_driver/parser.py` and `driver.py`, worth reading on GitHub):

- It has a `check_nmea_checksum` function that does the same XOR loop as lesson 0.4 and drops sentences that fail. That's your `bad_checksum` bucket.
- It maps the GGA fix-quality number to a `NavSatStatus` value with a **dict lookup**, exactly like lesson 0.8: quality 0 means no fix, 1 is a plain GPS fix, 2 is a differential (SBAS) fix, and 4/5 are RTK fixes.

### (b) Your own subscriber node

Create a workspace and a Python package. `--node-name` makes the node file and registers it, so `ros2 run` can find it:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python --dependencies rclpy sensor_msgs --node-name fix_listener gps_listener
```

That gives you this layout:

```
~/ros2_ws/
  src/
    gps_listener/
      package.xml                 # declares the rclpy and sensor_msgs dependencies
      setup.py                    # entry point: fix_listener = gps_listener.fix_listener:main
      setup.cfg
      resource/gps_listener
      gps_listener/
        __init__.py
        fix_listener.py           # <-- replace this file's contents
      test/
```

Open `~/ros2_ws/src/gps_listener/gps_listener/fix_listener.py` and replace everything in it with:

```python
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix, NavSatStatus

# Same idea as your fix_quality_counts: a dict from a status number to a name.
STATUS_NAMES = {
    NavSatStatus.STATUS_NO_FIX: "NO_FIX",      # -1
    NavSatStatus.STATUS_FIX: "FIX",            #  0
    NavSatStatus.STATUS_SBAS_FIX: "SBAS_FIX",  #  1
    NavSatStatus.STATUS_GBAS_FIX: "GBAS_FIX",  #  2
}


class FixListener(Node):
    def __init__(self):
        super().__init__("fix_listener")
        self.count = 0
        # topic name, callback, queue depth (how many messages to buffer)
        self.sub = self.create_subscription(NavSatFix, "fix", self.on_fix, 10)
        self.get_logger().info("Listening on /fix")

    def on_fix(self, msg):
        """Called once for every NavSatFix message that arrives."""
        self.count += 1
        code = msg.status.status
        name = STATUS_NAMES.get(code, f"UNKNOWN({code})")
        if code == NavSatStatus.STATUS_NO_FIX:
            self.get_logger().warn(f"#{self.count}: no fix yet")
            return
        self.get_logger().info(
            f"#{self.count}: lat={msg.latitude:.6f} lon={msg.longitude:.6f} "
            f"alt={msg.altitude:.1f} m status={name}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = FixListener()
    try:
        rclpy.spin(node)            # wait for messages; calls on_fix for each one
    except (KeyboardInterrupt, ExternalShutdownException):
        pass                        # Ctrl+C: stop cleanly
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
```

The `class` lines are new (classes come in Module 1). For now, read it as a template: `__init__` runs once at startup, and `on_fix` runs every time a message arrives. Everything inside `on_fix` is Module 0: a dict `.get` with a default, an `if` with an early `return`, and f-strings with `:.6f`. Notice the latitude is already in **decimal degrees** with a **sign** (negative for west): the driver did your lesson 0.9 conversion for you.

Build, source, and run:

```bash
cd ~/ros2_ws
colcon build --packages-select gps_listener
source install/setup.bash        # in EVERY terminal where you want to run your node
ros2 run gps_listener fix_listener
```

If `ros2 run` says *No executable found*, you either forgot `source install/setup.bash` in that terminal or the build failed (scroll up in the `colcon build` output).

### (c) Test without hardware

No GPS? Publish a fake fix by hand. With `fix_listener` running, in a second terminal (after sourcing ROS):

```bash
ros2 topic pub -r 1 /fix sensor_msgs/msg/NavSatFix \
  "{header: {frame_id: gps}, status: {status: 0, service: 1}, latitude: 42.3398, longitude: -71.0892, altitude: 12.3}"
```

`-r 1` publishes once per second, like a real receiver. Your node should log `lat=42.339800 lon=-71.089200 alt=12.3 m status=FIX` every second. Stop it with Ctrl+C, then try a no-fix message (use `--once` to send just one):

```bash
ros2 topic pub --once /fix sensor_msgs/msg/NavSatFix "{status: {status: -1}}"
```

You should see the `no fix yet` warning. That's the ROS version of your cold-start test.

**Optional: feed it real NMEA text.** The same package has a `nmea_topic_driver` that parses sentences published on the `nmea_sentence` topic instead of a serial port. Run your listener in one terminal, the driver in a second, and publish one of the sentences from `gps_log.txt` in a third:

```bash
ros2 run nmea_navsat_driver nmea_topic_driver
```

```bash
ros2 topic pub --once /nmea_sentence nmea_msgs/msg/Sentence \
  '{header: {frame_id: gps}, sentence: "$GPGGA,140000.00,4220.38800,N,07105.35200,W,1,06,1.37,12.3,M,-33.1,M,,*54"}'
```

Note the **single quotes** around the whole message: inside double quotes, bash would treat `$GPGGA` as a variable and replace it with nothing. Now change one digit of the latitude without fixing the checksum and publish again: the driver rejects it and your node sees nothing, exactly like your `bad_checksum` bucket. (If nothing arrives even for a good sentence, run `ros2 topic list` while the driver is running to check the topic name in your version.)

### (d) Humble now, Jazzy over winter break

Your node code above runs **unchanged** on both. What changes:

| | Humble (now) | Jazzy (winter break) |
|---|---|---|
| Ubuntu | 22.04 | 24.04 (Jazzy doesn't install on 22.04) |
| Python | 3.10 | 3.12 |
| Install | `ros-humble-nmea-navsat-driver` | `ros-jazzy-nmea-navsat-driver` (confirm with `apt search ros-jazzy-nmea`) |
| Source | `/opt/ros/humble/setup.bash` | `/opt/ros/jazzy/setup.bash` |
| Support ends | May 2027 | May 2029 |

- **Never source both distros in one terminal**, and don't reuse a workspace's `build/`, `install/`, and `log/` folders across distros. After switching, delete those three folders and run `colcon build` again.
- **pip is locked down on Ubuntu 24.04.** `pip install something` into the system Python fails with `externally-managed-environment`. Use the apt package (`sudo apt install python3-<name>`) or a virtual environment. On 22.04 it still works, but it's a bad habit there too.
- **Ctrl+C shutdown** behaves slightly differently between rclpy versions; on newer ones `spin` can raise `ExternalShutdownException` instead of `KeyboardInterrupt`. That's why the node catches both and only calls `rclpy.shutdown()` if ROS is still running.
- `colcon build` may print a `SetuptoolsDeprecationWarning` on either distro. It's harmless for `ament_python` packages; your node still builds.
