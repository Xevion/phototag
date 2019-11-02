import os
import sys
import rawpy
import imageio
import io
import iptcinfo3
from PIL import Image
from google.cloud.vision import types
from google.cloud import vision

from . import TEMP_PATH, INPUT_PATH, OUTPUT_PATH
from .xmp import XMPParser

class FileProcessor(object):
    def __init__(self, file_name, xmp_name=None):
        self.file_name, self.xmp_name = file_name, xmp_name
        self.base, self.ext = os.path.splitext(self.file_name)
        self.temp_file_path = os.path.join(TEMP_PATH, self.base + '.jpeg')

    def rawOptimize(self):
        rgb = rawpy.imread(os.path.join(INPUT_PATH, self.file_name))
        imageio.imsave(temp_file_path, rgb.postprocess())
        rgb.close()

        # Information on file sizes
        print("Raw Size: {} {}".format(*_size(os.path.join(INPUT_PATH, self.file_name))), end=' | ')
        print("Resave Size: {} {}".format(*_size(temp_file_path)), end=' | ')
        pre = os.path.getsize(temp_file_path)
        _optimize(temp_file_path)
        post = os.path.getsize(temp_file_path)
        print("Optimized Size: {} {} ({}% savings)".format(*_size(temp_file_path), round((1.0 - (post / pre)) * 100), 2) )
    
    def basicOptimize(self):
        pre = os.path.getsize(os.path.join(INPUT_PATH, self.file_name))
        _optimize(os.path.join(INPUT_PATH, self.file_name), copy=temp_file_path)
        post = os.path.getsize(temp_file_path)
        print("Optimized Size: {} {} ({}% savings)".format(*_size(temp_file_path), round((1.0 - (post / pre)) * 100), 2) )


    def run(self, client):
        try:
            if self.xmp_name:
                # Process the file into a JPEG
                self.rawOptimize()
            else:
                self.basicOptimize()

            # Open the image, read as bytes, convert to types Image
            image = Image.open(temp_file_path)
            bytesIO = io.BytesIO()
            image.save(bytesIO, format='jpeg')
            image.close()
            image = vision.types.Image(content=bytesIO.getvalue())
            
            # Performs label detection on the image file
            response = client.label_detection(image=image)
            labels = [label.description for label in response.label_annotations]
            print('\tLabels: {}'.format(', '.join(labels)))
            
            # XMP sidecar file specified, write to it using XML module
            if self.xmp_name:
                print('\tWriting {} tags to output XMP...'.format(len(labels)))
                parser = XMPParser(os.path.join(INPUT_PATH, self.xmp_name))
                parser.add_keywords(labels)
                # Save the new XMP file
                parser.save(os.path.join(OUTPUT_PATH, self.xmp_name))
                # Remove the old XMP file
                os.remove(os.path.join(INPUT_PATH, self.xmp_name))
            # No XMP file is specified, using IPTC tagging
            else:
                print('\tWriting {} tags to output {}'.format(len(labels), ext[1:].upper()))
                info = iptcinfo3.IPTCInfo(os.path.join(INPUT_PATH, self.file_name))
                info['keywords'].extend(labels)
                info.save()
                # Remove the weird ghsot file created by this iptc read/writer.
                os.remove(os.path.join(INPUT_PATH, self.file_name + '~'))

            # Copy dry-run
            # shutil.copy2(os.path.join(INPUT_PATH, self.file_name), os.path.join(OUTPUT_PATH, self.file_name))
            os.rename(os.path.join(INPUT_PATH, self.file_name), os.path.join(OUTPUT_PATH, self.file_name))
        except:
            self._cleanup()
            raise
        self._cleanup()

    # Remove the temporary file
    def _cleanup(self):
        if os.path.exists(self.temp_file_path):
            # Deletes the temporary file
            os.remove(self.temp_file_path)

    # Get the size of the file. Is concerned with filesize type. 1024KiB -> 1MiB
    def _size(self, file_path):
        size, type = os.path.getsize(file_path) / 1024, 'KiB'
        if size >= 1024: size /= 1024; type = 'MiB'
        return round(size, 2), type

    # Optimizes a file using JPEG thumbnailing and compression.
    def _optimize(self, file_path, size=(512, 512), quality=85, copy=None):
        image = Image.open(file_path)
        image.thumbnail(size, resample=Image.ANTIALIAS)
        if copy:
            image.save(copy, format='jpeg', optimize=True, quality=quality)
        else:
            image.save(file_path, format='jpeg', optimize=True, quality=quality)