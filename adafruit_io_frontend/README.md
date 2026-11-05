# Adafruit IO dashboard

Open `index.html`, enter the Adafruit IO username and key, and connect. Feed settings, refresh interval and limits can be adjusted in the settings panel. Saving settings omits the key unless **Remember the AIO key** is checked. On load, a key stored by an older version without explicit opt-in is removed and must be entered again. A key intentionally remembered is accessible to scripts and users of that browser profile; use Clear to remove saved settings. Snapshots and JSON exports exclude the AIO key.

The remote firmware contract is described in the [project README](../README.md). A displayed control feed is not an acknowledgement that the ESP32 received or applied it. `main.py` does not subscribe to dashboard controls; remote mode requires deploying `main_remote_control.py` as the device entry point and creating the listed feeds.

Start/Stop records the points loaded by successful polls during the browser session. Failed polls, responses reaching the configured history limit, and stopping during a poll are recorded as possible gaps in session JSON; errors and finite API history mean recordings are not guaranteed complete. CSV exports contain samples, not gap metadata: retain the JSON for gap review. CSV text cells beginning with spreadsheet formula characters are prefixed with an apostrophe; numeric measurements retain their values. Browser localStorage is device/profile storage, not a backup.

The `od-water` dashboard transformation has unresolved calibration units; see the project README before using those readings or exports for scientific conclusions. Raw experimental data and calibration constants have not been changed.
