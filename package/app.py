import io, sys, os, time, rawpy, imageio, progressbar, shutil, iptcinfo3
from google.cloud.vision import types
from google.cloud import vision
from package import xmp
from PIL import Image

# The name of the image file to annotate
input_path = os.path.join(sys.path[0], 'package', 'processing', 'input')
temp_path = os.path.join(sys.path[0], 'package', 'processing', 'temp')
output_path = os.path.join(sys.path[0], 'package', 'processing', 'output')

# Process a single file in these steps:
# 1) Create a temporary file
# 2) Send it to GoogleAPI
# 3) Read XMP, then write new tags to it
# 4) Delete temporary file, move NEF/JPEG and XMP

def process_file(file_name, xmp_name=None):
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
    def _optimize(file_path, size=(512, 512), quality=85, copy=None):
        image = Image.open(file_path)
        image.thumbnail(size, resample=Image.ANTIALIAS)
        if copy:
            image.save(copy, format='jpeg', optimize=True, quality=quality)
        else:
            image.save(file_path, format='jpeg', optimize=True, quality=quality)

    base, ext = os.path.splitext(file_name)
    temp_file_path = os.path.join(temp_path, base + '.jpeg')

    try:
        if xmp_name:
            # Process the file into a JPEG
            rgb = rawpy.imread(os.path.join(input_path, file_name))
            imageio.imsave(temp_file_path, rgb.postprocess())
            rgb.close()

            # Information on file sizes
            print("Raw Size: {} {}".format(*_size(os.path.join(input_path, file_name))), end=' | ')
            print("Resave Size: {} {}".format(*_size(temp_file_path)), end=' | ')
            pre = os.path.getsize(temp_file_path)
            _optimize(temp_file_path)
            post = os.path.getsize(temp_file_path)
            print("Optimized Size: {} {} ({}% savings)".format(*_size(temp_file_path), round((1.0 - (post / pre)) * 100), 2) )
        else:
            pre = os.path.getsize(os.path.join(input_path, file_name))
            _optimize(os.path.join(input_path, file_name), copy=temp_file_path)
            post = os.path.getsize(temp_file_path)
            print("Optimized Size: {} {} ({}% savings)".format(*_size(temp_file_path), round((1.0 - (post / pre)) * 100), 2) )

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
        if xmp_name:
            print('\tWriting {} tags to output XMP...'.format(len(labels)))
            parser = xmp.XMPParser(os.path.join(input_path, xmp_name))
            parser.add_keywords(labels)
            # Save the new XMP file
            parser.save(os.path.join(output_path, xmp_name))
            # Remove the old XMP file
            os.remove(os.path.join(input_path, xmp_name))
        # No XMP file is specified, using IPTC tagging
        else:
            print('\tWriting {} tags to output {}'.format(len(labels), ext[1:].upper()))
            info = iptcinfo3.IPTCInfo(os.path.join(input_path, file_name))
            info['keywords'].extend(labels)
            info.save()
            # Remove the weird ghsot file created by this iptc read/writer.
            os.remove(os.path.join(input_path, file_name + '~'))

        # Copy dry-run
        # shutil.copy2(os.path.join(input_path, file_name), os.path.join(output_path, file_name))
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
    select = [file for file in files if os.path.splitext(file)[1] != '.xmp']

    # Create the 'temp' directory
    print(f'Initializing file processing for {len(select)} files...')
    os.makedirs(temp_path)

    try:
        # Process files
        for index, file in progressbar.progressbar(list(enumerate(select)), redirect_stdout=True, term_width=110):
            name, ext = os.path.splitext(file)
            ext = ext.upper()
            # Raw files contain their metadata in an XMP file usually
            if ext in ['.NEF', '.CR2']:
                # Get all possible files
                identicals = [possible for possible in files
                            if possible.startswith(os.path.splitext(file)[0])
                            and not possible.endswith(os.path.splitext(file)[1])
                            and not possible.upper().endswith('.XMP')]

                # Alert the user that there are duplicates in the directory and ask whether or not to continue
                if len(identicals) > 0:
                    print('Identical files were found in the directory, continue?')
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
                    process_file(file_name=file, xmp_name=xmps[0])
            elif ext in ['.JPEG', '.JPG', '.PNG']:
                print('Processing file {}, \'{}\''.format(index + 1, file), end=' | ')
                process_file(file_name=file)

    except:
        os.rmdir(temp_path)
        raise

    # Remove the directory, we are done here
    print('Cleaning up temporary directory...')
    os.rmdir(temp_path)