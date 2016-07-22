# DisplayPy

This small script is used for simple digital signage applications on the
Raspberry Pi. It has been tested on a Pi 3.

It will loop through a folder of videos and pictures, displaying them on the
screen for a period of time. Videos (with or without subtitles) are also
supported through [omxplayer](http://elinux.org/Omxplayer).

## Usage

python displaypy.py /path/to/content [-q|--quiet] [-nf|noflip] [-s|--seconds x]
 [-r|--random]

 * **-q | --quiet** - Do not display an error message if there is no content.
 * **-nc | --nocointoss** - Play a video every time it is encountered, don't flip a coin.
 * **-s | --seconds _x_** - Display each image for _x_ seconds. Default 8.
 * **-r | --random** - Randomise the order the content is displayed.

The only mandatory argument is the path to the content. All others are optional.

## Screen size

This script will automatically determine the resolution of the screen and scale
still images and videos up or down to fit the screen appropriately.

## Content

This script will display the following file formats:

 * \*.jpg \*.jpeg
 * \*.png  
 * \*.bmp  
 * \*.mp4

A list of files is generated at the start of the script, and each item of
content is displayed in sequence for the time determined by the '-s/--seconds'
command line argument. The default is 8 seconds, and obviously videos play for
their full length. The list can be shuffled after it is generated to vary the
order the content is displayed. To do so use the '-r|--random' argument.

Should a file be missing when the script tries to load it, the list of files
will be regenerated and the process will start from the beginning. This allows
the content manager to update the display at any time, adding and removing
images and videos as they see fit. New content will be introduced into the list
once the last item has been displayed instead.

If there is no content in the folder passed from the command line an error
message will be displayed on screen. This can be disabled by
using the '-q/--quiet' command line argument which will cause a black screen to
be displayed.

## Videos

Videos are played in [omxplayer](http://elinux.org/Omxplayer). The content is
filtered to only find MP4 files. There are two Media Encoder presets which are
known to work nicely with the Raspberry Pi 3 in this folder.

Video content is usually much longer and more imposing than slides, therefore
before an MP4 file is played a virtual coin toss occurs. If the random number
generator returns a 1 then the video will play, otherwise it will skip it an
move on to the next item in the list. This behaviour can be disabled with the
'-nf/--noflip' command line argument.

### Subtitles

To display subtitles over videos ensure that the .srt file is named exactly
the same and in the same folder. For example:

/home/kiosk/display/video1.mp4  
/home/kiosk/display/video1.srt

## ToDo

 * Centralise the keyboard handling to allow smooth exit.
 * Allow exit during video playback (currently have to wait for video to finish)
