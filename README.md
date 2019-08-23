# photo-tagging

## What is this repository?

This repository is for a interesting project involving Google's Vision API and support for automatic photo tagging, with support for Adobe's XMP metadata and other file property based metadata.

## How does it work?

This application is built in Python and utilizes the `google-cloud` python module. Install using `pip install google-cloud`. A key should be provided by google in a `.json` file, insert this at `./package/key/photo_tagging_service.json`.

## Features

Automatic tagging of photos using a high quality Vision API

Automatic compression of photos for minimal data usage on both your and Google's end

Support for .NEF RAW file compression with .XMP metadata files.

- With added support for all non .NEF files with basic 

## Learning

I've typed up a good file with everything I've learned about XMP files, Adobe, and just how complex this problem really was for me.

[./LEARNING.md](./LEARNING.md)