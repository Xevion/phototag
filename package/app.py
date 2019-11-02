import io, sys, os, time, rawpy, imageio, progressbar, shutil

from .xmp import XMPParser
from google.cloud import vision

from .process import FileProcessor
from . import INPUT_PATH, TEMP_PATH, OUTPUT_PATH, PROCESSING_PATH
from . import RAW_EXTS, LOSSY_EXTS

# Process a single file in these steps:
# 1) Create a temporary file
# 2) Send it to GoogleAPI
# 3) Read XMP, then write new tags to it
# 4) Delete temporary file, move NEF/JPEG and XMP

# Driver code for the package
def run():
    # Ensure that 'input' and 'output' directories are created
    if not os.path.exists(INPUT_PATH):
        print('Input directory did not exist, creating and quitting.')
        os.makedirs(INPUT_PATH)
        return

    if not os.path.exists(OUTPUT_PATH):
        print('Output directory did not exist. Creating...')
        os.makedirs(OUTPUT_PATH)

    # Client
    client = vision.ImageAnnotatorClient()

    # Find files we want to process based on if they have a corresponding .XMP
    files = os.listdir(INPUT_PATH)
    select = [file for file in files if os.path.splitext(file)[1] != '.xmp']

    # Create the 'temp' directory
    print(f'Initializing file processing for {len(select)} files...')
    os.makedirs(TEMP_PATH)

    try:
        # Process files
        for index, file in progressbar.progressbar(list(enumerate(select)), redirect_stdout=True, term_width=110):
            name, ext = os.path.splitext(file)
            ext = ext.lower().strip('.')
            # Raw files contain their metadata in an XMP file usually
            if ext in RAW_EXTS:
                # Get all possible files
                identicals = [possible for possible in files
                            if possible.startswith(os.path.splitext(file)[0])
                            and not possible.endswith(os.path.splitext(file)[1])
                            and not possible.upper().endswith('.XMP')]

                # Alert the user that there are duplicates in the directory and ask whether or not to continue
                if len(identicals) > 0:
                    print('Identical files were the directory, continue?')
                    print(',\n\t'.join(identicals))

                xmps = [possible for possible in files
                        if possible.startswith(os.path.splitext(file)[0])
                        and possible.upper().endswith('.XMP')]

                # Skip and warn if more than 1 possible files, user error
                if len(xmps) > 1:
                    print('More than 1 possible XMP metadata file for \'{}\'...'.format(file))
                    print(',\n'.join(['\t{}'.format(possible) for possible in xmps]))
                # Zero possible files, user error, likely
                elif len(xmps) <= 0:
                    print('No matching XMP metadata file for \'{}\'. skipping...'.format(file))
                # Process individual file
                else:
                    print('Processing file {}, \'{}\''.format(index + 1, xmps[0]), end=' | ')
                    file = FileProcessor(file, xmps[0])
                    file.run(client)
            elif ext in LOSSY_EXTS:
                print('Processing file {}, \'{}\''.format(index + 1, file), end=' | ')
                file = FileProcessor(file)
                file.run(client)
    except:
        os.rmdir(TEMP_PATH)
        raise

    # Remove the directory, we are done here
    print('Cleaning up temporary directory...')
    os.rmdir(TEMP_PATH)