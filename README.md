# Mussels to Muscles — DTU 22400 Design Build 4

ESP32/MicroPython experiment controllers and an Adafruit IO browser dashboard. Firmware variants have different behavior: choose deliberately and bench-test the selected variant before operation.

## Firmware modes

| Entry point | Network | Control and measurements | Status |
|---|---|---|---|
| `adafruit/main.py` | Wi-Fi, MQTT publish | Local PI cooling, pump and LTR329 readings; no dashboard commands | Experiment mode; device entry point |
| `adafruit/main_offline.py` | None | Local PI cooling, pump and LTR329 readings | Offline alternative; deploy as `main.py` |
| `adafruit/main_remote_control.py` | Wi-Fi, MQTT subscribe and publish | Remote enable, setpoint, test parameters and reset; PI cooling and pump | Remote alternative; deploy as `main.py` |
| `adafruit/publish.py` | Wi-Fi and MQTT | Older relay/hysteresis prototype with a different feed contract | Legacy; imports `tcs34725`, absent from this tree |

`pi_controller_real.py` is a legacy prototype importing an absent `calibration` module. `adafruit/tests/` contains hardware diagnostics, not desktop tests. The notebook, scan outputs, CSVs and plots are experiment/calibration material; retain original data and pin/lookup constants.

Copy `adafruit/config.example.py` to `config.py` on the device and fill it privately. Do not commit the real file. Firmware requires an ESP32 MicroPython build with `network`, `machine`, `utime`, and (for network modes) `umqtt.simple`, plus the local sensor/display drivers. Runtime and MQTT library versions are not recorded in this repository; capture them and device installation details before reproducing or changing a deployment. Dashboard is static HTML/CSS/JavaScript and calls Adafruit IO over HTTPS.

## Feed contract

The remote mode publishes `temperature1` (degrees Celsius), `pwm-duty` (percent), `light` (LTR329 raw CH0 counts), `od-water` (a dimensionless estimate), and `elapsed-test-s` (seconds). It subscribes to `setpoint-temp`, `system-enable`, `test-number`, `test-duration-s`, and `system-reset`. `main.py` publishes temperature, PWM, and raw light but does not consume remote controls. Legacy `publish.py` uses other names in `sensor_config.py`; do not assume those are this dashboard's contract. Control feed displays show the latest cloud value, not a device acknowledgement.

Remote firmware computes `max(0, log10(blank / CH0))` for `od-water`; `OD_BLANK_CH0` falls back to `OD_BLANK_LUX = 100.0`, which is not established as a calibrated CH0 reference. Dashboard `app.js` then applies `-0.000307 * value + 1545.2` to `od-water`, and recording/export use that transformed value. The physical quantity and units of that second formula are not established. Do not interpret it as validated OD or cell concentration. The owner must identify the raw calibration dataset, blank measurement and intended formula input/output before changing the conversion or reporting calibrated values.

Logs now use numbered filenames per session. Back them up before storage fills; the filename allocation assumes one firmware process writes a directory at a time.

## Network and device safety

The networked variants currently use plaintext MQTT on port 1883, exposing the Adafruit IO key and commands to network observers. Do not use them on an untrusted network. Before implementing TLS, identify the deployed MicroPython build and `umqtt.simple` version, verify their certificate and hostname validation APIs, provision a trusted CA and hostname, and test trusted, untrusted, expired, and wrong-host certificates. Fail closed rather than falling back to plaintext. Rotate any key that may have crossed an observable network and update devices and browser settings.

DNS, TCP/MQTT connection and driver calls are not proven to have bounded duration; the socket timeout is set after connection. The control loop can stall with its last output active. Define a communication-failure policy independently for the pump and cooler for each experiment, including a maximum duration, local emergency stop, and independent thermal/fluid safeguards. Do not assume that one shutdown policy fits every setup. Sensor fault paths attempt to turn outputs off; pump cleanup can only run when Python regains control. Remote mode holds PI integration after a detected missed interval; a blocked network call can still prevent timely control. Local and offline modes need their own timing policy review. MQTT controls do not yet have freshness tokens or device acknowledgements.

## Calibration and verification

The calibration notebook displays the computed R² without the former 0.01 label offset. The affected saved plot was restored from the version before that offset; the calculation and printed R² are unchanged. Confirm previously shared figures and `run_plot.png` against the original data before relying on them. The separate PNG's provenance remains unverified.

The desktop checks use stubs and do not validate MicroPython APIs or physical hardware:

```sh
python -m unittest discover -s tests -p 'test_*.py'
node tests/test_dashboard.js
```

On a safe bench, verify GPIO startup and shutdown, watchdogs, timing, Wi-Fi and broker loss, DNS/TCP hangs, failed subscriptions, malformed and replayed commands, sensor faults, reset/power loss, storage exhaustion, PI response, and the calibration against reference measurements.
