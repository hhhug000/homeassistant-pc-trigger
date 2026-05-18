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

MQTT_BROKER = parse_args().broker

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Trigger received with payload: {payload}")
    
    module_path = os.path.join(os.path.dirname(__file__), f"{payload}.py")
    
    try:
        spec = importlib.util.spec_from_file_location(payload, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, 'main'):
            module.main()
        else:
            print(f"Error: {payload}.py does not have a main() function")
    except FileNotFoundError:
        print(f"Error: {payload}.py not found in {os.path.dirname(__file__)}")
    except Exception as e:
        print(f"Error executing {payload}.py: {e}")
    


client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.subscribe(MQTT_TOPIC)

print("Listening for HA triggers...")
client.loop_forever()