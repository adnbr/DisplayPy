# Displays all the images and MP4 videos in a folder for simplistic digital
# signage applications.
#
# TODO: Centralise the keyboard event handling (for quitting)
# TODO: Allow exiting during video playback

import sys
import pygame
import os
import random
import time
import datetime
import subprocess
import random
import threading
import argparse
import re
from pygame.locals import *
from threading import Thread

# Scale image, keeping the aspect ratio the same. Slightly modified from the
# original by using smoothscale and casting to int. This produces a much better
# end result when enlarging.
# Frank Raiser http://www.pygame.org/pcr/transform_scale/

included_extensions = ['jpg', 'jpeg', 'bmp', 'png', 'mp4']

def aspect_scale(img, (bx, by)):
    # Scales 'img' to fit into box bx/by.
    # This method will retain the original image's aspect ratio
    ix, iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx / float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by / float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by / float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx / float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    return pygame.transform.smoothscale(img, (int(sx), int(sy)))


def wait_a_while(seconds):
    # Display the image for a number of seconds before moving on. Listen for
    # the Escape key to exit.
    for x in range(1, seconds * 2):
        time.sleep(0.5)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit("Told to quit (Escape key pressed)")


def play_video(content):

    # Look for a subtitle (.srt) file with the same name to use
    # with the video content.
    sub_path = os.path.splitext(content)[0] + ".srt"

    if (os.path.isfile(sub_path)):
        print ("Found a subtitle (.srt) file: " + sub_path)
        subprocess.call(["omxplayer", "--subtitles", sub_path, content])
    else:
        subprocess.call(["omxplayer", content])

def display_image(content):
    # Fill screen with black to remove remnants of the previous
    # image displayed
    display_screen.fill(000000)
    if safe_fileexists(content) is False:
        print "Cannot load image: " + image_name
        return False

    img = pygame.image.load(content)
    # Convert image to 32 to allow scaling
    img = img.convert(32)
    img = aspect_scale(img, (width, height))

        # Place the resized image in the centre of the screen.
    size = img.get_rect()
    display_screen.blit(img, ((width / 2 - (size.width / 2)), (height / 2 - (size.height / 2))))

    # Actually update the display.
    pygame.display.flip()
    return True

# Use to prevent a hang in the case of the network going away.
# https://stackoverflow.com/questions/33786125/can-os-listdir-hang-with-network-drives-what-system-call-does-it-use
def safe_listdir(directory, timeout = 4):
    contents = []
    t = threading.Thread(target=lambda: contents.extend(os.listdir(directory)))
    t.daemon = True  # don't delay program's exit
    t.start()
    t.join(timeout)
    if t.is_alive():
        return None
    return contents

def safe_fileexists(file, timeout = 4):
    print "Checking if " + file + " exists."
    t = threading.Thread(target=lambda: os.path.exists(file))
    t.daemon = True  # don't delay program's exit
    t.start()
    t.join(timeout)
    if t.is_alive():
        return False
    return True

def display_no_content():
    # There are no files to display, so display an error/warning message
    # Fill screen with black to remove remnants of the previous image
    # displayed
    display_screen.fill(000000)

    if not args.quiet:
        # We've not been told to be quiet, so display the error on screen
        label = display_font.render("Content location empty.", 1, (255, 0, 0))
        display_screen.blit(label, (200, 200))
        label = display_font.render(args.path, 1, (255, 0, 0))
        display_screen.blit(label, (200, 300))

    pygame.display.flip()

# Some of the files will have a date sensitivity, process these and remove them
# from the list if required.
# !UNTIL-DDMMYYYY!filename.jpg - Display a file if the specified date has not passed.
# !ONLY-DDMMYYYY!filename.jpg - Display a file only on the date specified.
def filter_date_content(file_names):
	for file in file_names[:]:
		print ("Checking file" + file)
    		if file.startswith("!"):
			print ("Starts with !")
			p = re.compile(ur"!(.*?)-(.*?)!")
			regex_result = re.search(p, file)
			action = regex_result.group(1)
			print action
			display_date = datetime.datetime.strptime(regex_result.group(2), "%d%m%Y").date()
			print display_date
			if action == "UNTIL":
				if display_date < datetime.datetime.today().date():
					print("Content no longer relevant, removing " + file)
					file_names.remove(file)
			if action == "ONLY":
				if display_date != datetime.datetime.today().date():
					file_names.remove(file)
					print("Content not for display today, removing " + file)
	return file_names

# Loop this continually
def display_content_from_folder(content_folder, seconds_per_image):
    # Get a list of all the eligible files from the folder, then shuffle them.
    print ("Refreshing content list.")
    file_names = safe_listdir(content_folder)
    file_names = filter_date_content(file_names)

    if file_names is None:
        print ("Couldn't load files from " + content_folder + " as it doesn't exist.")
        return
    # Randomisation requested.
    if (args.random):
        random.shuffle(file_names)

    if not file_names:
        display_no_content()
        wait_a_while(args.seconds)

    # Print out a list of the files as they will be shown.
    print ("Content to be displayed:")
    x = 1

    for file in file_names:
        print(str(x) + ".\t" + file)
        x = x + 1

    # Loop through all the content, perform appropriate actions.
    for content in file_names:

        if any(content.endswith(ext) for ext in included_extensions):

            # Create a concat path.
            content_fullname = os.path.join(content_folder, content)

            # If an image then display it.
            if (content_fullname.endswith(".mp4")):
                # We want to display videos less frequently, so only show it if
                # the RNG returns 1, unless we have nocointoss flag in which case
                # play it every time.
                if (random.randint(0, 1) or args.nocointoss):
                    print("Displaying Video Content: " + content_fullname)
                    play_video(content_fullname)
                else:
                    print("Skipped Video Content: " + content_fullname)
            else: # is an image, display it.
                # Open the image and scale it to the correct size.
                print("Displaying: " + content_fullname)
                did_display = display_image(content_fullname)
                if did_display is True:
                    wait_a_while(seconds_per_image)
                else:
                    break

        else:
            # We've got lost somewhere along the way, this file doesn't exist
            # Quit out of the loop and reload all the files.
            print("Lost a file. Restarting the loop.")
            return

def count_files_in_folder (content_folder):
    return len([fn for fn in safe_listdir(content_folder) if any(fn.endswith(ext) for ext in included_extensions)])


# ensure the number in 'fb0' matches the device name of framebuffer
os.putenv('SDL_FBDEV', '/dev/fb0')
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_NOMOUSE', '1')

# Create command line arguments.
parser = argparse.ArgumentParser()
parser.add_argument("path", help="Absolute path to the content directory.")  # required
parser.add_argument("-q", "--quiet", help="Don't display no content error.",
                    action="store_true")  # optional
parser.add_argument("-r", "--random", help="Sort the content randomly before playback.",
                    action="store_false")  # optional
parser.add_argument("-nc", "--nocointoss",
                    help="Play videos every time they are encountered, don't flip a coin. Default False, coin will be flipped.", action="store_false")  # optional
parser.add_argument("-s", "--seconds", help="Number of seconds to display each image. Default 8 seconds.",
                    default=8, type=int)  # optional
parser.add_argument("-p", "--period", help="Lobby mode only. How many seconds should the default images be displayed for before showing the slideshow. Default is 300 seconds (5 minutes).", default=300, type=int)
parser.add_argument('mode', choices=('simple', 'lobby'), default="simple", help="Simple mode displays all the images in a folder. Lobby mode displays a default image, override images when applicable and intersperses slideshow images.")


args = parser.parse_args()

print("Loading content from: " + args.path)
included_extensions = ['jpg', 'jpeg', 'bmp', 'png', 'mp4']

random.seed()
pygame.init()

# Get the current screen resolution and extract the size to more friendly vars.
width, height = pygame.display.Info().current_w, pygame.display.Info().current_h

# Create a new surface - screen res, full screen and 32 bit colour, and hide
# the mouse. Set the window title - it's going to be hidden, but why not.
pygame.display.set_caption('DisplayPy')
display_screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN, 32)
pygame.mouse.set_visible(0)
display_font = pygame.font.SysFont("roboto", 34)

if (args.mode == "simple"):
    while True:
        display_content_from_folder(args.path, args.seconds)
elif (args.mode == "lobby"):
    default_path = os.path.join(args.path, "default")
    override_path = os.path.join(args.path, "override")
    content_path = os.path.join(args.path, "content")
    # Loop this forever
    while True:
        # Check if there is any content in the Override folder.
        override_count = count_files_in_folder(override_path)
        if (override_count > 0):
            display_content_from_folder(override_path)
        else:
            default_count = count_files_in_folder(default_path)
            default_seconds_per_image = int(round(args.period / default_count))

            display_content_from_folder(default_path, default_seconds_per_image)
            display_content_from_folder(content_path, args.seconds)
