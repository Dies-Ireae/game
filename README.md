# Dies Irae
## Table of Contents
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Setting Up the Repository](#setting-up-the-repository)
- [Running the Game](#running-the-game)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Requirements
Before setting up Dies Irae, ensure you have the following installed on your system:

- Python 3.9+
- pip (Python package manager)
- Git
- A virtual environment tool such as `venv` or `virtualenv` for Python.


### Setting Up the Repository

Follow these steps to set up the repository:

1. Clone the repository
2. Run the setup command:
   ```bash
   python setup.py
   ```

This will:
- Create a virtual environment in Python.
- Install project dependencies.
- Initialize the database.
- Create a `secret_settings.py` file if it doesn't exist.
- Start the Evennia server.

## Running the Game
If for some reason you need to start or stop the server after running setup.py, or run other evennia commands you can follow the examples below depending on your operating system:

#### Linux/macOS
1. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   evennia <any command>
   ```


#### Windows
1. Activate the virtual environment:
   ```bash
   venv\Scripts\activate
   evennia <any command>
   ```

## Contributing

We welcome contributions to Dies Irae! To contribute:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b my-feature-branch
   ```
3. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Add my awesome feature"
   ```
4. Push your branch to your fork:
   ```bash
   git push origin my-feature-branch
   ```
5. Open a Pull Request to the main repository.