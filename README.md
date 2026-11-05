# **Mussels to Muscles** - 22400 Design-build 4: Autonomous devices for controlling and studying living systems

This repository contains the code for the **Mussels to Muscles** DB4 project: an autonomous monitoring system for studying a living mussel system using ESP32-based sensing and an Adafruit IO web interface.

## Repository structure

```text
db4/
├── adafruit/
│   ├── main.py
│   ├── main_offline.py
│   ├── main_remote_control.py
│   ├── publish.py
│   ├── sensor_config.py
│   ├── LTR329.py
│   ├── thermistor.py
│   └── tests/
│       ├── test_double_thermistor.py
│       ├── test_light_sensor.py
│       ├── test_light_sensor_module.py
│       └── test_wifi_scan.py
│
├── adafruit_io_frontend/
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── assets/
│
├── .gitignore
└── README.md
```

## ESP32 firmware

The ESP32 firmware is located in:

```text
adafruit/
```

The main firmware files are:

* `main.py` - ESP32 entry point with local control and telemetry
* `main_offline.py` - offline version of the experiment controller
* `main_remote_control.py` - alternative entry point with dashboard controls
* `sensor_config.py` - feed names, pin numbers, and sampling settings
* `LTR329.py` - light sensor driver
* `thermistor.py` - thermistor reading code

`publish.py` is an older prototype and requires a light sensor driver not included in this repository.

Private credentials are stored locally in:

```text
adafruit/config.py
```

This file must NOT be committed to Git. Use `adafruit/config.example.py` as a template.

## Adafruit IO feeds

The frontend and remote-control firmware use these main feed keys:

```text
temperature1
light
od-water
pwm-duty
```

The web dashboard will show errors until the ESP32 has successfully published data to these feeds.

## Frontend dashboard

The static frontend is located in:

```text
adafruit_io_frontend/
```

## Test scripts

Hardware test scripts are stored in:

```text
adafruit/tests/
```

These are used for checking individual components before running the full system.

## Security note

PLEASE do NOT commit:

```text
adafruit/config.py
```

This file contains WiFi credentials and the Adafruit IO key. The root `.gitignore` should include:

```gitignore
adafruit/config.py
```

## Note

This is a historical course project: the networked firmware uses plaintext MQTT, and hardware safety and calibration have not been revalidated. The dashboard’s optical-density conversion requires further calibration before its values are used for scientific conclusions.
