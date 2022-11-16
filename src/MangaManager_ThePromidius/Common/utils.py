import os
import re
import sys
from io import BytesIO
from pathlib import Path
from typing import IO

from PIL import Image

from src.MangaManager_ThePromidius.Common.naturalsorter import natsort_key_with_path_support

# Patterns for picking cover
IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif', 'webp')
cover_r1 = '^!*0+.[a-z]+$'
cover_r2 = '.*cover.*.[a-z]+$'
covers_patterns = [cover_r1, cover_r2]
COVER_PATTERN = re.compile(f"(?i)({'|'.join(covers_patterns)})")
cover_r3_alt = '^!*0+1\\.[a-z]+$'
ALT_COVER_PATTERN = re.compile(f"(?i)({'|'.join([cover_r3_alt])})")
IS_IMAGE_PATTERN = re.compile(rf"(?i).*.(?:{'|'.join(IMAGE_EXTENSIONS)})$")


def obtain_cover_filename(file_list) -> str:
    """
    Helper function to find a cover file based on a list of filenames
    :param file_list:
    :return:
    """
    cover = None
    # Cover stuff
    possible_covers = [filename for filename in file_list
                       if IS_IMAGE_PATTERN.findall(filename) and COVER_PATTERN.findall(filename)]
    if possible_covers:
        cover = possible_covers[0]
        return cover
    # Try to get 0001
    possible_covers = [filename for filename in file_list if ALT_COVER_PATTERN.findall(filename)]
    if possible_covers:
        cover = possible_covers[0]
        return cover
    # Resource back to first filename available that is a cover
    list_image_files = (filename for filename in file_list if IS_IMAGE_PATTERN.findall(filename))
    cover = sorted(list_image_files, key=natsort_key_with_path_support, reverse=False)
    if cover:
        cover = cover[0]
        return cover


webp_supported_formats = (".png", ".jpeg", ".jpg")


def getNewWebpFormatName(currentName: str) -> str:
    filename, file_format = os.path.splitext(currentName)
    if filename.endswith("."):
        filename = filename.strip(".")
    return filename + ".webp"


def convertToWebp(image_bytes_to_convert: IO[bytes]) -> bytes:
    """
    Converts the provided image to webp and returns the converted image bytes
    :param image_bytes_to_convert: The image that has to be converted
    :return:
    """
    # TODO: Bulletproof image passed not image
    image = Image.open(image_bytes_to_convert).convert()
    # print(image.size, image.mode, len(image.getdata()))
    converted_image = BytesIO()

    image.save(converted_image, format="webp")
    image.close()
    return converted_image.getvalue()


def get_platform():
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
    }

    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]


class ShowPathTreeAsDict:
    """Builds a tree like structure out of a list of paths"""
    def __init__(self, base_path, paths: list):

        new_path_dict = {"subfolders": [],
                         "files": [],
                         "current": Path(base_path)}
        self.new_path_dict = new_path_dict
        for path in paths:

            self._recurse(new_path_dict, Path(path).parts)
        ...

    def _recurse(self,parent_dic: dict, breaked_subpath):

        if len(breaked_subpath) == 0:
            return
        if len(breaked_subpath) == 1:
            # parent_dic[breaked_subpath[0]] = None
            parent_dic["files"].append(breaked_subpath[0])
            self.on_file(parent_dic,breaked_subpath[0])
            return

        key, *new_chain = breaked_subpath
        if key == "\\":
            key = "root"
        if key not in parent_dic:
            parent_dic[key] = {"subfolders": [], "files": [], "current": Path(parent_dic.get("current"), key)}
            parent_dic["subfolders"].append(key)
            # parent_dic["current"] = Path(parent_dic.get("current"),key)
            self.on_subfolder(parent_dic,key)
        self._recurse(parent_dic[key], new_chain)
        return

    def get(self):
        return self.new_path_dict

    def on_file(self, parent_dict: dict, breaked_subpath):
        ...

    def on_subfolder(self, parent_dict: dict, subfolder):
        ...



