import ast
import pathlib
import types
import unittest
from unittest.mock import Mock

ROOT = pathlib.Path(__file__).resolve().parents[1]

def functions(path, names, env):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    selected = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert len(selected) == len(names)
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), env)
    return env

class FirmwareTests(unittest.TestCase):
    def setUp(self):
        self.env = functions("adafruit/main_remote_control.py", ["as_text", "as_bool", "command_number"], {})

    def test_boolean_validation(self):
        self.assertTrue(self.env["as_bool"](b"ON"))
        self.assertFalse(self.env["as_bool"]("off"))
        for value in ("junk", "", "2"):
            with self.assertRaises(ValueError): self.env["as_bool"](value)

    def test_numeric_validation(self):
        parse = self.env["command_number"]
        self.assertEqual(parse("18.5", 10, 30), 18.5)
        self.assertEqual(parse("10", 1, 30, True), 10)
        for value in ("nan", "inf", "-inf", "bad", "31"):
            with self.assertRaises(ValueError): parse(value, 10, 30)
        with self.assertRaises(ValueError): parse("1.5", 1, 30, True)

    def test_reconnect_none_respects_backoff(self):
        clock = types.SimpleNamespace(ticks_ms=lambda: 100, ticks_diff=lambda a,b:a-b, ticks_add=lambda a,b:a+b)
        reconnect = Mock(return_value=False)
        env = functions("adafruit/main_remote_control.py", ["check_controls"], {"utime":clock,"client":None,"_try_reconnect":reconnect,"_pub_pause_until_ms":None,"RECONNECT_BACKOFF_S":30})
        env["check_controls"](); env["check_controls"]()
        self.assertEqual(reconnect.call_count, 1)
        self.assertEqual(env["_pub_pause_until_ms"], 30100)

    def test_subscription_failure_never_reports_ready(self):
        client = Mock()
        client.subscribe.side_effect = OSError("failed")
        env = {"client":None,"base":None,"_pub_pause_until_ms":None,"MQTTClient":Mock(return_value=client), "cfg":types.SimpleNamespace(MQTT_CLIENT_ID="test"),"AIO_USER":"test","AIO_KEY":"placeholder", "on_message":lambda *x:None,"control_feeds":lambda:("a","b"),"time":types.SimpleNamespace(sleep=lambda x:None),"wifi_connect":lambda:None,"gc":types.SimpleNamespace(collect=lambda:None)}
        functions("adafruit/main_remote_control.py", ["mqtt_connect"], env)
        with self.assertRaises(OSError): env["mqtt_connect"]()
        self.assertIsNone(env["client"])
        self.assertEqual(client.disconnect.call_count, 5)

    def test_pump_off_on_exception(self):
        pump = Mock()
        env={"state":{"system_enabled":True}, "pump":pump, "time":types.SimpleNamespace(time=lambda:0), "screen":lambda *x:None, "wait_with_controls":Mock(side_effect=RuntimeError("fault"))}
        functions("adafruit/main_remote_control.py", ["pump_and_measure"], env)
        with self.assertRaises(RuntimeError): env["pump_and_measure"](1,None)
        self.assertEqual(pump.value.call_args_list[-1].args, (0,))

    def test_log_names_avoid_existing(self):
        env=functions("adafruit/main.py", ["next_log_path"], {})
        from unittest.mock import patch
        with patch("os.listdir", return_value=["temp_pwm_log_1.csv", "temp_pwm_log_2.csv"]):
            self.assertEqual(env["next_log_path"]("temp_pwm_log.csv"), "temp_pwm_log_3.csv")

    def test_missed_cycle_holds_integral(self):
        env=functions("adafruit/main_remote_control.py", ["pi_step"], {"_integral":2, "CONTROL_PERIOD_MS":1000, "state":{"setpoint_temp":17}, "cfg":types.SimpleNamespace(Kp=0.08,Ki=0.002)})
        env["pi_step"](18, 0)
        self.assertEqual(env["_integral"], 2)
        env["pi_step"](18, 1)
        self.assertEqual(env["_integral"], 3)

if __name__ == "__main__": unittest.main()
