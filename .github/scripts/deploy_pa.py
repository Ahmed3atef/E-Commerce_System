import os
import sys
import time
import requests

# Get configuration from environment variables
USERNAME = os.environ.get('PA_USERNAME')
API_TOKEN = os.environ.get('PA_API_TOKEN')
DOMAIN_NAME = os.environ.get('PA_DOMAIN_NAME')
PROJECT_PATH = os.environ.get('PROJECT_PATH', '')

if not all([USERNAME, API_TOKEN, DOMAIN_NAME, PROJECT_PATH]):
    print("Error: Missing required environment variables.")
    sys.exit(1)

HOST = "www.pythonanywhere.com"
API_BASE = f"https://{HOST}/api/v0/user/{USERNAME}/"

def make_request(method, endpoint, data=None):
    url = API_BASE + endpoint
    headers = {'Authorization': f'Token {API_TOKEN}'}
    try:
        if method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Error {method} {url}: {e}")
        if e.response is not None:
             print(f"Response: {e.response.text}")
        sys.exit(1)

print(f"Starting deployment to {DOMAIN_NAME}...")

# 1. Create a Console
print("Creating bash console...")
resp = make_request('POST', 'consoles/', {'executable': 'bash'})
console_id = resp.json()['id']
print(f"Console {console_id} created.")

# 2. Wait for console to be ready (handle 412 Precondition Failed)
print("Waiting for console to initialize...")
max_init_retries = 20
console_ready = False
for i in range(max_init_retries):
    # Use requests directly to avoid make_request's sys.exit() on error
    url = API_BASE + f'consoles/{console_id}/get_latest_output/'
    headers = {'Authorization': f'Token {API_TOKEN}'}
    resp = requests.get(url, headers=headers)
    
    if resp.status_code == 200:
        print("\nConsole ready.")
        console_ready = True
        break
    elif resp.status_code == 412: # Console not yet started
        print(".", end='', flush=True)
        time.sleep(2)
        continue
    else:
        # Some other error
        print(f"\nError checking console status: {resp.status_code} {resp.text}")
        break

if not console_ready:
    print("\nError: Console failed to initialize. Aborting.")
    # Clean up
    url = API_BASE + f'consoles/{console_id}/'
    headers = {'Authorization': f'Token {API_TOKEN}'}
    requests.delete(url, headers=headers)
    sys.exit(1)

try:
    # 3. Run git pull
    command = f"cd {PROJECT_PATH} && git pull\n"
    print(f"Executing: {command.strip()}")
    make_request('POST', f'consoles/{console_id}/send_input/', {'input': command})
    
    # Wait and fetch output
    print("Waiting for git pull output...")
    # Poll for output for up to 30 seconds
    max_retries = 10
    for i in range(max_retries):
        resp = make_request('GET', f'consoles/{console_id}/get_latest_output/')
        output = resp.json().get('output', '')
        if output:
            print(output, end='')
        time.sleep(3)
    print("\nCommand execution window finished.")

    # 3. Reload Web App
    print(f"Reloading webapp {DOMAIN_NAME}...")
    make_request('POST', f'webapps/{DOMAIN_NAME}/reload/')
    print("Webapp reloaded successfully.")

finally:
    # Cleanup console
    print(f"Deleting console {console_id}...")
    # We accept valid or 404/500 here just to be safe, but make_request exits on error.
    # Finer control:
    url = API_BASE + f'consoles/{console_id}/'
    headers = {'Authorization': f'Token {API_TOKEN}'}
    requests.delete(url, headers=headers)

print("Deployment script finished.")
