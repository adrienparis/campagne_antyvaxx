from genericpath import exists
import os
import time
import io
import tkinter as tk
from datetime import datetime


from tkinter import filedialog

PROGSEARCHSIZE = 30

class SearchingBar():
    def __init__(self):
        self.i = 0
        self.direction = 1
        self.speed = 0.01
        self.size = PROGSEARCHSIZE

    def print(self):
        totalSize = os.get_terminal_size().columns
        if self.i >= self.size:
            self.direction = -1
        elif self.i <= 0:
            self.direction = 1
        self.i += self.direction * self.speed 
        cursor = int(self.i)
        bar = " " * cursor + "*" + " " * (self.size - cursor) 
        line = "█{}█".format(bar)
        line = line[:totalSize]
        print(line, end="\r")


def isCorrupt(path):
    corruptNode = 'vaccine_gene'
    with io.open(path, "rb") as f:
        if bytes(corruptNode, 'utf-8') in f.read():
            return True
    return False

def progress(i, total, f, perct=False):
    i += 1
    if perct == False:
        percent = int((i * 100.0)/total)
    else:
        percent = int(perct)
    size = PROGSEARCHSIZE / 100.0
    totalSize = os.get_terminal_size().columns
    p = int(percent * size)
    maxSize = int(100 * size)
    progressBar = "█" * p + " " * (maxSize - p)
    line = "{: 3d} % |{}| {: {}d}/{}  -> {}".format(percent, progressBar,i, len(str(total)) + 1, total, f)
    line = line + " " * (totalSize - len(line))
    line = line[:totalSize - 1]
    print(line, end="\r")

def unzipFile(path):
    pass

def getMayaFiles(directory):
    print("\nSearching maya files")
    schBar = SearchingBar()
    mayaFilesList = []
    for root, subdirs, files in os.walk(directory):
        mayaFiles = [os.path.join(root, x) for x in files if x.endswith(".ma")]
        mayaFilesList += mayaFiles
        schBar.print()
    return mayaFilesList

def searching():
    print("Starting")
    mayaFilesList = getMayaFiles(directory_path)
    totalSize = sum([os.path.getsize(x) for x in mayaFilesList])
    print("\n {} bytes to analyze".format(totalSize))
    print("\nAnalyzing maya files")
    nbFiles = len(mayaFilesList)
    oldPercent = 0
    corruptedFiles = []
    searchedSize = 0.0
    try:
        for i, mf_path in enumerate(mayaFilesList):
            mf_path = os.path.normpath(mf_path)

            progress(i, nbFiles, mf_path, searchedSize * 100.0 / totalSize)
            searchedSize += os.path.getsize(mf_path)
            if isCorrupt(mf_path):
                time_str = time.ctime(os.path.getmtime(mf_path))
                t = datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
                corruptedFiles.append([t, mf_path])
        progress(nbFiles, nbFiles, "Done !", 100.0)
    except KeyboardInterrupt:
        progress(i, nbFiles, "CANCELED", searchedSize * 100.0 / totalSize)
        print("\n\nStop the search at : \n\t" + mf_path)
    print("\n\nDone !")
    return corruptedFiles



root = tk.Tk()
root.withdraw()
directory_path = filedialog.askdirectory(title="Sélectionnez un dossier à analyser")
if directory_path == "":
    quit()
FolderName = directory_path.replace("/", "_").replace(":", "")


corruptedFiles = searching()
corruptedFiles = sorted(corruptedFiles, key=lambda x: x[0])
reportFileName = "report_{}.txt".format(FolderName)
lines = ["{} - {}\n".format(x[0], x[1]) for x in corruptedFiles]
with open(reportFileName, "w+") as report:
    report.writelines(lines)
os.system('notepad.exe "{}"'.format(reportFileName))
