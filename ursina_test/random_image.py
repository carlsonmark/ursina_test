#
# Get a random image (downloading some if needed)
#

from pathlib import Path
import urllib.request
from random import sample
from typing import List


def ensure_enough_random_images(width: int, height: int, count:int, path:Path) -> List[Path]:
    """
    Make sure there are enough random images available
    :param width: The width of the image, in pixels
    :param height: The height of the image, in pixels
    :param count: The number of images to make available
    :param path: The path containing the images
    """
    full_path = path.joinpath('random', f'{width}', f'{height}')
    if not full_path.exists():
        full_path.mkdir(parents=True, exist_ok=True)
    files = list(full_path.glob('*'))
    existing = len(files)
    to_get = count - existing
    print(f'Need to get {to_get} files')
    if to_get > 0:
        for i in range(to_get):
            urllib.request.urlretrieve(f'https://picsum.photos/{width}/{height}',
                                       str(full_path.joinpath(f'{existing + i}.jpg')))
    return list(full_path.glob('*'))


def random_image(width: int, height: int, path:Path, minimum_count: int=20) -> Path:
    """
    Get the name of a random image file
    :param width: The width of the image, in pixels
    :param height: The height of the image, in pixels
    :param path: The base path containing the images
    :param minimum_count:
    :return:
    """
    files = ensure_enough_random_images(width, height, minimum_count, path)
    return sample(files, 1)[0]
