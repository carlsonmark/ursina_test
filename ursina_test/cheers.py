import json
from shutil import copy2
from ursina import *
from typing import Dict, Any, List

# Where cheer data is stored
cheer_data_filename = 'cheer.json'


def load_cheer_data() -> Dict[str, Any]:
    """
    Load cheer data from the file
    """
    cheer_data = json.load(open(cheer_data_filename, 'r'))
    return cheer_data


def save_cheer_data(cheer_data: Dict):
    # Back up the file first
    copy2(cheer_data_filename, f'{cheer_data_filename}.bak')
    json.dump(cheer_data, open(cheer_data_filename, 'w+'), indent=2)
    return


class CheerScoreboard(Text):
    def __init__(self, attendees: Dict[str,str]):
        self._sort_key = 'cheer_available'
        self._cheer_data = load_cheer_data()
        for name in attendees.keys():
            username = attendees[name]
            self.add_attendee(username, name)
        super().__init__(text='',
                         name='cheer',
                         position=window.bottom_right,
                         z=-999,
                         eternal=True,
                         origin=(.5, -.5),
                         # scale = (.05, .025),
                         color=color.white.tint(-.2),
                         font='VeraMono.ttf'
                         )
        self.update_cheer_text()
        return

    def set_sort_key(self, sort_key: str):
        self._sort_key = sort_key
        self.update_cheer_text()
        return

    def add_attendee(self, username, name: str):
        if not username in self._cheer_data:
            self._cheer_data[username] = {
                "cheer_available": 0,
                "cheer_given": 0,
                "name": name
            }
        return

    def give_everyone_points(self, points):
        """
        Give everyone points, without updating the "Given" stat
        :param points: The number of points to give
        """
        for attendee in self._cheer_data:
            self._cheer_data[attendee]['cheer_available'] += points
        self.update_cheer_text()
        save_cheer_data(self._cheer_data)
        return

    def transfer_points(self, name_from: str, name_to: str, points: int):
        """
        Transfer points from one attendee to another
        :param name_from: Who to transfer the points from
        :param name_to: Who to transfer the points to
        :param points: The number of points to transfer
        """
        attendee_from = self._cheer_data[name_from]
        attendee_to = self._cheer_data[name_to]
        from_points = attendee_from['cheer_available']
        from_points -= points
        from_points = max(0, from_points)
        transferred = attendee_from['cheer_available'] - from_points
        attendee_from['cheer_available'] = from_points
        attendee_from['cheer_given'] += transferred
        attendee_to['cheer_available'] += transferred
        self.update_cheer_text()
        save_cheer_data(self._cheer_data)
        return

    def update_cheer_text(self):
        """
        Update the cheer text
        :param sort_key: Which cheer_data key to sort by
        """
        order = reversed(sorted(self._cheer_data,
                                key=lambda item: self._cheer_data[item][self._sort_key]))
        text = 'Name   Points   Given\n'
        text += '-----+--------+------\n'
        for username in order:
            participant = self._cheer_data[username]
            text += f'{participant["name"]} | {participant["cheer_available"]:6} | {participant["cheer_given"]:5}\n'
        self.text = text
        self.create_background()
        return
