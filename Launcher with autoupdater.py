import PySimpleGUI as sg
import os
import requests
import json
import urllib
import shutil
import traceback
from datetime import datetime
from os.path import exists
from pathlib import Path
import subprocess
AppdataPATH = os.getenv('APPDATA') + "\\OpenGOAL-UnofficialModLauncher\\"

def show_progress(block_num, block_size, total_size):
    if total_size > 0:
        try:
            window['progress_bar'].UpdateBar(block_num * block_size, total_size)
        except Exception as e:
            pass  # Handle the exception if the window or element does not exist

def try_remove_file(file):
    if exists(file):
        os.remove(file)

def try_remove_dir(dir):
    if exists(dir):
        shutil.rmtree(dir)

def check_for_updates():
    

    launch_url = "https://api.github.com/repos/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/releases"
    response = requests.get(url=launch_url, params={'address': "yolo"})

    if response is not None and response.status_code == 200:
        r = json.loads(json.dumps(response.json()))
        latest_release = datetime.strptime(r[0].get("published_at").replace("T", " ").replace("Z", ""),
                                           '%Y-%m-%d %H:%M:%S')
        latest_release_assets_url = (json.loads(
            json.dumps(requests.get(url=r[0].get("assets_url"), params={'address': "yolo"}).json())))[0].get(
            "browser_download_url")
    else:
        print("WARNING: Failed to query GitHub API, you might be rate-limited. Using default fallback release instead.")
        latest_release = datetime(2023, 7, 23)
        latest_release_assets_url = "https://github.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/releases/download/v1.10fixoldpckernel/openGOALModLauncher.exe"

    last_write = datetime(2020, 5, 17)
    if os.path.exists(AppdataPATH + "\\OpengoalModLauncher.exe"):
        last_write = datetime.utcfromtimestamp(Path(AppdataPATH + "\\OpengoalModLauncher.exe").stat().st_mtime)

    need_update = bool((last_write < latest_release))

    window['installed_version'].update(f"Currently installed version created on: {last_write.strftime('%Y-%m-%d %H:%M:%S')}")
    window['newest_version'].update(f"Newest version created on: {latest_release.strftime('%Y-%m-%d %H:%M:%S')}")

    if need_update:
        window['update_status'].update("An update is available. Click 'Update' to install.")
        window['update_button'].update(visible=True)
        window['launch_button'].update(visible=False)
    else:
        window['update_status'].update("You are up to date.")
        window['update_button'].update(visible=False)
        window['launch_button'].update(visible=True)

def download_newest_mod():
    AppdataPATH = os.getenv('APPDATA') + "\\OpenGOAL-UnofficialModLauncher\\"

    launch_url = "https://api.github.com/repos/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/releases"
    response = requests.get(url=launch_url, params={'address': "yolo"})

    if response is not None and response.status_code == 200:
        r = json.loads(json.dumps(response.json()))
        latest_release = datetime.strptime(r[0].get("published_at").replace("T", " ").replace("Z", ""),
                                           '%Y-%m-%d %H:%M:%S')
        latest_release_assets_url = (json.loads(
            json.dumps(requests.get(url=r[0].get("assets_url"), params={'address': "yolo"}).json())))[0].get(
            "browser_download_url")
    else:
        print("WARNING: Failed to query GitHub API, you might be rate-limited. Using default fallback release instead.")
        latest_release = datetime(2023, 7, 23)
        latest_release_assets_url = "https://github.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/releases/download/v1.10fixoldpckernel/openGOALModLauncher.exe"

    last_write = datetime(2020, 5, 17)
    if os.path.exists(AppdataPATH + "\\OpengoalModLauncher.exe"):
        last_write = datetime.utcfromtimestamp(Path(AppdataPATH + "\\OpengoalModLauncher.exe").stat().st_mtime)

    need_update = bool((last_write < latest_release))

    if need_update:
        window['update_status'].update("Starting Update...")
        try_remove_dir(AppdataPATH + "/temp")
        if not os.path.exists(AppdataPATH + "/temp"):
            os.makedirs(AppdataPATH + "/temp")

        window['update_status'].update("Downloading update from " + latest_release_assets_url)
        file = urllib.request.urlopen(latest_release_assets_url)
        urllib.request.urlretrieve(latest_release_assets_url, AppdataPATH + "/temp/OpengoalModLauncher.exe", show_progress)
        window['update_status'].update("Done downloading")

        window['update_status'].update("Removing previous installation " + AppdataPATH)
        try_remove_dir(AppdataPATH + "/data")
        try_remove_file(AppdataPATH + "/gk.exe")
        try_remove_file(AppdataPATH + "/goalc.exe")
        try_remove_file(AppdataPATH + "/extractor.exe")

        window['update_status'].update("Extracting update")
        temp_dir = AppdataPATH + "/temp"
        try_remove_file(temp_dir + "/updateDATA.zip")
        sub_dir = temp_dir
        all_files = os.listdir(sub_dir)
        for f in all_files:
            shutil.move(sub_dir + "/" + f, AppdataPATH + "/" + f)
        try_remove_dir(temp_dir)
        window['update_status'].update("Update complete")
        window['update_button'].update(visible=False)
        window['launch_button'].update(visible=True)

layout = [
    [sg.Text("OpenGOAL Mod Updater", font=("Helvetica", 16))],
    [sg.Text("Installed Version:", size=(20, 1)), sg.Text("", size=(20, 1), key='installed_version')],
    [sg.Text("Newest Version:", size=(20, 1)), sg.Text("", size=(20, 1), key='newest_version')],
    [sg.ProgressBar(100, orientation='h', size=(20, 20), key='progress_bar')],
    [sg.Text("", size=(40, 1), key='update_status')],
    [sg.Button("Check for Updates"), sg.Button("Update", visible=False, key='update_button'), sg.Button("Launch", visible=False, key='launch_button'), sg.Button("Exit")]
]

window = sg.Window("OpenGOAL Mod Updater", layout, finalize=True)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    elif event == "Check for Updates":
        check_for_updates()
    elif event == "update_button":
        download_newest_mod()
    elif event == "launch_button":
        window.close()
        subprocess.call([ AppdataPATH + "openGOALModLauncher.exe"])

window.close()
