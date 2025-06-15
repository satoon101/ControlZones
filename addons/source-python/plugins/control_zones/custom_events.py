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
    "My_Event",
)


# =============================================================================
# >> CLASSES
# =============================================================================
# ruff: noqa: N801
class My_Event(CustomEvent):
    """Called when a player levels up."""

    userid = ShortVariable("The userid of player")
    name = StringVariable("The name of the player")


# =============================================================================
# >> RESOURCE FILE
# =============================================================================
resource_file = ResourceFile(info.name, My_Event)
resource_file.write()
resource_file.load_events()
