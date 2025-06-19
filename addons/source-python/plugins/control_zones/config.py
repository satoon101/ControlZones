# ../control_zones/config.py

"""Creates server configuration and user settings."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from config.manager import ConfigManager
from paths import CFG_PATH

# Site-package
from configobj import ConfigObj

# Plugin
from .info import info
from .strings import CONFIG_STRINGS

# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = (
    "map_coordinates",
    "seconds_to_control",
)


# =============================================================================
# >> CONFIGURATION
# =============================================================================
# Create the control_zones.cfg file and execute it upon __exit__
with ConfigManager(f"{info.name}/config", "cz_") as config:
    seconds_to_control = config.cvar(
        name="seconds_to_control",
        default=10,
        description=CONFIG_STRINGS["seconds_to_control"],
    )

_map_coordinates_file = CFG_PATH / info.name / "map_coordinates.ini"
map_coordinates = ConfigObj(_map_coordinates_file)
if not map_coordinates:
    map_coordinates["gg_aim_ag_texture5-l"] = {
        "South": {
            "point1": "155 -923 448",
            "point2": "527 -1168 522",
        },
        "Mid": {
            "point1": "846 592 64",
            "point2": "189 751 148",
        },
        "North": {
            "point1": "599 -112 648",
            "point2": "431 -272 732",
        },
    }
    map_coordinates.write()
