import paho.mqtt.client as mqtt
import socket
import importlib.util
import os
import argparse
import logging
import sys
from pathlib import Path

PC_NAME = socket.gethostname()
MQTT_TOPIC = "homeassistant-pc-trigger/" + PC_NAME

def parse_args():
    parser = argparse.ArgumentParser(description="MQTT listener for Home Assistant PC triggers")
    parser.add_argument("broker", help="MQTT broker IP address")
    parser.add_argument("--logfile", "-l", help="Path to append run logs (will be created)")
    return parser.parse_args()

args = parse_args()
MQTT_BROKER = args.broker

username = os.getenv("HA_INTEGRATION_USER")
password = os.getenv("HA_INTEGRATION_PASS")


def setup_logging(logfile: str | None):
    logger = logging.getLogger("ha_pc_trigger")
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z")

    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # File handler (append mode) if provided
    if logfile:
        path = Path(logfile).expanduser()
        try:
            if not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(path, mode="a", encoding="utf-8")
            fh.setFormatter(fmt)
            logger.addHandler(fh)
        except Exception as e:
            logger.error(f"Could not open logfile {logfile}: {e}")

    return logger

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    parts = payload.split()

    if not parts:
        logger.warning("Received empty payload")
        return

    script_name = parts[0]
    script_args = parts[1:] if len(parts) > 1 else []

    # Log the incoming trigger with timestamp and params
    logger.info("Trigger received: script=%s args=%s payload=%s", script_name, script_args, payload)

    module_path = Path(__file__).parent / f"{script_name}.py"

    try:
        if not module_path.exists():
            logger.error("%s not found in %s", module_path.name, str(module_path.parent))
            return

        spec = importlib.util.spec_from_file_location(script_name, str(module_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, "main"):
            try:
                module.main(*script_args)
                logger.info("Executed %s with args=%s", script_name, script_args)
            except Exception:
                logger.exception("Error while executing %s", script_name)
        else:
            logger.error("%s does not have a main() function", module_path.name)
    except Exception:
        logger.exception("Unexpected error loading %s", module_path)


def on_connect(client, userdata, connect_flags, reason_code, properties):
    if reason_code == 0:
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Authentication required or connection failed: {reason_code}")


def on_disconnect(client, userdata, disconnect_flags, reason_code, properties):
    pass


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    pass
    


client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe


if __name__ == "__main__":
    args = args
    logger = setup_logging(getattr(args, "logfile", None))

    if username and password:
        client.username_pw_set(username, password)

    try:
        client.connect(MQTT_BROKER, 1883, 60)
        logger.info("Listening for HA triggers on %s", MQTT_TOPIC)
        client.loop_forever()
    except Exception:
        logger.exception("MQTT client failed")