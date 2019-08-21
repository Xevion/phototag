# photo-tagging

## First Objectives

This project really was an experience, I'll not ever deny that.

My first goal was to basically be able to read and image, upload to Google and receive back labels.
This was accomplished very quickly, and the next step was either learning how to parse the weird `.XMP` files I had found in the folder.
I did not understand them and why they were detached from the `.NEF`, and only later did I learn later that only `RAW` format files use this XMP file, which I only recently learned was called a `Sidecar file` in filesystems.

I started off with trying to parse, read, and write tags to and from an XMP file quickly. I had much trouble with this, as I could not find a working (Windows) Python module for `XMP` parsing fast enough, as the only one available required `exempi`, which was not officially supported for Windows at the time. To this date, I still have not figured out how I could have gone about it. Please message me if you know how, I'd still love to see if Exempi had what I was looking for.

I even tried an `XML` parser, but after learning that it was in fact a `XML` parser, I dropped it, oblivious to the fact that `XML` is essentially `XMP`.

After a long while of unsuccessful searches on the subject, I gave up and looked into how I could do it myself - with minimal effort...

 *I turned to Regex.*

Surprisingly, Regex worked pretty well, and added tags without problem 99% of the time. However, I would only learn a long while after that there were serious caveats to what I was doing here.

After "successfully" figuring out XMP parsing, I moved onto making a proper package and drew of a plan for how I could parse files. This one took a while since I'd never done image resizing or anything with input/output of files on this kind of scale (small scale) before.

After a couple of hours, I had a working prototype which took files, compressed, uploaded to Google for labelling, and received a set of labels while keeping processing/uploading times at a minimum. It was rather speedy for what I could expect, at around 0.5 images a second.

The real punch in the gut comes now - Time to implement that actual tagging operation. I learned here that only `.NEF` files carried the `.XMP` sidecar file, and had to split up my tagging operation into IPTC tagging and XMP based tagging, and I had to think about the complex file enviroment I would need to parse - What if two files had the same name, different extension, and one was a `.NEF` with a `.XMP` sidecar file? Does the `.NEF` get priority? Do we quit? Do we give an alert?  What happens here?

I also had to think about turning this application into a commandline utility for quickly tagging all the photos on my machine - Would it overwrite files in place? What happens if my utility goes haywire? Would I be storing backups of the `.XMP` files? What happens when it's a heavily modified `.XMP` file, those can get very large!

Before I could even think about all that, I had to verify that I could work with `.XMP` files in the first place, as my current setup using Regex was failing when it came down to adding tags to something that has never been tagged before. Worse yet, I had and still have no idea what most of the stuff present in a `.XMP` file means, so it was clear that I had to resort to something with true XMP read and write capabilities.

