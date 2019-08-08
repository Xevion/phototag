import io, sys, os, time, rawpy, imageio, progressbar
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image
from package.xmp import writeTags

# The name of the image file to annotate
input_path = os.path.join(sys.path[0], 'package', 'processing', 'input')
temp_path = os.path.join(sys.path[0], 'package', 'processing', 'temp')
output_path = os.path.join(sys.path[0], 'package', 'processing', 'output')

# Process a single file in these steps:
# 1) Create a temporary file
# 2) Send it to GoogleAPI
# 3) Read XMP, then write new tags to it
# 4) Delete temporary file, move NEF/JPEG and XMP

def process_file(file_name, xmp):
    global client

    # Remove the temporary file
    def _cleanup():
        if os.path.exists(temp_file_path):
            # Deletes the temporary file
            os.remove(temp_file_path)

    # Get the size of the file. Is concerned with filesize type. 1024KiB -> 1MiB
    def _size(file_path):
        size, type = os.path.getsize(file_path) / 1024, 'KiB'
        if size >= 1024: size /= 1024; type = 'MiB'
        return round(size, 2), type

    # Optimizes a file using JPEG thumbnailing and compression.
    def _optimize(file_path, size=(512, 512), quality=85):
        image = Image.open(file_path)
        image.thumbnail(size, resample=Image.ANTIALIAS)
        image.save(file_path, format='jpeg', optimize=True, quality=quality)

    base = os.path.splitext(file_name)[0]
    temp_file_path = os.path.join(temp_path, base + '.jpeg')

    try:
        # Process the file into a JPEG
        rgb = rawpy.imread(os.path.join(input_path, file_name))
        imageio.imsave(os.path.join(temp_file_path), rgb.postprocess())
        rgb.close()

        # Information on file sizes
        print("Raw Size: {} {}".format(*_size(os.path.join(input_path, file_name))), end=' | ')
        print("Resave Size: {} {}".format(*_size(temp_file_path)), end=' | ')
        pre = os.path.getsize(temp_file_path)
        _optimize(temp_file_path)
        post = os.path.getsize(temp_file_path)
        print("Optimized Size: {} {} ({}% savings)".format(*_size(temp_file_path), round((1.0 - (post / pre)) * 100), 2) )

        # Open the image, read as bytes, convert to types Image
        image = Image.open(temp_file_path)
        bytesIO = io.BytesIO()
        image.save(bytesIO, format='jpeg')
        image.close()
        image = types.Image(content=bytesIO.getvalue())
        
        # Performs label detection on the image file
        response = client.label_detection(image=image)
        labels = [label.description for label in response.label_annotations]
        print('\tLabels: {}'.format(', '.join(labels)))

        print('\tWriting {} tags to output folder...')
        writeTags(os.path.join(input_path, xmp), os.path.join(output_path, xmp), labels)
        print('\tMoving associated original image file...')
        os.rename(os.path.join(input_path, file_name), os.path.join(output_path, file_name))
        
    except:
        _cleanup()
        raise
    _cleanup()

# Driver code for the package
def run():
    global client

    # Ensure that 'input' and 'output' directories are created
    if not os.path.exists(input_path):
        print('Input directory did not exist, creating and quitting.')
        os.makedirs(input_path)
        return

    if not os.path.exists(output_path):
        print('Output directory did not exist. Creating...')
        os.makedirs(output_path)

    # Clients
    client = vision.ImageAnnotatorClient()

    # Find files we want to process based on if they have a corresponding .XMP
    files = os.listdir(input_path)
    select = [file for file in files if os.path.splitext(file)[1] == '.xmp']

    # Create the 'temp' directory
    print(f'Initializing file processing for {len(select)} files...')
    os.makedirs(temp_path)

    try:
        # Process files
        for index, file in progressbar.progressbar(list(enumerate(select)), redirect_stdout=True, term_width=110):
            # Get all possible files
            possibles = [possible for possible in files if
            possible.startswith(os.path.splitext(file)[0])
            and not possible.endswith(os.path.splitext(file)[1])]
            
            # Skip and warn if more than 1 possible files, user error
            if len(possibles) > 1:
                print('More than 1 possible binding file for \'{}\'...'.format(file))
                print('\n'.join(['>>> {}'.format(possible) for possible in possibles]))
            # Zero possible files, user error, likely
            elif len(possibles) <= 0:
                print('Zero possible files for \'{}\'. skipping...'.format(file))
            # Process individual file
            else:
                print('Processing file {}, \'{}\''.format(index + 1, possibles[0]), end=' | ')
                process_file(file_name=possibles[0], xmp=file)
                time.sleep(0.3)
    except:
        os.rmdir(temp_path)
        raise

    # Remove the directory, we are done here
    print('Cleaning up temporary directory...')
    os.rmdir(temp_path)