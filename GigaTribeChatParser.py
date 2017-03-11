# -*-coding:utf-8 -*

# Extract GigaTribe messages from the user directory.
#
# On the path "\Users\<user>\AppData\Local\Shalsoft\GigaTribe\", you have multiple directories :
#      - "1234567" <-- directory of the user which has ID 1234567
#      - "9876543" <-- directory of the user which has ID 9876543
#      - "avatars" <-- not used
#      - "blogs"   <-- not used
#
# Each "user directory" has subdirectories :
#      - "chat"         <-- contains chats in binary format
#      - "ressources"   <-- contains some shared files including images
#      - "sharefolders" <-- XML configuration files
#      - some others
#
# The chat file format is specified in this article : http://fr.scribd.com/doc/57669321/Parsing-the-Chat-Logs-for-GigaTribe-Version-3#scribd
# The "HTML message" part can contain <img> tag which can point to the "resources" folder.
#
# This script takes in argument the user directory and a output directory.
# So with the previous example, we must extract the "1234567" and the "9876543" directory and execute two times the command :
#     $ gigatribechatparser.py 1234567 output_1234567
#     $ gigatribechatparser.py 9876543 output_9876543
#
# This script exports chat files in HTML format. If available, images are included. If not, a replace image shows the "Image not found" text.

import sys
import os
import io
import re
from struct import *
import shutil
import math

# HTML header
HTML_HEADER = "<html> \
             <head> \
                <meta http-equiv=\"content-type\" content=\"text/html; charset=UTF-8\"> \
                <style> \
                    table { \
                        padding: 0; \
                        margin: 0; \
                        border-collapse: collapse; \
                        border: 1px solid #333; \
                        font-family: Verdana, Arial, Helvetica, sans-serif; \
                        font-size: 0.9em; \
                        color: #000; \
                    } \
                    table th, table td { \
                        border: 1px dotted; \
                        padding: 0.5em; \
                        text-align: left; \
                    } \
                    .image_not_found:before { \
                        content: url('data:image/png;base64,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') \
                    } \
                </style> \
             </head> \
             <body> \
                <table> \
                    <tr> \
                        <th>Sender</th> \
                        <th>Date</th> \
                        <th>Message</th> \
                    </tr>"

# HTML table row
HTML_TABLE_ROW =  " <tr> \
                      <td>%s</td> \
                      <td>%s</td> \
                      <td>%s</td> \
                    </tr>"

# HTML footer
HTML_FOOTER = "     </table> \
              </body> \
           </html>"

def readInt32(fd):
    '''
    Read a "int" 4 bytes in big-endian from the file descriptor provided

    :param fd: file descriptor of the binary data
    :return: the "int32" value
    '''
    return unpack(">i", fd.read(4))[0]

def readUInt32(fd):
    '''
    Read a "unsigned int" 4 bytes in big-endian from the file descriptor provided

    :param fd: file descriptor of the binary data
    :return: the "unsigned int32" value
    '''
    return unpack(">I", fd.read(4))[0]

def readUInt64(fd):
    '''
    Read a "unsigned int" 8 bytes in big-endian from the file descriptor provided

    :param fd: file descriptor of the binary data
    :return: the "unsigned int64" value
    '''
    return unpack(">Q", fd.read(8))[0]

def readByte(fd):
    '''
    Read a 1 byte big-endian from the file descriptor provided

    :param fd: file descriptor of the binary data
    :return: the "bool" value
    '''
    return unpack(">c", fd.read(1))[0]

def readQString(fd):
    '''
    Read a QString (from Qt framework) from the file descriptor provided

    The QString is structured like this :
        0x00 : uint32 giving the length of the string in bytes
        0x04 : the string in unicode

    If the length part has the value 0xFFFFFFFF, the QString is NULL.

    :param fd: file descriptor of the binary data
    :return: the UTF8 string
    '''
    length = readUInt32(fd)
    if length == 0xFFFFFFFF:  # The QString represents a NULL string
        return None

    str = []
    for i in range(0, length, 2):
        str.append(chr(unpack(">H", fd.read(2))[0]))

    # Assemble the characters
    return "".join(str)

# Source : https://gist.github.com/jiffyclub/1294443
def jd_to_date(jd):
    """
    Convert Julian Day to date.

    Algorithm from 'Practical Astronomy with your Calculator or Spreadsheet',
        4th ed., Duffet-Smith and Zwart, 2011.

    Parameters
    ----------
    jd : float
        Julian Day

    Returns
    -------
    year : int
        Year as integer. Years preceding 1 A.D. should be 0 or negative.
        The year before 1 A.D. is 0, 10 B.C. is year -9.

    month : int
        Month as integer, Jan = 1, Feb. = 2, etc.

    day : float
        Day, may contain fractional part.

    Examples
    --------
    Convert Julian Day 2446113.75 to year, month, and day.

    >>> jd_to_date(2446113.75)
    (1985, 2, 17.25)

    """
    #jd = jd + 0.5 # does'nt apply tho GigaTribe chat

    F, I = math.modf(jd)
    I = int(I)

    A = math.trunc((I - 1867216.25)/36524.25)

    if I > 2299160:
        B = I + 1 + A - math.trunc(A / 4.)
    else:
        B = I

    C = B + 1524
    D = math.trunc((C - 122.1) / 365.25)
    E = math.trunc(365.25 * D)
    G = math.trunc((C - E) / 30.6001)
    day = C - E + F - math.trunc(30.6001 * G)

    if G < 13.5:
        month = G - 1
    else:
        month = G - 13

    if month > 2.5:
        year = D - 4716
    else:
        year = D - 4715

    return year, month, int(day)

def msToTime(msSinceMidnight):
    '''
    Compute the time from the format "ms since midnight".

    :param msSinceMidnight: ms since midnight
    :return: time in three parts (hh, mm, ss)
    '''
    secSinceMidnight = msSinceMidnight / 1000
    hh = int(secSinceMidnight / 3600)
    mm = int((secSinceMidnight % 3600) / 60)
    ss = int((secSinceMidnight % 3600) % 60)
    return hh, mm, ss

def readQDatetime(fd):
    '''
    Read a QDatetime.

    A QDatetime is formatted like this :
        0x00 : uint32 which is the "julian date" (date part)
        0x04 : uint32 which is the time in ms since midnight (time part)
        0x08 : 1 byte : 0x0 if in UTC, 0x1 if in local time

    :param fd: file descriptor of the binary data
    :return: the date/time part in a string formatted "dd/mm/yyy hh:mm:ss"
    '''
    date = jd_to_date(readUInt32(fd))
    time = msToTime(readUInt32(fd))

    # The doc says that this byte is either 0 or 1 (0 : local time | 1 : UTC) but when tested, I only get the value "2"
    timezone = readByte(fd)

    return "%s/%s/%s %s:%s:%s" % (str(date[2]).zfill(2), str(date[1]).zfill(2), date[0], str(time[0]).zfill(2), str(time[1]).zfill(2), str(time[2]).zfill(2))

def cleanHTML(raw_html):
    '''
    Clean the HTML message to only keep text and img

    In GigaTribe, a HTML message look like this :

        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
        <html><head><meta name="qrichtext" content="1" /><style type="text/css">
        p, li { white-space: pre-wrap; }
        </style></head><body style=" font-family:'Arial'; font-size:16pt; font-weight:400; font-style:normal;">
        <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><img src="/ressources/stil_1374904166_1358413_1272.png" width="207" height="256" />TEXT MESSAGE <a href="result_box"></a> TEST MESSAGE 2</p></body></html>

    We want to only keep the <img> tags and the text :

        <img src="/ressources/stil_1374904166_1358413_1272.png" width="207" height="256" />TEXT MESSAGE TEST MESSAGE 2

    The message is always included in <p></p> tag.

    :param raw_html: the HTML message
    :return: HTML cleaned message
    '''
    if not raw_html:
        return None

    # We extract all data between the <p></p> tag. Because of the DOTALL flag, the "." matches NEWLINE (\n)
    extract = re.search("<p.*?>(.*)</p>", raw_html, re.IGNORECASE|re.DOTALL)
    if extract:
        # We keep only data (<p>DATA</p>)
        raw_html = extract.group(1)

    # We must remove other HTML tag except the <img> tag
    cleaner = re.compile("<(?!img).*?>")
    raw_html = re.sub(cleaner, "", raw_html)

    return raw_html

def processImgTag(outputDir, html):
    '''
    Process img tags of the GigaTribe HTML message.

    Img tags have the following synthax : <img src="IMG_SRC" width="WIDTH_PX" height="HEIGHT_PX" />
    The img src can be :
       - the image is a sended/recieved picture : /ressources/*
       - a link to a custom smileys system

    We only keep the img tag where the src attribute points to a sended/recieved picture which is exists in the ressources folder.
    If the file doesn't exist anymore, we replace the img tag by the following HTML code which'll display "Image not found" :

        <span class="image_not_found"></span>

    :param outputDir: output directory
    :param html: the cleaned HTML message
    :return: the HTML message
    '''
    if not html:
        return None

    # We find each <img> tag. We process matching results in reversed order because we'll replace some substrings.
    # If we process from the left and the replace string doesn't have the same length that the replaced one, all index are going to be wrong.
    # If we process from the right, it doesn't affect index.
    for m in reversed(list(re.finditer("<img src=\"([a-zA-Z0-9_/:\.]+)\" width=\"\d+\" height=\"\d+\" />", html))):
        # Flag to known if we must remove the tag
        mustRemoveImgTag = True

        # If the src attribute points to the ressources folder
        if m.group(1).startswith("/ressources/"):

            # We check if the file exists
            filePath = inputDir + m.group(1)
            if os.path.exists(inputDir + m.group(1)):
                mustRemoveImgTag = False

                # We create the "ressources" folder in the output directory if necessary (it's the case for the first file found)
                if not os.path.exists(outputDir + "/ressources/"):
                    os.makedirs(outputDir + "/ressources/")

                # Copy the file from the <input>/ressources to the <output>/ressources
                shutil.copy(filePath, outputDir + m.group(1))

        if not mustRemoveImgTag:
            # If we keep the <img> tag, we must remove the first "/" to have relative path in our HTML output file
            # We take the chance to use the correct path separator
            html = html[:m.start(1)] + m.group(1).replace("/ressources/", "ressources" + os.path.sep) + html[m.end(1):]
        else:
            # If the file is not found, we replace the tag by this HTML code which will display a embedded img showing the text "Image not found" (see HTML_HEADER)
            html = html[:m.start()] + "<span class=\"image_not_found\"></span>" + html[m.end():]

    return html

# Main entry point
if __name__ == '__main__':
    # Usage checker
    if len(sys.argv) != 3:
        print("[USAGE] GigaTribeChatParser.py <gigatribe_userid_directory> <output_dir>")
        exit(1)

    # Input and output directories
    inputDir = sys.argv[1]
    outputDir = sys.argv[2]

    # Chats directory
    chatsDirectory = inputDir + os.path.sep + "chat"

    # List all .dat chat file and process it
    for chatFile in os.listdir(chatsDirectory):
        fd = io.open(chatsDirectory + os.path.sep + chatFile, "rb")

        # File signature checking
        # Some .dat files are JPG (or other file)
        signature = fd.read(2)
        if signature != b'ch':
            print("Skipping %s (not a chat file)" % chatFile)
            fd.close()
            continue

        # Print the current file
        print("Processing %s" % chatFile)

        # Create the output file
        fdHTMLOut = io.open(outputDir + os.path.sep + chatFile + ".html", "w", encoding="utf-8")
        fdHTMLOut.write(HTML_HEADER)

        # String version
        versionStr = readQString(fd)

        # Read one byte to check the EOF
        while fd.read(1):
            # Go back of one byte to cancel the EOF check
            fd.seek(-1, 1)

            # ID of the message
            messageId = readUInt32(fd)

            # Say if it's a offline message
            offlineMessage = unpack(">?", fd.read(1))[0]

            # Timestamp of the message (sended if online message, received if offline message)
            timestamp = readQDatetime(fd)

            # Sender ID
            senderId = readUInt32(fd)

            # Sender name
            senderName = readQString(fd)

            # Number of users in the chat
            nbUsersIDFollowing = readUInt32(fd)

            # Users ID
            for i in range(0, nbUsersIDFollowing):
                readUInt32(fd)

            # Number of users in the chat (normally the same value as nbUsersIDFollowing)
            nbUsersIDFollowing2 = readUInt32(fd)

            # Users name
            for i in range(0, nbUsersIDFollowing2):
                readQString(fd)

            # The message is the old GigaTribe format
            messageGigaTribeFormat = readQString(fd)

            # The message is HTML format
            messageHTML = readQString(fd)

            # Supplemental message is a message generated by GigaTribe and not by the sender (Invitation, etc...)
            supplementalMessage = readQString(fd)

            # Nb bytes read
            nbBytesRead = readUInt64(fd)

            # We choose the message to output.
            #  - If available, the HTML message.
            #  - If not, the GigaTribe format or the supplemental message (if available)
            messageFinal = None
            if messageHTML:
                messageFinal = processImgTag(outputDir, cleanHTML(messageHTML))
            elif messageGigaTribeFormat:
                messageFinal = messageGigaTribeFormat
            elif supplementalMessage:
                messageFinal = supplementalMessage

            if not messageFinal:
                messageFinal = ""

            # Write the line
            fdHTMLOut.write(HTML_TABLE_ROW % (senderName, timestamp, messageFinal))

        # We close the file descriptor
        fd.close()

        # Write HTML footer
        fdHTMLOut.write(HTML_FOOTER)
