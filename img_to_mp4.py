#!/usr/bin/env python3
# - *- coding: utf- 8 - *-
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import UnidentifiedImageError
from os import walk
import subprocess
import sys
import os
import shutil
from argparse import ArgumentParser

MAX_H = 1280
FONT_SIZE = 40
MARGIN = 60
TEXT_PADDING = 8

parser = ArgumentParser()

parser.add_argument("-i", "--input_dir", dest="input_dir", type=str, required=True,
                    help="Path to directory where images reside")
parser.add_argument("-a", "--audio", dest="audio", type=str, default="",
                    help="Path to audio file you want to play in animation, if ommited there will be no sound")
parser.add_argument("-o", "--output", dest="output", default="out.mp4", type=str,
                    help="Path to resulting mp4 file, defaults to out.mp4")
parser.add_argument("-f", "--font", dest="font", type=str, default="",
                    help="Path to True Type font file used for frame titles, if ommited there will be no titles")

args = parser.parse_args()
input_dir = args.input_dir
audio_file = args.audio
output_file = args.output
font_file = args.font


def prepare_tmp_dir():
    tmp_dir = "./titled"
    try:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        os.makedirs(tmp_dir)
        return tmp_dir
    except OSError as e:
        print("Cannot create tmp directory for storing images.")
        sys.exit()


def prepare_images(input_directory, output_directory):
    errors = []
    filenames = next(walk(input_directory), (None, None, []))[2]
    for filename in filenames:
        filename = filename.strip()
        parts = filename.split("-")
        if len(parts) < 3:
            errors.append(f"Filename {filename} is not properly formatted. This file will be skipped.")
            continue
        duration = parts[1]
        rest = "-".join(parts[2:])
        if not duration.isdigit():
            errors.append(f"Duration segment in filename {filename} is not integer. This file will be skipped.")
            continue
        try:
            img = Image.open(f"{input_directory}/{filename}")
            ow, oh = img.size
            if oh > MAX_H:
                new_h = MAX_H
                new_w = int((ow * MAX_H) / oh)
                new_size = (new_w, new_h)
                img = img.resize(new_size, resample=3)
            if font_file:
                draw = ImageDraw.Draw(img)
                w, h = img.size
                font = ImageFont.truetype(font_file, FONT_SIZE)
                x, y = (MARGIN, h - MARGIN)
                text = ".".join(rest.split(".")[:-1])
                tw, th = font.getsize(text)
                draw.rectangle((x, y, x + tw + 2 * TEXT_PADDING, y + th), fill='black')
                draw.text((x + TEXT_PADDING, y - TEXT_PADDING), text, fill='white', font=font)
            img.save(f"{output_directory}/{filename}")
        except UnidentifiedImageError:
            pass
    return errors


def create_video(image_dir):
    filenames = []
    for _, _, files in os.walk(image_dir):
        for f in files:
            filenames.append(f)
    filenames.sort()
    durations = [int(f.split("-")[1]) for f in filenames]
    loops = []
    filters = []
    filter_end = []
    for i, filename in enumerate(filenames):
        loops.append(f'-loop 1 -t {durations[i]} -i "{image_dir}/{filename}"')
        if i == 0:
            filters.append(f"[{i}:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fade=t=out:st={durations[i] - 1}:d=1[v{i}];")
        else:
            filters.append(f"[{i}:v]scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fade=t=in:st=0:d=1,fade=t=out:st={durations[i] - 1}:d=1[v{i}];")
        filter_end.append(f"[v{i}]")

    a1 = " ".join(loops)
    a2 = " ".join(filters)
    a3 = "".join(filter_end)
    a4 = len(loops)
    audio_input = f"-i {audio_file}" if audio_file else ""
    audio_map = f"-map {a4}:a -shortest" if audio_file else ""

    command = f'ffmpeg {a1} {audio_input} -filter_complex "{a2} {a3}concat=n={a4}:v=1:a=0,format=yuv420p[v]" -map "[v]" {audio_map} {output_file}'
    subprocess.call(command, shell=True)


tmp_dir = prepare_tmp_dir()
preparation_errors = prepare_images(input_dir, tmp_dir)

if preparation_errors:
    print(os.linesep)
    print(f"Preparation warnings")
    print(os.linesep)
    print(os.linesep.join(preparation_errors))
    print(os.linesep)
    print("----------------------------------------------------------------------------------------")

create_video(tmp_dir)

# cleanup
shutil.rmtree(tmp_dir, ignore_errors=True)
