import sys, os
from package import app

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(sys.path[0], 'package', 'key', 'photo_tagging_service.json')

if __name__ == "__main__":
    sys.exit(app.run())