from pathlib import Path
from random import choice
from string import ascii_lowercase
from typing import List, Callable, Tuple

import pytest

from phototag.helpers import walk

letter: Callable[[], str] = lambda: choice(ascii_lowercase)
extension: Callable[[], str] = lambda: choice(['jpeg', 'jpg', 'png'])
file: Callable[[], str] = lambda: f"{letter()}.{extension()}"


@pytest.fixture()
def tmp_walkable(tmp_path: Path):
    """
    Creates a directory structure that can be walked
    """
    current_dir: Path = tmp_path
    sub_dir_counts: List[int] = [i * 2 for i in range(5)]

    results: List[List[Path]] = []
    for index, file_count in enumerate(sub_dir_counts):
        files: List[Path] = [current_dir / file() for _ in range(file_count)]
        for path in files:
            path.touch()

        results.append(files)

        # Create next subdirectory
        if index < len(sub_dir_counts) - 1:
            current_dir = current_dir / letter()
            current_dir.mkdir()

    return tmp_path, results


def test_walk(tmp_walkable: Tuple[Path, List[List[Path]]]):
    root: Path = tmp_walkable[0]
    counts: List[int] = list(map(len, tmp_walkable[1]))

    assert len(list(walk(root))) == sum(counts), "All files"
    assert len(list(walk(root, depth=1))) == sum(counts[:1]), "Depth 1"
    assert len(list(walk(root, depth=2))) == sum(counts[:2]), "Depth 2"
    assert len(list(walk(root, depth=3))) == sum(counts[:3]), "Depth 3"
