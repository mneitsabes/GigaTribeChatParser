# Introduction

GigaTribe is a private, secure and unlimited file sharing software. Once installed, the user can create an account and choose the files he wants to share. He can also chat with other users and give them access to his shared files. This software is often used to trade child pornography.

Chats are (partially?) stored locally. These chats may contain images, that may still be recoverable from the computer. 

# Locating relevant files

By default, the GigaTribe application data folder can be found in the following location : 

    Windows XP : C:\Documents and Settings\<user>\Local Settings\Application Data\GigaTribe
    Windows Vista/7 : C:\Users\<user>\AppData\Local\Shalsoft\GigaTribe

In this repertory, there is one directory per user (the User ID consists in only numbers). E.g.: if I have these two users "123456" and "987654", I'll have two subdirectories : 

    C:\Users\<user>\AppData\Local\Shalsoft\GigaTribe\123456\
    C:\Users\<user>\AppData\Local\Shalsoft\GigaTribe\987654\

Each user directory has subdirectories :

* **chat** : contains chats in binary format
* **resources** : contains some shared files, including images
* **sharefolders** : XML configuration files
* some others

The **chat** folder contains chats, but also some other files (pictures, DLL, ...) with the ".dat"-extension. Each message sent / received is stored in the file as an old screen "GigaTribe" as well as HTML. The chat logs format is described on this document. 

# Requirements

Using Python 3.x interpreter

# Usage

```[USAGE] GigaTribeChatParser.py <gigatribe_userid_directory> <output_dir>```

The script can only process one user directory at a time. For the example given in the introduction, it is necessary to run the script twice : 

    $ GigaTribeChatParser.py D:\MyExtractDirectory\Shalsoft\123456 D:\MyOutputDirectory\GigaTribe\123456
    Processing chathistory_1568169_1734884.dat
    Processing chathistory_1568169_1740609.dat
    Skipping chathistory_1568169_1743908.dat (not a chat file)
    Processing chathistory_1568169_1750295.dat
    [...]
    $ GigaTribeChatParser.py D:\MyExtractDirectory\Shalsoft\987654 D:\MyOutputDirectory\GigaTribe\987654
    Processing chathistory_1568169_1707034.dat
    Processing chathistory_1568169_1709999.dat
    Processing chathistory_1568169_1711278.dat
    [...]

# Troubleshooting

* **I have the following error "fdHTMLOut.write(HTML_HEADER) TypeError: must be unicode, not str"**

You execute the script with the Python 2.x interpreter, use the Python 3.x interpreter instead 

* **I have the following error "struct.error: unpack requires a bytes object of length x" or "UnicodeEncodeError: 'utf-8' codec can't encode character '\udca4' in position 265: surrogates not allowed"**

Either this is a very old or new version of chat log files, or the file is corrupted. If other files are well processed, it is probably the second case.

Verify that the file concerned was not carved and therefore contains inconsistent data at the end of file. If this is the case, delete the file to skip it. 

* **What is the time zone of the date/time part ?**

Unfortunately, I do not know :'( (Local time or UTC ?) 
