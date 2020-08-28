"""
process.py

Holds the FileProcessor object, used for working with images in order to label and edit/tag their metadata.
"""

import io
import logging
import os
import shutil
from threading import Thread
from typing import Tuple, AnyStr, Optional, List, Dict

import imageio
import iptcinfo3
import rawpy
from PIL import Image
from google.cloud import vision

from . import TEMP_PATH, INPUT_PATH, RAW_EXTS
from .config import config
from .xmp import XMPParser

log = logging.getLogger("process")


class MasterFileProcessor(object):
    """
    Controls FileProcessor objects in the context of threading according to configuration options.
    """

    def __init__(self, files: List[str], image_count: int, buffer_size: int, single_override: bool):
        """
        Initializes a MasterFileProcessor object.

        :param files: The files each FileProcessor object will shadow.
        :param image_count: The number of files allowed to be running at any time.
        :param buffer_size: The maximum total size of the files allowed to be loaded/running at any time.
        :param single_override: If true, the previous configuration values will disregarded in order to keep at least one FileProcessor running.
        """
        self.files, self.image_count = files, image_count
        self.buffer_size, self.single_override = buffer_size, single_override

        self.waiting: Dict[int, FileProcessor] = {}  # FileProcessors that are ready to process, but are not.
        self.running: Dict[int, Tuple[FileProcessor, Thread]] = {}  #  FileProcessors that are currently being processed in threads.
        self.finished: Dict[int, FileProcessor] = {}  # FileProcessors that have finished processing.

        processors = [FileProcessor(file) for file in files]
        processors.sort(key=lambda fp: fp.size)

        for index, fp in enumerate(processors):
            self.waiting[index] = fp

        self._precheck()

    def _precheck(self) -> None:
        """
        Checks that the MasterFileProcessor can successfully process all files with the current configuration options.

        :except Exception: when the current configuration will be unable to complete based on the current parameters.
        """
        # single_override ensures that the application will always complete, even if slowly, one-by-one
        if not self.single_override:
            # Check that all files are under the set buffer limit
            for key, fp in self.waiting.keys():
                if fp.size > self.buffer_size:
                    raise Exception("Invalid Configuration - the buffer size is too low. Please raise the buffer size "
                                    "or enable single_override.")

            # Check that image_count is at least 1
            if self.image_count <= 0:
                raise Exception("Invalid Configuration - the image_count is too low. Please set it to a positive "
                                "non-zero integer or enable single_override.")

    def load(self) -> None:
        """
        Starts FileProcessor threads, loading zero or more threads simultaneously based on configuration options.
        """

    def _finished(self, key: int) -> None:
        """
        Called when a FileProcessor's thread has finished.

        :param int key: The FileProcessor's integer key in the running array.
        """
        pass

    @property
    def total_active(self) -> int:
        """
        Returns the number of currently running files.

        :return: a integer describing the number of threads currently processing files.
        """
        return len(list(self.running.values()))

    @property
    def total_size(self) -> int:
        """
        Returns the sum of all currently running files in memory, in bytes.

        :return: the total number of bytes the images in the buffer take up on the disk.
        """
        return sum(processor.size for processor in self.running.values())


class FileProcessor(object):
    """
    A FileProcessor object shadows a given file, providing methods for optimizing, labeling
    and tagging Raw (.NEF, .CR2) and Lossy (.JPEG, .PNG) format pictures.

    Acts as a slave to the MasterFileProcessor, but can be controlled individually.
    """

    def __init__(self, file_name: str):
        """
        Initializes a FileProcessor object.

        :param file_name: The file that the FileProcessor object will shadow.
        """

        self.file_name = file_name
        self.base, self.ext = os.path.splitext(self.file_name)
        self.ext = self.ext[1:]  # remove the prepended dot

        # Path to temporary file that will be optimized for upload to Google
        self.temp_file_path = os.path.join(TEMP_PATH, self.base + ".jpeg")

        # Decide whether a XMP file is available
        self.xmp = None
        if self.ext.lower() in RAW_EXTS:  # if the extension is in the RAW extensions array, it might have an XMP (?)
            self.xmp = self.base + ".xmp"
            self.input_xmp = os.path.join(INPUT_PATH, self.xmp)
            if not os.path.exists(self.input_xmp):
                raise Exception("Sidecar file for '{}' does not exist.".format(self.xmp))

    @staticmethod
    def _optimize(file: AnyStr, size: Tuple[int, int] = (512, 512), quality: int = 85,
                  copy: Optional[AnyStr] = None) -> None:
        """
        A special static method for optimizing a JPEG file using thumbnailing and quality reduction/compression.

        :param file: The path of the original file you want to optimize.
        :param size: The width and height of the image you want generated.
        :param quality: The quality of the file you want generated, from 0 to 100.
        :param copy:  The path you want to copy the optimized file to. If not specified, the original file will be overwritten.
        """
        image = Image.open(file)
        image.thumbnail(size, resample=Image.ANTIALIAS)  # Thumbnail the image

        # Copy or overwrite the file while optimizing & applying new quality
        if copy:
            image.save(copy, format="jpeg", optimize=True, quality=quality)
        else:
            image.save(file, format="jpeg", optimize=True, quality=quality)

    def optimize(self) -> None:
        """
        Optimize the file shadowed by this object, supporting RAW files as needed.
        """
        if self.xmp:
            # CPU-Bound task, needs threading or async applied
            rgb = rawpy.imread(os.path.join(INPUT_PATH, self.file_name))
            imageio.imsave(self.temp_file_path, rgb.postprocess())
            rgb.close()
            self._optimize(self.temp_file_path)
        else:
            self._optimize(os.path.join(INPUT_PATH, self.file_name), copy=self.temp_file_path)

    def run(self, client: vision.ImageAnnotatorClient) -> None:
        """
        Optimize, find labels for and tag the file.

        :param client: The ImageAnnotatorClient to be used for interacting with the Google Vision API.
        """

        try:
            self.optimize()  # Optimize the file first before sending to the Google Vision API

            # Open the image, read as bytes, convert to types Image
            image = Image.open(self.temp_file_path)
            bytesIO = io.BytesIO()
            image.save(bytesIO, format="jpeg")
            image.close()
            image = vision.types.Image(content=bytesIO.getvalue())

            # Performs label detection on the image file
            response = client.label_detection(image=image)
            labels = [label.description for label in response.label_annotations]
            log.info("Keywords Identified: {}".format(", ".join(labels)))

            # XMP sidecar file specified, write to it using XML module
            if self.xmp:
                log.info(f"Writing {len(labels)} tags to output XMP.")
                parser = XMPParser(self.input_xmp)
                parser.add_keywords(labels)

                # Generate a temporary XMP file name
                head, tail = os.path.split(self.input_xmp)
                name, ext = os.path.splitext(tail)
                temp_name = os.path.join(head, f'{name} temp{ext}')

                # Finish up processing XMP file
                os.rename(self.input_xmp, temp_name)  # rename the original file
                parser.save(self.input_xmp)  # save the new file
                shutil.copystat(temp_name, self.input_xmp)  # copy file metadata over
                os.remove(temp_name)  # remove the renamed original file
                log.debug("New XMP file saved with original file metadata. Old XMP file removed.")

            # No XMP file is specified, using IPTC tagging
            else:
                log.info("Writing {} tags to image IPTC".format(len(labels)))
                info = iptcinfo3.IPTCInfo(os.path.join(INPUT_PATH, self.file_name))
                info["keywords"].extend(labels)
                info.save()

                # Remove the weird ghost file created by this iptc read/writer.
                os.remove(os.path.join(INPUT_PATH, self.file_name + "~"))

            # Copy dry-run
            # shutil.copy2(os.path.join(INPUT_PATH, self.file_name), os.path.join(OUTPUT_PATH, self.file_name))
            # os.rename(os.path.join(INPUT_PATH, self.file_name), os.path.join(OUTPUT_PATH, self.file_name))
        except:
            raise
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """
        Cleanup function. Removes the temporary file generated.
        """
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)

    @property
    def size(self) -> int:
        """
        Returns the size of the image in bytes that this FileProcessor objet shadows.

        :return: the number of bytes the shadowed image takes up on the disk
        """
        return os.path.getsize(self.file_name)
