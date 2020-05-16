import json
from pathlib import Path
from shutil import copy2
from ursina import *
from typing import Dict, Any, Optional, List

# Where cheer data is stored
cheer_data_filename = 'cheer.json'
# All of the "cheers"
cheers = []


def _cheers_textures() -> List[str]:
    globbed = Path('textures/cheers').glob('*')
    textures = [p.stem for p in globbed]
    return textures


cheers_textures = _cheers_textures()


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


class Cheer(Entity):
    def __init__(self, position, scale, texture, duration=10):
        self._duration = duration
        self._initial_scale = Vec3(scale)
        self._expiry_time = time.monotonic() + duration
        rotation_scale = 100
        self._rotation_speed = Vec3(random.random() * rotation_scale,
                                    random.random() * rotation_scale,
                                    random.random() * rotation_scale)
        super().__init__(
            model='cube',
            position=position,
            scale=scale,
            texture=texture
        )
        destroy(self, duration)
        return

    def update(self):
        # Slowly fade the entity out
        self.set_scale_for_remaining_time()
        # Jitter around a bit
        self.move_jittery()
        # Rotate
        self.rotate()
        return

    def set_scale_for_remaining_time(self):
        remaining = self._expiry_time - time.monotonic()
        scale = self._initial_scale * (remaining / self._duration)
        self.scale = scale
        return

    def move_jittery(self):
        move_per_second = 1
        x = random.random() * move_per_second - move_per_second / 2
        y = random.random() * move_per_second - move_per_second / 2
        z = random.random() * move_per_second - move_per_second / 2
        self.position = self.position + Vec3(x, y, z) * time.dt
        return

    def rotate(self):
        self.rotation += self._rotation_speed * time.dt
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

    def transfer_points(self, name_from: str, name_to: str, points: int, texture: Optional[str]):
        """
        Transfer points from one attendee to another
        :param name_from: Who to transfer the points from
        :param name_to: Who to transfer the points to
        :param points: The number of points to transfer
        :param texture: The texture to use
        """
        attendee_from = self._cheer_data[name_from]
        attendee_to = self._cheer_data[name_to]
        from_points = attendee_from['cheer_available']
        from_points -= points
        from_points = max(0, from_points)
        transferred = attendee_from['cheer_available'] - from_points
        attendee_from['cheer_available'] = from_points
        if not name_from == name_to:
            attendee_from['cheer_given'] += transferred
        attendee_to['cheer_available'] += transferred
        self.update_cheer_text(name_from=attendee_from['name'], name_to=attendee_to['name'])
        save_cheer_data(self._cheer_data)
        if not texture or texture not in cheers_textures:
            texture = 'star'
        self.add_cheers(count=points, texture=f'textures/cheers/{texture}')
        return

    def add_cheers(self, count: int, texture: str):
        for i in range(min(50, count)):
            max_pos = 2
            position = (random.random() * max_pos - max_pos / 2,
                        random.random() * max_pos - max_pos / 2,
                        -2)
            max_scale = .2
            random_scale = random.random() * max_scale - max_scale
            scale = Vec3(random_scale, random_scale, random_scale, )
            e = Cheer(position=position, scale=scale, texture=texture, duration=10)
            cheers.append(e)
        return

    def update_cheer_text(self, name_from=None, name_to=None):
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
            participant_name = participant['name']
            if name_from == name_to and name_from == participant_name:
                color = 'yellow'
            elif name_from == participant_name:
                color = 'red'
            elif name_to == participant_name:
                color = 'green'
            else:
                color = 'white'
            text += f'<{color}>{participant["name"]}<white> | {participant["cheer_available"]:6} | {participant["cheer_given"]:5}\n'
        self.text = text
        self.create_background()
        return
