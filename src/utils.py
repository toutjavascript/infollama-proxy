import os
import glob
import importlib.metadata
import sys
import platform
import json
from datetime import datetime


# Return true if the python script is running in a venv environment
def in_venv():
    return sys.prefix != sys.base_prefix

# Return true if the python script is running on a windows platform (with .bat support)
def is_windows():
    return platform.system().lower().find("windows")>=0

def formatBytes(B, round_to=2):
    B = float(B)
    KB = float(1024)
    MB = float(KB ** 2) # 1,048,576
    GB = float(KB ** 3) # 1,073,741,824
    TB = float(KB ** 4) # 1,099,511,627,776

    if B < KB:
        return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
    elif KB <= B < MB:
        return "{0:.2f} KB".format(B/KB)
    elif MB <= B < GB:
        return "{0:.2f} MB".format(B/MB)
    elif GB <= B < TB:
        return "{0:.2f} GB".format(B/GB)
    elif TB <= B:
        return "{0:.2f} TB".format(B/TB)

def get_diff_date(dt1, dt2="now"):
    if dt2 == "now":
        dt2 = datetime.now().isoformat()
    dt1 = datetime.fromisoformat(dt1)
    dt2 = datetime.fromisoformat(dt2)
    
    if dt1.tzinfo is None and dt2.tzinfo is not None:
        dt1 = dt1.replace(tzinfo=dt2.tzinfo)
    elif dt1.tzinfo is not None and dt2.tzinfo is None:
        dt2 = dt2.replace(tzinfo=dt1.tzinfo)
    
    delta = dt1 - dt2
    if round(delta.total_seconds() / 60)>0:
        return str(round(delta.total_seconds() / 60))+" min"  # return difference in minutes
    return str(round(delta.total_seconds() / 60 / 60))+" sec"  # return difference in seconds



def formatFrequencies(H, round_to=1):
    H = float(H)
    KH = float(1000)
    MH = float(KH ** 2) # 1,048,576
    GH = float(KH ** 3) # 1,073,741,824
    TH = float(KH ** 4) # 1,099,511,627,776

    if H < KH:
        return '{0} {1}'.format(H,'Hz' if 0 == H > 1 else 'Hz')
    elif KH <= H < MH:
        return "{0:.2f} KHz".format(H/KH)
    elif MH <= H < GH:
        return "{0:.2f} MHz".format(H/MH)
    elif GH <= H < TH:
        return "{0:.2f} GHz".format(H/GH)

# create a folder if it doesn't exist    
def checkFolder(directory):
    if not os.path.exists(directory):
        # print("Creating directory: " + directory)
        os.makedirs(directory)

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

def getAppPath():
    realpath=os.path.realpath(__file__)
    appPath=os.path.dirname(realpath)[0:-4]
    #print("os.path.realpath(__file__):"+os.path.realpath(__file__)) # => C:\IA\FoooXus-Fooocus-Extender\src\utils.py
    #print('full path =', appPath) # => C:\IA\FoooXus-Fooocus-Extender

    return appPath

def getFiles(dir, extension):
    if extension[0]==".":
        extension=extension[1:]
    files = glob.glob(os.path.join(dir,"*." + extension))
    for i in range(len(files)):
        files[i] = files[i].replace(dir+'\\', "")
    return files


def getPythonVersion():
    if sys.version.find(" ")>1:
        return sys.version[0:sys.version.find(" ")]
    return sys.version

def getOS():
    os=platform.system().strip()+" "+platform.release()
    release=platform.release()
    version=platform.version()
    build=version
    if os=="Windows 10":
        build=version[version.rfind(".")+1:]
        if (build>="22000"):
            release="11"
    if platform.system().strip()=="Darwin":
        os="macOS"
        build=release
        release=""
        return os

    return platform.system()+" "+release+" Build "+build


def checkVersions(modules):
    versions={}
    for module in modules:
        try:
            versions[module]=importlib.metadata.version(module)
        except:
            versions[module]="ERROR"
    return versions


def getRequirements(file="requirements.txt", display=False):
    requirements={}
    
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            line=line.strip()
            if line.find("==")>1:
                name=line[0: line.find("==")].strip()
                val=line[line.find("==")+2:].strip()
            else:
                name=line
                val=""
            requirements[name]=val
        
    if display:
        print("Content of "+file)
        for module in requirements:
            print(" "+"{:<18}".format(module)+requirements[module])
        print(checkVersions(requirements))

    return requirements

def pathJoin(dir, file):
    return os.path.join(dir, file.replace("/", "\\"))

if __name__ == "__main__":
    print(getRequirements("./requirements.txt", True))
