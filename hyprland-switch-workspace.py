import subprocess


def main(*args):
    if not args:
        print("Error: workspace name required")
        return
    
    workspace_name = args[0]
    
    try:
        subprocess.run(["hyprctl", "dispatch", "workspace", workspace_name], check=True)
        print(f"Switched to workspace: {workspace_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error switching workspace: {e}")
    except FileNotFoundError:
        print("Error: hyprctl not found. Make sure Hyprland is installed.")
