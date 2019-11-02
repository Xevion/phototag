import os
import sys
import rawpy
import imageio
import io
import iptcinfo3
import logging
from PIL import Image
from google.cloud.vision import types
from google.cloud import vision

from . import TEMP_PATH, INPUT_PATH, OUTPUT_PATH
from .xmp import XMPParser


class FileProcessor(object):
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.base, self.ext = os.path.splitext(
            self.file_name)  # fileNAME and fileEXTENSIOn
        # Path to temporary file that will be optimized for upload to Google
        self.temp_file_path = os.path.join(TEMP_PATH, self.base + '.jpeg')
        # Decide whether a XMP file is available
        self.xmp = os.path.join(INPUT_PATH, base + '.xmp')
        self.xmp = self.xmp if os.path.exists(self.xmp) else None
        
    # Optimizes a file using JPEG thumbnailing and compression.
    def _optimize(self, file: str, size: tuple = (512, 512), quality : int = 85, copy : str = None):
        image = Image.open(file)
        image.thumbnail(size, resample=Image.ANTIALIAS)
        if copy:
            image.save(copy, format='jpeg', optimize=True, quality=quality)
        else:
            image.save(file, format='jpeg', optimize=True, quality=quality)

    def optimize(self):
        if self.hasXMP:
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
            print('\tLabels: {}'.format(', '.join(labels)))

            # XMP sidecar file specified, write to it using XML module
            if self.hasXMP:
                logging.info(
                    '\tWriting {} tags to output XMP.'.format(len(labels)))
                parser = XMPParser(os.path.join(INPUT_PATH, self.xmp_name))
                parser.add_keywords(labels)
                # Save the new XMP file
                loggin.debug('Saving to new XMP file.')
                parser.save(os.path.join(OUTPUT_PATH, self.xmp_name))
                logging.debug('Removing old XMP file.')
                os.remove(os.path.join(INPUT_PATH, self.xmp_name))
            # No XMP file is specified, using IPTC tagging
            else:
                logging.info(
                    '\tWriting {} tags to image IPTC'.format(len(labels)))
                info = iptcinfo3.IPTCInfo(
                    os.path.join(INPUT_PATH, self.file_name))
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
