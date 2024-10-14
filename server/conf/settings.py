r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *
from evennia.contrib.base_systems import color_markups
import os

ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
######################################################################
# Evennia base server config
######################################################################
SERVERNAME = "Dies Irae"

TELNET_PORTS = [4201]  
WEBSERVER_PORTS = [(4200, 4005)] 
WEBSOCKET_CLIENT_PORT = 4202
EVENNIA_ADMIN=False
LOCK_FUNC_MODULES = [
    "evennia.locks.lockfuncs",
    "world.wod20th.locks", 
]
SITE_ID = 2

MAX_CHARACTERS_PER_ACCOUNT = 5

COLOR_ANSI_EXTRA_MAP = color_markups.MUX_COLOR_ANSI_EXTRA_MAP
COLOR_XTERM256_EXTRA_FG = color_markups.MUX_COLOR_XTERM256_EXTRA_FG
COLOR_XTERM256_EXTRA_BG = color_markups.MUX_COLOR_XTERM256_EXTRA_BG
COLOR_XTERM256_EXTRA_GFG = color_markups.MUX_COLOR_XTERM256_EXTRA_GFG
COLOR_XTERM256_EXTRA_GBG = color_markups.MUX_COLOR_XTERM256_EXTRA_GBG
COLOR_ANSI_XTERM256_BRIGHT_BG_EXTRA_MAP = color_markups.MUX_COLOR_ANSI_XTERM256_BRIGHT_BG_EXTRA_MAP

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'diesiraemu.com']
CSRF_TRUSTED_ORIGINS = ['http://localhost:4005', 'http://localhost:4000', 'https://diesiraemu.com']

INSTALLED_APPS += ["world.wod20th"]  # Add your app to the list of installed apps
BASE_ROOM_TYPECLASS = "typeclasses.rooms.RoomParent"
  # Change 8001 to your desired websocket port
######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(GAME_DIR, 'evennia.db3'),
    }
}

# Maximum number of accounts that can be created
MAX_ACCOUNTS = 10000  # Adjust this number as needed

# Maximum number of characters per account
MAX_CHARACTERS_PER_ACCOUNT = 5  # Adjust this number as needed
