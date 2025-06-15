# ../control_zones/control_zones.py

"""."""

# ==============================================================================
# >> IMPORTS
# ==============================================================================
from collections import defaultdict

from colors import BLUE, Color, RED, WHITE, BLACK
from effects import box
from engines.precache import Model
from filters.players import PlayerIter
from listeners.tick import Repeat
from mathlib import Vector


beam_model = Model("sprites/laser.vmt")
boxes = [
    {
        "point1": "155 -923 448",
        "point2": "527 -1168 522",
    },
    {
        "point1": "846 592 64",
        "point2": "189 751 148",
    },
    {
        "point1": "599 -112 648",
        "point2": "431 -272 732",
    },
]
ALL_PLAYERS = PlayerIter()
color_checks = {
    2: "r",
    3: "b",
}


class ControlZone:

    def __init__(self, point1, point2):
        self.count = 0
        self.has_printed = False
        self.point1 = Vector(*map(float, point1.split()))
        self.point2 = Vector(*map(float, point2.split()))
        self.color = Color(0, 0, 0, 255)


    def display_beam(self):
        if self.count == 30:
            print(self.color)
            self.count = 0
        box(
            recipients=ALL_PLAYERS,
            start=self.point1,
            end=self.point2,
            start_width=40,
            end_width=40,
            color=WHITE if self.color == BLACK else self.color,
            life_time=0.1,
            model=beam_model,
            halo=beam_model,
        )

    def check_for_players(self):
        self.count += 1
        team_players = defaultdict(int)
        for player in PlayerIter("alive"):
            if player.origin.is_within_box(self.point1, self.point2):
                team_players[player.team_index] += 1

        if not team_players:
            return

        if len(team_players) == 2:
            # TODO: write logic to allow for difference vs disable
            return

        team_index = list(team_players)[0]
        player_count = team_players[team_index]
        total_change = max(1, int(512 / 600 * player_count))
        amounts = {
            value: getattr(self.color, value)
            for value in color_checks.values()
        }
        remove_color = color_checks[5 - team_index]
        if not self.has_printed:
            print(team_index)# 2
            print(player_count)# 1
            print(total_change)# 1
            print(amounts)# r: 255, b: 255
            print(remove_color)# r
        if amounts[remove_color]:
            change_amount = min(amounts[remove_color], total_change)
            total_change -= change_amount
            print(f"Removing {remove_color} by {change_amount}")
            setattr(
                self.color,
                remove_color,
                amounts[remove_color] - change_amount,
            )
            if not self.has_printed:
                print(change_amount)
                print(total_change)

        if not total_change:
            if not self.has_printed:
                print(f"Stopped for 1")
                self.has_printed = True
            return

        add_color = color_checks[team_index]
        if amounts[add_color] >= 255:
            if not self.has_printed:
                print(f"Stopped for 2")
                self.has_printed = True
            return

        print(f"Adding {add_color} by {total_change}")
        setattr(
            self.color,
            add_color,
            min(amounts[add_color] + total_change, 255),
        )

control_zones = []
for point in boxes:
    control_zones.append(ControlZone(point["point1"], point["point2"]))


@Repeat
def main():
    for control_zone in control_zones:
        control_zone.check_for_players()
        control_zone.display_beam()

main.start(0.1)
