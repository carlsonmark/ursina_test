from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

objects = {}


class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        # texture = Texture(random_image(width=200, height=200, path=Path(application.textures_folder), minimum_count=30))
        super().__init__(
            parent = scene,
            position = position,
            model = 'cube',
            origin = Vec3(0,0,0),
            texture = 'white_cube',
            color = color.color(0, 0, random.uniform(.9, 1.0)),
            highlight_color = color.lime,
        )
        self._rotation_speed = Vec3(0, 0, 0)
        return

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
        objects['voxel'].rotation_speed = Vec3(rot_x, rot_y, rot_z) * 1000
        return

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                self.rotate_randomly()
        return

    def update(self):
        self.rotation_x += time.dt * self._rotation_speed.x
        self.rotation_y += time.dt * self._rotation_speed.y
        self.rotation_z += time.dt * self._rotation_speed.z
        return


def set_debug_text(text: str):
    text_box = objects.get('debug_console', None)
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
    objects['voxel'] = Voxel(position=(0, 0, 0))
    Text.default_resolution = 1080 * Text.size
    window.exit_button.visible = False
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
        camera.look_at(objects['voxel'].origin)
        objects['voxel'].rotate_randomly()
    return


def update():
    text = f'\nCamera position: {camera.position}'
    text += f'\nCamera rotation: {camera.rotation}'
    set_debug_text(text)
    return


def main():
    global player
    init()
    # player = FirstPersonController(
    #     position=Vec3(0, -1, 7),
    #     rotation=Vec3(0, -180, 0)
    # )
    window.size = (640, 480)
    window.borderless = False
    app.run()

