#!/usr/bin/env python3
# coding: utf-8

"""Extracts files from ~/.minecraft/assets/objects."""

import json
import os
import shutil
import sys
from pathlib import Path

UNPACKED = 'unpacked_minecraft_assets'


def main():
    # find .minecraft directory
    platform = sys.platform
    home = Path("~").expanduser()
    minecraft_path = None
    if platform == 'win32':
        minecraft_path = Path(os.getenv('APPDATA'))/'.minecraft'
    elif platform in ('linux', 'cygwin'):
        minecraft_path = home/'.minecraft'
    elif platform == 'darwin':
        minecraft_path = home/'Library'/'Application Support'/'minecraft'

    # check if we found .minecraft directory
    if minecraft_path is None:
        print(f'System "{sys.platform}" is not supported', file=sys.stderr)
        return 1

    # check if .minecraft directory exists
    if not minecraft_path.exists():
        print(f"Can't find {minecraft_path.absolute()}", file=sys.stderr)
        return 1

    # now we have access to indexes and objects
    indexes_path = minecraft_path/'assets'/'indexes'
    objects_path = minecraft_path/'assets'/'objects'

    # check if they exists
    for directory in (indexes_path, objects_path):
        if not directory.exists():
            print(f"Can't find {directory}", file=sys.stderr)
            return 1

    # determine what versions are downloaded by launcher
    versions = [f.stem for f in indexes_path.iterdir() if f.suffix == '.json']
    if not versions:
        print(f"There's no available versions in {indexes_path}",
              file=sys.stderr)
        return 1

    # ask user for version to process
    print("Available versions:")
    for number, version in enumerate(versions):
        print(f"{number}:\t{version}")
    answer = input("Choose version to unpack: ")
    if not answer.isdigit() or int(answer) not in range(len(versions)):
        print(f'"{answer}" is not a valid number', file=sys.stderr)
        return 1
    chosen_version = versions[int(answer)]

    # read objects from json
    with open(indexes_path/Path(chosen_version + ".json"), 'r') as fobj:
        data = json.load(fobj)
    objects = data.get("objects", dict())
    objects = {info['hash']: file_path for file_path, info in objects.items()}

    # prepare to unpack
    destination = Path(UNPACKED)/chosen_version
    os.makedirs(destination, exist_ok=True)

    # unpack
    for hashstring, file in objects.items():
        # `sys.stdout.write()` prints much faster than `print()`
        sys.stdout.write(f"{hashstring}: {file}\n")
        os.makedirs(destination/Path(file).parent, exist_ok=True)
        shutil.copy(objects_path/hashstring[:2]/hashstring, destination/file)

    print(f"\n{len(objects)} files extracted to {destination.absolute()}")


if __name__ == "__main__":
    sys.exit(main())
