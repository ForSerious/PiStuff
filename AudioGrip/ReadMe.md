This is the script to streamline my audio enhancement pipeline. It's very rigid and probably only useful to me. Maybe it can make a good starting point for your one script.

This script dictates the control of several programs and bases the commands it generates on predefined variables found in the audio id3 tags.
These are the programs:
* StereoTool from https://www.thimeo.com/stereo-tool/download/
* dBpoweramp Music Converter (DMC) from https://www.dbpoweramp.com/dmc.htm
* an old version of tinytag from https://github.com/tinytag/tinytag
* A little java program I wrote to tame the peaks when the declipper goes a little to far.
* Java, to run that jar file.

and what they are used for:
* StereoTool does calculated frequency restoration, declipping, and auto equalization.
* dBpoweramp does all the audio conversions, resampling and volume leveling.
* comp.jar finds and reduces the volume of peaks above a threshold.
* tinytag reads id3tags for various aspects of the script. (now that I look at it, it could be replaced by DMC.)

# Installation

Once you have those installed, (I'm providing tinytag, but in case I shouldn't be, you know where to get it.)
To get DMC working, you will need to make a python script that can read the scripting DLL that comes with it.
I don't remember exactly what I used, but it generated the dMC.py provided in this repo.
(My guess is that it won't just work on every other computer. [I'll probably have to not include it if that's the case.])

Set the globals.
* DEBUG. Adds some printouts.
* VERSION_NUMBER. Used to mark what version of the sts file was used. This gets added to the comments tag in the audio file.
* DBPOWER. Full path to dBpoweramp CoreConverter.exe with quotes.
* DBOUTPATH. Full path to the intermediate folder where audio is converted to wav. No quotes.
* FINALOUT. Full path to folder where the final flac files should go. No quotes.
* STTOOL. Full path to stereo_tool_cmd.exe. With quotes.
* STSPATH. Full path to folder where the sts files are stored. No quotes.
* RECOMPPATH. Full path to the intermediate folder where wav files are written to by the comp.jar. No quotes.
* DUMMYPATH. Full path to a folder containing a bunch of short files that are used to reduce the amount of glitched files. There's a bug where if you start converting a bunch of songs at the same time, they somehow share data across conversions.
* FOLDERLISTPATH. Full path to the ArtisiList.txt file. With quotes.
* PREDIR. Path to the top folder where every artist folder can be found that's listed in ArtisiList.txt. No quotes.
* LOGPATH. Full path and file name of the results log file you want written. With quotes.
* JAVAPATH. Full path to java.exe. With quotes.
* COMPJARPATH. Full path to the provided comp.jar file. With quotes.
* STEREOKEY. Your Stereo Tool Key. No quotes. Include the open and close wakas.
* NUMBEROFCORES. Don't include hyperthreaded cores. I have 12 cores, I could probably do 16… but 12 seems heavy enough on the CPU.


Stereo Tool uses sts files. By default, this script looks for one named H.sts. You'll have to learn the ways of Stereo Tool to generate your own sts files. If you need to override what sts files gets used you can add an sts entry to the id3 tag any song needing it with the dBpoweramp tag editor.
In fact that is how to control the main things that happen to each music file that gets processed.
Guiding tags:
* gain. Amount of dB that should be applied to the final file. (examples: 1.4, -4.7) This is needed for albums that have no gap between tracks.
* reco. Any value put in here will stop the comp.jar from running on this song.
* trim. The amount of milliseconds to be trimmed from the start of the audio file. Some of the features of Stereo Tool take a noticeable second to kick in. Duplicating the start of the song, and using this to cut it off corrects that.
* trim2. the amount of milliseconds to be trimmed from the end of the audio file.
* sts. The sts file to use. Uses H.sts if left blank. I made a bunch to sts files for the various issues songs have. H for high like CD sourced audio. M for medium for anything without frequencies above 15kHz. L for low for songs without frequencies above 11kHz. And so on.


# Usage
Once you have at least one sts file defined named H.sts
Fill out the ArtisiList.txt file with the lower folders you want all the audio files processed in.
I like to run it in the Python IDLE with F5 since it opens separate command prompts for each file.