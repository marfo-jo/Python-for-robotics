### Why read this

C++ is the most requested language in robotics job postings, and most production GPS drivers, ROS 2 core packages, and embedded firmware are written in it. You don't have to write C++ yet. The goal here is **reading practice**: you've now written an NMEA parser in Python, so you know what every line below is *for*. Read the C++ with your Python open next to it and match them up.

This is reading material, not a graded exercise, so the whole program is here.

### The program: `nmea_parse.cpp`

It does a cut-down version of your project: classify every line, and print each valid GGA fix in decimal degrees.

```cpp
// nmea_parse.cpp: classify NMEA lines and print GGA fixes (C++17).
#include <cctype>      // std::isxdigit
#include <fstream>     // std::ifstream
#include <iomanip>     // std::setprecision
#include <iostream>    // std::cout, std::cerr
#include <map>         // std::map
#include <sstream>     // std::stringstream
#include <stdexcept>   // std::invalid_argument, std::out_of_range
#include <string>
#include <string_view>
#include <vector>

// Python: line.strip()
std::string strip(const std::string& s) {
    const char* ws = " \t\r\n";
    const auto first = s.find_first_not_of(ws);
    if (first == std::string::npos) {
        return "";                               // all whitespace
    }
    const auto last = s.find_last_not_of(ws);
    return s.substr(first, last - first + 1);
}

// Python: for ch in body: value = value ^ ord(ch)
unsigned int checksum(std::string_view body) {
    unsigned int value = 0;
    for (char ch : body) {
        value ^= static_cast<unsigned char>(ch);
    }
    return value;
}

// Python: text.split(",")
std::vector<std::string> split(const std::string& text, char sep) {
    std::vector<std::string> fields;
    std::stringstream ss(text);
    std::string field;
    while (std::getline(ss, field, sep)) {
        fields.push_back(field);
    }
    // getline drops a trailing empty field ("a,b," gives 2 fields, not 3).
    // Python's split keeps it, and NMEA field positions depend on it.
    if (!text.empty() && text.back() == sep) {
        fields.push_back("");
    }
    return fields;
}

// Python: your classify_line
std::string classify_line(const std::string& raw) {
    const std::string text = strip(raw);
    if (text.empty()) {
        return "blank";
    }
    const auto star = text.find('*');
    if (text[0] != '$' || star == std::string::npos ||
        text.find('*', star + 1) != std::string::npos) {
        return "malformed";                      // no '$', no '*', or two '*'
    }
    const std::string given = text.substr(star + 1);
    if (given.size() != 2 ||
        !std::isxdigit(static_cast<unsigned char>(given[0])) ||
        !std::isxdigit(static_cast<unsigned char>(given[1]))) {
        return "malformed";
    }
    const unsigned int expected = std::stoul(given, nullptr, 16);  // "7c" -> 124
    const std::string_view body(text.data() + 1, star - 1);        // between '$' and '*'
    return checksum(body) == expected ? "valid" : "bad_checksum";
}

// Python: 0 if field == "" else int(field)
int to_int(const std::string& field) {
    if (field.empty()) {
        return 0;
    }
    return std::stoi(field);                     // throws on "abc", like int("abc")
}

// Python: int(text[:digits]) + float(text[digits:]) / 60, negated for S or W
double to_degrees(const std::string& text, std::size_t digits, const std::string& hemi) {
    const double degrees = std::stod(text.substr(0, digits));
    const double minutes = std::stod(text.substr(digits));
    double value = degrees + minutes / 60.0;
    if (hemi == "S" || hemi == "W") {
        value = -value;
    }
    return value;
}

int main(int argc, char* argv[]) {
    const std::string path = (argc > 1) ? argv[1] : "gps_log.txt";
    std::ifstream file(path);                    // Python: with open(path) as f:
    if (!file) {
        std::cerr << "cannot open " << path << "\n";
        return 1;
    }

    std::map<std::string, int> counts;           // Python: a dict of counters
    std::string line;
    int line_no = 0;
    while (std::getline(file, line)) {           // Python: for line in f:
        ++line_no;
        const std::string kind = classify_line(line);
        counts[kind] += 1;                       // a missing key starts at 0
        if (kind != "valid") {
            continue;
        }
        const std::string text = strip(line);
        const std::string body = text.substr(1, text.find('*') - 1);
        const std::vector<std::string> f = split(body, ',');
        // Check the size BEFORE indexing: || stops at the first true test.
        if (f.size() < 8 || f[0].size() != 5 || f[0].substr(2) != "GGA") {
            continue;
        }
        try {
            const int quality = to_int(f[6]);
            const int sats = to_int(f[7]);
            if (quality == 0 || f[2].empty() || f[4].empty()) {
                continue;                        // no fix: nothing to print
            }
            const double lat = to_degrees(f[2], 2, f[3]);
            const double lon = to_degrees(f[4], 3, f[5]);
            std::cout << "line " << line_no << ": " << f[1]
                      << std::fixed << std::setprecision(6)
                      << " lat=" << lat << " lon=" << lon
                      << " q=" << quality << " sats=" << sats << "\n";
        } catch (const std::invalid_argument&) { // Python: except ValueError:
            std::cerr << "line " << line_no << ": bad number\n";
        } catch (const std::out_of_range&) {
            std::cerr << "line " << line_no << ": number too large\n";
        }
    }

    for (const auto& [kind, n] : counts) {       // Python: for kind, n in counts.items():
        std::cout << kind << ": " << n << "\n";
    }
    return 0;
}
```

### Build and run it in the VM

`g++` comes with `build-essential`, which a ROS 2 install already pulls in. Put `nmea_parse.cpp` and a copy of `gps_log.txt` in one folder, then:

```bash
sudo apt install build-essential        # only if g++ is missing
g++ -std=c++17 -Wall -Wextra -O2 -o nmea_parse nmea_parse.cpp
./nmea_parse gps_log.txt
```

`-std=c++17` turns on the C++17 features used here (`std::string_view` and the `[kind, n]` unpacking). `-Wall -Wextra` asks the compiler for every warning: treat each one like a compiler telling you about a bug before you've run anything. Compare the counts it prints at the end with your Python analyzer's `blank`, `malformed`, `bad_checksum`, and `valid`. They should match exactly.

### Line by line: C++ vs your Python

| C++ | Your Python | What's different |
|---|---|---|
| `#include <string>` | (nothing: built in) | C++ pulls in each part of the standard library explicitly, like `import`. |
| `std::string strip(const std::string& s)` | `def strip(s):` | Every parameter and return value has a **declared type**. `const ... &` means "pass a read-only reference, don't copy it". |
| `s.find_first_not_of(" \t\r\n")` | `s.strip()` | No built-in `strip()`: you find the first and last non-whitespace positions and take a `substr`. |
| `std::string::npos` | `-1` from `str.find` | "Not found" is a special huge number, not `-1`. |
| `value ^= static_cast<unsigned char>(ch);` | `value = value ^ ord(ch)` | A `char` already *is* a number in C++, so there's no `ord()`. The cast avoids negative values for bytes above 127. |
| `std::getline(ss, field, ',')` in a `while` | `text.split(",")` | Reads one field at a time. **Trap:** it drops a trailing empty field, so the code adds it back. This is a real bug source when people port NMEA parsers. |
| `std::vector<std::string>` | `list` of `str` | A vector holds one declared type only. `fields.push_back(x)` is `fields.append(x)`. |
| `f[7]` | `fields[7]` | Same indexing, but an out-of-range index is **undefined behavior**, not an `IndexError`. It may crash, or silently return garbage. That's why the code checks `f.size() < 8` before touching `f[0]` or `f[7]`. |
| `std::stoi("08")`, `std::stod("4220.388")` | `int("08")`, `float("4220.388")` | Both throw on bad text. `std::stoi("")` throws `std::invalid_argument`, just like `int("")` raises `ValueError`. So empty fields still need the `to_int` guard. |
| `std::stoul(given, nullptr, 16)` | `int(given, 16)` | Parses hex text. Lowercase `7c` works, just as in Python. |
| `try { ... } catch (const std::invalid_argument&) { ... }` | `try: ... except ValueError: ...` | Same idea, different exception names. |
| `std::map<std::string, int> counts; counts[kind] += 1;` | `counts[kind] = counts.get(kind, 0) + 1` | `[]` on a missing key **creates it with 0**, so no `.get` is needed. (Opposite of Python, where `d[key]` on a missing key raises `KeyError`.) A `std::map` also keeps its keys **sorted**, so the counts print alphabetically. |
| `std::ifstream file(path); if (!file)` | `with open(path) as f:` | No exception on a missing file by default: you check the stream yourself. The file closes automatically when `file` goes out of scope, which is C++'s version of `with`. |
| `std::cout << std::fixed << std::setprecision(6) << lat` | `f"{lat:.6f}"` | Formatting is done with stream manipulators. (C++20 adds `std::format`, much closer to f-strings.) |
| `for (const auto& [kind, n] : counts)` | `for kind, n in counts.items():` | C++17 "structured bindings" are tuple unpacking (lesson 0.7). |

### The same subscriber in rclcpp (reading only)

For comparison with your rclpy node from the robots bridge, here is the heart of the same `/fix` listener in C++. Building it needs a CMake package (`ament_cmake`), which comes in a later module, so just read it:

```cpp
#include <memory>
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/nav_sat_fix.hpp>

class FixListener : public rclcpp::Node {
public:
    FixListener() : Node("fix_listener") {
        sub_ = create_subscription<sensor_msgs::msg::NavSatFix>(
            "fix", 10,
            [this](const sensor_msgs::msg::NavSatFix::SharedPtr msg) {
                RCLCPP_INFO(get_logger(), "lat=%.6f lon=%.6f status=%d",
                            msg->latitude, msg->longitude, msg->status.status);
            });
    }

private:
    rclcpp::Subscription<sensor_msgs::msg::NavSatFix>::SharedPtr sub_;
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<FixListener>());
    rclcpp::shutdown();
    return 0;
}
```

Same three steps as Python: create a node, subscribe to `fix` with a queue depth of 10 and a callback, then spin. `msg->latitude` is C++ for `msg.latitude` (the message arrives as a pointer), and `"%.6f"` is the C-style version of `:.6f`.
