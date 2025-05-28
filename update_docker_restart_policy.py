import subprocess
import json

def get_all_container_ids():
    try:
        result = subprocess.run(['docker', 'ps', '-a', '-q'], capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error getting container IDs: {e}")
        return []

def get_container_restart_policy(container_id):
    try:
        result = subprocess.run(['docker', 'inspect', container_id], capture_output=True, text=True, check=True)
        container_info = json.loads(result.stdout)[0]
        return container_info['HostConfig']['RestartPolicy']['Name']
    except subprocess.CalledProcessError as e:
        print(f"Error inspecting container {container_id}: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON for container {container_id}")
        return None

def update_container_restart_policy(container_id, policy):
    try:
        subprocess.run(['docker', 'update', '--restart', policy, container_id], check=True)
        print(f"Updated restart policy for container {container_id} to '{policy}'")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating restart policy for container {container_id}: {e}")
        return False

def main():
    container_ids = get_all_container_ids()
    if not container_ids:
        print("No Docker containers found.")
        return

    for container_id in container_ids:
        policy = get_container_restart_policy(container_id)
        if policy and policy not in ["always", "unless-stopped"]:
            print(f"Container {container_id} has restart policy '{policy}'. Changing to 'unless-stopped'.")
            update_container_restart_policy(container_id, "unless-stopped")
        elif policy:
            print(f"Container {container_id} has restart policy '{policy}'. No change needed.")
        else:
            print(f"Could not determine restart policy for container {container_id}. Skipping.")

if __name__ == "__main__":
    main()