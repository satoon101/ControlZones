# ../control_zones/control_zones.py

"""Plugin where players battle to control zones on the map to win."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Python
from collections import defaultdict
from enum import IntEnum

# Source.Python
from colors import BLUE, RED, WHITE
from cvars.tags import sv_tags
from effects import box
from engines.precache import Model
from engines.server import global_vars
from entities.entity import Entity
from events import Event
from filters.players import PlayerIter
from listeners import OnLevelInit
from listeners.tick import Delay, Repeat
from mathlib import Vector
from messages import HudMsg

# Plugin
from .config import map_coordinates, seconds_to_control
from .custom_events import Control_Zone_Captured, Control_Zone_Lost
from .strings import MESSAGE_STRINGS


beam_model = Model("sprites/laser.vmt")
TEAM_COLORS = {
    2: RED,
    3: BLUE,
}
ALL_PLAYERS = PlayerIter()
START_CHANNEL = 6
START_Y_OFFSET = -0.6


# =============================================================================
# >> ENUMS
# =============================================================================
class ControlZoneState(IntEnum):
    NEUTRAL = 0
    GAINING = 1
    CAPTURED = 2
    LOSING = 3


# =============================================================================
# >> CLASSES
# =============================================================================
class ControlZone:

    team_index = None
    last_color = None
    points = 0

    def __init__(self, name, offset, **values):
        self.name = name
        self.state = ControlZoneState.NEUTRAL
        self.point1 = Vector(*map(float, values["point1"].split()))
        self.point2 = Vector(*map(float, values["point2"].split()))
        self.y = START_Y_OFFSET - (0.05 * offset)
        self.channel = START_CHANNEL + offset

    @property
    def enemy_team_index(self):
        return 5 - self.team_index

    @property
    def color(self):
        if self.state is ControlZoneState.NEUTRAL:
            return WHITE

        color = TEAM_COLORS.get(self.team_index, WHITE)
        if self.state is ControlZoneState.CAPTURED:
            return color

        self.last_color = {
            WHITE: color,
            color: WHITE,
        }.get(self.last_color, WHITE)
        return self.last_color

    def send_hudmsg(self, color):
        HudMsg(
            message=MESSAGE_STRINGS["zone_state"],
            color1=color,
            x=1.5,
            y=self.y,
            effect=0,
            fade_in=0,
            fade_out=0,
            hold_time=0.6,
            fx_time=0,
            channel=self.channel,
        ).send(
            name=self.name,
            state=self.state.name.title(),
        )

    def display_beam(self, color):
        box(
            recipients=ALL_PLAYERS,
            start=self.point1,
            end=self.point2,
            start_width=20,
            end_width=20,
            color=color,
            life_time=0.6,
            model=beam_model,
            halo=beam_model,
        )

    def determine_change_in_control(self):
        team_players_in_zone = defaultdict(int)
        for player in PlayerIter("alive"):
            if player.origin.is_within_box(self.point1, self.point2):
                team_players_in_zone[player.team_index] += 1

        max_points = int(seconds_to_control) * 2
        same_count = (
            len(team_players_in_zone) == 2 and
            len(set(team_players_in_zone.values())) == 1
        )
        if same_count or (
            not team_players_in_zone and
            self.state in (ControlZoneState.NEUTRAL, ControlZoneState.CAPTURED)
        ):
            return

        if not team_players_in_zone:
            if self.state is ControlZoneState.GAINING:
                self.state = ControlZoneState.NEUTRAL
                self.points = 0
            if self.state is ControlZoneState.LOSING:
                self.state = ControlZoneState.CAPTURED
                self.points = max_points
            return

        team_index = max(
            team_players_in_zone,
            key=team_players_in_zone.get,
        )
        if self.state is ControlZoneState.NEUTRAL:
            self.state = ControlZoneState.GAINING
            self.team_index = team_index

        points = (
            team_players_in_zone[team_index] -
            team_players_in_zone.get(5 - team_index, 0)
        )
        if team_index == self.team_index:
            if self.state is ControlZoneState.CAPTURED:
                return

            self.points += points
            if self.points >= max_points:
                self.points = max_points
                self.state = ControlZoneState.CAPTURED
                with Control_Zone_Captured() as event:
                    print(f'Firing event: {event.name}')
                    event.team = self.team_index
                    event.zone_name = self.name

            return

        if self.state is ControlZoneState.CAPTURED:
            self.state = ControlZoneState.LOSING

        self.points -= points
        if self.points > 0:
            return

        self.team_index = self.enemy_team_index
        self.points = abs(self.points)
        previous_state = self.state
        self.state = (
            ControlZoneState.NEUTRAL
            if not self.points
            else ControlZoneState.GAINING
        )
        if previous_state is ControlZoneState.LOSING:
            with Control_Zone_Lost() as event:
                event.team = self.enemy_team_index
                event.zone_name = self.name


class ControlZones(dict):
    def __init__(self):
        super().__init__()
        self.repeat = Repeat(self.update_control_zones)

    def clear(self):
        self.repeat.stop()
        super().clear()

    def create_control_zones(self):
        if self or global_vars.map_name is None:
            return

        coordinates = map_coordinates.get(global_vars.map_name)
        if coordinates is None:
            # TODO: raise/warn
            return

        for offset, (name, values) in enumerate(coordinates.items()):
            self[name] = ControlZone(name, offset, **values)

        self.repeat.start(0.5)

    def update_control_zones(self):
        if not self:
            return

        for control_zone in self.values():
            control_zone.determine_change_in_control()
            color = control_zone.color
            control_zone.display_beam(color)
            control_zone.send_hudmsg(color)


control_zones = ControlZones()


# =============================================================================
# >> LOAD & UNLOAD
# =============================================================================
def load():
    sv_tags.add("control_zones")
    control_zones.create_control_zones()


def unload():
    sv_tags.remove("control_zones")


# =============================================================================
# >> LISTENERS
# =============================================================================
@OnLevelInit
def _level_init(map_name):
    control_zones.create_control_zones()


# =============================================================================
# >> GAME EVENTS
# =============================================================================
@Event("control_zone_captured")
def _end_game(game_event):
    for control_zone in control_zones.values():
        if control_zone.state is not ControlZoneState.CAPTURED:
            return
    entity = Entity.find_or_create("game_end")
    entity.end_game()
    Delay(0, control_zones.clear)
