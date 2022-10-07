# -*- coding: utf-8 -*-
"""
Created on Fri Aug 12 06:51:37 2022

@author: Zed
"""
from datetime import datetime
from os.path import exists
from tkinter import filedialog
from utils import githubUtils
import json
import os
import pathlib
import progressbar
import requests
import shutil
import subprocess
import sys
import time
import tkinter as tk
import urllib.request
import zipfile

EXTRACT_ON_UPDATE="true"            
FILE_DATE_TO_CHECK="gk.exe"
UPDATE_FILE_EXTENTION=".zip"

# Folder where script is placed, It looks in this for the Exectuable
if getattr(sys, 'frozen', False):
    LauncherDir = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    LauncherDir = os.path.dirname(__file__)

extractOnUpdate = bool(str(EXTRACT_ON_UPDATE).replace("t","T").replace("f", "F"))
ExecutableName = str(FILE_DATE_TO_CHECK) # Executable we're checking the 'modified' time of
FileExt = str(UPDATE_FILE_EXTENTION) # content_type of the .deb release is also "application\zip", so rely on file ext
FileIdent = "" # If we ever get to multiple .zip files in a release, include other identifying information from the name (e.g. "windows-x64")


pbar = None

def installedlist(PATH):
    print(PATH)
    scanDir = PATH
    directories = [d for d in os.listdir(scanDir) if os.path.isdir(os.path.join(os.path.abspath(scanDir), d))]
    print(directories)
    for i in directories:
        print(i)
    print(os.path.dirname(os.path.dirname(PATH)))

def show_progress(block_num, block_size, total_size):
    if total_size > 0:
        global pbar
        if pbar is None:
            pbar = progressbar.ProgressBar(maxval=total_size)
            pbar.start()

        downloaded = block_num * block_size
        
        if downloaded < total_size:
            pbar.update(downloaded)
        else:
            pbar.finish()
            pbar = None

def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    try:
        # use buildin check_output right away
        output = subprocess.check_output(call).decode()
        # check in last line for process name
        last_line = output.strip().split('\r\n')[-1]
        # because Fail message could be translated
        return last_line.lower().startswith(process_name.lower())
    except:
        return False

def try_kill_process(process_name):
    if process_exists(process_name):
        os.system("taskkill /f /im " + process_name)

def try_remove_file(file):
    if exists(file):
        os.remove(file)

def try_remove_dir(dir):
    if exists(dir):
        shutil.rmtree(dir)

def local_mod_image(MOD_NAME):
    path = os.getenv('APPDATA') + "\\OpenGOAL-Mods\\" + MOD_NAME + "\\ModImage.png"
    if exists(path):
        return path
    return None

def launch_local(MOD_NAME):
    try:
        #Close Gk and goalc if they were open.
        try_kill_process("gk.exe")
        try_kill_process("goalc.exe")

        time.sleep(1)
        InstallDir = os.getenv('APPDATA') + "\\OpenGOAL-Mods\\" + MOD_NAME
        AppdataPATH = os.getenv('APPDATA')
        UniversalIsoPath = AppdataPATH + "\OpenGOAL\jak1\mods\data\iso_data\iso_data"
        GKCOMMANDLINElist = [InstallDir +"\gk.exe", "-proj-path", InstallDir + "\\data", "-boot", "-fakeiso", "-v"]
        print(GKCOMMANDLINElist)
        subprocess.Popen(GKCOMMANDLINElist, shell=True)
    except e:
        return str(e)

def openFolder(path):
    FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    subprocess.run([FILEBROWSER_PATH, path])

def reinstall(MOD_NAME):
    InstallDir = os.getenv('APPDATA') + "\\OpenGOAL-Mods\\" + MOD_NAME
    AppdataPATH = os.getenv('APPDATA')
    UniversalIsoPath = AppdataPATH + "\OpenGOAL\jak1\mods\data\iso_data\iso_data"
    GKCOMMANDLINElist = [InstallDir +"\gk.exe", "-proj-path", InstallDir + "\\data", "-boot", "-fakeiso", "-v"]

    #if ISO_DATA has content, store this path to pass to the extractor
    if (exists(UniversalIsoPath +r"\jak1\Z6TAIL.DUP")):
        iso_path = UniversalIsoPath + "\jak1"
    else:
        #if ISO_DATA is empty, prompt for their ISO and store its path.
        root = tk.Tk()
        print("Please select your iso.")
        root.title("Select ISO")
        root.geometry('230x1')
        iso_path = filedialog.askopenfilename()
        root.destroy()
        if (pathlib.Path(iso_path).is_file):
            if ((not (pathlib.Path(iso_path).suffix).lower() == '.iso')):
                1/0

    #Close Gk and goalc if they were open.
    try_kill_process("gk.exe")
    try_kill_process("goalc.exe")
    print("Done update starting extractor\n")
    extractor_command_list = [InstallDir +"\extractor.exe", "-f", iso_path]
    print(extractor_command_list)
    
    subprocess.Popen(extractor_command_list)

    #wait for extractor to finish
    while (process_exists("extractor.exe")):
            print("extractor.exe still running, sleeping for 1s")
            time.sleep(1)
    
    #move the extrated contents to the universal launchers directory for next time.
    if not (exists(( UniversalIsoPath + r"\jak1\Z6TAIL.DUP"))):
        #os.makedirs(AppdataPATH + "\OpenGOAL-Launcher\data\iso_data")
        print("The new directory is created!")
        shutil.move(InstallDir + "/data/iso_data", "" + UniversalIsoPath +"")
        #try_remove_dir(InstallDir + "/data/iso_data")
        #os.symlink("" + UniversalIsoPath +"", InstallDir + "/data/iso_data")

def launch(URL, MOD_NAME, LINK_TYPE):
    if URL is None:
        return

    #start of update check method
    #Github API Call
    launchUrl = URL
    if LINK_TYPE == githubUtils.LinkTypes.BRANCH:
        launchUrl = githubUtils.branchToApiURL(URL)

    print("\nlaunching from " + launchUrl)
    PARAMS = {'address':"yolo"} 
    r = json.loads(json.dumps(requests.get(url = launchUrl, params = PARAMS).json()))

    #paths  
    InstallDir = os.getenv('APPDATA') + "\\OpenGOAL-Mods\\" + MOD_NAME
    AppdataPATH = os.getenv('APPDATA')
    UniversalIsoPath = AppdataPATH + "\OpenGOAL\jak1\mods\data\iso_data\iso_data"
    GKCOMMANDLINElist = [InstallDir +"\gk.exe", "-proj-path", InstallDir + "\\data", "-boot", "-fakeiso", "-v"]

    #store Latest Release and check our local date too.
    if LINK_TYPE == githubUtils.LinkTypes.BRANCH:
        LatestRel = datetime.strptime(r.get("commit").get("commit").get("author").get("date").replace("T"," ").replace("Z",""),'%Y-%m-%d %H:%M:%S')
        LatestRelAssetsURL = githubUtils.branchToArchiveURL(URL)
    elif LINK_TYPE == githubUtils.LinkTypes.RELEASE:
        LatestRel = datetime.strptime(r[0].get("published_at").replace("T"," ").replace("Z",""),'%Y-%m-%d %H:%M:%S')
        LatestRelAssetsURL = (json.loads(json.dumps(requests.get(url = r[0].get("assets_url"), params = PARAMS).json())))[0].get("browser_download_url")
        response = requests.get(url = LatestRelAssetsURL, params = PARAMS)
        content_type = response.headers['content-type']

    
    LastWrite = datetime(2020, 5, 17)
    if (exists(InstallDir + "/" + ExecutableName)):
        LastWrite = datetime.utcfromtimestamp( pathlib.Path(InstallDir + "/" + ExecutableName).stat().st_mtime)

    #update checks
    NotExtracted = bool(not (exists(UniversalIsoPath +r"\jak1\Z6TAIL.DUP")))
    NotCompiled = bool(not (exists (InstallDir + r"\data\out\jak1\fr3\GAME.fr3")))
    needUpdate = bool((LastWrite < LatestRel) or (NotExtracted) or NotCompiled)

    print("Currently installed version created on: " + LastWrite.strftime('%Y-%m-%d %H:%M:%S'))
    print("Newest version created on: " + LatestRel.strftime('%Y-%m-%d %H:%M:%S'))

    if (needUpdate):
        
        #start the actual update method if needUpdate is true
        print("\nNeed to update")
        print("Starting Update...")
        #Close Gk and goalc if they were open.
        try_kill_process("gk.exe")
        try_kill_process("goalc.exe")

        #download update from github
        # Create a new directory because it does not exist
        try_remove_dir(InstallDir + "/temp")
        if not os.path.exists(InstallDir + "/temp"):
            print("Creating install dir: " + InstallDir)
            os.makedirs(InstallDir + "/temp")
        
        
        r = requests.get(LatestRelAssetsURL, allow_redirects=True)
        r.status_code  # 302
        #print(r.url)  # http://github.com, not https.
        #print(r.headers)  # https://github.com/ -- the redirect destination

        response = requests.get(LatestRelAssetsURL)
        if response.history:
            print("Request was redirected")
            for resp in response.history:
                print(resp.status_code, resp.url)
                print("Final destination:")
                print(response.status_code, response.url)
                LatestRelAssetsURL = response.url
                
        else:
            print("Request was not redirected")
    

        print("Downloading update from " + LatestRelAssetsURL)
        file = urllib.request.urlopen(LatestRelAssetsURL)
        print()
        print(str("File size is ") + str(file.length))
        urllib.request.urlretrieve(LatestRelAssetsURL, InstallDir + "/temp/updateDATA.zip", show_progress)
        print("Done downloading")
        r = requests.head(LatestRelAssetsURL, allow_redirects=True)
    
        
        #delete any previous installation
        print("Removing previous installation " + InstallDir)
        try_remove_dir(InstallDir + "/data")
        try_remove_file(InstallDir + "/gk.exe")
        try_remove_file(InstallDir + "/goalc.exe")
        try_remove_file(InstallDir + "/extractor.exe")

        #if ISO_DATA has content, store this path to pass to the extractor
        if (exists(UniversalIsoPath +r"\jak1\Z6TAIL.DUP")):
            iso_path = UniversalIsoPath + "\jak1"
        else:
            #if ISO_DATA is empty, prompt for their ISO and store its path.
            root = tk.Tk()
            print("Please select your iso.")
            root.title("Select ISO")
            root.geometry('230x1')
            iso_path = filedialog.askopenfilename()
            root.destroy()
            if (pathlib.Path(iso_path).is_file):
                if ((not (pathlib.Path(iso_path).suffix).lower() == '.iso')):
                    1/0
        #extract update
        print("Extracting update")
        TempDir = InstallDir + "/temp"
        with zipfile.ZipFile(TempDir + "/updateDATA.zip","r") as zip_ref:
            zip_ref.extractall(TempDir)

        #delete the update archive
        try_remove_file(TempDir + "/updateDATA.zip")

        SubDir = TempDir
        if LINK_TYPE == githubUtils.LinkTypes.BRANCH or len(os.listdir(SubDir)) == 1:
            # for branches, the downloaded zip puts all files one directory down
            SubDir = SubDir + "/" + os.listdir(SubDir)[0]

        print("Moving files from " + SubDir + " up to " + InstallDir)
        allfiles = os.listdir(SubDir)
        for f in allfiles:
            shutil.move(SubDir + "/" + f, InstallDir + "/" + f)
        try_remove_dir(TempDir)

        #if extractOnUpdate is True, check their ISO_DATA folder

        #Close Gk and goalc if they were open.
        try_kill_process("gk.exe")
        try_kill_process("goalc.exe")
        print("Done update starting extractor This one can take a few moments! \n")
        extractor_command_list = [InstallDir +"\extractor.exe", "-f", iso_path]
        print(extractor_command_list)
        
        subprocess.Popen(extractor_command_list)
        
        #move the extrated contents to the universal launchers directory for next time.
        if not (exists(( UniversalIsoPath + r"\jak1\Z6TAIL.DUP"))):
            while (process_exists("extractor.exe")):
                print("extractor.exe still running, sleeping for 1s")
                time.sleep(1)
        if not (exists(( UniversalIsoPath + r"\jak1\Z6TAIL.DUP"))):
            #os.makedirs(AppdataPATH + "\OpenGOAL-Launcher\data\iso_data")
            print("The new directory is created!")
            shutil.move(InstallDir + "/data/iso_data", "" + UniversalIsoPath +"")
            #try_remove_dir(InstallDir + "/data/iso_data")
            #os.symlink("" + UniversalIsoPath +"", InstallDir + "/data/iso_data")

    else:
        #if we dont need to update, then close any open instances of the game and just launch it
        print("Game is up to date!")
        print("Launching now!")
        launch_local(MOD_NAME)