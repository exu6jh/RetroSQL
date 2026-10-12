from __future__ import annotations

import csv
from functools import cache
from pathlib import Path

# Takes a folder name and returns the tuple of file paths of all its contents
@cache
def get_filenames(folder: Path) -> tuple[str, ...]:
    return tuple(sorted(path for path in folder.iterdir() if path.is_file()))

def sort_dict(dct: dict, key: int = 0) -> dict:
    return dict(sorted(dct.items(), key=lambda item:item[key]))

def construct_player_dict():
    dct = {}
    with open(Path(__file__).resolve().parent.parent / 'alldata' / 'biodata' / 'biofile.csv', newline='', encoding="utf8") as biofile:
        logreader = csv.reader(biofile)

        for row in logreader:
            dct[row[0]] = f"{row[3]} {row[1]}"
    return dct