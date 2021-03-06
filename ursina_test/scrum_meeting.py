from collections import namedtuple
from copy import deepcopy
from typing import List

from ursina import *
from random_image import random_image
from cheers import CheerScoreboard, cheers_textures

USE_SLACK_BOT = True
slack_thread = None

app = Ursina()

objects = {}


def set_if_not_exists(d, key, value):
    """
    Set an item in a dictionary if it does not exist.
    """
    if key not in d:
        d[key] = value
    return


class ScrumParticipant(Button):
    def __init__(self, name: str, image: str='random', **kwargs):
        self.participant_name = name
        self.participant_image = image
        set_if_not_exists(kwargs, 'position', Vec3(0, 0, 0))
        set_if_not_exists(kwargs, 'model', 'cube')
        set_if_not_exists(kwargs, 'origin', Vec3(0, 0, 0))
        set_if_not_exists(kwargs, 'texture', None)
        set_if_not_exists(kwargs, 'color', color.color(0, 0, random.uniform(.9, 1.0)))
        kwargs['texture'] = self.which_texture(kwargs['texture'])
        super().__init__(parent=scene, **kwargs)
        # Maximum rotation speed in degrees per second?
        self.max_rotation_speed = 100
        self._rotation_speed = Vec3(0, 0, 0)
        self.rotate_randomly()
        return

    def which_texture(self, possible_texture):
        if possible_texture is not None:
            texture = possible_texture
        elif self.participant_image == 'random':
            texture = Texture(
                random_image(width=200, height=200, path=Path(application.textures_folder), minimum_count=30))
        else:
            texture = Texture(self.participant_image)
        return texture

    @property
    def rotation_speed(self):
        return self._rotation_speed

    @rotation_speed.setter
    def rotation_speed(self, rotation_speed: Vec3):
        self._rotation_speed = rotation_speed
        return

    def rotating(self):
        """
        Get whether it is rotating or not
        """
        return self._rotation_speed != Vec3(0, 0, 0)

    def rotate_randomly(self):
        rot_x = random.random() - 0.5
        rot_y = random.random() - 0.5
        rot_z = random.random() - 0.5
        self.rotation_speed = Vec3(rot_x, rot_y, rot_z) * self.max_rotation_speed
        return

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                scrum_list = objects['scrum_list']
                scrum_list.select_participant('next')
            if key == 'right mouse down':
                scrum_list = objects['scrum_list']
                scrum_list.select_participant('previous')
        return

    def update(self):
        self.rotation_x += time.dt * self._rotation_speed.x
        self.rotation_y += time.dt * self._rotation_speed.y
        self.rotation_z += time.dt * self._rotation_speed.z
        return


class ScrumList(Text):
    ALL_PARTICIPANTS = [
        # {'name': 'Mark Carlson', 'model': 'untitled', 'image': 'textures/untitled.png'},
        # {'name': 'Mark Carlson', 'image': 'textures/mark.jpg'},
        # {'name': 'Mark Carlson', 'image': 'textures/blinking-lego.mp4'},
        {'name': 'Mark Carlson', 'image': 'textures/simpsons-climbing.mp4'},
        # {'name': 'Mark Carlson', 'image':'textures/dan-osmond.mp4'},
        # {'name': 'Neal', 'image':'textures/neal.jpg'},
        {'name': 'Pablo De Biase', 'image': 'textures/pablo.png'},
        {'name': 'Scott Ho', 'image': 'textures/scott.png'},
        {'name': 'Narinder Singh', 'image': 'textures/narinder.jpg'},
        {'name': 'Iain Barkley', 'image': 'textures/iain.png'},
        {'name': 'Darby McGraw', 'image': 'textures/darby.png'},
        # {'name': 'Anna Chaykovska', 'image': 'textures/anna.jpg'},
        # {'name': 'Anna Chaykovska', 'model': 'indoor plant_02', 'image': 'textures/anna.jpg'},
        # {'name': 'Anna Chaykovska', 'model': 'indoor plant_02', 'color': color.green},
        {'name': 'Jannalie Taylor', 'image': 'textures/jannalie.jpg'},
    ]

    def __init__(self):
        self.current_participant = 0
        self.shuffled_participants = deepcopy(self.ALL_PARTICIPANTS)
        self.preload_models()
        random.shuffle(self.shuffled_participants)
        super().__init__(text='',
                         name='scrum_list',
                         position=window.bottom_left,
                         z=-999,
                         eternal=True,
                         origin=(-.5, -.5),
                         # origin=(0, 0),
                         # scale = (.05, .025),
                         color=color.green.tint(-.2),
                         font='VeraMono.ttf'
                         )
        self.set_text_for_current_participant()
        return

    def attendee_names(self) -> List[str]:
        return list(set(
            [p['name'] for p in self.ALL_PARTICIPANTS]
        ))

    def preload_models(self):
        """
        Create .ursinamesh files for all of the models so they load faster next time.
        """
        for d in self.ALL_PARTICIPANTS:
            model = d.get('model', None)
            if model:
                print(f'loading model: {model}')
                load_model(model)

        return

    def select_participant(self, which='next'):
        if which == 'next':
            self.current_participant += 1
        elif which == 'previous':
            self.current_participant -= 1
        else:
            self.current_participant = which
        total = len(self.ALL_PARTICIPANTS)
        if self.current_participant < 0:
            self.current_participant = total - 1
        elif self.current_participant >= total:
            self.current_participant = 0
        self.set_text_for_current_participant()
        self.show_selected_participant()
        return

    def set_text_for_current_participant(self):
        i = 0
        text = ''
        for participant in self.shuffled_participants:
            if i == self.current_participant:
                text += f'*** '
            text += f'{participant["name"]}\n'
            i += 1
        self.text = text
        self.create_background()
        return

    def show_selected_participant(self):
        current_participant_entity = objects.get('participant', None)
        if current_participant_entity:
            destroy(current_participant_entity)
        current_participant = self.shuffled_participants[self.current_participant]
        kwargs = deepcopy(current_participant)
        objects['participant'] = ScrumParticipant(**kwargs)
        return


DEBUG = False


def set_debug_text(text: str):
    text_box = objects.get('debug_console', None)
    if DEBUG:
        if not text_box:
            text_box = Text(
                name='debug_console',
                position=window.top_left,
                z=-999,
                eternal=True,
                origin=(-.5, .5),
                # origin=(0, 0),
                #scale = (.05, .025),
                color=color.red.tint(-.2),
                text=text)
            objects['debug_console'] = text_box
        text_box.text = text
        text_box.create_background()
    return


def init():
    global slack_thread
    # Create a single cube
    Text.default_resolution = 1080 * Text.size
    window.exit_button.visible = False
    scrum_list = ScrumList()
    objects['scrum_list'] = scrum_list
    scrum_list.show_selected_participant()
    if USE_SLACK_BOT:
        from slack_bot import init as slack_bot_init
        from slack_bot import user_info
        slack_bot_init(objects, textures=cheers_textures)
        info = user_info()
        names = scrum_list.attendee_names()
        attendees = {}
        for name in names:
            for username in info.keys():
                if name == info[username]:
                    attendees[info[username]] = username
        cheer_scoreboard = CheerScoreboard(attendees=attendees)
        objects['cheer_scoreboard'] = cheer_scoreboard
    return


def input(key):
    print(f'{key=}')
    if key == 'escape':
        print('Bye')
        if USE_SLACK_BOT:
            from slack_bot import stop
            stop()
        application.quit()
    elif key == 'scroll up':
        camera.z += 2
    elif key == 'scroll down':
        camera.z -= 2
    elif key == 'space':
        camera.look_at(objects['participant'].origin)
        objects['participant'].rotate_randomly()
    elif key == 'g':
        objects['cheer_scoreboard'].give_everyone_points(5)
    elif key == 't':
        # deleteme
        objects['cheer_scoreboard'].transfer_points('Mark', 'Scott', 5)
    elif key == '1':
        objects['cheer_scoreboard'].set_sort_key("cheer_available")
    elif key == '2':
        objects['cheer_scoreboard'].set_sort_key("cheer_given")
    elif key == 'c':
        objects['cheer_scoreboard'].add_cheers(10, 'textures/cheers/star')
    return


def update():
    text = f'Camera position: {camera.position}'
    text += f'\nCamera rotation: {camera.rotation}'
    set_debug_text(text)
    return


def main():
    global player
    window.size = (1024, 768)
    window.borderless = False
    init()
    # player = FirstPersonController(
    #     position=Vec3(0, -1, 7),
    #     rotation=Vec3(0, -180, 0)
    # )
    app.run()

