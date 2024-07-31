# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 20:46:07 2022

@author: Zed
"""
from datetime import datetime
from os.path import exists
import json
import os
import pathlib
import progressbar
import requests
import shutil
import subprocess
import urllib
import traceback

pbar = None
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

def try_remove_file(file):
    if exists(file):
        os.remove(file)

def try_remove_dir(dir):
    if exists(dir):
        shutil.rmtree(dir)
        
def downloadNewestLauncher():
    
    InstallDir = AppdataPATH
    
    launchUrl ="https://api.github.com/repos/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/releases"
    response = requests.get(url = launchUrl, params = {'address':"yolo"})
    if response is not None and response.status_code == 200:
      # didnt get rate limited yay
      r = json.loads(json.dumps(response.json()))
      LatestRel = datetime.strptime(r[0].get("published_at").replace("T"," ").replace("Z",""),'%Y-%m-%d %H:%M:%S')
      LatestRelAssetsURL = (json.loads(json.dumps(requests.get(url = r[0].get("assets_url"), params = {'address':"yolo"}).json())))[0].get("browser_download_url")
    else:
      # fall back to some hard-coded release, surely we won't forget to update this occasionally
      print("WARNING: failed to query github API, you might be rate-limited. Using default fallback release instead.")
      LatestRel = datetime(2023, 7, 23)
      LatestRelAssetsURL = "https://github.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/releases/download/v1.10fixoldpckernel/openGOALModLauncher.exe"

    LastWrite = datetime(2020, 5, 17)
    if (os.path.exists(AppdataPATH + "\\OpengoalModLauncher.exe")):
        LastWrite = datetime.utcfromtimestamp( pathlib.Path(AppdataPATH + "\\OpengoalModLauncher.exe").stat().st_mtime)

    #update checks

    needUpdate = bool((LastWrite < LatestRel))

    print("Currently installed version created on: " + LastWrite.strftime('%Y-%m-%d %H:%M:%S'))
    print("Newest version created on: " + LatestRel.strftime('%Y-%m-%d %H:%M:%S'))

    if (needUpdate):
        
        #start the actual update method if needUpdate is true
        print("Starting Update...")
        #download update from github
        # Create a new directory because it does not exist
        try_remove_dir(AppdataPATH + "/temp")
        if not os.path.exists(AppdataPATH + "/temp"):
            print("Creating install dir: " + AppdataPATH)
            os.makedirs(AppdataPATH + "/temp")

        print("Downloading update from " + LatestRelAssetsURL)
        file = urllib.request.urlopen(LatestRelAssetsURL)
        print(file.length)
        
        urllib.request.urlretrieve(LatestRelAssetsURL, AppdataPATH + "/temp/OpengoalModLauncher.exe", show_progress)
        print("Done downloading")
        
        
        #delete any previous installation
        print("Removing previous installation " + AppdataPATH)
        try_remove_dir(InstallDir + "/data")
        try_remove_file(InstallDir + "/gk.exe")
        try_remove_file(InstallDir + "/goalc.exe")
        try_remove_file(InstallDir + "/extractor.exe")
        print("Extracting update")
        TempDir = InstallDir + "/temp"
        

        #delete the update archive
        try_remove_file(TempDir + "/updateDATA.zip")

        SubDir = TempDir
        print("Moving files from " + SubDir + " up to " + InstallDir)
        allfiles = os.listdir(SubDir)
        for f in allfiles:
            shutil.move(SubDir + "/" + f, InstallDir + "/" + f)
        try_remove_dir(TempDir)
        
# check for launcher update
try:
  AppdataPATH = os.getenv('APPDATA') + "\\OpenGOAL-UnofficalModLauncher\\"
  print(AppdataPATH)

  if os.path.exists(AppdataPATH) == False:
      print("Creating Directory " + AppdataPATH)
      os.mkdir(AppdataPATH)

  downloadNewestLauncher()
except Exception as e:
  print("An unexcepted error occurred: ", e)
  traceback.print_exc()

# run launcher
try:
  subprocess.call([AppdataPATH + "OpengoalModLauncher.exe"])
except Exception as e:
  print("An unexcepted error occurred: ", e)
  traceback.print_exc()  