# ../control_zones/custom_events.py

"""Leveling based events."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Source.Python
from events.custom import CustomEvent
from events.resource import ResourceFile
from events.variable import ShortVariable, StringVariable

# Plugin
from .info import info

# =============================================================================
# >> ALL DECLARATION
# =============================================================================
__all__ = (
    "Control_Zone_Captured",
    "Control_Zone_Lost",
)


# =============================================================================
# >> CLASSES
# =============================================================================
# ruff: noqa: N801
class Control_Zone_Lost(CustomEvent):
    """Called when a team loses control of a control zone."""

    team = ShortVariable("The index of the team who lost control.")
    zone_name = StringVariable("The name of the control zone.")


class Control_Zone_Captured(CustomEvent):
    """Called when a team gains control of a control zone."""

    team = ShortVariable("The index of the team who gained control.")
    zone_name = StringVariable("The name of the control zone.")


# =============================================================================
# >> RESOURCE FILE
# =============================================================================
resource_file = ResourceFile(info.name, Control_Zone_Captured, Control_Zone_Lost)
resource_file.write()
resource_file.load_events()
