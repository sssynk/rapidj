from os import wait
import os
import os.path
import eel
import eel.browsers

import time
import subprocess
import wx
import sys
import unicodedata

running = False
currentfile = None

def setcurrentfile():
    f = open(os.getcwd()+"/data.rapidj", "w")
    f.writelines([currentfile])

def getasfile():
    if os.path.exists("data.rapidj"):
        f = open(os.getcwd()+"/data.rapidj", "r")
        return f.readline()
    else:
        return None

@eel.expose
def run(jinput):
    global running
    global currentfile
    print(currentfile)
    if not running:
        running = True
        if currentfile is not None:
            check = open(currentfile, "r")
            if jinput is not check.read():
                print("File Not Saved Dialogue")
            setcurrentfile()
            f = open(currentfile, "w")
            f.write(jinput)
            f.close()
            print("Running:")
            print(["javac", "-g", currentfile])
            currentfilename = os.path.basename(currentfile)
            currentfiledir = os.path.dirname(currentfile)
            ret = subprocess.Popen(["javac", "-g", currentfilename], cwd=currentfiledir,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            error = ret.communicate()
            if ret.returncode == 1:
                print("Unable to compile.")
                if error[0] == '':
                    eel.error(ret.returncode, error[1])
                else:
                    eel.error(ret.returncode, error[0])
                running = False
            else:
                output = None
                print("Compile success!")
                eel.compilesuccess()
                print("Running")
                if isinstance(currentfilename, str):
                    currentfilestr = currentfilename
                else:
                    currentfilestr = unicodedata.normalize('NFKD', currentfilename).encode('ascii', 'ignore')
                currentfilenoend = currentfilestr[0:int(len(currentfilestr)-5)]
                print("Running:")
                print(["java", currentfilenoend])
                proc = subprocess.Popen(["java", currentfilenoend], cwd=currentfiledir,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output = proc.communicate()
                final = []
                for item in output:
                    if item is not '':
                        final.append(item)
                eel.outputj(final)
                while proc.poll() is None:
                    time.sleep(0.1)
                eel.finished()
                running = False
                print("Finished run")
        else:
            eel.error("1", "File not found, Make sure file is saved\n")

@eel.expose
def openFile(wildcard="*"):
    global currentfile
    app = wx.App(None)
    style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
    dialog = wx.FileDialog(None, 'Open Java File', wildcard="Java files (*.java)|*.java", style=style)
    if dialog.ShowModal() == wx.ID_OK:
        path = dialog.GetPath()
        currentfile = dialog.GetPath()
        cf = open(path, "r")
        eel.setFile(cf.read(), currentfile)
    else:
        path = None
    dialog.Destroy()
    return path
        
@eel.expose
def saveFile(input):
    global currentfile
    if not currentfile:
        app = wx.App(None)
        style = wx.FD_SAVE
        dialog = wx.FileDialog(None, 'Save Java File', wildcard="Java files (*.java)|*.java", style=style)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            c = open(path, "w")
            c.write(input)
            c.close()
            currentfile = path
            eel.setFile(input, path)
            print("saved")
        dialog.Destroy()
        setcurrentfile()
    else:
        c = open(currentfile, "w")
        c.write(input)
        c.close()
        print("saved")
        setcurrentfile()

@eel.expose
def newFile():
    global currentfile
    currentfile = None

@eel.expose
def initC():
    global currentfile
    currentfile = getasfile()
    if currentfile is not None:
        print(currentfile)
        cf = open(currentfile, "r")
        eel.setFile(cf.read(), currentfile)

eel.init('ui')
#eel.browsers.set_path('electron', 'jwilson/Applications/Electron.app/Contents/MacOS/Electron')
eel.start('index.html', mode='chrome')