# Home Assistant PC Trigger

Small MQTT listener that runs local Python scripts on demand from Home Assistant or any MQTT publisher.

## How it works

The app listens on the topic:

`homeassistant-pc-trigger/<hostname>`

When a message arrives, the first word of the payload is treated as the script name and the rest of the words are passed as arguments to that script’s `main()` function.

Examples:

- `hyprland-switch-workspace` → runs `hyprland-switch-workspace.py`
- `hyprland-switch-workspace 1` → runs `hyprland-switch-workspace.py` with argument `1`

## Requirements

- Python 3
- `paho-mqtt`
- An MQTT broker
- Optional: `hyprctl` if you want to use `hyprland-switch-workspace.py`

Install the Python dependency:

```bash
pip install paho-mqtt
```

## Authentication

MQTT credentials are read from environment variables:

- `HA_INTEGRATION_USER`
- `HA_INTEGRATION_PASS`

If your broker allows anonymous access, you can skip these.

Example:

```bash
export HA_INTEGRATION_USER=hugopc
export HA_INTEGRATION_PASS=3305
```

## Run

Start the listener with the MQTT broker IP:

```bash
python main.py 192.168.1.111
```

Optional logfile:

```bash
python main.py 192.168.1.111 --logfile ./ha-trigger.log
```
## Adding scripts

Place a Python file next to `main.py` and make sure it exposes a `main()` function.

Example script:

```python
def main(*args):
    print(args)
```

## Included script

`hyprland-switch-workspace.py` switches to a Hyprland workspace using the first payload argument:

```text
hyprland-switch-workspace 1
hyprland-switch-workspace gaming
```

## MQTT payload examples

Publish to the topic for your machine:

```text
homeassistant-pc-trigger/<your-hostname>
```

Payload examples:

```text
hyprland-switch-workspace 1
hyprland-switch-workspace gaming
```

## Notes

- The script name must match the `.py` filename.
- Additional payload words are forwarded as positional arguments.
- Errors from the script are printed to the console and, if configured, appended to the logfile.
