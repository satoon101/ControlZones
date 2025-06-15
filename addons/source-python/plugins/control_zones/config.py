# ../control_zones/config.py

"""Creates server configuration and user settings."""

# ==============================================================================
# >> IMPORTS
# ==============================================================================
# Source.Python
from config.manager import ConfigManager

# Plugin
from .info import info
from .strings import CONFIG_STRINGS

# ==============================================================================
# >> ALL DECLARATION
# ==============================================================================
__all__ = (
)


# ==============================================================================
# >> CONFIGURATION
# ==============================================================================
# Create the control_zones.cfg file and execute it upon __exit__
with ConfigManager(info.name, "cz_") as config:
