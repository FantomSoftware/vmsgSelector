#-*-coding:utf8;-*-
#qpy:3
#qpy:console

# VMSG selector for backuping and migrating selected mobile SMS
# can split the output to several files per some amount of msgs
# -h to help
# inbuild config in the header of this file

import sys
import argparse
import fileinput
import os

#CONFIG:
inputFile = 'sms.vmsg'
phoneNumber_interest_list = ['666123456','777123456']
outputFilePrefix = 'SelectedSmS_'
outputFileSuffix = '.vmsg'
outputFileMaxMsg = 40000
iRemoveSmallerThen = 12

# ----

telPrefix = 'TEL:'
msgPrefix = 'BEGIN:VMSG'
msgSuffixList = ['END:VMSG', msgPrefix]
textPrefix = 'Subject;ENCODING=QUOTED-PRINTABLE;CHARSET=UTF-8:'
textSuffix = 'END:VBODY'
smsStorage = []
verb = False

parser = argparse.ArgumentParser(description='VMSG selector for importing selected mobile SMS')
parser.add_argument('-i', action="store_true", help='input not from file but from stdin')
parser.add_argument('-v', action="store_true", help='verbous info to console')
args = parser.parse_args([])

#set current working dir on skript dir - for e.q.android
os.chdir(os.path.split(sys.argv[0])[0])

parser.print_help()

if args.v:
    verb = True
    
if args.i:
    inputFile = ''

def unifyNumber(tel):
    tel = tel.replace("-", "")
    tel = tel.replace("(", "")
    tel = tel.replace(")", "")
    tel = tel.replace(" ", "")
    return tel

def compareNumber(telX, tel2X):
    result = False
    tel = unifyNumber(telX)
    tel2 = unifyNumber(tel2X)
    if (len(tel)<9 or len(tel2)<9):
        result = (tel == tel2)
    else:
        if ((tel in tel2) or (tel2 in tel)):
            result = True
    return result

# ------------- search for filtering -------------

def scanMsg(inputStream):
    saving = False
    inMsg = False
    cSave = 0

    msg = ""

    for line in inputStream:
        if inMsg:
            msg+=line
            if (line.startswith(telPrefix)):
                if (any(compareNumber(telNumber,line[len(telPrefix):-1]) for telNumber in phoneNumber_interest_list)):
                    saving = True
            if (inMsg and (any(line.startswith(endMsg) for endMsg in msgSuffixList))):
                #end of msg
                if (saving):
                    smsStorage.append(msg)
                inMsg = False
                saving = False
                msg = ""
        else:
            if (line.startswith(msgPrefix)):
                #start of msg
                inMsg = True
                msg+=line
    print('>>> Found '+str(len(smsStorage))+' messages for selected numbers')


def removeDuplicityOrSmall():
    lastText = ''
    cLess = 0
    cDupp = 0
    smsTemp = []
    for msg in smsStorage:
        start = msg.find(textPrefix)
        end = msg.find(textSuffix)
        if (start > 0 and end > start):
            textOnLine = msg[start+len(textPrefix):end-1]
            if (textOnLine == lastText):
                if verb: print('DUPLA: '+textOnLine)
                cDupp += 1
            elif (len(textOnLine) < iRemoveSmallerThen):
                if verb: print('SHORT: '+textOnLine)
                cLess += 1
            else:
                smsTemp.append(msg)
            lastText = textOnLine
    
    print(">>> Count dupp = " + str(cDupp))
    print(">>> Count less = " + str(cLess))
    print(">>> Rest count = " + str(len(smsTemp)))
    return smsTemp


def getFile(telNum, count):
    fileName = outputFilePrefix + unifyNumber(telNum) + '_' + str(count) + outputFileSuffix
    oFile = None
    try:
        oFile = open(fileName, "w")
    except IOError:
        print('Error: Open output file '+fileName)
    return oFile

def printMsgOfNumberToFiles(telNum):
    fileCount = 0
    smsCount = outputFileMaxMsg
    oFile = None
    for line in smsStorage:
        if smsCount >= outputFileMaxMsg:
            print('>>> Creating output file number ' + str(fileCount))
            fileCount += 1
            smsCount = 0
            if not (oFile is None): oFile.close()
            oFile = getFile(telNum,fileCount)
            if oFile is None: return False
        start = line.find(telPrefix) + len(telPrefix)
        if (compareNumber(telNum,line[start:start+13])):
            oFile.write(line)
            smsCount += 1
    if not (oFile is None): oFile.close()
    return True

# ------------- main start -------------

oFile = sys.stdin
if (len(inputFile)>0):
    try:
        oFile = open(inputFile)
    except IOError:
        print('Error: Cannot open file '+inputFile)
        quit()

#lets start and load selected messages
scanMsg(oFile)
#remove duplicites and tiny ones
smsStorage = removeDuplicityOrSmall()
#save them in several files
for tel in phoneNumber_interest_list:
    printMsgOfNumberToFiles(tel)
    
#cleaning
if (len(inputFile)>0):
    try:
        oFile.close()
    except IOError:
        quit()
