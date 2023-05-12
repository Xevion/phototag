from abc import ABC
from pathlib import Path
from typing import List, Set

import iptcinfo3


class Tagger(ABC):
    """
    A base class for all Taggers
    """

    def __init__(self, path: Path) -> None:
        self.path = path
        self.__saved = True
        self.__current_tags = set(self.__load())

    @property
    def current_tags(self) -> Set[str]:
        """The current tags in the tagger instance"""
        return self.__current_tags

    @property
    def saved(self) -> bool:
        """Whether the current tags have been saved to the filesystem"""
        return self.__saved

    def reload(self) -> None:
        """
        Reloads the tags from the filesystem. Discards any unsaved changes.
        """
        self.__current_tags = set(self.__load())
        self.__saved = True

    def save(self) -> None:
        """
        Saves the current tags to the filesystem.
        """
        self.save()
        self.__saved = True

    def add(self, tag: str) -> None:
        """
        Adds a tag to the tagger
        :param tag: The tag to add
        """
        self.__current_tags.add(tag)

    def remove(self, tag: str) -> None:
        """
        Removes a tag from the tagger
        :param tag: The tag to remove
        """
        self.__current_tags.remove(tag)

    def clear(self) -> None:
        """
        Clears all current tags
        """
        self.__current_tags.clear()

    def extend(self, tags: List[str]) -> None:
        """
        Extends the current tags with a list of tags
        :param tags: The tags to add
        """
        self.__current_tags.update(tags)

    def __load(self) -> List[str]:
        """
        Filesystem loading implementation.
        """
        raise NotImplementedError()

    def __save(self) -> None:
        """
        Filesystem saving implementation
        """
        raise NotImplementedError()


class IPTCTagger(Tagger):
    def __init__(self, path: Path) -> None:
        super().__init__(path)

        self.iptc = iptcinfo3.IPTCInfo(str(path))

    def __load(self) -> List[str]:
        """
        Loads the tags from the filesystem
        :return: The tags
        """
        return self.iptc['keywords']

    def __save(self) -> None:
        """
        Saves the tags to the filesystem
        """
        self.iptc['keywords'] = list(self.__current_tags)
        self.iptc.save()

# TODO: XMPTagger implementation
