from pathlib import Path
from random import choice
from string import ascii_lowercase
from typing import List, Callable

from phototag.helpers import walk

letter: Callable[[], str] = lambda: choice(ascii_lowercase)
extension: Callable[[], str] = lambda: choice(['jpeg', 'jpg', 'png'])
file: Callable[[], str] = lambda: f"{letter()}.{extension()}"


def test_walk(tmp_path: Path):
    files: List[Path] = [tmp_path / file(), tmp_path / file()]

    current_dir: Path = tmp_path
    sub_dir_counts: List[int] = [2, 4, 2]
    for file_count in sub_dir_counts:
        current_dir = current_dir / letter()
        current_dir.mkdir()

        for _ in range(file_count):
            path = current_dir / file()
            files.append(path)
            path.touch()

    assert len(list(walk(tmp_path))) == sum(sub_dir_counts), "All files"
    assert len(list(walk(tmp_path, depth=1))) == sum(sub_dir_counts[:1]), "Depth 1"
    assert len(list(walk(tmp_path, depth=2))) == sum(sub_dir_counts[:2]), "Depth 2"
    assert len(list(walk(tmp_path, depth=3))) == sum(sub_dir_counts[:3]), "Depth 3"

    return files
