<div align="center">
    <a href="#">
        <img src="./.media/banner.png" alt="phototag Repository Banner">
    </a>
    <br>
    <sub>
        Built by Xevion
    </sub>
</div>

Phototag is a personal tool I use to automatically generate and layer tags describing a photo in a fast and easy way. It
uses Google's Vision API and supports IPTC metadata and Adobe XMP Sidecar files on Windows.

## Features

* Automatic tagging of photos using Google's Vision API
    * Cheap, Fast and Accurate
* Minimal Data Usage
    * Compresses and thumbnails images before sending to Google
* Support for both JPEG and RAW
    * Store tags in JPEG via IPTC metadata
    * Store tags in RAW files via Adobe's XMP sidecar files
        * Full support for NEF only, CR2 and more untested
        * Requires a existing XMP file to be available

## Installation

For basic usage, the project is currently not on PyPi. Until then, clone and install like so:

```bash
pip install
```

For development, install all dependencies with `pipenv`:

```bash
pipenv install
pip install -e .  # Editable mode to use the folder's current source files
# You can also install the Phototag package with
pipenv install -e .
```

## Usage

```bash
# Copy the JSON authentication file for Google Vision API access
phototag auth [file]
phototag run
````

## Uninstallation

```bash
pip uninstall phototag
```

## How does it work?

This application is built in Python and utilizes the `google-cloud` python module family.

The basic process for each photo be tagged is as follows

1. Build relevant paths and identify important information used throughout the process
2. Save RAW files as JPEG using `rawpy`
3. Optimize JPEG files using thumbnailing and quality measures
4. Open and send the file to Google using the Vision API with `google_cloud.vision`
5. Compile and save the image's labels from Google
    - JPEGs use the `iptcinfo3` module to save
    - RAW files use a messy implementation of the `xml` module to read and write tags (experimental) from and to the XMP
      Sidecar file used by Adobe
6. Delete the temporary (optimized) file and move the original image to the output folder.

The command used to access this program is `phototag run`, which would process and label all eligible images in the
current working directory.

## To-do

* Implement async or (proper) parallel processing to convert & tag photos faster or in batches
    * Move to more precise logging system
* Test with different RAW file formats
    * Stress test use with Adobe sidecar files
* Make more robust configuration file system
    * Integration with click CLI
* Better, to-the-point logging
