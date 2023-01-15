# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 18:33:45 2022

@author: Zed
"""

# we will clean these up later but for now leave even unused imports

from PIL import Image
from utils import launcherUtils, githubUtils
import PySimpleGUI as sg
import cloudscraper
import io
import json
import os.path
import requests
import time
import datetime
import sys
import webbrowser
import os
from os.path import exists
import urllib.request
import shutil
import tkinter
from appdirs import AppDirs

sg.theme("DarkBlue3")

def openLauncherWebsite():
  webbrowser.open("https://opengoal-unofficial-mods.github.io/")

def exitWithError():
  sys.exit(1)

# Folder where script is placed, It looks in this for the Exectuable
if getattr(sys, "frozen", False):
    # If we are a pyinstaller exe get the path of this file, not python
    LauncherDir = os.path.dirname(os.path.realpath(sys.executable))

    # Detect if a user has downloaded a release directly, if so point them to the autoupdater
    if LauncherDir != os.getenv("APPDATA") + "\\OpenGOAL-UnofficalModLauncher" and os.getlogin() != "NinjaPC":
        # Creating the tkinter window
        root = tkinter.Tk()
        root.winfo_toplevel().title("Error")
        root.title = "test"
        root.geometry("700x150")
        message = tkinter.Label(
            root,
            text="Launcher not installed properly! \n Please download from: \n https://opengoal-unofficial-mods.github.io/",
        )
        message.config(font=("Courier", 14))
        message.pack()

        website_button = tkinter.Button(root, text="Visit Website", command=openLauncherWebsite)
        website_button.pack()

        # Button for closing

        exit_button = tkinter.Button(root, text="Exit", command=exitWithError)
        exit_button.pack()

        root.mainloop()
elif __file__:
    # if we are running the .py directly use this path
    LauncherDir = os.path.dirname(__file__)

installpath = str(LauncherDir + "\\resources\\")

# intialize default variables so they are never null
currentModderSelected = None
currentModSelected = None
currentModURL = None
currentModImage = None
steamDIR = None
dirs = AppDirs(roaming=True)
# C:\Users\USERNAME\AppData\Roaming\OPENGOAL-UnofficalModLauncher\
AppdataPATH = os.path.join(dirs.user_data_dir, "OPENGOAL-UnofficalModLauncher", "")

# C:\Users\USERNAME\AppData\Roaming\OpenGOAL-Mods\
ModFolderPATH = os.path.join(dirs.user_data_dir, "OpenGOAL-Mods", "")

# grab images from web

# url to splash screen image
url = "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/overhaul/resources/modlaunchersplash.png"
jpg_data = (
    cloudscraper.create_scraper(
        browser={"browser": "firefox", "platform": "windows", "mobile": False}
    )
    .get(url)
    .content
)

pil_image = Image.open(io.BytesIO(jpg_data))
png_bio = io.BytesIO()
pil_image.save(png_bio, format="PNG")
splashfile = png_bio.getvalue()

# url to icon for the window
url = "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/appicon.ico"
jpg_data = (
    cloudscraper.create_scraper(
        browser={"browser": "firefox", "platform": "windows", "mobile": False}
    )
    .get(url)
    .content
)

pil_image = Image.open(io.BytesIO(jpg_data))
png_bio = io.BytesIO()
pil_image.save(png_bio, format="PNG")
iconfile = png_bio.getvalue()

# url to use if we have no image
url = "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/noRepoImageERROR.png"
jpg_data = (
    cloudscraper.create_scraper(
        browser={"browser": "firefox", "platform": "windows", "mobile": False}
    )
    .get(url)
    .content
)

pil_image = Image.open(io.BytesIO(jpg_data))
png_bio = io.BytesIO()
pil_image.save(png_bio, format="PNG")
noimagefile = png_bio.getvalue()

table_headings = [
    "id",
    "Name",
    "Description",
    "Tags",
    "Contributors",
    "Install Date",
    # "Latest Update Date",
    "URL",
    "website_url",
    "videos_url",
    "photos_url",
]

col_vis = [
    False,
    True,
    False,
    True,
    True,
    True,
    # True,
    False,
    False,
    False,
    False,
]

vis_col_map = [
    1,  # name
    3,  # tags
    4,  # contributors
    5,  # install date
]

col_width = [
    0,  # id
    40,  # name
    0,  # desc
    25,  # tags
    25,  # contributors
    15,  # install date
    0,  # url
    0,  # website
    0,  # videos
    0,  # photos
]

FILTER_STR = ""
INCLUDE_INSTALLED = True
INCLUDE_UNINSTALLED = True
LATEST_TABLE_SORT = [0, True]


def getRefreshedTableData(sort_col_idx):
    # uncomment/comment the next two lines if you want to test with a local file
    mod_dict = requests.get(
        "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/overhaul/resources/mods.json"
    ).json()
    # mod_dict = json.loads(open("resources/mods.json", "r").read())
    mod_table_data = []
    installed_mod_subfolders = {
        f.name: f.stat().st_mtime for f in os.scandir(ModFolderPATH) if f.is_dir()
    }

    for mod_id in mod_dict:
        mod = mod_dict[mod_id]
        mod_name = mod["name"]

        # determine local install datetime
        mod["install_date"] = "Not Installed"
        if mod_id in installed_mod_subfolders:
            mod[
                "install_date"
            ] = f"{datetime.datetime.fromtimestamp(installed_mod_subfolders[mod_id]):%Y-%m-%d %H:%M}"
        elif mod_name in installed_mod_subfolders:
            # previous installation using mod_name (will migrate after this step)
            mod[
                "install_date"
            ] = f"{datetime.datetime.fromtimestamp(installed_mod_subfolders[mod_name]):%Y-%m-%d %H:%M}"
            # migrate folder to use mod_id instead of mod_name
            shutil.move(ModFolderPATH + "/" + mod_name, ModFolderPATH + "/" + mod_id)

        mod["contributors"] = ", ".join(mod["contributors"])
        mod["tags"] = ", ".join(mod["tags"])

        # determine latest available update datetime - disabled as too easy to get rate-limited by github (can we do in bulk maybe?)
        # mod["latest_available_update_date"] = "1900-01-01 00:00"
        # update_date = githubUtils.getLatestAvailableUpdateDatetime(mod["URL"])
        # if update_date:
        #   mod["latest_available_update_date"] = f"{update_date:%Y-%m-%d %H:%M}"

        # only add to data if passes filter (if any)
        if (
            FILTER_STR is None
            or FILTER_STR == ""
            or FILTER_STR in mod_name.lower()
            or FILTER_STR in mod["contributors"].lower()
            or FILTER_STR in mod["tags"].lower()
        ):
            if (INCLUDE_INSTALLED and mod["install_date"] != "Not Installed") or (
                INCLUDE_UNINSTALLED and mod["install_date"] == "Not Installed"
            ):
                mod_table_data.append(
                    [
                        mod_id,
                        mod_name,
                        mod["desc"],
                        mod["tags"],
                        mod["contributors"],
                        mod["install_date"],
                        # mod["latest_available_update_date"],
                        mod["URL"],
                        (mod["website_url"] if "website_url" in mod else ""),
                        (mod["videos_url"] if "videos_url" in mod else ""),
                        (mod["photos_url"] if "photos_url" in mod else ""),
                    ]
                )

    if sort_col_idx is None:
        # not from a heading click, retain sorting
        remapped_col_idx = LATEST_TABLE_SORT[0]
    else:
        # heading click, adjust sorting
        remapped_col_idx = vis_col_map[sort_col_idx]

        if remapped_col_idx == LATEST_TABLE_SORT[0]:
            LATEST_TABLE_SORT[1] = not LATEST_TABLE_SORT[
                1
            ]  # same column, flip asc/desc
        else:
            LATEST_TABLE_SORT[0] = remapped_col_idx
            LATEST_TABLE_SORT[1] = True

    mod_table_data.sort(key=lambda x: x[remapped_col_idx].lower())

    if not LATEST_TABLE_SORT[1]:
        mod_table_data.reverse()

    # print(mod_table_data)
    return mod_table_data


LATEST_TABLE_DATA = getRefreshedTableData(0)

# ----- Full layout -----
layout = [
    [sg.Frame(title="", key='-SPLASHFRAME-', border_width=0, size=(972, 609), visible=True, element_justification="center", vertical_alignment="center", 
      layout=
      [
        [sg.Image(key='-SPLASHIMAGE-', source=githubUtils.resize_image(splashfile, 970, 607), expand_y=True)]
      ])
    ],
    [sg.Frame(title="", key='-MAINFRAME-', border_width=0, visible=False, layout=
      [
        [
          sg.Column(
              [
                  [
                      sg.Text(
                          "",
                          key="-SELECTEDMODNAME-",
                          font=("Helvetica", 13),
                          metadata={"id": "", "url": ""},
                      )
                  ],
                  [sg.Text("", key="-SELECTEDMODDESC-", size=(55, 7))],
                  [sg.Text("Tags:", key="-SELECTEDMODTAGS-")],
                  [sg.Text("Contributors:", key="-SELECTEDMODCONTRIBUTORS-")],
                  [sg.Text("")],
                  [
                      sg.Btn(button_text="Launch", key="-LAUNCH-", expand_x=True),
                      sg.Btn(
                          button_text="View Folder", key="-VIEWFOLDER-", expand_x=True
                      ),
                      sg.Btn(button_text="Reinstall", key="-REINSTALL-", expand_x=True),
                      sg.Btn(button_text="Uninstall", key="-UNINSTALL-", expand_x=True),
                  ],
                  [
                      sg.Btn(
                          button_text="Website",
                          key="-WEBSITE-",
                          expand_x=True,
                          metadata={"url": ""},
                      ),
                      sg.Btn(
                          button_text="Video(s)",
                          key="-VIDEOS-",
                          expand_x=True,
                          metadata={"url": ""},
                      ),
                      sg.Btn(
                          button_text="Photo(s)",
                          key="-PHOTOS-",
                          expand_x=True,
                          metadata={"url": ""},
                      ),
                  ],
              ],
              size=(400, 300),
              expand_x=True,
              expand_y=True,
          ),
          sg.Frame(
              title="",
              element_justification="center",
              vertical_alignment="center",
              border_width=0,
              layout=[[sg.Image(key="-SELECTEDMODIMAGE-", expand_y=True)]],
              size=(500, 300),
          ),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Text("Search"),
            sg.Input(expand_x=True, enable_events=True, key="-FILTER-"),
            sg.Checkbox(
                text="Show Installed",
                default=True,
                enable_events=True,
                key="-SHOWINSTALLED-",
            ),
            sg.Checkbox(
                text="Show Uninstalled",
                default=True,
                enable_events=True,
                key="-SHOWUNINSTALLED-",
            ),
        ],
        [
            sg.Table(
                values=LATEST_TABLE_DATA,
                headings=table_headings,
                visible_column_map=col_vis,
                col_widths=col_width,
                auto_size_columns=False,
                num_rows=15,
                text_color="black",
                background_color="lightblue",
                alternating_row_color="white",
                justification="left",
                selected_row_colors="black on yellow",
                key="-MODTABLE-",
                expand_x=True,
                expand_y=True,
                enable_click_events=True,
            )
        ],
      ])
    ]
]

window = sg.Window("OpenGOAL Mod Launcher", layout, icon=iconfile, finalize=True)


def handleModTableSelection(row):
    global LATEST_TABLE_DATA
    mod = LATEST_TABLE_DATA[row]
    # print(mod)

    mod_id = mod[0]
    mod_name = mod[1]
    mod_desc = mod[2]
    mod_tags = mod[3]
    mod_contributors = mod[4]
    mod_install_date = mod[5]
    mod_url = mod[6]
    mod_website_url = mod[7]
    mod_videos_url = mod[8]
    mod_photos_url = mod[9]

    # update text and metadata
    window["-LAUNCH-"].update(
        "Install" if mod_install_date == "Not Installed" else "Launch"
    )
    window["-SELECTEDMODNAME-"].update(mod_name)
    window["-SELECTEDMODNAME-"].metadata["id"] = mod_id
    window["-SELECTEDMODNAME-"].metadata["url"] = mod_url
    window["-SELECTEDMODDESC-"].update(mod_desc)
    window["-SELECTEDMODTAGS-"].update(f"Tags: {mod_tags}")
    window["-SELECTEDMODCONTRIBUTORS-"].update(f"Contributors: {mod_contributors}")
    window["-VIEWFOLDER-"].update(disabled=(mod_install_date == "Not Installed"))
    window["-REINSTALL-"].update(disabled=(mod_install_date == "Not Installed"))
    window["-UNINSTALL-"].update(disabled=(mod_install_date == "Not Installed"))
    window["-WEBSITE-"].update(disabled=(mod_website_url == ""))
    window["-WEBSITE-"].metadata["url"] = mod_website_url
    window["-VIDEOS-"].update(disabled=(mod_videos_url == ""))
    window["-VIDEOS-"].metadata["url"] = mod_videos_url
    window["-PHOTOS-"].update(disabled=(mod_photos_url == ""))
    window["-PHOTOS-"].metadata["url"] = mod_photos_url

    # load mod image
    mod_image_url = githubUtils.returnModImageURL(mod_url)
    try:
        r = requests.head(mod_image_url).status_code
        if r == 200:
            jpg_data = (
                cloudscraper.create_scraper(
                    browser={
                        "browser": "firefox",
                        "platform": "windows",
                        "mobile": False,
                    }
                )
                .get(mod_image_url)
                .content
            )

            pil_image = Image.open(io.BytesIO(jpg_data))
            png_bio = io.BytesIO()
            pil_image.save(png_bio, format="PNG")
            png_data = png_bio.getvalue()
            window["-SELECTEDMODIMAGE-"].update(githubUtils.resize_image(png_data, 500.0, 300.0))
            # prints the int of the status code. Find more at httpstatusrappers.com :)
        else:
            window["-SELECTEDMODIMAGE-"].update(githubUtils.resize_image(noimagefile, 500.0, 300.0))

    except requests.exceptions.MissingSchema:
        window["-SELECTEDMODIMAGE-"].update(githubUtils.resize_image(noimagefile, 500.0, 300.0))


def reset():
    global LATEST_TABLE_DATA
    LATEST_TABLE_DATA = getRefreshedTableData(None)
    window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
    window["-MODTABLE-"].update(select_rows=[0])
    handleModTableSelection(0)


# this is the main event loop where we handle user input
reset()
bootstart = time.time()
while True:
    event, values = window.read(timeout=100)

    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "__TIMEOUT__":
      if bootstart is not None:
        curtime = time.time()
        if curtime - bootstart > 3:
          # switch from splash screen to main screen after 3s
          bootstart = None
          window["-MAINFRAME-"].update(visible=True)
          window["-MAINFRAME-"].unhide_row()
          window["-SPLASHFRAME-"].update(visible=False)
          window["-SPLASHFRAME-"].hide_row()
          window.refresh()
          # print("SIZE:", window.size)
    elif isinstance(event, tuple):
        if event[0] == "-MODTABLE-":
            row = event[2][0]
            col = event[2][1]
            if row == -1:
                # heading row, sort by col
                LATEST_TABLE_DATA = getRefreshedTableData(col)
                window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
            else:
                # data row, mod selected
                handleModTableSelection(row)
    elif event == "-FILTER-":
        FILTER_STR = values["-FILTER-"].lower()
        LATEST_TABLE_DATA = getRefreshedTableData(None)
        window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
    elif event == "-SHOWINSTALLED-":
        INCLUDE_INSTALLED = window["-SHOWINSTALLED-"].get()
        LATEST_TABLE_DATA = getRefreshedTableData(None)
        window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
    elif event == "-SHOWUNINSTALLED-":
        INCLUDE_UNINSTALLED = window["-SHOWUNINSTALLED-"].get()
        LATEST_TABLE_DATA = getRefreshedTableData(None)
        window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
    elif event == "-REFRESH-":
        reset()
    elif event == "-LAUNCH-":
        tmpModName = window["-SELECTEDMODNAME-"].get()
        tmpModSelected = window["-SELECTEDMODNAME-"].metadata["id"]
        tmpModURL = window["-SELECTEDMODNAME-"].metadata["url"]

        # online launch
        window["-LAUNCH-"].update(disabled=True)
        window["-LAUNCH-"].update("Updating...")
        [linkType, tmpModURL] = githubUtils.identifyLinkType(tmpModURL)
        launcherUtils.launch(tmpModURL, tmpModSelected, tmpModName, linkType)

        # turn the button back on
        window["-LAUNCH-"].update("Launch")
        window["-LAUNCH-"].update(disabled=False)
    elif event == "-VIEWFOLDER-":
        tmpModSelected = window["-SELECTEDMODNAME-"].metadata["id"]
        subfolders = [f.name for f in os.scandir(ModFolderPATH) if f.is_dir()]

        if tmpModSelected in subfolders:
            dir = dirs.user_data_dir + "\\OpenGOAL-Mods\\" + tmpModSelected
            launcherUtils.openFolder(dir)
        else:
            sg.Popup("Selected mod is not installed", keep_on_top=True, icon=iconfile)
    elif event == "-REINSTALL-":
        tmpModSelected = window["-SELECTEDMODNAME-"].metadata["id"]
        subfolders = [f.name for f in os.scandir(ModFolderPATH) if f.is_dir()]

        if tmpModSelected in subfolders:
            dir = dirs.user_data_dir + "\\OpenGOAL-Mods\\" + tmpModSelected
            ans = sg.popup_ok_cancel(
                "Confirm: reinstalling "
                + dir
                + " \n\nNote: this will re-extract texture_replacements too",
                icon=iconfile,
            )
            if ans == "OK":
                launcherUtils.reinstall(tmpModSelected)
                reset()
        else:
            sg.Popup("Selected mod is not installed", keep_on_top=True, icon=iconfile)
    elif event == "-UNINSTALL-":
        tmpModSelected = window["-SELECTEDMODNAME-"].metadata["id"]
        subfolders = [f.name for f in os.scandir(ModFolderPATH) if f.is_dir()]

        if tmpModSelected in subfolders:
            dir = dirs.user_data_dir + "\\OpenGOAL-Mods\\" + tmpModSelected
            ans = sg.popup_ok_cancel("Confirm: uninstalling " + dir, icon=iconfile)
            if ans == "OK":
                launcherUtils.try_remove_dir(dir)
                reset()
                sg.popup("Uninstalled " + tmpModSelected, icon=iconfile)
        else:
            sg.Popup("Selected mod is not installed", keep_on_top=True, icon=iconfile)
    elif event == "-WEBSITE-":
        window = window.refresh()
        url = window["-WEBSITE-"].metadata["url"]
        if url:
            webbrowser.open(url)
    elif event == "-VIDEOS-":
        window = window.refresh()
        url = window["-VIDEOS-"].metadata["url"]
        if url:
            webbrowser.open(url)
    elif event == "-PHOTOS-":
        window = window.refresh()
        url = window["-PHOTOS-"].metadata["url"]
        if url:
            webbrowser.open(url)
    else:
        print("unhandled event:", event, values)

window.close()
