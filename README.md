# img-to-mp4

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

Python 3 command line tool for converting images into mp4 video/slideshow with optional audio and frame titles.


### Requirements

Tool has dependency on PIL image processing library, so it has to be installed on the system.
```
pip install pillow
```

Another dependency is `ffmpeg` command line tool, which can be installed from https://www.ffmpeg.org/download.html

### Usage

Put all images in one directory on the local filesystem and name them using following pattern:

`<ORDER OF IMAGE IN VIDEO WITH LEADING ZEROES>-<DURATION OF FRAME IN SECONDS>-<TITLE YOU WANT TO APPEAR IN FRAME>.<FILE EXTENSION>`. 

Example of one such file name:
`014-6-West side slopes in rain.jpg`

Path to directory with input images is the only mandatory input argument with option `-i` or `--input`.

Other optional arguments are

- `-a` or `--audio`, path to audio file on local disk in mp3 or m4a format that you want to play in resulting video. If ommited, no audio will be used to produce output.
- `-f` or `--font`, path to TrueType font file on local disk to be used for frame title (appears in the lower left corner of each image). If ommited, frames will have no titles.
- `-o` or `--output`, path to resulting mp4 video file on local disk. Defaults to `out.mp4` in current directory.


### Usage example

```
% python3 img_to_mp4.py -i /Users/username/Pictures/prepared_pictures/ -a /Users/username/Music/loop.mp3 -f /Library/Fonts/Arial.ttf -o /Users/username/Desktop/slideshow.mp4
```
