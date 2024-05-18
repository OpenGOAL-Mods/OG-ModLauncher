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
from zipfile import BadZipFile
from appdirs import AppDirs
import platform
import stat
from pathlib import Path
import time
import ctypes

FILE_DATE_TO_CHECK = "gk.exe"
UPDATE_FILE_EXTENTION = ".zip"

# Folder where script is placed, It looks in this for the Exectuable
if getattr(sys, "frozen", False):
    LauncherDir = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    LauncherDir = os.path.dirname(__file__)

ExecutableName = str(
    FILE_DATE_TO_CHECK
)  # Executable we're checking the 'modified' time of
FileExt = str(
    UPDATE_FILE_EXTENTION
)  # content_type of the .deb release is also "application\zip", so rely on file ext
FileIdent = ""  # If we ever get to multiple .zip files in a release, include other identifying information from the name
dirs = AppDirs(roaming=True)
currentOS = platform.system()
ModFolderPATH = os.path.join(dirs.user_data_dir, "OpenGOAL-Mods", "")
AppdataPATH = dirs.user_data_dir


pbar = None







def installedlist(PATH):
    print(PATH)
    scanDir = PATH
    directories = [
        d
        for d in os.listdir(scanDir)
        if os.path.isdir(os.path.join(os.path.abspath(scanDir), d))
    ]
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
    call = "TASKLIST", "/FI", "imagename eq %s" % process_name
    try:
        # use buildin check_output right away
        output = subprocess.check_output(call).decode()
        # check in last line for process name
        last_line = output.strip().split("\r\n")[-1]
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

def is_junction(path: str) -> bool:
    try:
        return bool(os.readlink(path))
    except OSError:
        return False

def try_remove_dir(dir):
    if exists(dir):
        print(f"found dir {dir}, attempting to remove")
        shutil.rmtree(dir)
    else:
        print(f"didnt find dir {dir}")


def local_mod_image(MOD_ID):
    path = ModFolderPATH + MOD_ID + "/ModImage.png"
    if exists(path):
        return path
    return None



def moveDirContents(src, dest):
  # moves all files from src to dest, without moving src dir itself
  for f in os.listdir(src):
      src_path = os.path.join(src, f)
      dst_path = os.path.join(dest, f)
      shutil.move(src_path, dst_path)

def makeDirSymlink(link, target):
    subprocess.check_call('mklink /J "%s" "%s"' % (link, target), shell=True)


def makeFileSymlink(link, target):
    # if ctypes.windll.shell32.IsUserAnAdmin():
    #     subprocess.check_call('mklink "%s" "%s"' % (link, target), shell=True)
    # else:
    subprocess.check_call('mklink /H "%s" "%s"' % (link, target), shell=True)

def link_files_by_extension(source_dir, destination_dir):
    # Ensure the source directory exists
    if not os.path.exists(source_dir):
        print(f"Source directory '{source_dir}' does not exist.")
        return

    # Ensure the destination directory exists
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Loop through the contents of the source directory
    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)

        # Check if it's a file and its extension matches the specified extension
        if os.path.isfile(file_path):
            # Construct the destination path
            destination_path = os.path.join(destination_dir, filename)

            # Check if the destination file already exists
            if os.path.exists(destination_path):
                # Delete the file from the destination location.
                os.remove(destination_path)

            # Create a symbolic link from the source location to the destination location.
            #print("making " + destination_path + "<-des source ->" + file_path)
            makeFileSymlink(destination_path, file_path)

def openFolder(path):
    if not exists(dirs.user_data_dir + "/OpenGOAL/" + "mods/data/iso_data/jak2"):
        os.makedirs(dirs.user_data_dir + "/OpenGOAL/" + "mods/data/iso_data/jak2")
    FILEBROWSER_PATH = os.path.join(os.getenv("WINDIR"), "explorer.exe")
    print(path)
    subprocess.run([FILEBROWSER_PATH, path])

def replaceText(path, search_text, replace_text):
    # Check if the file exists
    if not os.path.isfile(path):
        print(f"File '{path}' does not exist.")
        return

    # Open the file in read-only mode
    with open(path, "r") as file:
        data = file.read()

    # Perform the search and replace operation
    data = data.replace(search_text, replace_text)

    # Open the file in write mode to write the replaced content
    with open(path, "w") as file:
        file.write(data)

    print(f"Text replaced successfully in file '{path}'.")

def ensure_dir(path):
    path.mkdir(parents=True, exist_ok=True)

def open_browser_link():
    url = "https:/google.com"  # Replace with the desired URL
    if sys.platform.startswith('linux'):
        subprocess.Popen(["xdg-open", url])
    elif sys.platform.startswith('win'):
        subprocess.Popen(["start", url], shell=True)
    elif sys.platform.startswith('darwin'):
        subprocess.Popen(["open", url])
    else:
        print("Unsupported platform")

def open_folder(path):
    folder_path = path  # Replace with the desired folder path
    if not os.path.exists(path):
    # Create the directory
        try:
            os.makedirs(path)
            print(f"Directory '{path}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{path}': {e}")
    os.startfile(folder_path)

def divide_by_zero():
    1 / 0

def ensure_jak_folders_exist():
    directory = dirs.user_data_dir + "/OpenGOAL-Mods/_iso_data"
    jak1_path = os.path.join(directory, "jak1")
    jak2_path = os.path.join(directory, "jak2")
    jak3_path = os.path.join(directory, "jak3")

    if not os.path.exists(jak1_path):
        os.makedirs(jak1_path)
        print(f"Created 'jak1' folder at {jak1_path}")

    if not os.path.exists(jak2_path):
        os.makedirs(jak2_path)
        print(f"Created 'jak2' folder at {jak2_path}")

    if not os.path.exists(jak3_path):
        os.makedirs(jak3_path)
        print(f"Created 'jak3' folder at {jak3_path}")


#check if we have decompiler in the path, if not check if we have a backup, if so use it, if not download a backup then use it
def getHfragVert(path):
    decompiler_exe = "hfrag.vert"
    decompiler_url = "https://raw.githubusercontent.com/OpenGOAL-Mods/OG-Mod-Base/main/hfrag/"+decompiler_exe

    # Check if the decompiler exists in the provided path
    if os.path.exists(os.path.join(path, decompiler_exe)):
        print(f"Found {decompiler_exe} in the directory.")
        return
    else:
        # Check if the backup decompiler exists
        print(f"Couldn't find {decompiler_exe} in the directory or backup. Downloading it...")
        urllib.request.urlretrieve(decompiler_url, os.path.join(path, decompiler_exe))
        print(f"{decompiler_exe} downloaded successfully as backup.")
    while not os.path.exists(os.path.join(path, decompiler_exe)):
        time.sleep(1)  # Wait for the download to complete

    decompiler_exe = "hfrag_montage.frag"
    decompiler_url = "https://raw.githubusercontent.com/OpenGOAL-Mods/OG-Mod-Base/main/hfrag/"+decompiler_exe


    # Check if the decompiler exists in the provided path
    if os.path.exists(os.path.join(path, decompiler_exe)):
        print(f"Found {decompiler_exe} in the directory.")
        return
    else:
        # Check if the backup decompiler exists
        print(f"Couldn't find {decompiler_exe} in the directory or backup. Downloading it...")
        urllib.request.urlretrieve(decompiler_url, os.path.join(path, decompiler_exe))
        print(f"{decompiler_exe} downloaded successfully as backup.")
    while not os.path.exists(os.path.join(path, decompiler_exe)):
        time.sleep(1)  # Wait for the download to complete

    decompiler_exe = "hfrag_montage.vert"
    decompiler_url = "https://raw.githubusercontent.com/OpenGOAL-Mods/OG-Mod-Base/main/hfrag/"+decompiler_exe


    # Check if the decompiler exists in the provided path
    if os.path.exists(os.path.join(path, decompiler_exe)):
        print(f"Found {decompiler_exe} in the directory.")
        return
    else:
        # Check if the backup decompiler exists
        print(f"Couldn't find {decompiler_exe} in the directory or backup. Downloading it...")
        urllib.request.urlretrieve(decompiler_url, os.path.join(path, decompiler_exe))
        print(f"{decompiler_exe} downloaded successfully as backup.")
    while not os.path.exists(os.path.join(path, decompiler_exe)):
        time.sleep(1)  # Wait for the download to complete

    decompiler_exe = "hfrag.frag"
    decompiler_url = "https://raw.githubusercontent.com/OpenGOAL-Mods/OG-Mod-Base/main/hfrag/"+decompiler_exe

    # Check if the decompiler exists in the provided path
    if os.path.exists(os.path.join(path, decompiler_exe)):
        print(f"Found {decompiler_exe} in the directory.")
        return
    else:
        # Check if the backup decompiler exists
        print(f"Couldn't find {decompiler_exe} in the directory or backup. Downloading it...")
        urllib.request.urlretrieve(decompiler_url, os.path.join(path, decompiler_exe))
        print(f"{decompiler_exe} downloaded successfully as backup.")
    while not os.path.exists(os.path.join(path, decompiler_exe)):
        time.sleep(1)  # Wait for the download to complete

    return







def launch_local(MOD_ID, GAME):
    try:
        # Close Gk and goalc if they were open.
        try_kill_process("gk.exe")
        try_kill_process("goalc.exe")

        time.sleep(1)
        InstallDir = ModFolderPATH + MOD_ID

        if GAME == "jak1":
          GKCOMMANDLINElist = [
              os.path.abspath(InstallDir + "/gk.exe"),  # Using os.path.abspath to get the absolute path.
              "--proj-path",
              os.path.abspath(InstallDir + "/data"),  # Using absolute path for data folder too.
              "-boot",
              "-fakeiso",
              "-v",
          ]
        elif GAME == "jak2":
          GKCOMMANDLINElist = [
            InstallDir + "/gk.exe",
            "--proj-path",
            InstallDir + "/data",
            "-v",
            "--game",
            GAME,
            "--",
            "-boot",
            "-fakeiso"
          ]
        else: # GAME == "jak3"
          GKCOMMANDLINElist = [
            InstallDir + "/gk.exe",
            "--proj-path",
            InstallDir + "/data",
            "-v",
            "--game",
            GAME,
            "--",
            "-boot",
            "-fakeiso",
            "-debug" # TODO retail mode once ready
          ]

        print("Running: ", GKCOMMANDLINElist)

        # with check=True, nonzero return code will throw CalledProcessError and be caught below
        subprocess.run(GKCOMMANDLINElist, shell=True, cwd=os.path.abspath(InstallDir), check=True)
    except subprocess.CalledProcessError as err:
        print(f"Subprocess error: {err}")
    except Exception as e:  # Catch all exceptions and print the error message.
        print("Encountered exception: ", e)

def download_and_unpack_mod(URL, MOD_ID, MOD_NAME, LINK_TYPE, InstallDir, LatestRelAssetsURL):
    #start the actual update method if needUpdate is true
    print("\nNeed to update")
    print("Starting Update...")
    # Close Gk and goalc if they were open.
    try_kill_process("gk.exe")
    try_kill_process("goalc.exe")

    # download update from github
    # Create a new directory because it does not exist
    try_remove_dir(InstallDir + "/temp")
    if not os.path.exists(InstallDir + "/temp"):
        print("Creating install dir: " + InstallDir)
        os.makedirs(InstallDir + "/temp", exist_ok=True)

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
    urllib.request.urlretrieve(
        LatestRelAssetsURL, InstallDir + "/temp/updateDATA.zip", show_progress
    )
    print("Done downloading")
    r = requests.head(LatestRelAssetsURL, allow_redirects=True)

    # delete any previous installation
    print("Removing previous installation " + InstallDir)
    try_remove_dir(InstallDir + "/data")
    try_remove_dir(InstallDir + "/.github")
    try_remove_dir(InstallDir + "/SND")
    try_remove_file(InstallDir + "/gk.exe")
    try_remove_file(InstallDir + "/goalc.exe")
    try_remove_file(InstallDir + "/extractor.exe")
    #jak2hack
    try_remove_file(InstallDir + "/decompiler.exe")

    # extract mod zipped update
    print("Extracting update")
    TempDir = InstallDir + "/temp"
    try:
      with zipfile.ZipFile(TempDir + "/updateDATA.zip", "r") as zip_ref:
        zip_ref.extractall(TempDir)
    except BadZipFile as e:
      print("Error while extracting from zip: ", e)
      return

    # delete the mod zipped update archive
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

    getHfragVert(InstallDir + "/data/game/graphics/opengl_renderer/shaders/")
    #replace the settings and discord RPC texts automatically before we build the game.
    replaceText(
      InstallDir + "/data/goal_src/jak1/pc/pckernel.gc",
      "Playing Jak and Daxter: The Precursor Legacy",
      "Playing " + MOD_NAME,
    )
    replaceText(
      InstallDir + "/data/goal_src/jak1/pc/pckernel.gc",
      "/pc-settings.gc",
      "/" + MOD_ID + "-settings.gc",
    )
    replaceText(
      InstallDir + "/data/goal_src/jak1/pc/pckernel-common.gc",
      "/pc-settings.gc",
      "/" + MOD_ID + "-settings.gc",
    )
    replaceText(
      InstallDir + "/data/goal_src/jak1/pc/pckernel-common.gc",
      "/pc-settings.gc",
      "/" + MOD_ID + "-settings.gc",
    )
    replaceText(
      InstallDir + "/data/decompiler/config/jak1_ntsc_black_label.jsonc",
      "\"process_tpages\": true,",
      "\"process_tpages\": false,",
    )
    replaceText(
      InstallDir + "/data/decompiler/config/jak1_pal.jsonc",
      "\"process_tpages\": true,",

      "\"process_tpages\": false,",
    )

def rebuild(URL, MOD_ID, MOD_NAME, LINK_TYPE, GAME, should_extract):
  try:
    InstallDir = ModFolderPATH + MOD_ID
    UniversalIsoPath = AppdataPATH + "/OpenGOAL-Mods/_iso_data"

    print("Looking for some ISO data in " + UniversalIsoPath + "/" + GAME + "/")
    # jak3 jak 3 3 jak
    found_universal_iso = exists(UniversalIsoPath + "/" + GAME + "/" + "Z6TAIL.DUP") or exists(UniversalIsoPath + "/" + GAME + "/" + "ZZTAIL.DAT")

    #if ISO_DATA has content, store this path to pass to the extractor
    if found_universal_iso:
        print("We found ISO data from a previous mod installation! Lets use it!")
        print("Found in " + UniversalIsoPath +"/" + GAME + "/" + "Z6TAIL.DUP")
        iso_path = UniversalIsoPath + "/" + GAME

        # if not is_junction(InstallDir + "/data/iso_data"):
        #   # we have iso extracted to universal folder already, just symlink it. otherwise we'll copy it there and symlink after extractor closes
        #   try_remove_dir(InstallDir + "/data/iso_data/")
        #   makeDirSymlink(InstallDir + "/data/iso_data/", UniversalIsoPath)
    else:
        print("We did not find " + GAME + " ISO data from a previous mod, lets ask for some!")

        # cleanup and remove a corrupted iso
        # jak3 jak 3 3 jak
        if GAME != "jak3" and os.path.exists(UniversalIsoPath + "/" + GAME) and os.path.isdir(UniversalIsoPath) and not (exists((UniversalIsoPath + "/" + GAME + "/" + "Z6TAIL.DUP"))) or (exists((UniversalIsoPath + "/" + GAME + "/" + "ZZTAIL.DAT"))) :
            print("Removing corrupted iso destination...")
            shutil.rmtree(UniversalIsoPath + "/" + GAME)
            ensure_jak_folders_exist()

        # prompt for their ISO and store its path
        root = tk.Tk()
        prompt = "Please select your " + GAME + " ISO"
        print(prompt)
        root.title(prompt)
        root.geometry("230x1")
        root.wm_attributes('-topmost', 1)
        iso_path = filedialog.askopenfilename(parent=root, title=prompt)
        root.destroy()
        if iso_path == "":
          print("user closed popup")
          return
        if pathlib.Path(iso_path).is_file:
            if not (pathlib.Path(iso_path).suffix).lower() == ".iso":
                print("yo, this is not an ISO: " + (pathlib.Path(iso_path).suffix).lower())
                return

    # Close Gk and goalc if they were open.
    try_kill_process("gk.exe")
    try_kill_process("goalc.exe")
    print("Done updating, starting extractor. This can take a few minutes! \n")

    #Extract and compile
    if GAME == "jak1":
        extractor_command_list = [InstallDir + "/extractor.exe", "-f", iso_path, "-v", "-c"]
        if should_extract:
            extractor_command_list.append("-e")
            extractor_command_list.append("-d")
        print(extractor_command_list)

        # with check=True, nonzero return code will throw CalledProcessError and be caught below
        subprocess.run(extractor_command_list, shell=True, cwd=os.path.abspath(InstallDir), check=True)

    else: # GAME == "jak2" or GAME == "jak3"
        extractor_command_list = [InstallDir + "/extractor.exe", "-f", iso_path, "-v", "-c", "-g", GAME]
        if should_extract:
            extractor_command_list.append("-e")
            extractor_command_list.append("-d")
        print(extractor_command_list)

        # with check=True, nonzero return code will throw CalledProcessError and be caught below
        subprocess.run(extractor_command_list, shell=True, cwd=os.path.abspath(InstallDir), check=True)

    # symlink isodata for custom levels art group (goalc doesnt take -f flag)
    # if exists(UniversalIsoPath + r"" + "/" + GAME + "/" + "Z6TAIL.DUP") and GAME == "jak1":
    #     ensure_jak_folders_exist();
    #     makeDirSymlink(InstallDir + "/data/iso_data/" + GAME, UniversalIsoPath + "/" + GAME)

    # move the extracted contents to the universal launchers directory for next time.
    if not found_universal_iso:
        ensure_jak_folders_exist()
        moveDirContents(InstallDir + "/data/iso_data/" + GAME, UniversalIsoPath + "/" + GAME)
        # # replace iso_data with symlink
        # try_remove_dir(InstallDir + "/data/iso_data/")
        # makeDirSymlink(InstallDir + "/data/iso_data", UniversalIsoPath)

    print("Done extracting! Launching game!")

    launch_local(MOD_ID, GAME)
  except subprocess.CalledProcessError as err:
    print(f"Subprocess error: {err}")
  except Exception as e:
    print("Caught exception: ", e)

def update_and_launch(URL, MOD_ID, MOD_NAME, LINK_TYPE, GAME):
    if URL is None:
        return

    # start of update check method
    # Github API Call
    launchUrl = URL
    if LINK_TYPE == githubUtils.LinkTypes.BRANCH:
      launchUrl = githubUtils.branchToApiURL(URL)
    LatestRelAssetsURL = ""

    print("\nlaunching from " + launchUrl)
    PARAMS = {"address": "yolo"}
    r = json.loads(json.dumps(requests.get(url=launchUrl, params=PARAMS).json()))

    # paths
    InstallDir = ModFolderPATH + MOD_ID
    UniversalIsoPath = AppdataPATH + "/OpenGOAL-Mods/_iso_data"
    ensure_jak_folders_exist()

    # store Latest Release and check our local date too.
    if LINK_TYPE == githubUtils.LinkTypes.BRANCH:
      LatestRel = datetime.strptime(
          r.get("commit")
          .get("commit")
          .get("author")
          .get("date")
          .replace("T", " ")
          .replace("Z", ""),
          "%Y-%m-%d %H:%M:%S",
      )
      LatestRelAssetsURL = githubUtils.branchToArchiveURL(URL)
    elif LINK_TYPE == githubUtils.LinkTypes.RELEASE:
      LatestRel = datetime.strptime(
          r[0].get("published_at").replace("T", " ").replace("Z", ""),
          "%Y-%m-%d %H:%M:%S",
      )
      assets = json.loads(json.dumps(requests.get(url=r[0].get("assets_url"), params=PARAMS).json()))
      for asset in assets:
        # TODO: fork here based on sys.platform
        if "linux" in asset.get("name") or "macos" in asset.get("name") or "json" in asset.get("name"):
          print("Release asset " + asset.get("name") + " is not for windows - SKIPPING!")
        else:
          print("USING: Release asset " + asset.get("name") + "! Downloading from " + asset.get("browser_download_url"))
          LatestRelAssetsURL = asset.get("browser_download_url")
          break

      # response = requests.get(url=LatestRelAssetsURL, params=PARAMS)
      # content_type = response.headers["content-type"]

    LastWrite = datetime(2020, 5, 17)
    if exists(InstallDir):
        LastWrite = datetime.utcfromtimestamp(
            pathlib.Path(InstallDir).stat().st_mtime
        )

    # update checks
    Outdated = bool(LastWrite < LatestRel)
    # jak3 jak 3 3 jak
    if GAME == "jak3":
        NotExtracted = (bool(not (exists(UniversalIsoPath + "/" + GAME + "/" + "ZZTAIL.DAT"))))
    else:
        NotExtracted = (bool(not (exists(UniversalIsoPath + "/" + GAME + "/" + "Z6TAIL.DUP"))))

    NotCompiled = bool(not (exists(InstallDir + "/data/out" + "/" + GAME + "/" + "fr3/GAME.fr3")))
    needUpdate = bool(Outdated or NotExtracted or NotCompiled)

    print("Currently installed version created on: " + LastWrite.strftime('%Y-%m-%d %H:%M:%S'))
    print("Newest version created on: " + LatestRel.strftime('%Y-%m-%d %H:%M:%S'))
    if(NotExtracted):
        print("Error! Iso data does not appear to be extracted to " + UniversalIsoPath +"/" + GAME + "/" + "Z6TAIL.DUP")
        print("Will ask user to provide ISO")
    if(NotCompiled):
        print("Error! The game is not compiled")
    if((LastWrite < LatestRel)):
        print("Looks like we need to download a new update!")
        print(LastWrite)
        print(LatestRel)
        print("Is newest posted update older than what we have installed? " + str((LastWrite < LatestRel)))

    # attempt to migrate any old settings files from using MOD_NAME to MOD_ID
    if exists(AppdataPATH + "/OpenGOAL" + "/" + GAME + "/" + "settings/" + MOD_NAME + "-settings.gc"):
        # just to be safe delete the migrated settings file if it already exists (shouldn't happen but prevents rename from failing below)
        if exists(AppdataPATH + "/OpenGOAL" + "/" + GAME + "/" + "settings/" + MOD_ID + "-settings.gc"):
            os.remove(
                AppdataPATH + "/OpenGOAL" + "/" + GAME + "/" + "settings/" + MOD_ID + "-settings.gc"
            )

        # rename settings file
        os.rename(
            AppdataPATH + "/OpenGOAL" + "/" + GAME + "/" + "settings/" + MOD_NAME + "-settings.gc",
            AppdataPATH + "/OpenGOAL" + "/" + GAME + "/" + "settings/" + MOD_ID + "-settings.gc",
        )

        # force update to ensure we recompile with adjusted settings filename in pckernel.gc
        needUpdate = True

    if needUpdate:
        download_and_unpack_mod(URL, MOD_ID, MOD_NAME, LINK_TYPE, InstallDir, LatestRelAssetsURL)
        rebuild(URL, MOD_ID, MOD_NAME, LINK_TYPE, GAME, True)
    else:
      # dont need to update, close any open instances of the game and just launch it
      print("Game is up to date!")
      print("Launching now!")
      launch_local(MOD_ID, GAME)
