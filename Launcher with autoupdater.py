# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 20:46:07 2022

@author: Zed
"""


from PIL import Image 
from datetime import datetime
from os.path import exists
from tkinter import filedialog
from utils import launcherUtils, githubUtils
import PySimpleGUI as sg
import base64
import cloudscraper
import io
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
		
def downloadNewestmod():
	print("test")
	InstallDir = AppdataPATH
	
	launchUrl ="https://api.github.com/repos/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/releases"
	PARAMS = {'address':"yolo"} 
	r = json.loads(json.dumps(requests.get(url = launchUrl, params = PARAMS).json()))
	LatestRel = datetime.strptime(r[0].get("published_at").replace("T"," ").replace("Z",""),'%Y-%m-%d %H:%M:%S')
	LatestRelAssetsURL = (json.loads(json.dumps(requests.get(url = r[0].get("assets_url"), params = PARAMS).json())))[0].get("browser_download_url")
	response = requests.get(url = LatestRelAssetsURL, params = PARAMS)
	content_type = response.headers['content-type']

	LastWrite = datetime(2020, 5, 17)
	if (os.path.exists(AppdataPATH + "\\OpengoalModLauncher.exe")):
		LastWrite = datetime.utcfromtimestamp( pathlib.Path(InstallDir + "/" + ExecutableName).stat().st_mtime)
	print(LastWrite)
	
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
		request.urlretrieve(LatestRelAssetsURL, AppdataPATH + "/temp/OpengoalModLauncher.exe", show_progress)
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
		

	
	
	
if getattr(sys, 'frozen', False):
    LauncherDir = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    LauncherDir = os.path.dirname(__file__)

installpath = str(LauncherDir + "\\resources\\")
AppdataPATH = os.getenv('APPDATA') + "\\OpenGOAL-UnofficalModLauncher\\"
print(AppdataPATH)

if os.path.exists(AppdataPATH) == False:
	print("Creating Directory " + AppdataPATH)
	os.mkdir(AppdataPATH)

	if os.path.exists(AppdataPATH + "\\OpengoalModLauncher.exe") == False:
		print("No Mod Launcher detected")
		downloadNewestmod()
print("test")
subprocess.call([AppdataPATH + "OpengoalModLauncher.exe"])
	
	