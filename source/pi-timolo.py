#!/usr/bin/python

# pi-timolo - Raspberry Pi Long Duration Timelapse, Motion Tracking, with Low Light Capability
# written by Claude Pageau Jul-2017 (release 7.x)
# This release uses OpenCV to do Motion Tracking.  It requires updated config.py

progVer = "ver 9.1"
__version__ = "9.1"   # May test for version number at a future time

import datetime
import logging
import os
import sys
import subprocess
import shutil
import glob

mypath = os.path.abspath(__file__)  # Find the full path of this python script
baseDir = os.path.dirname(mypath)   # get the path location only (excluding script name)
baseFileName = os.path.splitext(os.path.basename(mypath))[0]
progName = os.path.basename(__file__)
logFilePath = os.path.join(baseDir, baseFileName + ".log")

print("----------------------------------------------------------------------------------------------")
print("%s %s  written by Claude Pageau" %( progName, progVer ))
print("INFO  - Initializing ....")

# Check that pi camaera module is installed and enabled
camResult = subprocess.check_output("vcgencmd get_camera", shell=True)
camResult = camResult.decode("utf-8")
camResult = camResult.replace("\n", "")
if (camResult.find("0")) >= 0:   # Was a 0 found in vcgencmd output
    print("ERROR - Pi Camera Module Not Found %s" % camResult)
    print("        if supported=0 Enable Camera using command sudo raspi-config")
    print("        if detected=0 Check Pi Camera Module is Installed Correctly")
    print("INFO  - Exiting %s Due to Error" % progName)
    quit()
else:
    print("INFO  - Pi Camera Module is Enabled and Connected %s" % camResult )

# Check for config.py variable file to import and error out if not found.
configFilePath = os.path.join(baseDir, "config.py")
if not os.path.exists(configFilePath):
    print("ERROR - Cannot Import Configuration Variables. Missing Configuration File %s" % ( configFilePath ))
    quit()
else:
    # Read Configuration variables from config.py file
    print("INFO  - Import Configuration Variables from File %s" % ( configFilePath ))
    from config import *

if pluginEnable:     # Check and verify plugin and load variable overlay
    pluginDir = os.path.join(baseDir,"plugins")
    if pluginName.endswith('.py'):      # Check if there is a .py at the end of pluginName variable
        pluginName = pluginName[:-3]    # Remove .py extensiion
    pluginPath = os.path.join(pluginDir, pluginName + '.py')
    print("INFO  - pluginEnabled - loading pluginName %s" % pluginPath)
    if not os.path.isdir(pluginDir):
        print("ERROR - plugin Directory Not Found at %s" % pluginDir )
        print("        Suggest you Rerun github curl install script to install plugins")
        print("        https://github.com/pageauc/pi-timolo/wiki/How-to-Install-or-Upgrade#quick-install")
        print("INFO  - Exiting %s Due to Error" % progName)
        quit()

    elif not os.path.exists(pluginPath):
        print("ERROR - File Not Found pluginName %s" % pluginPath )
        print("        Check Spelling of pluginName Value in %s" % configFilePath)
        print("        ------- Valid Names -------")
        validPlugin = glob.glob(pluginDir + "/*py")
        validPlugin.sort()
        for entry in validPlugin:
            pluginFile = os.path.basename(entry)
            plugin = pluginFile.rsplit('.', 1)[0]
            if not ((plugin == "__init__") or (plugin == "current")):
                print("        %s"  % plugin)
        print("        ------- End of List -------")
        print("        Note: pluginName Should Not have .py Ending.")
        print("INFO  - or Rerun github curl install command.  See github wiki")
        print("        https://github.com/pageauc/pi-timolo/wiki/How-to-Install-or-Upgrade#quick-install")
        print("INFO  - Exiting %s Due to Error" % progName)
        quit()
    else:
        pluginCurrent = os.path.join(pluginDir, "current.py")
        try:    # Copy image file to recent folder
            print("INFO  - Copy %s to %s" %( pluginPath, pluginCurrent ))
            shutil.copy(pluginPath, pluginCurrent)
        except OSError as err:
            print('ERROR - Copy Failed from %s to %s - %s' % ( pluginPath, pluginCurrent, err))
            Pring("        Check permissions, disk space, Etc.")
            print("INFO  - Exiting %s Due to Error" % progName)
            quit()
        print("INFO  - Import Plugin %s" % pluginPath)
        sys.path.insert(0,pluginDir)    # add plugin directory to program PATH
        from plugins.current import *
        try:
            if os.path.exists(pluginCurrent):
                os.remove(pluginCurrent)
            pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
            if os.path.exists(pluginCurrentpyc):
                os.remove(pluginCurrentpyc)
        except OSError as err:
            print("ERROR - Failed Removal of %s - %s" % ( pluginCurrentpyc, err ))
            print("INFO  - Exiting %s Due to Error" % progName)

else:
    print("INFO  - No Plugins Enabled per pluginEnable=%s" % pluginEnable)

# Setup Logging now that variables are imported from config.py
if logDataToFile:
    print("INFO  - Sending Logging Data to %s  (Console Messages Disabled)" %( logFilePath ))
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=logFilePath,
                    filemode='w')
elif verbose:
    print("INFO  - Logging to Console per Variable verbose=True")
    logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
else:
    logging.basicConfig(level=logging.CRITICAL,
                    format='%(asctime)s %(levelname)-8s %(funcName)-10s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

print("INFO  - Loading Python Libraries Please Wait ...")  # import remaining python libraries
try:
    import cv2
except:
    if (sys.version_info > (2, 9)):
        print("ERROR - python3 Failed to import cv2 opencv ver 3.x")
        print("        Try installing opencv for python3")
        print("        see https://github.com/pageauc/opencv3-setup")
    else:
        print("ERROR - python2 Failed to import cv2")
        print("        Try reinstalling per command")
        print("        sudo apt-get install python-opencv")
    print("INFO  - Exiting %s Due to Error" % progName)
    quit()

try:
    from picamera import PiCamera
except:
    print("ERROR - Problem importing picamera module")
    print("        Try command below to import module")
    print("")
    if (sys.version_info > (2, 9)):
        print("        sudo apt-get install python3-picamera")
    else:
        print("        sudo apt-get install python-picamera")
    print("")
    print("INFO  - Exiting %s Due to Error" % progName)
    quit()

from picamera.array import PiRGBArray
import picamera.array

# For python3 install of pyexiv2 lib See https://github.com/pageauc/pi-timolo/issues/79
try:  # Bypass pyexiv2 if library Not Found  (Transfers image exif data in writeTextToImage)
    import pyexiv2
except:
    pass

import time
import math
from threading import Thread
import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from fractions import Fraction

#==================================
#      System Variables
# Should Not need to be customized
#==================================
SECONDS2MICRO = 1000000    # Used to convert from seconds to microseconds
nightMaxShut = int(nightMaxShutSec * SECONDS2MICRO)  # default=5 sec IMPORTANT- 6 sec works sometimes but occasionally locks RPI and HARD reboot required to clear
darkAdjust = int((SECONDS2MICRO/5.0) * nightDarkAdjust)
testWidth = 128            # width of rgb image stream used for timelapse day/night changes
testHeight = 80            # height of rgb image stream used for timelapse day/night changes
daymode = False            # default should always be False.
motionPath = os.path.join(baseDir, motionDir)  # Store Motion images
motionNumPath = os.path.join(baseDir, motionPrefix + baseFileName + ".dat")  # dat file to save currentCount
motionStreamStopSec = 0.5  # default= 0.5 seconds  Time to close stream thread
timelapsePath = os.path.join(baseDir, timelapseDir)  # Store Time Lapse images
timelapseNumPath = os.path.join(baseDir, timelapsePrefix + baseFileName + ".dat")  # dat file to save currentCount
lockFilePath = os.path.join(baseDir, baseFileName + ".sync")

# Video Stream Settings for motion Tracking using opencv motion tracking
CAMERA_WIDTH = 640     # width of video stream
CAMERA_HEIGHT = 480    # height of video stream
bigImage = motionTrackQPBigger  # increase size of motionTrackQuickPic image
bigImageWidth = int(CAMERA_WIDTH * bigImage)
bigImageHeight = int(CAMERA_HEIGHT * bigImage)
CAMERA_FRAMERATE = motionTrackFrameRate  # camera framerate
TRACK_TRIG_LEN = motionTrackTrigLen  # Length of track to trigger speed photo
TRACK_TRIG_LEN_MIN = int(motionTrackTrigLen / 4)
TRACK_TRIG_LEN_MAX = int(CAMERA_HEIGHT / 2)  # Set max over triglen allowed half cam height
TRACK_TIMEOUT = motionTrackTimeOut   # Timeout seconds Stops motion tracking when no activity
MIN_AREA = motionTrackMinArea    # OpenCV Contour sq px area must be greater than this.

BLUR_SIZE = 10              # OpenCV setting for Gaussian difference image blur
THRESHOLD_SENSITIVITY = 20  # OpenCV setting for difference image threshold

#-----------------------------------------------------------------------------------------------
class PiVideoStream:
    def __init__(self, resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAMERATE, rotation=0, hflip=False, vflip=False):
        # initialize the camera and stream
        try:
           self.camera = PiCamera()
        except:
           print("ERROR - PiCamera Already in Use by Another Process")
           print("INFO  - Exiting %s Due to Error" % progName)
           quit()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.camera.rotation = rotation
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        # initialize the frame and the variable used to indicate
        # if the thread should be stopped
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

#-----------------------------------------------------------------------------------------------
def userMotionCodeHere():
    # Users can put code here that needs to be run prior to taking motion capture images
    # Eg Notify or activate something.

    # User code goes here

    return

#-----------------------------------------------------------------------------------------------
def shut2Sec (shutspeed):
    shutspeedSec = shutspeed/float(SECONDS2MICRO)
    shutstring = str("%.4f") % ( shutspeedSec )
    return shutstring

#-----------------------------------------------------------------------------------------------
def showTime():
    rightNow = datetime.datetime.now()
    currentTime = ("%04d-%02d-%02d %02d:%02d:%02d" % (rightNow.year, rightNow.month, rightNow.day,
    rightNow.hour, rightNow.minute, rightNow.second))
    return currentTime

#-----------------------------------------------------------------------------------------------
def showDots(dotcnt):
    if motionDotsOn:
        if motionTrackOn and verbose:
            dotcnt += 1
            if dotcnt > motionDotsMax + 2:
                print("")
                dotcnt = 0
            elif dotcnt > motionDotsMax:
                print("")
                stime = showTime() + " ."
                sys.stdout.write(stime)
                sys.stdout.flush()
                dotcnt = 0
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
        return dotcnt

#-----------------------------------------------------------------------------------------------
def checkConfig():
    if not motionTrackOn and not timelapseOn:
        logging.warning("Both Motion and Timelapse are turned OFF - motionTrackOn=%s timelapseOn=%s", motionTrackOn, timelapseOn)
        sys.exit(2)

#-----------------------------------------------------------------------------------------------
def displayInfo(motioncount, timelapsecount):
    if verbose:
        print("-------------------------------------- Settings ----------------------------------------------")
        print("Config File .. configName=%s  configTitle=%s" % (configName, configTitle))
        print("     Plugin .. pluginEnable=%s  pluginName=%s (Overlays config.py Settings)" % (pluginEnable, pluginName))
        print("")
        print("Image Info ... Size=%ix%i  Prefix=%s  VFlip=%s  HFlip=%s  Rotation=%i  Preview=%s"
              % (imageWidth, imageHeight, imageNamePrefix, imageVFlip, imageHFlip, imageRotation, imagePreview))
        print("               JpegQuality=%i 1=highest 40=lowest" % ( imageJpegQuality ))
        print("   Low Light.. nightTwilightThreshold=%i  nightDarkThreshold=%i  nightBlackThreshold=%i"
                           % ( nightTwilightThreshold, nightDarkThreshold, nightBlackThreshold ))
        print("               nightMaxShutSec=%.2f  nightMaxISO=%i  nightDarkAdjust=%.2f  nightSleepSec=%i"
                           % ( nightMaxShutSec, nightMaxISO, nightDarkAdjust, nightSleepSec ))
        print("   No Shots .. noNightShots=%s   noDayShots=%s" % ( noNightShots, noDayShots ))
        if showDateOnImage:
            print("   Img Text .. On=%s  Bottom=%s (False=Top)  WhiteText=%s (False=Black)  showTextWhiteNight=%s"
                         % ( showDateOnImage, showTextBottom, showTextWhite, showTextWhiteNight ))
            print("               showTextFontSize=%i px height" % (showTextFontSize))
        else:
            print("    No Text .. showDateOnImage=%s  Text on Image is Disabled"  % (showDateOnImage))
        print("")
        if motionTrackOn:
            print("Motion Track.. On=%s  Prefix=%s  MinArea=%i sqpx  TrigLen=%i-%i px  TimeOut=%i sec"
                             % (motionTrackOn, motionPrefix, motionTrackMinArea,
                                                      motionTrackTrigLen, TRACK_TRIG_LEN_MAX, motionTrackTimeOut))
            print("               motionTrackInfo=%s   motionDotsOn=%s"  % ( motionTrackInfo, motionDotsOn ))
            print("   Stream .... size=%ix%i  framerate=%i fps  motionStreamStopSec=%.2f  QuickPic=%s" %
                                  ( CAMERA_WIDTH, CAMERA_HEIGHT, motionTrackFrameRate, motionStreamStopSec, motionTrackQuickPic ))
            print("   Img Path .. motionPath=%s  motionCamSleep=%.2f sec" % (motionPath, motionCamSleep))
            print("   Force ..... forceTimer=%i min (If No Motion)"  % (motionForce/60))
            if motionNumOn:
                print("   Num Seq ... motionNumOn=%s  numRecycle=%s  numStart=%i   numMax=%i  current=%s"
                                   % (motionNumOn, motionNumRecycle, motionNumStart, motionNumMax, motioncount))
                print("   Num Path .. motionNumPath=%s " % (motionNumPath))

            else:
                print("   Date-Time.. motionNumOn=%s  Image Numbering is Disabled" % (motionNumOn))
            if motionQuickTLOn:
                print("   Quick TL .. motionQuickTLOn=%s   motionQuickTLTimer=%i sec  motionQuickTLInterval=%i sec (0=fastest)"
                                   % (motionQuickTLOn, motionQuickTLTimer, motionQuickTLInterval))
            else:
                print("   Quick TL .. motionQuickTLOn=%s  Quick Time Lapse Disabled" % (motionQuickTLOn))
            if motionVideoOn:
                print("   Video ..... motionVideoOn=%s   motionVideoTimer=%i sec  motionVideoFPS=%i (superseded by QuickTL)"
                                   % (motionVideoOn, motionVideoTimer, motionVideoFPS))
            else:
                print("   Video ..... motionVideoOn=%s  Motion Video is Disabled" % (motionVideoOn))
            print("   Sub-Dir ... motionSubDirMaxHours=%i (0-off)  motionSubDirMaxFiles=%i (0=off)" %
                                ( motionSubDirMaxHours, motionSubDirMaxFiles ))
            print("   Recent .... motionRecentMax=%i (0=off)  motionRecentDir=%s" %
                                ( motionRecentMax, motionRecentDir ))
        else:
            print("Motion ....... motionTrackOn=%s  Motion Tracking is Disabled)" % (motionTrackOn))
        print("")
        if timelapseOn:
            print("Time Lapse ... On=%s  Prefix=%s   Timer=%i sec   timelapseExitSec=%i (0=Continuous)"
                        % (timelapseOn, timelapsePrefix, timelapseTimer, timelapseExitSec))
            print("               timelapseMaxFiles=%i" % ( timelapseMaxFiles ))
            print("   Img Path .. timelapsePath=%s  timelapseCamSleep=%.2f sec" % (timelapsePath, timelapseCamSleep))
            if timelapseNumOn:
                print("   Num Seq ... On=%s  numRecycle=%s  numStart=%i   numMax=%i  current=%s"
                          % (timelapseNumOn, timelapseNumRecycle, timelapseNumStart, timelapseNumMax, timelapsecount))
                print("   Num Path .. numPath=%s" % (timelapseNumPath))
            else:
                print("   Date-Time.. motionNumOn=%s  Numbering Disabled" % (timelapseNumOn))
            print("   Sub-Dir ... timelapseSubDirMaxHours=%i (0=off)  timelapseSubDirMaxFiles=%i (0=off)" %
                                ( timelapseSubDirMaxHours, timelapseSubDirMaxFiles ))
            print("   Recent .... timelapseRecentMax=%i (0=off)  timelapseRecentDir=%s" %
                                ( timelapseRecentMax, timelapseRecentDir ))
            if createLockFile:
                print("")
                print("gdrive Sync .. On=%s  Path=%s  Note: syncs for motion images only." % (createLockFile, lockFilePath))
        else:
            print("Time Lapse ... timelapseOn=%s  Timelapse is Disabled" % (timelapseOn))
        print("")
        if spaceTimerHrs > 0:   # Check if disk mgmnt is enabled
            print("Disk Space  .. Enabled - Manage Target Free Disk Space. Delete Oldest %s Files if Required" % (spaceFileExt))
            print("               Check Every spaceTimerHrs=%i (0=off)  Target spaceFreeMB=%i (min=100 MB)  spaceFileExt=%s" %
                                 (spaceTimerHrs, spaceFreeMB, spaceFileExt))
            print("               Delete Oldest spaceFileExt=%s  spaceMediaDir=%s" %
                                 ( spaceFileExt, spaceMediaDir))
        else:
            print("Disk Space  .. spaceTimerHrs=%i (Disabled) - Manage Target Free Disk Space. Delete Oldest %s Files" %
                                   ( spaceTimerHrs, spaceFileExt))
            print("            .. Check Every spaceTimerHrs=%i (0=Off)  Target spaceFreeMB=%i (min=100 MB)" %
                                             ( spaceTimerHrs, spaceFreeMB))
        print("")
        print("Logging ...... verbose=%s (True=Enabled False=Disabled)" % ( verbose ))
        print("   Log Path .. logDataToFile=%s  logFilePath=%s" % ( logDataToFile, logFilePath ))
        print("------------------------------------ Log Activity --------------------------------------------")
    checkConfig()

#-----------------------------------------------------------------------------------------------
def subDirLatest(directory): # Scan for directories and return most recent
    dirList = [ name for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name)) ]
    if len(dirList) > 0:
        lastSubDir = sorted(dirList)[-1]
        lastSubDir = os.path.join(directory, lastSubDir)
    else:
        lastSubDir = directory
    return lastSubDir

#-----------------------------------------------------------------------------------------------
def subDirCreate(directory, prefix):
    now = datetime.datetime.now()
    # Specify folder naming
    subDirName = ('%s%d-%02d-%02d-%02d%02d' % (prefix, now.year, now.month, now.day, now.hour, now.minute))
    subDirPath = os.path.join(directory, subDirName)
    if not os.path.exists(subDirPath):
        try:
            os.makedirs(subDirPath)
        except OSError as err:
            logging.error('Cannot Create Directory %s - %s, using default location.', subDirPath, err)
            subDirPath = directory
        else:
            logging.info('Created %s', subDirPath)
    else:
        subDirPath = directory
    return subDirPath

#-----------------------------------------------------------------------------------------------
def subDirCheckMaxFiles(directory, filesMax):  # Count number of files in a folder path
    fileList = glob.glob(directory + '/*jpg')
    count = len(fileList)
    if count > filesMax:
        makeNewDir = True
        dotCount = showDots(motionDotsMax + 2)
        logging.info('Total Files in %s Exceeds %i ' % ( directory, filesMax ))
    else:
        makeNewDir = False
    return makeNewDir

#-----------------------------------------------------------------------------------------------
def subDirCheckMaxHrs(directory, hrsMax, prefix):   # Note to self need to add error checking
    # extract the date-time from the directory name
    dirName = os.path.split(directory)[1]   # split dir path and keep dirName
    dirStr = dirName.replace(prefix,'')   # remove prefix from dirName so just date-time left
    dirDate = datetime.datetime.strptime(dirStr, "%Y-%m-%d-%H:%M")  # convert string to datetime
    rightNow = datetime.datetime.now()   # get datetime now
    diff =  rightNow - dirDate           # get time difference between dates
    days, seconds = diff.days, diff.seconds
    dirAgeHours = days * 24 + seconds // 3600  # convert to hours
    if dirAgeHours > hrsMax:   # See if hours are exceeded
        makeNewDir = True
        dotCount = showDots(motionDotsMax + 2)
        logging.info('MaxHrs %i Exceeds %i for %s' % ( dirAgeHours, hrsMax, directory ))
    else:
        makeNewDir = False
    return makeNewDir

#-----------------------------------------------------------------------------------------------
def subDirChecks(maxHours, maxFiles, directory, prefix):
    # Check if motion SubDir needs to be created
    if maxHours < 1 and maxFiles < 1:  # No Checks required
        # logging.info('No sub-folders Required in %s', directory)
        subDirPath = directory
    else:
        subDirPath = subDirLatest(directory)
        if subDirPath == directory:   # No subDir Found
            logging.info('No sub folders Found in %s' % directory)
            subDirPath = subDirCreate(directory, prefix)
        elif ( maxHours > 0 and maxFiles < 1 ):   # Check MaxHours Folder Age Only
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                subDirPath = subDirCreate(directory, prefix)
        elif ( maxHours < 1 and maxFiles > 0):   # Check Max Files Only
            if subDirCheckMaxFiles(subDirPath, maxFiles):
                subDirPath = subDirCreate(directory, prefix)
        elif maxHours > 0 and maxFiles > 0:   # Check both Max Files and Age
            if subDirCheckMaxHrs(subDirPath, maxHours, prefix):
                if subDirCheckMaxFiles(subDirPath, maxFiles):
                    subDirPath = subDirCreate(directory, prefix)
                else:
                    logging.info('MaxFiles Not Exceeded in %s', subDirPath)
    os.path.abspath(subDirPath)
    return subDirPath

#-----------------------------------------------------------------------------------------------
def checkMediaPaths():
    # Checks for image folders and creates them if they do not already exist.
    if motionTrackOn:
        if not os.path.isdir(motionPath):
            logging.info("INFO  - Create Motion Media Folder %s", motionPath)
            try:
                os.makedirs(motionPath)
            except OSError as err:
                print("ERROR - Could Not Create %s - %s" % (motionPath, err))
                quit()
            if os.path.exists(motionNumPath):
                logging.info("INFO  - Delete Motion dat File %s", motionNumPath)
                os.remove(motionNumPath)

    if timelapseOn:
        if not os.path.isdir(timelapsePath):
            logging.info("INFO  - Create TimeLapse Image Folder %s", timelapsePath)
            try:
                os.makedirs(timelapsePath)
            except OSError as err:
                print("ERROR - Could Not Create %s - %s" % ( motionPath, err ))
                quit()
            if os.path.exists(timelapseNumPath):
               print("INFO  - Delete TimeLapse dat file %s" % timelapseNumPath)
               os.remove(timelapseNumPath)

    # Check for Recent Image Folders and create if they do not already exist.
    if motionRecentMax > 0:
        if not os.path.isdir(motionRecentDir):
            logging.info("INFO  - Create Motion Recent Folder %s", motionRecentDir)
            try:
                os.makedirs(motionRecentDir)
            except OSError as err:
                print('ERROR - Failed to Create %s - %s' % ( motionRecentDir, err ))
                quit()

    if timelapseRecentMax > 0:
        if not os.path.isdir(timelapseRecentDir):
            print("INFO  - Create TimeLapse Recent Folder %s" % timelapseRecentDir)
            try:
                os.makedirs(timelapseRecentDir)
            except OSError as err:
                print('ERROR - Failed to Create %s - %s' % ( timelapseRecentDir, err ))
                quit()

#-----------------------------------------------------------------------------------------------
def deleteOldFiles(maxFiles, dirPath, prefix):
    # Delete Oldest files gt or eq to maxfiles that match filename prefix
    try:
        fileList = sorted(glob.glob(os.path.join(dirPath, prefix + '*')), key=os.path.getmtime)
    except OSError as err:
        logging.error('Problem Reading Directory %s - %s', dirPath, err)
    else:
        while len(fileList) >= maxFiles:
            oldest = fileList[0]
            oldestFile = oldest
            try:   # Remove oldest file in recent folder
                fileList.remove(oldest)
                os.remove(oldestFile)
            except OSError as err:
                logging.error('Cannot Remove %s - %s', oldestFile, err)

#-----------------------------------------------------------------------------------------------
def saveRecent(recentMax, recentDir, filename, prefix):
    # save specified most recent files (timelapse and/or motion) in recent subfolder
    deleteOldFiles(recentMax, recentDir, prefix)
    try:    # Copy image file to recent folder
        shutil.copy(filename, recentDir)
    except OSError as err:
        logging.error('Copy from %s to %s - %s', filename, oldestFile, err)

#-----------------------------------------------------------------------------------------------
def filesToDelete(mediaDirPath, extension=imageFormat):
    return sorted(
        (os.path.join(dirname, filename)
        for dirname, dirnames, filenames in os.walk(mediaDirPath)
        for filename in filenames
        if filename.endswith(extension)),
        key=lambda fn: os.stat(fn).st_mtime, reverse=True)

#-----------------------------------------------------------------------------------------------
def freeSpaceUpTo(spaceFreeMB, mediaDir, extension=imageFormat):
    # Walks mediaDir and deletes oldest files until spaceFreeMB is achieved
    # Use with Caution
    mediaDirPath = os.path.abspath(mediaDir)
    if os.path.isdir(mediaDirPath):
        MB2Bytes = 1048576  # Conversion from MB to Bytes
        targetFreeBytes = spaceFreeMB * MB2Bytes
        fileList = filesToDelete(mediaDir, extension)
        totFiles = len(fileList)
        delcnt = 0
        logging.info('Session Started')
        while fileList:
            statv = os.statvfs(mediaDirPath)
            availFreeBytes = statv.f_bfree*statv.f_bsize
            if availFreeBytes >= targetFreeBytes:
                break
            filePath = fileList.pop()
            try:
                os.remove(filePath)
            except OSError as err:
                logging.error('Del Failed %s', filePath)
                logging.error('Error: %s', err)
            else:
                delcnt += 1
                logging.info('Del %s', filePath)
                logging.info('Target=%i MB  Avail=%i MB  Deleted %i of %i Files ',
                                   targetFreeBytes / MB2Bytes, availFreeBytes / MB2Bytes, delcnt, totFiles )
                if delcnt > totFiles / 4:  # Avoid deleting more than 1/4 of files at one time
                    logging.warning('Max Deletions Reached %i of %i', delcnt, totFiles)
                    logging.warning('Deletions Restricted to 1/4 of total files per session.')
                    break
        logging.info('Session Ended')
    else:
        logging.error('Directory Not Found - %s', mediaDirPath)

#-----------------------------------------------------------------------------------------------
def freeDiskSpaceCheck(lastSpaceCheck):
    if spaceTimerHrs > 0:   # Check if disk free space timer hours is enabled
        # See if it is time to do disk clean-up check
        if ((datetime.datetime.now() - lastSpaceCheck).total_seconds() > spaceTimerHrs * 3600):
            lastSpaceCheck = datetime.datetime.now()
            if spaceFreeMB < 100:   # set freeSpaceMB to reasonable value if too low
                diskFreeMB = 100
            else:
                diskFreeMB = spaceFreeMB
            logging.info('spaceTimerHrs=%i  diskFreeMB=%i  spaceMediaDir=%s spaceFileExt=%s',
                           spaceTimerHrs, diskFreeMB, spaceMediaDir, spaceFileExt)
            freeSpaceUpTo(diskFreeMB, spaceMediaDir, spaceFileExt)
    return lastSpaceCheck

#-----------------------------------------------------------------------------------------------
def getCurrentCount(numberpath, numberstart):
    # Create a .dat file to store currentCount or read file if it already Exists
    # Create numberPath file if it does not exist
    if not os.path.exists(numberpath):
        logging.info("Creating New File %s numberstart= %s", numberpath, numberstart)
        open(numberpath, 'w').close()
        f = open(numberpath, 'w+')
        f.write(str(numberstart))
        f.close()
    # Read the numberPath file to get the last sequence number
    with open(numberpath, 'r') as f:
        writeCount = f.read()
        f.closed
        try:
            numbercounter = int(writeCount)
        except ValueError:   # Found Corrupt dat file since cannot convert to integer
            # Try to determine if this is motion or timelapse
            if numberpath.find(motionPrefix) > 0:
                filePath = motionPath + "/*" + imageFormat
                fprefix = motionPath + motionPrefix + imageNamePrefix
            else:
                filePath = timelapsePath + "/*" + imageFormat
                fprefix = timelapsePath + timelapsePrefix + imageNamePrefix
            try:
               # Scan image folder for most recent file and try to extract numbercounter
                newest = max(glob.iglob(filePath), key=os.path.getctime)
                writeCount = newest[len(fprefix)+1:newest.find(imageFormat)]
            except:
                writeCount = numberstart
            try:
                numbercounter = int(writeCount)+1
            except ValueError:
                numbercounter = numberstart
            logging.error("Invalid Data in %s Reset Counter to %s", numberpath, numbercounter)

        f = open(numberpath, 'w+')
        f.write(str(numbercounter))
        f.close()
        f = open(numberpath, 'r')
        writeCount = f.read()
        f.closed
        numbercounter = int(writeCount)
    return numbercounter

#-----------------------------------------------------------------------------------------------
def writeTextToImage(imagename, datetoprint, daymode):
    # function to write date/time stamp directly on top or bottom of images.
    if showTextWhite:
        FOREGROUND = ( 255, 255, 255 )  # rgb settings for white text foreground
        textColour = "White"
    else:
        FOREGROUND = ( 0, 0, 0 )  # rgb settings for black text foreground
        textColour = "Black"
        if showTextWhiteNight and ( not daymode):
            FOREGROUND = ( 255, 255, 255 )  # rgb settings for black text foreground
            textColour = "White"

    img = cv2.imread(imagename)
    height, width, channels = img.shape
    # centre text and compensate for graphics text being wider
    x = int((width/2) - (len(imagename)*2))
    if showTextBottom:
        y = (height - 50)  # show text at bottom of image
    else:
        y = 10  # show text at top of image

    TEXT = imageNamePrefix + datetoprint
    font_path = '/usr/share/fonts/truetype/freefont/FreeSansBold.ttf'
    font = ImageFont.truetype(font_path, showTextFontSize, encoding='unic')
    try:
        text = TEXT.decode('utf-8')   # required for python2
    except:
        text = TEXT   # Just set for python3
        pass
    img = Image.open(imagename)

    # For python3 install of pyexiv2 lib See https://github.com/pageauc/pi-timolo/issues/79
    try:  # Read exif data since ImageDraw does not save this metadata
        metadata = pyexiv2.ImageMetadata(imagename)
        metadata.read()
    except:
        pass

    draw = ImageDraw.Draw(img)
    # draw.text((x, y),"Sample Text",(r,g,b))
    draw.text(( x, y ), text, FOREGROUND, font=font)
    img.save(imagename)
    logging.info("Added %s Text [ %s ]", textColour, datetoprint)

    try:
        metadata.write()    # Write previously saved exif data to image file
    except:
        logging.warn("Image EXIF Data Not Transferred.")
        pass

    logging.info("%s" % imagename)

#-----------------------------------------------------------------------------------------------
def postImageProcessing(numberon, counterstart, countermax, counter, recycle, counterpath, filename, daymode):
    # If required process text to display directly on image
    if (not motionVideoOn):
        rightNow = datetime.datetime.now()
        if showDateOnImage:
            dateTimeText = ("%04d%02d%02d_%02d:%02d:%02d"
                         % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second))
            if numberon:
                counterStr = "%i    "  % ( counter )
                imageText =  counterStr + dateTimeText
            else:
                imageText = dateTimeText
            # Now put the imageText on the current image
            writeTextToImage(filename, imageText, daymode)
        if createLockFile and motionTrackOn:
            createSyncLockFile(filename)
    # Process currentCount for next image if number sequence is enabled
    if numberon:
        counter += 1
        if countermax > 0:
            if (counter > counterstart + countermax):
                if recycle:
                    counter = counterstart
                else:
                    logging.info("Exceeded Image Count numberMax=%i" % ( countermax ))
                    logging.info("Exiting %s" % progName)
                    sys.exit(2)
        # write next image counter number to dat file
        writeCount = str(counter)
        if not os.path.exists(counterpath):
            logging.info("Create New Counter File writeCount=%s %s", writeCount, counterpath)
            open(counterpath, 'w').close()
        f = open(counterpath, 'w+')
        f.write(str(writeCount))
        f.close()
        logging.info("Next Counter=%s %s", writeCount, counterpath)
    return counter

#-----------------------------------------------------------------------------------------------
def getVideoName(path, prefix, numberon, counter):
    # build image file names by number sequence or date/time
    if numberon:
        if motionVideoOn or videoRepeatOn:
            filename = os.path.join(path, prefix + str(counter) + ".h264")
    else:
        if motionVideoOn or videoRepeatOn:
            rightNow = datetime.datetime.now()
            filename = ("%s/%s%04d%02d%02d-%02d%02d%02d.h264"
                     % ( path, prefix ,rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second))
    return filename

#-----------------------------------------------------------------------------------------------
def getImageName(path, prefix, numberon, counter):
    # build image file names by number sequence or date/time
    if numberon:
        filename = os.path.join(path, prefix + str(counter) + imageFormat)
    else:
        rightNow = datetime.datetime.now()
        filename = ("%s/%s%04d%02d%02d-%02d%02d%02d%s"
                 % ( path, prefix ,rightNow.year, rightNow.month, rightNow.day,
                    rightNow.hour, rightNow.minute, rightNow.second, imageFormat))
    return filename


#-----------------------------------------------------------------------------------------------
def takeTrackQuickPic(image, filename):
    big_image = cv2.resize(image, (bigImageWidth, bigImageHeight))
    cv2.imwrite(filename, big_image)
    logging.info("Saved %ix%i Image to %s", bigImageWidth, bigImageHeight, filename)

#-----------------------------------------------------------------------------------------------
def takeDayImage(filename, cam_sleep_time):
    # Take a Day image using exp=auto and awb=auto
    with picamera.PiCamera() as camera:
        camera.resolution = (imageWidth, imageHeight)
        camera.framerate = 80
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        camera.rotation = imageRotation # Valid values 0, 90, 180, 270
        # Day Automatic Mode
        camera.exposure_mode = 'auto'
        camera.awb_mode = 'auto'
        time.sleep(cam_sleep_time)   # use motion or TL camera sleep to get AWB
        if imagePreview:
            camera.start_preview()
        if imageFormat == ".jpg":   # Set quality if image is jpg
            camera.capture(filename, quality=imageJpegQuality)
        else:
            camera.capture(filename)
        camera.close()
    logging.info("camSleepSec=%.2f exp=auto awb=auto Size=%ix%i "
              % ( cam_sleep_time, imageWidth, imageHeight ))
    if not showDateOnImage:   # showDateOnImage displays FilePath so avoid showing twice
        logging.info("FilePath  %s" % (filename))

#-----------------------------------------------------------------------------------------------
def getShut(pxAve):
    px = pxAve + 1  # avoid division by zero
    offset = nightMaxShut - ((nightMaxShut / float(nightDarkThreshold) * px))
    brightness = offset * (1/float(nightDarkAdjust))
    shut = (nightMaxShut * (1 / float(px))) + brightness # hyperbolic curve + brightness adjust
    return int(shut)

#-----------------------------------------------------------------------------------------------
def takeNightImage(filename):
    # Take low light Twilight or Night image
    dayStream = getStreamImage(True)  # Get a day image stream to calc pixAve below
    with picamera.PiCamera() as camera:
        time.sleep(1.5)  # Wait for camera to warm up to reduce green tint images
        camera.resolution = (imageWidth, imageHeight)
        camera.vflip = imageVFlip
        camera.hflip = imageHFlip
        camera.rotation = imageRotation # valid values 0, 90, 180, 270
        dayPixAve = getStreamPixAve(dayStream)
        # Format common settings string
        settings = ("camSleepSec=%i MaxISO=%i Size=%ix%i"
                 % (nightSleepSec, nightMaxISO, imageWidth, imageHeight))

        if dayPixAve >= nightDarkThreshold:  # Twilight so use variable framerate_range
            logging.info("TwilightThresh=%i/%i shutSec=range %s"
                      % ( dayPixAve, nightTwilightThreshold, settings ))
            camera.framerate_range = (Fraction(1, 6), Fraction(30, 1))
            time.sleep(2) # Give camera time to measure AWB
            camera.iso = nightMaxISO
        else:
            camera.framerate = Fraction(1, 6) # Set the framerate to a fixed value
            time.sleep(1)  # short wait to allow framerate to settle
            if dayPixAve <= nightBlackThreshold:  # Black (Very Low Light) so Use Max Settings
                camShut = nightMaxShut
                logging.info("BlackThresh=%i/%i shutSec=%s %s"
                          % ( dayPixAve, nightBlackThreshold, shut2Sec(camShut), settings ))
            else:
                # Dark so calculate camShut exposure time based on dayPixAve light curve + brightness
                camShut = getShut(dayPixAve)
                if camShut > nightMaxShut:
                    camShut = nightMaxShut
                logging.info("DarkThresh=%i/%i shutSec=%s %s"
                          % ( dayPixAve, nightDarkThreshold, shut2Sec(camShut), settings ))
            camera.shutter_speed = camShut  # Set the shutter for long exposure
            camera.iso = nightMaxISO   # Set the ISO to a fixed value for long exposure
            time.sleep(nightSleepSec)  # Give camera a long time to calc Night Settings
        if imageFormat == ".jpg" :
            camera.capture(filename,format='jpeg',quality=imageJpegQuality)
        else:
            camera.capture(filename)
        camera.close()
    if not showDateOnImage:  # showDateOnImage displays FilePath so avoid showing twice
        logging.info("FilePath %s" % filename)

#-----------------------------------------------------------------------------------------------
def takeQuickTimeLapse(moPath, imagePrefix, motionNumOn, motionNumCount, daymode, motionNumPath):
    logging.info("motion Quick Time Lapse for %i sec every %i sec" % (motionQuickTLTimer, motionQuickTLInterval))

    checkTimeLapseTimer = datetime.datetime.now()
    keepTakingImages = True
    filename = getImageName(moPath, imagePrefix, motionNumOn, motionNumCount)
    while keepTakingImages:
        yield filename
        rightNow = datetime.datetime.now()
        timelapseDiff = (rightNow - checkTimeLapseTimer).total_seconds()
        if timelapseDiff > motionQuickTLTimer:
            keepTakingImages=False
        else:
            motionNumCount = postImageProcessing(motionNumOn, motionNumStart, motionNumMax, motionNumCount, motionNumRecycle, motionNumPath, filename, daymode)
            filename = getImageName(moPath, imagePrefix, motionNumOn, motionNumCount)
            time.sleep(motionQuickTLInterval)

#-----------------------------------------------------------------------------------------------
def takeVideo(filename, duration, fps=30):
    # Take a short motion video if required
    logging.info("File : %s" % (filename))
    logging.info("Start: Size %ix%i for %i sec at %i fps" % (imageWidth, imageHeight, duration, fps))
    if motionVideoOn or videoRepeatOn:
        with picamera.PiCamera() as camera:
            camera.resolution = (imageWidth, imageHeight)
            camera.vflip = imageVFlip
            camera.hflip = imageHFlip
            camera.rotation = imageRotation # You can also use imageVFlip and imageHFlip variables
            camera.framerate = fps
            if showDateOnImage:
                rightNow = datetime.datetime.now()
                dateTimeText = (" Started at %04d-%02d-%02d %02d:%02d:%02d "
                             % (rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second))
                camera.annotate_text_size = showTextFontSize
                camera.annotate_foreground = picamera.Color('black')
                camera.annotate_background = picamera.Color('white')
                camera.annotate_text = dateTimeText
            camera.start_recording(filename)
            camera.wait_recording(duration)
            camera.stop_recording()
            camera.close()
        # This creates a subprocess that runs convid.sh with the filename as a parameter
        try:
            convid = "%s/convid.sh %s" % ( baseDir, filename )
            proc = subprocess.Popen(convid, shell=True, stdin=None, stdout=None,
                                                        stderr=None, close_fds=True)
        except IOError:
            logging.error("subprocess %s failed" %s ( convid ))
        createSyncLockFile(filename)

#-----------------------------------------------------------------------------------------------
def createSyncLockFile(imagefilename):
    # If required create a lock file to indicate file(s) to process
    if createLockFile:
        if not os.path.exists(lockFilePath):
            open(lockFilePath, 'w').close()
            logging.info("Create gdrive sync.sh Lock File %s", lockFilePath)
        rightNow = datetime.datetime.now()
        now = ("%04d%02d%02d-%02d%02d%02d"
            % ( rightNow.year, rightNow.month, rightNow.day, rightNow.hour, rightNow.minute, rightNow.second ))
        filecontents = now + " createSyncLockFile - "  + imagefilename + " Ready to sync using sudo ./sync.sh command."
        f = open(lockFilePath, 'w+')
        f.write(filecontents)
        f.close()

#-----------------------------------------------------------------------------------------------
def trackPoint(grayimage1, grayimage2):
    movementCenterPoint = []   # initialize list of movementCenterPoints
    biggestArea = MIN_AREA
    # Get differences between the two greyed images
    differenceimage = cv2.absdiff( grayimage1, grayimage2 )
    # Blur difference image to enhance motion vectors
    differenceimage = cv2.blur( differenceimage,(BLUR_SIZE,BLUR_SIZE ))
    # Get threshold of blurred difference image based on THRESHOLD_SENSITIVITY variable
    retval, thresholdimage = cv2.threshold( differenceimage, THRESHOLD_SENSITIVITY, 255, cv2.THRESH_BINARY )
    try:
        thresholdimage, contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
    except:
        contours, hierarchy = cv2.findContours( thresholdimage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )

    if contours:
        movement = False
        for c in contours:
            cArea = cv2.contourArea(c)
            if cArea > biggestArea:
                biggestArea = cArea
                ( x, y, w, h ) = cv2.boundingRect(c)
                cx = int(x + w/2)   # x centerpoint of contour
                cy = int(y + h/2)   # y centerpoint of contour
                movementCenterPoint = [cx,cy]
    return movementCenterPoint

#-----------------------------------------------------------------------------------------------
def trackDistance(mPoint1, mPoint2):
    x1, y1 = mPoint1
    x2, y2 = mPoint2
    trackLen = abs(math.hypot(x2 - x1, y2 - y1))
    return trackLen

#-----------------------------------------------------------------------------------------------
def getStreamImage(isDay):
    # Capture an image stream to memory based on daymode
    with picamera.PiCamera() as camera:
        camera.resolution = (testWidth, testHeight)
        with picamera.array.PiRGBArray(camera) as stream:
            if isDay:
                camera.exposure_mode = 'auto'
                camera.awb_mode = 'auto'
                time.sleep(motionCamSleep)   # sleep so camera can get AWB
            else:
                # use variable framerate_range for Low Light motion image stream
                camera.framerate_range = (Fraction(1, 6), Fraction(30, 1))
                time.sleep(2) # Give camera time to measure AWB
                camera.iso = nightMaxISO
            camera.capture(stream, format='rgb', use_video_port=useVideoPort)
            camera.close()
            return stream.array

#-----------------------------------------------------------------------------------------------
def getStreamPixAve(streamData):
    # Calculate the average pixel values for the specified stream (used for determining day/night or twilight conditions)
    pixAverage = int(np.average(streamData[...,1]))
    return pixAverage

#-----------------------------------------------------------------------------------------------
def checkIfDay(currentDayMode, image):
    # Try to determine if it is day, night or twilight.
    dayPixAverage = 0
    if currentDayMode:
        dayPixAverage = getStreamPixAve(image)
    else:
        dayStream = getStreamImage(True)
        dayPixAverage = getStreamPixAve(dayStream)

    if dayPixAverage > nightTwilightThreshold:
        currentDayMode = True
    else:
        currentDayMode = False
#   logging.info("daymode=%s dayPixAverage=%i" % (currentDayMode, dayPixAverage))
    return currentDayMode

#-----------------------------------------------------------------------------------------------
def checkIfDayStream(currentDayMode, image):
    # Try to determine if it is day, night or twilight.
    dayPixAverage = 0
    dayPixAverage = getStreamPixAve(image)

    if dayPixAverage > nightTwilightThreshold:
        currentDayMode = True
    else:
        currentDayMode = False
#   logging.info("daymode=%s dayPixAverage=%i" % (currentDayMode, dayPixAverage))
    return currentDayMode

#-----------------------------------------------------------------------------------------------
def timeToSleep(currentDayMode):
    if noNightShots:
       if currentDayMode:
          sleepMode=False
       else:
          sleepMode=True
    elif noDayShots:
        if currentDayMode:
           sleepMode=True
        else:
           sleepMode=False
    else:
        sleepMode=False
    return sleepMode

#-----------------------------------------------------------------------------------------------
def checkForTimelapse (timelapseStart):
    # Check if timelapse timer has expired
    rightNow = datetime.datetime.now()
    timeDiff = ( rightNow - timelapseStart).total_seconds()
    if timeDiff > timelapseTimer:
        timelapseStart = rightNow
        timelapseFound = True
    else:
        timelapseFound = False
    return timelapseFound

#-----------------------------------------------------------------------------------------------
def dataLogger():
    # Replace main() with this function to log day/night pixAve to a file.
    # Note variable logDataToFile must be set to True in config.py
    # You may want to delete pi-timolo.log to clear old data.
    print("dataLogger - One Moment Please ....")
    while True:
        dayStream = getStreamImage(True)
        dayPixAverage = getStreamPixAve(dayStream)
        nightStream = getStreamImage(False)
        nightPixAverage = getStreamPixAve(nightStream)
        logging.info("nightPixAverage=%i dayPixAverage=%i nightTwilightThreshold=%i nightDarkThreshold=%i "
                  % (nightPixAverage, dayPixAverage, nightTwilightThreshold, nightDarkThreshold))
        time.sleep(1)
    return

#-----------------------------------------------------------------------------------------------
def timolo():
    # Main program initialization and logic loop
    dotCount = 0   # Counter for showDots() display if not motion found (shows system is working)
    checkMediaPaths()
    timelapseNumCount = 0
    motionNumCount = 0
    tlstr = ""  # Used to display if timelapse is selected
    mostr = ""  # Used to display if motion is selected
    moCnt = "non"
    tlCnt = "non"
    daymode = False       # Used to keep track of night and day based on dayPixAve
    forceMotion = False   # Used for forcing a motion image if no motion for motionForce time exceeded
    motionFound = False

    if spaceTimerHrs > 0:
        lastSpaceCheck = datetime.datetime.now()

    if timelapseOn:
        tlstr = "TimeLapse"
        # Check if timelapse subDirs reqd and create one if non exists
        tlPath = subDirChecks( timelapseSubDirMaxHours, timelapseSubDirMaxFiles,
                               timelapseDir, timelapsePrefix)
        if timelapseNumOn:
            timelapseNumCount = getCurrentCount(timelapseNumPath, timelapseNumStart)
            tlCnt = str(timelapseNumCount)

    if motionTrackOn:
        mostr = "Motion Tracking"
        # Check if motion subDirs reqd and create one if required if non exists
        moPath = subDirChecks( motionSubDirMaxHours, motionSubDirMaxFiles,
                               motionDir, motionPrefix)
        if motionNumOn:
            motionNumCount = getCurrentCount(motionNumPath, motionNumStart)
            moCnt = str(motionNumCount)

        trackLen = 0.0
        trackTimeout = time.time()
        trackTimer = TRACK_TIMEOUT
        startPos = []
        startTrack = False
        logging.info("Start PiVideoStream ....")
        vs = PiVideoStream().start()
        vs.camera.rotation = imageRotation
        vs.camera.hflip = imageHFlip
        vs.camera.vflip = imageVFlip
        time.sleep(3)
        image1 = vs.read()
        image2 = vs.read()
        grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        logging.info("Motion Tracking is On")
        daymode = checkIfDayStream(daymode, image2)
    else:
        image1 = getStreamImage(True).astype(float)  #All functions should still work with float instead of int - just takes more memory
        image2 = getStreamImage(daymode)  # initialise image2 to use in main loop
        daymode = checkIfDay(daymode, image1)

    logging.info("daymode=%s  motionDotsOn=%s " % ( daymode, motionDotsOn ))

    if timelapseOn and motionTrackOn:
        tlstr = " and " + tlstr

    if videoRepeatOn:
        mostr = "Video Repeat"
        tlstr = ""
    displayInfo(moCnt, tlCnt)  # Display config.py settings

    timelapseStart = datetime.datetime.now()
    timelapseExitStart = timelapseStart
    checkMotionTimer = timelapseStart

    if logDataToFile:
        print("")
        print("logDataToFile=%s Logging to Console Disabled." % ( logDataToFile))
        print("Sending Console Messages to %s" % (logFilePath))
        print("Entering Loop for %s%s" % (mostr, tlstr))
    else:
        if pluginEnable:
            logging.info("plugin %s - Start %s%s Loop ..." % ( pluginName, mostr, tlstr))
        else:
            logging.info("Start %s%s Loop ..." % (mostr, tlstr))

    dotCount = showDots(motionDotsMax)  # reset motion dots
    # Start main program loop here.  Use Ctl-C to exit if run from terminal session.
    while True:
        motionFound = False
        forceMotion = False
        if spaceTimerHrs > 0:  # if required check free disk space and delete older files (jpg)
            lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)

        # use image2 to check daymode as image1 may be average that changes slowly, and image1 may not be updated
        if motionTrackOn:
            if daymode != checkIfDayStream(daymode, image2):
                daymode = not daymode
                image2 = vs.read()
                image1 = image2
            else:
                image2 = vs.read()
        else:
            if daymode != checkIfDay(daymode, image2):  # if daymode has changed, reset background, to avoid false motion trigger
                daymode = not daymode
                image2 = getStreamImage(daymode)  #get new stream
                image1 = image2.astype(float)      #reset background
            else:
                image2 = getStreamImage(daymode)  # This gets the second stream of motion analysis
        rightNow = datetime.datetime.now()   # refresh rightNow time
        if not timeToSleep(daymode):  # Don't take images if noNightShots or noDayShots settings are valid
            if timelapseOn:
                takeTimeLapse = checkForTimelapse(timelapseStart)
                if takeTimeLapse and timelapseExitSec > 0:
                    timelapseStart = datetime.datetime.now()  # Reset timelapse timer
                    if ( datetime.datetime.now() - timelapseExitStart ).total_seconds() > timelapseExitSec:
                        print("")
                        logging.info("timelapseExitSec=%i Exceeded: Suppressing Further Timelapse Images" % ( timelapseExitSec ))
                        logging.info("To Reset: Restart pi-timolo.py to restart timelapseExitSec Timer.")
                        takeTimeLapse = False  # Suppress further timelapse images
                if (takeTimeLapse and timelapseNumOn and (not timelapseNumRecycle)):
                    timelapseStart = datetime.datetime.now()  # Reset timelapse timer
                    if timelapseNumMax > 0 and timelapseNumCount >= (timelapseNumStart + timelapseNumMax):
                        print("")
                        logging.info("timelapseNumRecycle=%s and Counter=%i Exceeded: Surpressing Further Timelapse Images"
                              % ( timelapseNumRecycle, timelapseNumStart + timelapseNumMax  ))
                        logging.info("To Reset: Delete File %s and Restart pi-timolo.py" % timelapseNumPath )
                        takeTimeLapse = False  # Suppress further timelapse images
                if takeTimeLapse:
                    if motionDotsOn and motionTrackOn:
                        dotCount = showDots(motionDotsMax + 2)  # reset motion dots
                    else:
                        print("")
                    if pluginEnable:
                        logging.info("%s Sched TimeLapse  daymode=%s  Timer=%i sec",
                                                              pluginName, daymode, timelapseTimer)
                    else:
                        logging.info("Sched TimeLapse  daymode=%s  Timer=%i sec",
                                                                   daymode, timelapseTimer)
                    imagePrefix = timelapsePrefix + imageNamePrefix
                    filename = getImageName(tlPath, imagePrefix, timelapseNumOn, timelapseNumCount)
                    if motionTrackOn:
                        logging.info("Stop PiVideoStream ...")
                        vs.stop()
                        time.sleep(motionStreamStopSec)
                    timelapseStart = datetime.datetime.now()  # reset time lapse timer
                    if daymode:
                        takeDayImage(filename, timelapseCamSleep)
                    else:
                        takeNightImage(filename)
                    timelapseNumCount = postImageProcessing(timelapseNumOn, timelapseNumStart, timelapseNumMax,
                                                            timelapseNumCount, timelapseNumRecycle,
                                                            timelapseNumPath, filename, daymode)
                    if timelapseRecentMax > 0:
                        saveRecent(timelapseRecentMax, timelapseRecentDir, filename, imagePrefix)

                    if timelapseMaxFiles > 0:
                        deleteOldFiles(timelapseMaxFiles, timelapseDir, imagePrefix)

                    dotCount = showDots(motionDotsMax)
                    if motionTrackOn:
                        logging.info("Restart PiVideoStream ....")
                        vs = PiVideoStream().start()
                        vs.camera.rotation = imageRotation
                        vs.camera.hflip = imageHFlip
                        vs.camera.vflip = imageVFlip
                        time.sleep(2)
                    tlPath = subDirChecks( timelapseSubDirMaxHours, timelapseSubDirMaxFiles, timelapseDir, timelapsePrefix)

            if motionTrackOn:
                # IMPORTANT - Night motion tracking may not work very well due to long exposure times and low light
                image2 = vs.read()
                grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
                movePoint1 = trackPoint(grayimage1, grayimage2)
                grayimage1 = grayimage2
                if movePoint1 and not startTrack:
                    startTrack = True
                    trackTimeout = time.time()
                    startPos = movePoint1
                image2 = vs.read()
                grayimage2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
                movePoint2 = trackPoint(grayimage1, grayimage2)
                if movePoint2 and startTrack:   # Two sets of movement required
                    trackLen = trackDistance(startPos, movePoint2)
                    if trackLen > TRACK_TRIG_LEN_MIN:  # wait until track well started
                        trackTimeout = time.time()  # Reset tracking timer object moved
                        if motionTrackInfo:
                            logging.info("Track Start(%i,%i)  Now(%i,%i) trackLen=%.2f px",
                               startPos[0], startPos[1], movePoint2[0], movePoint2[1], trackLen)

                    # Track length triggered
                    if trackLen > TRACK_TRIG_LEN:
                        if trackLen > TRACK_TRIG_LEN_MAX:  # reduce chance of two objects at different postions
                            motionFound = False
                            if motionTrackInfo:
                                logging.info("TrackLen %.2f px Exceeded %i px Max Trig Len Allowed.",
                                                   trackLen, TRACK_TRIG_LEN_MAX)
                        else:
                            motionFound = True
                            if pluginEnable:
                                logging.info("%s Motion Triggered Start(%i,%i)  End(%i,%i) trackLen=%.2f px", pluginName,
                                startPos[0], startPos[1], movePoint2[0], movePoint2[1], trackLen)
                            else:
                                logging.info("Motion Triggered Start(%i,%i)  End(%i,%i) trackLen=%.2f px",
                                startPos[0], startPos[1], movePoint2[0], movePoint2[1], trackLen)
                        image1 = vs.read()
                        image2 = image1
                        grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
                        grayimage2 = grayimage1
                        startTrack = False
                        startPos = []
                        trackLen = 0.0

                # Track timed out
                if ((time.time() - trackTimeout > trackTimer) and startTrack):
                    image1 = vs.read()
                    image2 = image1
                    grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
                    grayimage2 = grayimage1
                    if motionTrackInfo:
                        logging.info("Track Timer %i sec Exceeded.  Reset Track", trackTimer)
                    startTrack = False
                    startPos = []
                    trackLen = 0.0

                rightNow = datetime.datetime.now()
                timeDiff = (rightNow - checkMotionTimer).total_seconds()
                if motionForce > 0 and timeDiff > motionForce:
                    image1 = vs.read()
                    image2 = image1
                    grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
                    grayimage2 = grayimage1
                    dotCount = showDots(motionDotsMax + 2)      # New Line
                    logging.info("No Motion Detected for %s minutes. Taking Forced Motion Image.", (motionForce / 60))
                    checkMotionTimer = rightNow
                    forceMotion = True

                if motionFound or forceMotion:
                    imagePrefix = motionPrefix + imageNamePrefix
                    if motionTrackQuickPic:  # Do not stop PiVideoStream
                        filename = getImageName(moPath, imagePrefix, motionNumOn, motionNumCount)
                        takeTrackQuickPic(image2, filename)
                        motionNumCount = postImageProcessing(motionNumOn, motionNumStart, motionNumMax,
                                                             motionNumCount, motionNumRecycle, motionNumPath,
                                                             filename, daymode)
                    else:
                        if motionTrackOn:
                            logging.info("Stop PiVideoStream ...")
                            vs.stop()
                            time.sleep(motionStreamStopSec)
                        checkMotionTimer = rightNow
                        if forceMotion:
                            forceMotion = False

                        # check if motion Quick Time Lapse option is On.  This option supersedes motionVideoOn
                        if motionQuickTLOn and daymode:
                            filename = getImageName(moPath, imagePrefix, motionNumOn, motionNumCount)
                            with picamera.PiCamera() as camera:
                                camera.resolution = (imageWidth, imageHeight)
                                camera.vflip = imageVFlip
                                camera.hflip = imageHFlip
                                camera.rotation = imageRotation # valid values 0, 90, 180, 270
                                time.sleep(motionCamSleep)
                                # This uses yield to loop through time lapse sequence but does not seem to be faster due to writing images
                                camera.capture_sequence(takeQuickTimeLapse(moPath, imagePrefix, motionNumOn, motionNumCount, daymode, motionNumPath))
                                camera.close()
                                motionNumCount = getCurrentCount(motionNumPath, motionNumStart)
                        else:
                            if motionVideoOn:
                                filename = getVideoName(motionPath, imagePrefix, motionNumOn, motionNumCount)
                                takeVideo(filename, motionVideoTimer, motionVideoFPS)
                            else:
                                filename = getImageName(moPath, imagePrefix, motionNumOn, motionNumCount)
                                if daymode:
                                    takeDayImage(filename, motionCamSleep)
                                else:
                                    takeNightImage(filename)
                            motionNumCount = postImageProcessing(motionNumOn, motionNumStart, motionNumMax,
                                                                 motionNumCount, motionNumRecycle, motionNumPath,
                                                                 filename, daymode)
                            if motionRecentMax > 0:
                                if not motionVideoOn:   # prevent h264 video files from being copied to recent
                                    saveRecent(motionRecentMax, motionRecentDir, filename, imagePrefix)

                        if motionTrackOn:
                            logging.info("Restart PiVideoStream ....")
                            vs = PiVideoStream().start()
                            vs.camera.rotation = imageRotation
                            vs.camera.hflip = imageHFlip
                            vs.camera.vflip = imageVFlip
                            time.sleep(2)
                            image1 = vs.read()
                            image2 = image1
                            grayimage1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
                            grayimage2 = grayimage1
                            trackLen = 0.0
                            trackTimeout = time.time()
                            startPos = []
                            startTrack = False
                            forceMotion = False

                    moPath = subDirChecks( motionSubDirMaxHours, motionSubDirMaxFiles, motionDir, motionPrefix)

                    if motionFound:
                        # =========================================================================
                        # Put your user code in userMotionCodeHere() function at top of this script
                        # =========================================================================
                        userMotionCodeHere()
                        dotCount = showDots(motionDotsMax)
                else:
                    dotCount = showDots(dotCount)  # show progress dots when no motion found

#-----------------------------------------------------------------------------------------------
def videoRepeat():
    if not os.path.isdir(videoPath):     # Check if folder exist and create if required
        logging.info("Create videoRepeat Folder %s", videoPath)
        os.makedirs(videoPath)
    print("------------------------------------------------------------------------------------------")
    print("VideoRepeat . videoRepeatOn=%s" % videoRepeatOn)
    print("   Info ..... Size=%ix%i  videoPrefix=%s  videoDuration=%i seconds  videoFPS=%i" %
                       ( imageWidth, imageHeight, videoPrefix, videoDuration, videoFPS ))
    print("   Vid Path . videoPath=%s" % videoPath)
    print("   Timer .... videoTimer=%i minutes  0=Continuous" % ( videoTimer ))
    print("   Num Seq .. videoNumOn=%s  videoNumRecycle=%s  videoNumStart=%i  videoNumMax=%i 0=Continuous" %
                         ( videoNumOn, videoNumRecycle, videoNumStart, videoNumMax ))
    print("------------------------------------------------------------------------------------------")
    print("WARNING: videoRepeatOn=%s Suppresses TimeLapse and Motion Settings." % videoRepeatOn)

    videoStartTime = datetime.datetime.now()
    lastSpaceCheck = datetime.datetime.now()
    videoCount = 0
    videoNumCounter = videoNumStart
    keepRecording = True
    while keepRecording:
        # if required check free disk space and delete older files
        #  Set variables spaceFileExt='mp4' and spaceMediaDir= to appropriate folder path
        if spaceTimerHrs > 0:
            lastSpaceCheck = freeDiskSpaceCheck(lastSpaceCheck)
        filename = getVideoName(videoPath, videoPrefix, videoNumOn, videoNumCounter )
        takeVideo(filename, videoDuration, videoFPS)
        timeUsed = (datetime.datetime.now() - videoStartTime).total_seconds()
        timeRemaining = ( videoTimer*60 - timeUsed ) / 60.0
        videoCount += 1
        if videoNumOn:
            videoNumCounter += 1
            if videoNumMax > 0:
                if videoNumCounter - videoNumStart > videoNumMax:
                    if videoNumRecycle:
                        videoNumCounter = videoNumStart
                        logging.info("Restart Numbering: videoNumRecycle=%s and videoNumMax=%i Exceeded",
                                             videoNumRecycle, videoNumMax)
                    else:
                        keepRecording = False
                        logging.info("Exit since videoNumRecycle=%s and videoNumMax=%i Exceeded  %i Videos Recorded",
                                             videoNumRecycle, videoNumMax, videoCount)
                logging.info("Recorded %i of %i Videos" % ( videoCount, videoNumMax))
            else:
                logging.info("Recorded %i Videos  videoNumMax=%i 0=Continuous" % (videoCount, videoNumMax))
        else:
            logging.info("Progress: %i Videos Recorded in Folder %s", videoCount, videoPath)

        if videoTimer > 0:
            if timeUsed > videoTimer * 60:
                keepRecording = False
                logging.info("Exit since videoTimer=%i minutes Exceeded", videoTimer)
            else:
                logging.info("Remaining Time %.1f of %i minutes", timeRemaining, videoTimer)
        else:
            videoStartTime = datetime.datetime.now()
    logging.info("Exit: %i Videos Recorded in Folder %s", videoCount, videoPath)

#-----------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Test if the pi camera is already in use
    print("INFO  - Testing if Pi Camera is in Use")
    ts = PiVideoStream().start()
    time.sleep(3)
    ts.stop()
    time.sleep(1)
    print("INFO  - Pi Camera is Available.")
    if pluginEnable:
        print("INFO  - Start pi-timolo per %s and plugins/%s.py Settings" % (configFilePath, pluginName))
    else:
        print("INFO  - Start pi-timolo per %s Settings" % configFilePath)

    if not verbose:
        print("INFO  - Note: Logging Disabled per Variable verbose=False")

    try:
        if debug:
            dataLogger()
        elif videoRepeatOn:
            videoRepeat()
        else:
            timolo()

    except KeyboardInterrupt:
        print("")
        print("+++++++++++++++++++++++++++++++++++")
        print("User Pressed Keyboard ctrl-c")
        print("%s %s - Exiting" % (progName, progVer))
        print("+++++++++++++++++++++++++++++++++++")
        print("")
        pass
    try:
        if pluginEnable:
            if os.path.exists(pluginCurrent):
                os.remove(pluginCurrent)
            pluginCurrentpyc = os.path.join(pluginDir, "current.pyc")
            if os.path.exists(pluginCurrentpyc):
                os.remove(pluginCurrentpyc)
    except OSError as err:
        print("ERROR - Failed Removal of %s - %s" % ( pluginCurrentpyc, err ))
        print("INFO  - Exiting %s Due to Error" % progName)
    quit(0)

