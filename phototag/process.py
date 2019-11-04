import os
import sys
import rawpy
import imageio
import io
import iptcinfo3
import logging
import string
import random
import shutil
from PIL import Image
from google.cloud.vision import types
from google.cloud import vision

from . import TEMP_PATH, INPUT_PATH, OUTPUT_PATH, RAW_EXTS, LOSSY_EXTS
from .xmp import XMPParser

log = logging.getLogger('process')

class FileProcessor(object):
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.base, self.ext = os.path.splitext(self.file_name)
        self.ext = self.ext[1:]
        # Path to temporary file that will be optimized for upload to Google
        self.temp_file_path = os.path.join(TEMP_PATH, self.base + '.jpeg')
        # Decide whether a XMP file is available
        self.xmp = None
        if self.ext.lower() in RAW_EXTS:
            self.xmp = self.base + '.xmp'
            self.input_xmp = os.path.join(INPUT_PATH, self.xmp)
            if not os.path.exists(self.input_xmp):
                raise Exception('Sidecar file for \'{}\' does not exist.'.format(self.xmp))

    # Optimizes a file using JPEG thumbnailing and compression.
    def _optimize(self, file: str, size: tuple = (512, 512), quality : int = 85, copy : str = None):
        image = Image.open(file)
        image.thumbnail(size, resample=Image.ANTIALIAS)
        if copy:
            image.save(copy, format='jpeg', optimize=True, quality=quality)
        else:
            image.save(file, format='jpeg', optimize=True, quality=quality)

    def optimize(self):
        if self.xmp:
            # Long runn
            rgb = rawpy.imread(os.path.join(INPUT_PATH, self.file_name))
            imageio.imsave(self.temp_file_path, rgb.postprocess())
            rgb.close()
            self._optimize(self.temp_file_path)
        else:
            self._optimize(os.path.join(
                INPUT_PATH, self.file_name), copy=self.temp_file_path)

    def run(self, client: vision.ImageAnnotatorClient):
        try:
            self.optimize()

            # Open the image, read as bytes, convert to types Image
            image = Image.open(self.temp_file_path)
            bytesIO = io.BytesIO()
            image.save(bytesIO, format='jpeg')
            image.close()
            image = vision.types.Image(content=bytesIO.getvalue())

            # Performs label detection on the image file
            response = client.label_detection(image=image)
            labels = [label.description for label in response.label_annotations]
            log.info('Keywords Identified: {}'.format(', '.join(labels)))

            # XMP sidecar file specified, write to it using XML module
            if self.xmp:
                log.info('Writing {} tags to output XMP.'.format(len(labels)))
                parser = XMPParser(self.input_xmp)
                parser.add_keywords(labels)
                # Save the new XMP file
                log.debug('Moving old XMP to temp XMP')
                temp_name = self.input_xmp + ''.join(random.choices(list(string.ascii_letters), k=10))
                os.rename(self.input_xmp, temp_name)
                log.debug('Saving new XMP')
                parser.save(self.input_xmp)
                log.debug('Copying old stats to new XMP')
                shutil.copystat(temp_name, self.input_xmp)
                log.debug('Removing temp file')
                os.remove(temp_name)
            # No XMP file is specified, using IPTC tagging
            else:
                log.info('Writing {} tags to image IPTC'.format(len(labels)))
                info = iptcinfo3.IPTCInfo(os.path.join(INPUT_PATH, self.file_name))
                info['keywords'].extend(labels)
                info.save()
                # Remove the weird ghsot file created by this iptc read/writer.
                os.remove(os.path.join(INPUT_PATH, self.file_name + '~'))
            
            # Copy dry-run
            # shutil.copy2(os.path.join(INPUT_PATH, self.file_name), os.path.join(OUTPUT_PATH, self.file_name))
            # os.rename(os.path.join(INPUT_PATH, self.file_name), os.path.join(OUTPUT_PATH, self.file_name))
        except:
            self._cleanup()
            raise
        self._cleanup()

    # Remove the temporary file (if it exists)
    def _cleanup(self):
        if os.path.exists(self.temp_file_path):
            os.remove(self.temp_file_path)
