# photo-tagging

## What is this repository?

This repository is for a interesting project involving Google's Vision API and support for automatic photo tagging, with support for Adobe's XMP metadata and other file property based metadata.

## How does it work?

This application is built in Python and utilizes the `google-cloud` python module family.

All requirements will be automatically be installed whenever `pip install .` is ran inside the `phototag` directory.

The basic process for each photo be tagged is as follows    
1. Build relevant paths and identify important information used throughout the process
2. Save RAW files as JPEG using `rawpy`
3. Optimize JPEG files using thumbnailing and quality measures
4. Open and send the file to Google using the Vision API with `google_cloud.vision`
5. Compile and save the image's labels from Google
    a. JPEGs use the `iptcinfo3` module to save
    b. RAW files use a messy implemetation of the `xml` module to read and write tags (experimental) from and to the XMP Sidecar file used by Adobe
6. Delete the temporary (optimized) file and move the original image to the output folder.

The command used to access this program is `phototag run`, which would process and label all eligible images in the working directory.

## Features

* Automatic tagging of photos using Google's Vision API
    * Fast and accurate, it returns specific keywords using Google's very own Labelling model
    * Can easily be used yourself if you sign up
        * Super cheap and easy to setup

* Automatic compression of photos for minimal data usage on both your and Google's end
    * Uses combination thumbnailing and general JPEG compression to reduce size to a mere some dozen kilobytes.

* Support for both JPEG and RAW
    * Store tags in JPEG via IPTC metadata
    * Store tags in RAW files through Adobe's XMP sidecar files
        * Full support for NEF only, it is assumed but not tested whether or not CR2 and other formats will behave the same.
        * Requires a existing XMP file to be available

## Usage

This repository was not originally, and may never be, built to serve users directly. If you have any issues, feel free to submit a issue and I'll see what I can do (no promises!).

To use, first, use `git clone <url>` to download the repository. Then install with `pip install .` inside the `phototag` directory.

If all went well, all requirements will be installed and you should be able to use `phototag` freely across any *new* terminals.

At this point, you're required to setup a account with Google for their Vision API to get a single function: Label Detection.

Use `phototag auth [file]` to copy/move the credentials file to the package config directory.

At this point, you should be able to fully take adantage of the module's capabilities by entering `phototag run` inside of directories you want to automatically label.

Once you're done, you can use `pip uninstall phototag` to remove the directory.

## To-do

* Implement async or parallel processing to conver & tag photos faster or in batches
    * Move to more precise logging system
* Test with different RAW file formats
    * Stress test use with Adobe sidecar files
* Make more robust configuration file system
    * Integration with click CLI
* Better, to-the-point logging
