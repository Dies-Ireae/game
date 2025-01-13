import os
import sys
import subprocess
import venv
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent
VENV_DIR = BASE_DIR / "venv"
REQUIREMENTS_FILE = BASE_DIR / "requirements.txt"
SECRET_SETTINGS_FILE = BASE_DIR / "server/conf/secret_settings.py"

# Helper functions
def run_command(command, cwd=None):
    """Run a shell command."""
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"Error: Command '{command}' failed with return code {result.returncode}")
        sys.exit(result.returncode)

def ensure_venv():
    """Ensure the virtual environment exists and is activated."""
    if not VENV_DIR.exists():
        print("Creating virtual environment...")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)
    
    # Activate the virtual environment
    activate_script = VENV_DIR / "bin/activate"
    if os.name == "nt":
        activate_script = VENV_DIR / "Scripts/activate"

    if "VIRTUAL_ENV" not in os.environ:
        print("Activating virtual environment...")
        activate_command = f"source {activate_script}" if os.name != "nt" else str(activate_script)
        os.environ["VIRTUAL_ENV"] = str(VENV_DIR)
        os.environ["PATH"] = f"{VENV_DIR / 'bin'}:{os.environ['PATH']}"

    print("Virtual environment is ready.")

def install_requirements():
    """Install or update dependencies from requirements.txt."""
    if REQUIREMENTS_FILE.exists():
        print("Installing requirements...")
        run_command(f"pip install -r {REQUIREMENTS_FILE}")
    else:
        print("No requirements.txt file found.")

def run_migrations():
    """Run Evennia migrations."""
    print("Running Evennia migrations...")
    run_command("evennia migrate")

def generate_secret_settings():
    """Generate a secret_settings.py file if it doesn't exist."""
    if not SECRET_SETTINGS_FILE.exists():
        print("Generating secret_settings.py...")
        SECRET_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        secret_key = os.urandom(24).hex()
        with open(SECRET_SETTINGS_FILE, "w") as f:
            f.write(f"SECRET_KEY = '{secret_key}'\n")
    else:
        print("secret_settings.py already exists.")

def start_server():
    """Start the Evennia server."""
    print("Starting Evennia server...")
    run_command("evennia start")

# Main bootstrap function
def main():
    print("Bootstrapping Evennia project...")
    ensure_venv()
    install_requirements()
    run_migrations()
    generate_secret_settings()
    start_server()

if __name__ == "__main__":
    main()
