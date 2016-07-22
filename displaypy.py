# Displays all the images and MP4 videos in a folder for simplistic digital
# signage applications.
#
# TODO: Centralise the keyboard event handling (for quitting)
# TODO: Allow exiting during video playback

import sys, pygame, os, random, time, subprocess, random, threading, argparse
from pygame.locals import *
from threading import Thread

# Scale image, keeping the aspect ratio the same. Slightly modified from the
# original by using smoothscale and casting to int. This produces a much better
# end result when enlarging.
# Frank Raiser http://www.pygame.org/pcr/transform_scale/
def aspect_scale(img,(bx,by)):
    # Scales 'img' to fit into box bx/by.
    # This method will retain the original image's aspect ratio
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by
    return pygame.transform.smoothscale(img, (int(sx),int(sy)))

def wait_a_while(seconds):
    # Display the image for 8 seconds before moving on. Listen for
    # the Escape key to exit.
    for x in range(1, seconds * 2):
        time.sleep (0.5)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit("Told to quit (Escape key pressed)")

# Create command line arguments.
parser = argparse.ArgumentParser()
parser.add_argument("path", help = "Absolute path to the content directory.") # required
parser.add_argument("-q", "--quiet", help="Don't display no content error.", action = "store_true") #optional
parser.add_argument("-r", "--random", help="Sort the content randomly before playback.", action = "store_false") #optional
parser.add_argument("-nc", "--nocointoss", help="Play videos every time they are encountered, don't flip a coin. Default False, coin will be flipped.", action = "store_false") # optional
parser.add_argument("-s", "--seconds", help="Number of seconds to display each image. Default 8 seconds.", default = 8, type = int) # optional
args = parser.parse_args()

print("Loading content from: " + args.path)
included_extensions = ['jpg','jpeg', 'bmp', 'png', 'mp4']

random.seed()
pygame.init()

# Get the current screen resolution and extract the size to more friendly vars.
width, height = pygame.display.Info().current_w, pygame.display.Info().current_h

# Create a new surface - screen res, full screen and 32 bit colour, and hide
# the mouse. Set the window title - it's going to be hidden, but why not.
pygame.display.set_caption('goggl')
display_screen = pygame.display.set_mode((width,height), pygame.FULLSCREEN, 32)
pygame.mouse.set_visible(0)
display_font = pygame.font.SysFont("roboto", 34)

# Loop this continually
while True:
    # Get a list of all the eligible files from the folder, then shuffle them.
    print ("Refreshing content list.")
    file_names = [fn for fn in os.listdir(args.path)
                  if any(fn.endswith(ext) for ext in included_extensions)]

    # Randomisation requested.
    if (args.random):
        random.shuffle(file_names)

    if not file_names:
        # There are no files to display, so display an error/warning message
        # Fill screen with black to remove remnants of the previous image
        # displayed
        display_screen.fill(000000)

        if not args.quiet:
            # We've not been told to be quiet, so display the error on screen
            label = display_font.render("Content location empty.", 1, (255,0,0))
            display_screen.blit(label, (200, 200))
            label = display_font.render(args.path, 1, (255,0,0))
            display_screen.blit(label, (200, 300))

        pygame.display.flip()
        wait_a_while(args.seconds)

    # Print out a list of the files as they will be shown.
    print ("Content to be displayed:")
    x = 1

    for file in file_names:
        print(str(x) + ".\t" + file)
        x = x + 1

    # Loop through all the content, perform appropriate actions.
    for content in file_names:
        # Create a concat path.
        content_fullname = os.path.join(args.path, content)

        if (os.path.isfile(content_fullname)):
            # If an image then display it.
            if (content_fullname.endswith(".jpg")) or (content_fullname.endswith(".jpeg")) or (content_fullname.endswith(".png")) or (content_fullname.endswith(".bmp")):
                # Open the image and scale it to the correct size.
                print("Displaying: " + content_fullname)
                img = pygame.image.load(content_fullname)
                img = aspect_scale(img, (width, height))

                # Fill screen with black to remove remnants of the previous image displayed
                display_screen.fill(000000)

                # Place the resized image in the centre of the screen.
                size = img.get_rect()
                display_screen.blit(img, ((width / 2 - (size.width/2)), (height / 2 - (size.height/2))))

                # Actually update the display.
                pygame.display.flip()
                wait_a_while(args.seconds)

            if (content_fullname.endswith(".mp4")):
                # We want to display videos less frequently, so only show it if
                # the RNG returns 1, unless we have nocointoss flag in which case
                # play it every time.
                if (random.randint(0, 1) or args.nocointoss):

                    print("Displaying Video Content: " + content_fullname)

                    # Look for a subtitle (.srt) file with the same name to use with the video content.
                    sub_path = os.path.splitext(content_fullname)[0] + ".srt"

                    if (os.path.isfile(sub_path)):
                        print ("Found a subtitle (.srt) file: " + sub_path)
                        subprocess.call(["omxplayer", "--subtitles", sub_path, content_fullname])
                    else:
                        subprocess.call(["omxplayer", content_fullname])

                else:
                    print("Skipped Video Content: " + content_fullname)
        else:
            # We've got lost somewhere along the way, this file doesn't exist
            # Quit out of the loop and reload all the files.
            print("Lost a file. Restarting the loop.")
            break
