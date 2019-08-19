import sys, os
from package import app

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(sys.path[0], 'package', 'key', 'photo_tagging_service.json')

# if __name__ == "__main__":
#     sys.exit(app.run())

import exif
path = 'E:\\Photography\\Colorado 2019\\DSC_7960.jpg'
image = exif.Image(open(path, 'rb'))
print(image.artist)
print(dir(image))