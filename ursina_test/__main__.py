from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

from random_image import random_image

app = Ursina()


class Voxel(Button):
    def __init__(self, position=(0,0,0)):
        texture = Texture(random_image(width=200, height=200, path=Path(application.textures_folder)))
        super().__init__(
            parent = scene,
            position = position,
            model = 'cube',
            origin_y = .5,
            texture = texture,
            color = color.color(0, 0, random.uniform(.9, 1.0)),
            highlight_color = color.lime,
        )
        return

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                voxel = Voxel(position=self.position + mouse.normal)

            if key == 'right mouse down':
                destroy(self)
        return


for z in range(8):
    for x in range(8):
        voxel = Voxel(position=(x,0,z))


def input(key):
    print(f'{key=}')
    if key == 'escape':
        print('Bye')
        application.quit()
    return


player = FirstPersonController()
app.run()
