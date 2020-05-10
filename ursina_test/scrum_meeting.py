from collections import namedtuple
from copy import deepcopy

from ursina import *
from random_image import random_image

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
        {'name':'Mark', 'model': 'untitled', 'image': 'textures/untitled.png'},
        # {'name':'Mark', 'image':'textures/mark.jpg'},
        {'name': 'Pablo', 'image': 'textures/pablo.png'},
        {'name': 'Scott', 'image': 'textures/scott.png'},
        {'name': 'Narinder', 'image': 'textures/narinder.jpg'},
        {'name': 'Iain', 'image': 'textures/iain.png'},
        {'name': 'Darby', 'image': 'textures/darby.png'},
        {'name': 'Anna', 'image': 'textures/anna.jpg'},
        {'name': 'Jannalie', 'image': 'random'},
    ]

    def __init__(self):
        self.current_participant = 0
        self.shuffled_participants = deepcopy(self.ALL_PARTICIPANTS)
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
                         )
        self.set_text_for_current_participant()
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
    # Create a single cube
    Text.default_resolution = 1080 * Text.size
    window.exit_button.visible = False
    scrum_list = ScrumList()
    objects['scrum_list'] = scrum_list
    scrum_list.show_selected_participant()
    return


def input(key):
    print(f'{key=}')
    if key == 'escape':
        print('Bye')
        application.quit()
    elif key == 'scroll up':
        camera.z += 2
    elif key == 'scroll down':
        camera.z -= 2
    elif key == 'space':
        camera.look_at(objects['participant'].origin)
        objects['participant'].rotate_randomly()
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
