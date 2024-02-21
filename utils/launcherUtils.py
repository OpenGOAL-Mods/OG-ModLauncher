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
import stat
from pathlib import Path
import time
import ctypes


# This function expects the name of the executable without .exe at the end
# For windows systems, it appends ".exe" to the executable name and returns this value
# For linux and mac, it returns it as-is
# It is meant to be called at the beginning of a script, where the results are stored
# into a string variable. The string variable can then be used in followup logic
def get_exe(executable):
    return executable + ".exe" if sys.platform == "win32" else executable


gk_exe = get_exe("gk")
decompiler_exe = get_exe("decompiler")
goalc_exe = get_exe("goalc")
extractor_exe = get_exe("extractor")

FILE_DATE_TO_CHECK = gk_exe
UPDATE_FILE_EXTENTION = ".zip"

# Executable we're checking the 'modified' time of
ExecutableName = str(
    FILE_DATE_TO_CHECK
)  # content_type of the .deb release is also "application\zip", so rely on file ext
FileExt = str(
    UPDATE_FILE_EXTENTION
)
FileIdent = ""  # If we ever get to multiple .zip files in a release, include other identifying information from the name
dirs = AppDirs(roaming=True)
ModFolderPATH = Path(dirs.user_data_dir) / "OpenGOAL-Mods"
AppdataPATH = Path(dirs.user_data_dir)

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
    if sys.platform == "win32":
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
    else:
        call = ["pgrep", "--list-name", "^" + process_name + "$"]
        try:
            output = subprocess.check_output(call).decode()
            return len(output) > 1
        except:
            return False


def try_kill_process(process_name):
    if process_exists(process_name):
        if sys.platform == "win32":
            os.system("taskkill /f /im " + process_name)
        else:
            os.system("pkill " + "^" + process_name + "$")


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
    path = ModFolderPATH / MOD_ID / "ModImage.png"
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
    if sys.platform == "win32":
        subprocess.check_call('mklink /J "%s" "%s"' % (link, target), shell=True)
    else:
        subprocess.check_call('ln -s "%s" "%s"' % (link, target), shell=True)


def makeFileSymlink(link, target):
    # if ctypes.windll.shell32.IsUserAnAdmin():
    #     subprocess.check_call('mklink "%s" "%s"' % (link, target), shell=True)
    # else:
    if sys.platform == "win32":
        subprocess.check_call('mklink /H "%s" "%s"' % (link, target), shell=True)
    else:
        subprocess.check_call('ln -s "%s" "%s"' % (link, target), shell=True)


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
            # print("making " + destination_path + "<-des source ->" + file_path)
            makeFileSymlink(destination_path, file_path)


def openFolder(path):
    jak2_path = Path(dirs.user_data_dir) / "OpenGOAL" / "mods" / "data" / "iso_data" / "jak2"
    if not jak2_path.exists():
        jak2_path.mkdir(parents=True)
    print(path)
    if sys.platform == "win32":
        os.startfile(path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, path])


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


def open_browser_link(url):
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
    directory = Path(dirs.user_data_dir) / "OpenGOAL-Mods" / "_iso_data"
    jak1_path = os.path.join(directory, "jak1")
    jak2_path = os.path.join(directory, "jak2")

    if not os.path.exists(jak1_path):
        os.makedirs(jak1_path)
        print(f"Created 'jak1' folder at {jak1_path}")

    if not os.path.exists(jak2_path):
        os.makedirs(jak2_path)
        print(f"Created 'jak2' folder at {jak2_path}")


# check if we have decompiler in the path, if not check if we have a backup, if so use it, if not download a backup then use it
def getDecompiler(path):
    decompiler_url = "https://github.com/OpenGOAL-Mods/OG-Mod-Base/raw/main/out/build/Release/bin/" + decompiler_exe

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


# TODO
def launch_local(MOD_ID, GAME):
    try:
        # Close Gk and goalc if they were open.
        try_kill_process(gk_exe)
        try_kill_process(goalc_exe)

        time.sleep(1)
        InstallDir = ModFolderPATH / MOD_ID

        if GAME == "jak2":
            GKCOMMANDLINElist = [
                InstallDir / gk_exe,
                "--proj-path",
                InstallDir / "data",
                "-v",
                "--game",
                "jak2",
                "--",
                "-boot",
                "-fakeiso"
            ]
        else:  # if GAME == "jak1":
            GKCOMMANDLINElist = [
                os.path.abspath(InstallDir / gk_exe),  # Using os.path.abspath to get the absolute path.
                "--proj-path",
                os.path.abspath(InstallDir / "data"),  # Using absolute path for data folder too.
                "-boot",
                "-fakeiso",
                "-v",
            ]

        print("running: ", GKCOMMANDLINElist)
        subprocess.run(GKCOMMANDLINElist, shell=True, cwd=os.path.abspath(InstallDir))
    except Exception as e:  # Catch all exceptions and print the error message.
        return str(e)


# TODO
def download_and_unpack_mod(URL, MOD_ID, MOD_NAME, LINK_TYPE, InstallDir, LatestRelAssetsURL):
    # start the actual update method if needUpdate is true
    print("\nNeed to update")
    print("Starting Update...")
    # Close Gk and goalc if they were open.
    try_kill_process(gk_exe)
    try_kill_process(goalc_exe)

    # download update from github
    # Create a new directory because it does not exist
    try_remove_dir(InstallDir / "temp")
    if not os.path.exists(InstallDir / "temp"):
        print(f"Creating install dir: {InstallDir}")
        os.makedirs(InstallDir / "temp", exist_ok=True)

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
        LatestRelAssetsURL, InstallDir / "temp" / "updateDATA.zip", show_progress
    )
    print("Done downloading")
    r = requests.head(LatestRelAssetsURL, allow_redirects=True)

    # delete any previous installation
    print(f"Removing previous installation {InstallDir}")
    try_remove_dir(InstallDir / "data")
    try_remove_dir(InstallDir / ".github")
    try_remove_dir(InstallDir / "SND")
    try_remove_file(InstallDir / gk_exe)
    try_remove_file(InstallDir / goalc_exe)
    try_remove_file(InstallDir / extractor_exe)
    # jak2hack
    try_remove_file(InstallDir / decompiler_exe)

    # extract mod zipped update
    print("Extracting update")
    TempDir = InstallDir / "temp"
    try:
        with zipfile.ZipFile(TempDir / "updateDATA.zip", "r") as zip_ref:
            zip_ref.extractall(TempDir)
    except BadZipFile as e:
        print("Error while extracting from zip: ", e)
        return

    # delete the mod zipped update archive
    try_remove_file(TempDir / "updateDATA.zip")

    SubDir = TempDir
    if LINK_TYPE == githubUtils.LinkTypes.BRANCH or len(os.listdir(SubDir)) == 1:
        # for branches, the downloaded zip puts all files one directory down
        SubDir = SubDir / os.listdir(SubDir)[0]

    print(f"Moving files from {SubDir} up to {InstallDir}")
    allfiles = os.listdir(SubDir)
    for f in allfiles:
        shutil.move(SubDir / f, InstallDir / f)
    try_remove_dir(TempDir)

    # replace the settings and discord RPC texts automatically before we build the game.
    replaceText(
        InstallDir / "data" / "goal_src" / "jak1" / "pc" / "pckernel.gc",
        "Playing Jak and Daxter: The Precursor Legacy",
        "Playing " + MOD_NAME,
    )
    replaceText(
        InstallDir / "data" / "goal_src" / "jak1" / "pc" / "pckernel.gc",
        "/pc-settings.gc",
        r"/" + MOD_ID + "-settings.gc",
    )
    replaceText(
        InstallDir / "data" / "goal_src" / "jak1" / "pc" / "pckernel-common.gc",
        "/pc-settings.gc",
        r"/" + MOD_ID + "-settings.gc",
    )
    replaceText(
        InstallDir / "data" / "goal_src" / "jak1" / "pc" / "pckernel-common.gc",
        "/pc-settings.gc",
        r"/" + MOD_ID + "-settings.gc",
    )
    replaceText(
        InstallDir / "data" / "decompiler" / "config" / "jak1_ntsc_black_label.jsonc",
        "\"process_tpages\": true,",
        "\"process_tpages\": false,",
    )
    replaceText(
        InstallDir / "data" / "decompiler" / "config" / "jak1_pal.jsonc",
        "\"process_tpages\": true,",
        "\"process_tpages\": false,",
    )


# TODO
def rebuild(URL, MOD_ID, MOD_NAME, LINK_TYPE, GAME, should_extract):
    InstallDir = ModFolderPATH / MOD_ID
    UniversalIsoPath = AppdataPATH / "OpenGOAL-Mods" / "_iso_data"

    print(f"Looking for some ISO data in {UniversalIsoPath / GAME}")
    found_universal_iso = exists(UniversalIsoPath / GAME / "Z6TAIL.DUP")

    # if ISO_DATA has content, store this path to pass to the extractor
    if found_universal_iso:
        print("We found ISO data from a previous mod installation! Lets use it!")
        print(f"Found in {UniversalIsoPath / GAME / 'Z6TAIL.DUP'}")
        iso_path = UniversalIsoPath / GAME

        if not is_junction(InstallDir / "data" / "iso_data"):
            # we have iso extracted to universal folder already, just symlink it. otherwise we'll copy it there and symlink after extractor closes
            try_remove_dir(InstallDir / "data" / "iso_data")
            makeDirSymlink(InstallDir / "data" / "iso_data", UniversalIsoPath)
    else:
        print("We did not find " + GAME + " ISO data from a previous mod, lets ask for some!")

        # cleanup and remove a corrupted iso
        if os.path.exists(UniversalIsoPath / GAME) and os.path.isdir(UniversalIsoPath) and not (
                exists((UniversalIsoPath / GAME / "Z6TAIL.DUP"))):
            print("Removing corrupted iso destination...")
            shutil.rmtree(UniversalIsoPath / GAME)
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
    try_kill_process(gk_exe)
    try_kill_process(goalc_exe)
    print("Done update starting extractor This one can take a few moments! \n")

    # Extract and compile
    if GAME == "jak1":
        extractor_command_list = [InstallDir / extractor_exe, "-f", iso_path, "-v", "-c"]
        if should_extract:
            extractor_command_list.append("-e")
            extractor_command_list.append("-d")
        print(extractor_command_list)
        extractor_result = subprocess.run(extractor_command_list, shell=True, cwd=os.path.abspath(InstallDir))

        if extractor_result.returncode == 0:
            print("done extracting!")
        else:
            print("Extractor error!")
            return

    elif GAME == "jak2":
        extractor_command_list = [InstallDir / extractor_exe, "-f", iso_path, "-v", "-c", "-g", "jak2"]
        if should_extract:
            extractor_command_list.append("-e")
            extractor_command_list.append("-d")
        print(extractor_command_list)
        extractor_result = subprocess.run(extractor_command_list, shell=True, cwd=os.path.abspath(InstallDir))

        if extractor_result.returncode == 0:
            print("done extracting!")
        else:
            print("Extractor error!")
            return

    # symlink isodata for custom levels art group (goalc doesnt take -f flag)
    # if exists(UniversalIsoPath + r"" + "//" + GAME + "//" + "Z6TAIL.DUP") and GAME == "jak1":
    #     ensure_jak_folders_exist();
    #     makeDirSymlink(InstallDir + "/data/iso_data/" + GAME, UniversalIsoPath + "//" + GAME)

    # move the extrated contents to the universal launchers directory for next time.
    if not found_universal_iso:
        ensure_jak_folders_exist()
        moveDirContents(InstallDir / "data" / "iso_data" / GAME, UniversalIsoPath / GAME)
        # replace iso_data with symlink
        try_remove_dir(InstallDir / "data" / "iso_data")
        makeDirSymlink(InstallDir / "data" / "iso_data", UniversalIsoPath)

    launch_local(MOD_ID, GAME)
    return


# TODO
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
    InstallDir = ModFolderPATH / MOD_ID
    UniversalIsoPath = AppdataPATH / "OpenGOAL-Mods" / "_iso_data"
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
                print("USING: Release asset " + asset.get("name") + "! Downloading from " + asset.get(
                    "browser_download_url"))
                LatestRelAssetsURL = asset.get("browser_download_url")
                break

        # response = requests.get(url=LatestRelAssetsURL, params=PARAMS)
        # content_type = response.headers["content-type"]

    LastWrite = datetime(2020, 5, 17)
    exe_path = InstallDir / ExecutableName
    if exe_path.exists():
        LastWrite = datetime.utcfromtimestamp(exe_path.stat().st_mtime)

    # update checks
    Outdated = bool(LastWrite < LatestRel)
    NotExtracted = bool(not (exists(UniversalIsoPath / GAME / "Z6TAIL.DUP")))
    NotCompiled = bool(not (exists(InstallDir / "data" / "out" / GAME / "fr3" / "GAME.fr3")))
    needUpdate = bool(Outdated or NotExtracted or NotCompiled)

    print("Currently installed version created on: " + LastWrite.strftime('%Y-%m-%d %H:%M:%S'))
    print("Newest version created on: " + LatestRel.strftime('%Y-%m-%d %H:%M:%S'))
    if (NotExtracted):
        print(f"Error! Iso data does not appear to be extracted to {UniversalIsoPath / GAME / 'Z6TAIL.DUP'}")
        print("Will ask user to provide ISO")
    if (NotCompiled):
        print("Error! The game is not compiled")
    if ((LastWrite < LatestRel)):
        print("Looks like we need to download a new update!")
        print(LastWrite)
        print(LatestRel)
        print("Is newest posted update older than what we have installed? " + str((LastWrite < LatestRel)))

    # attempt to migrate any old settings files from using MOD_NAME to MOD_ID
    mod_name_settings_path = AppdataPATH / "OpenGOAL" / GAME / "settings" / (MOD_NAME + "-settings.gc")
    if mod_name_settings_path.exists():
        # just to be safe delete the migrated settings file if it already exists (shouldn't happen but prevents rename from failing below)
        mod_id_settings_path = AppdataPATH / "OpenGOAL" / GAME / "settings" / (MOD_ID + "-settings.gc")
        if mod_id_settings_path.exists():
            mod_id_settings_path.unlink()

        # rename settings file
        mod_name_settings_path.rename(mod_id_settings_path)

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
