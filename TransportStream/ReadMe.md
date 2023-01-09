# Generating a Transport Stream

## Pre-Requisites

The tooling used in generating a transport stream from scratch is [Opencaster](https://github.com/aventuri/opencaster), which was last updated in 2014. The lack of updates means that it is no longer available as a packaged in Ubuntu 22.04 onwards. For that reason, you will need to install Ubuntu 20.04 as a base OS.

Once installed, Opencaster can be installed with

	sudo apt install opencaster

The age of the software means all scripts will be in Python 2.7. I have discovered no ports to Python 3 of the Opencaster libraries.

## Split a Video File into Elemental Streams

The transport stream standard that DVB-T relies on handles audio and video as seperate streams. This is done to allow flipping between multiple feeds in a single broadcast (e.g. different audio mixes for sports, alternate views, opting into audio description). So to "broadcast" a single video file, we need to split it in seperate audio and video feeds.

You will need FFMPEG installed to perform the split:

	sudo apt install ffmpeg

A script has been provided called elemental_from_video.py that perform a three stage conversion:

1. Convert the single video file into separate MP2 audio and video files.
2. Convert these files to [Paketized Elementary Streams (PES)](https://en.wikipedia.org/wiki/Paketized_elementary_stream).
3. Package the streams into standalone Transport Streams (TS) ready to multiplex.

As an example, to perform this conversion on the hayfever.mp4 files:

	python3 elemental_from_video.py --input Media/hayfever.mp4 --output Media/hayfever --video-pid 1001 --audio-pid 1002
