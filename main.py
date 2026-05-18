import paho.mqtt.client as mqtt
import socket
import importlib.util
import os
import argparse

PC_NAME = socket.gethostname()
MQTT_TOPIC = "homeassistant-pc-trigger/" + PC_NAME

def parse_args():
    parser = argparse.ArgumentParser(description="MQTT listener for Home Assistant PC triggers")
    parser.add_argument("broker", help="MQTT broker IP address")
    return parser.parse_args()

args = parse_args()
MQTT_BROKER = args.broker

username = os.getenv("HA_INTEGRATION_USER")
password = os.getenv("HA_INTEGRATION_PASS")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    parts = payload.split()
    
    script_name = parts[0]
    script_args = parts[1:] if len(parts) > 1 else []
    
    module_path = os.path.join(os.path.dirname(__file__), f"{script_name}.py")
    
    try:
        spec = importlib.util.spec_from_file_location(script_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'main'):
            module.main(*script_args)
        else:
            print(f"Error: {script_name}.py does not have a main() function")
    except FileNotFoundError:
        print(f"Error: {script_name}.py not found in {os.path.dirname(__file__)}")
    except Exception as e:
        print(f"Error executing {script_name}.py: {e}")


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

if username and password:
    client.username_pw_set(username, password)

client.connect(MQTT_BROKER, 1883, 60)

print("Listening for HA triggers...")
client.loop_forever()