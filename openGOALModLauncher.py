# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 18:33:45 2022

@author: Zed
"""
# we will clean these up later but for now leave even unused imports
from enum import IntEnum
import threading
from PIL import Image
from utils import launcherUtils, githubUtils
import PySimpleGUI as sg
import cloudscraper
import io
import json
import os.path
import requests
import time
from datetime import datetime, timedelta
import urllib.request
import sys
import webbrowser
import os
from os.path import exists
import shutil
import tkinter
from appdirs import AppDirs
import random

sg.theme("DarkBlue3")


def openLauncherWebsite():
    webbrowser.open("https://jakmods.dev")


def exitWithError():
    sys.exit(1)


# Folder where script is placed, It looks in this for the Exectuable
if getattr(sys, "frozen", False):
    # If we are a pyinstaller exe get the path of this file, not python
    LauncherDir = os.path.dirname(os.path.realpath(sys.executable))

    # Detect if a user has downloaded a release directly, if so point them to the autoupdater
    if (
        LauncherDir != os.getenv("APPDATA") + "\\OpenGOAL-UnofficalModLauncher"
        and os.getlogin() != "NinjaPC"
        and os.environ["COMPUTERNAME"] != "DESKTOP-BBN1CMN"
    ):
        # Creating the tkinter window
        root = tkinter.Tk()
        root.winfo_toplevel().title("Error")
        root.title = "test"
        root.geometry("700x150")
        message = tkinter.Label(
            root,
            text="Launcher not installed properly! \n Please download from: \n https://jakmods.dev/",
        )
        message.config(font=("Courier", 14))
        message.pack()

        website_button = tkinter.Button(
            root, text="Visit Website", command=openLauncherWebsite
        )
        website_button.pack()

        # Button for closing

        exit_button = tkinter.Button(root, text="Exit", command=exitWithError)
        exit_button.pack()

        root.mainloop()
elif __file__:
    # if we are running the .py directly use this path
    LauncherDir = os.path.dirname(__file__)

# intialize default variables so they are never null

dirs = AppDirs(roaming=True)

# C:\Users\USERNAME\AppData\Roaming\OpenGOAL-Mods\
ModFolderPATH = os.path.join(dirs.user_data_dir, "OpenGOAL-Mods", "")

# grab images from web

# url to splash screen image

def getPNGFromURL(URL):
    result = None  # Initialize the result variable

    def fetch_image(url):  # Accept the URL parameter
        nonlocal result  # Access the result variable in the outer scope
        jpg_data = (
            cloudscraper.create_scraper(
                browser={"browser": "firefox", "platform": "windows", "mobile": False}
            )
            .get(url)  # Use the provided URL parameter
            .content
        )

        pil_image = Image.open(io.BytesIO(jpg_data))
        png_bio = io.BytesIO()
        pil_image.save(png_bio, format="PNG")
        result = png_bio.getvalue()  # Store the fetched image in the result variable

    # Pass the URL as an argument
    try:
      thread = threading.Thread(target=fetch_image, args=(URL,))
      thread.start()
      thread.join()  # Wait for the thread to finish
    except:
      print("failed to get image " + URL)

    return result  # Return the fetched image data


# url to icon for the window

splashfile = getPNGFromURL("https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlaunchersplash.png")

noimagefile = getPNGFromURL("https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/noRepoImageERROR.png")

iconfile = getPNGFromURL("https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/appicon.ico")

loadingimage = getPNGFromURL("https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-0.png")

# make the modfolderpath if first install
if not os.path.exists(ModFolderPATH):
    os.makedirs(ModFolderPATH)

class ColumnEnum(IntEnum):
    SPECIAL = -1
    ID = 0
    NAME = 1
    DESC = 2
    TAGS = 3
    CONTRIBUTORS = 4
    RELEASE_DATE = 5
    INSTALL_DATE = 6
    LAUNCH_DATE = 7
    INSTALL_URL = 8
    WEBSITE_URL = 9
    VIDEOS_URL = 10
    PHOTOS_URL = 11
    THUMBNAIL_URL = 12
    GAME = 13

table_headings = [
    "id",
    "Name",
    "Description",
    "Tags",
    "Contributors",
    "Release Date",
    "Install Date",
    "Last Launch",
    # "Latest Update Date",
    "URL",
    "website_url",
    "videos_url",
    "photos_url",
]

sorted_table_headings = [
    "id",
    "Name",
    "Description",
    "Tags",
    "Contributors",
    "Release Date"
    "Install Date",
    "Last Launch",
    # "Latest Update Date",
    "URL",
    "website_url",
    "videos_url",
    "photos_url",
]

col_vis = [
    False,  # id
    True,   # name
    False,  # desc
    True,   # tags
    True,   # contributors
    True,   # release date
    False,  # install date
    True,   # last launched
    # True, # last updated
    False,  # install url
    False,  # website
    False,  # videos
    False,  # photos
]

vis_col_map = [
    ColumnEnum.NAME,  # name
    ColumnEnum.TAGS,  # tags
    ColumnEnum.CONTRIBUTORS,  # contributors
    ColumnEnum.RELEASE_DATE,  # release date
    ColumnEnum.LAUNCH_DATE,  # last launched
]

col_width = [
    0,  # id
    25,  # name
    0,  # desc
    20,  # tags
    20,  # contributors
    16,   # release date
    0,  # install date
    13,  # launch date
    0,  # url
    0,  # website
    0,  # videos
    0,  # photos
]

FILTER_STR = ""
FILTER_GAME = "jak1"
FILTER_CAT = "mods"
INCLUDE_INSTALLED = True
INCLUDE_UNINSTALLED = True
LATEST_TABLE_SORT = [ColumnEnum.SPECIAL, False]  # wakeup special case -1 that does coalsece(last launch, release date)


def getRefreshedTableData(sort_col_idx):
    main_file_path = f"{LauncherDir}/resources/jak1_mods.json"

    # try to re-download json file from the remote URL
    try:
      remote_url = "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/jak1_mods.json"
      urllib.request.urlretrieve(
          remote_url, main_file_path, False
      )
      print("downloaded mod list successfully")
    except:
      print("failed to download mod list, will try to continue with local list")

    remote_mods = json.loads(open(main_file_path, "r").read())

    # Load data from the extra local file if it exists
    local_mods = None
    local_file_path_1 = "resources/jak1_mods2.json"
    local_file_path_2 = "jak1_mods2.json"
    if os.path.exists(f"{LauncherDir}/{local_file_path_1}"):
        local_mods = json.loads(open(f"{LauncherDir}/{local_file_path_1}", "r").read())
    elif os.path.exists(f"{LauncherDir}/{local_file_path_2}"):
        local_mods = json.loads(open(f"{LauncherDir}/{local_file_path_2}", "r").read())

    # Initialize an empty dictionary to store the combined data
    mod_dict = {}

    if local_mods is not None:
        # Merge the remote and local data while removing duplicates
        mod_dict = {**remote_mods, **local_mods}
    else:
        mod_dict = {**remote_mods}

    mod_dict = dict(
        sorted(mod_dict.items(), key=lambda x: x[1]["release_date"], reverse=False)
    )

    mod_table_data = []
    installed_mod_subfolders = {
        f.name: f.stat().st_mtime for f in os.scandir(ModFolderPATH) if f.is_dir()
    }

    seenJak3 = False
    for mod_id in mod_dict:
        mod = mod_dict[mod_id]
        mod_name = mod["name"]

        if mod["game"] == "jak3":
            seenJak3 = True

        mod["install_date"] = "Not Installed"
        mod["access_date"] = "Not Installed"

        # determine local install/access datetime
        if mod_id in installed_mod_subfolders:
            mod[
                "install_date"
            ] = f"{datetime.fromtimestamp(installed_mod_subfolders[mod_id]):%Y-%m-%d %H:%M}"

            if exists(f"{ModFolderPATH}/{mod_id}/gk.exe"):
                gk_stat = os.stat(f"{ModFolderPATH}/{mod_id}/gk.exe")
                mod[
                    "access_date"
                ] = f"{datetime.fromtimestamp(gk_stat.st_atime):%Y-%m-%d %H:%M}"
        elif mod_name in installed_mod_subfolders:
            # previous installation using mod_name (will migrate after this step)
            mod[
                "install_date"
            ] = f"{datetime.fromtimestamp(installed_mod_subfolders[mod_name]):%Y-%m-%d %H:%M}"
            # migrate folder to use mod_id instead of mod_name
            shutil.move(ModFolderPATH + "/" + mod_name, ModFolderPATH + "/" + mod_id)

            if exists(f"{ModFolderPATH}/{mod_id}/gk.exe"):
                gk_stat = os.stat(f"{ModFolderPATH}/{mod_id}/gk.exe")
                mod[
                    "access_date"
                ] = f"{datetime.fromtimestamp(gk_stat.st_atime):%Y-%m-%d %H:%M}"

        mod["contributors"] = ", ".join(mod["contributors"])
        mod["tags"].sort()
        mod["tags"] = ", ".join(mod["tags"])

        # determine latest available update datetime - disabled as too easy to get rate-limited by github (can we do in bulk maybe?)
        # mod["latest_available_update_date"] = "1900-01-01 00:00"
        # update_date = githubUtils.getLatestAvailableUpdateDatetime(mod["URL"])
        # if update_date:
        #   mod["latest_available_update_date"] = f"{update_date:%Y-%m-%d %H:%M}"

        # only add to data if passes string filter (if any)
        matches_filter = (
            FILTER_STR is None
            or FILTER_STR == ""
            or FILTER_STR in mod_name.lower()
            or FILTER_STR in mod["contributors"].lower()
            or FILTER_STR in mod["tags"].lower()
        ) and "hidden" not in mod["tags"].lower()

        secret_check = (
            "hidden" in mod["tags"].lower()
            and FILTER_STR == "lbood"
        )

        if matches_filter or secret_check:
            if mod["game"] == FILTER_GAME:
                # filter mods vs texture packs
                if (FILTER_CAT == "tex") == (mod["tags"] == "texture-mod"):
                    if (
                        INCLUDE_INSTALLED and mod["access_date"] != "Not Installed"
                    ) or (
                        INCLUDE_UNINSTALLED and mod["access_date"] == "Not Installed"
                    ):
                        release_date_str = str(mod["release_date"])
                        release_date = datetime.strptime(mod["release_date"], '%Y-%m-%d')
                        if datetime.now() - release_date < timedelta(days = 10):
                            release_date_str = release_date_str + " ✨NEW✨"

                        mod_table_data.append(
                            [
                                mod_id,
                                mod_name,
                                mod["desc"],
                                mod["tags"],
                                mod["contributors"],
                                release_date_str,
                                mod["install_date"],
                                mod["access_date"],
                                # mod["latest_available_update_date"],
                                mod["URL"],
                                (mod["website_url"] if "website_url" in mod else ""),
                                (mod["videos_url"] if "videos_url" in mod else ""),
                                (mod["photos_url"] if "photos_url" in mod else ""),
                                (
                                    mod["image_override_url"]
                                    if "image_override_url" in mod
                                    else ""
                                ),
                                (mod["game"] if "game" in mod else "jak1"),
                            ]
                        )

    if sort_col_idx is None:
        # not from a heading click, retain sorting
        remapped_col_idx = LATEST_TABLE_SORT[0]
    else:
        # heading click, adjust sorting
        remapped_col_idx = vis_col_map[sort_col_idx]

        if remapped_col_idx == LATEST_TABLE_SORT[0]:
            # same column, flip asc/desc
            LATEST_TABLE_SORT[1] = not LATEST_TABLE_SORT[1]
        else:
            LATEST_TABLE_SORT[0] = remapped_col_idx
            LATEST_TABLE_SORT[1] = True

    global sorted_table_headings, table_headings
    sorted_table_headings = table_headings.copy()
    if LATEST_TABLE_SORT[0] != ColumnEnum.SPECIAL:
      # add asc/desc arrows if not in our wakeup sort special case
      sorted_table_headings[remapped_col_idx] += " ↑" if LATEST_TABLE_SORT[1] else " ↓"

    if remapped_col_idx == ColumnEnum.SPECIAL:
        # special sort for wakeup, do coalesce(access date,release date)
        mod_table_data.sort(
            key=lambda x: x[ColumnEnum.RELEASE_DATE]
            if x[ColumnEnum.LAUNCH_DATE] == "Not Installed"
            else x[ColumnEnum.LAUNCH_DATE].lower()
        )
    elif remapped_col_idx == ColumnEnum.LAUNCH_DATE or remapped_col_idx == ColumnEnum.INSTALL_DATE:
        # special sort for date cols that might not have data
        mod_table_data.sort(
            key=lambda x: "0"
            if x[remapped_col_idx] == "Not Installed"
            else x[remapped_col_idx].lower()
        )
    else:
        mod_table_data.sort(key=lambda x: x[remapped_col_idx].lower())

    if not LATEST_TABLE_SORT[1]:
        mod_table_data.reverse()

    # enable/disable jak3 section based on list of mods
    window["jak3/mods"].update(disabled=not seenJak3)
    window["jak3/tex"].update(disabled=not seenJak3)

    # print(mod_table_data)
    return mod_table_data


LATEST_TABLE_DATA = []

# ----- Full layout -----
layout = [
    [
        sg.Frame(
            title="",
            key="-SPLASHFRAME-",
            border_width=0,  # Set border_width to 0
            visible=True,
            element_justification="center",
            vertical_alignment="center",
            layout=[
                [
                    sg.Image(
                        key="-SPLASHIMAGE-",
                        source=githubUtils.resize_image(splashfile, 970, 607),
                        pad=(0, 0),  # Set padding to 0
                        expand_x=True,
                        expand_y=True,
                    )
                ]
            ],
        )
    ],
    [
        sg.Frame(
            title="",
            key="-LOADINGFRAME-",
            border_width=0,  # Set border_width to 0
            visible=False,
            element_justification="center",
            vertical_alignment="center",
            layout=[
                [
                    sg.Image(
                        key="-LOADINGIMAGE-",
                        source=githubUtils.resize_image(loadingimage, 970, 607),
                        pad=(0, 0),  # Set padding to 0
                        expand_x=True,
                        expand_y=True,
                    ),
                    sg.Text("~~~ LOADING ~~~", key="-LOADINGBACKUP-", visible=False)
                ]
            ],
        )
    ],
    [
        sg.Frame(
            title="",
            key="-MAINFRAME-",
            border_width=0,
            visible=False,
            layout=[
                [
                    sg.Column(  # nav sidebar
                        [
                            [sg.Text("JAK 1", font=("Helvetica", 16, "bold"))],
                            [
                                sg.Radio(
                                    "Mods",
                                    "filter",
                                    font=("Helvetica", 12),
                                    enable_events=True,
                                    key="jak1/mods",
                                    default=True,
                                )
                            ],
                            [
                                sg.Radio(
                                    "Texture Packs",
                                    "filter",
                                    enable_events=True,
                                    font=("Helvetica", 12),
                                    key="jak1/tex",
                                )
                            ],
                            [sg.Text("")],
                            [sg.Text("JAK 2", font=("Helvetica", 16, "bold"))],
                            [
                                sg.Radio(
                                    "Mods",
                                    "filter",
                                    font=("Helvetica", 12),
                                    enable_events=True,
                                    key="jak2/mods",
                                )
                            ],
                            [
                                sg.Radio(
                                    "Texture Packs",
                                    "filter",
                                    font=("Helvetica", 12),
                                    enable_events=True,
                                    key="jak2/tex",
                                )
                            ],
                            [sg.Text("")],
                            [sg.Text("JAK 3", font=("Helvetica", 16, "bold"))],
                            [
                                sg.Radio(
                                    "Mods",
                                    "filter",
                                    font=("Helvetica", 12),
                                    enable_events=True,
                                    key="jak3/mods",
                                )
                            ],
                            [
                                sg.Radio(
                                    "Texture Packs",
                                    "filter",
                                    font=("Helvetica", 12),
                                    enable_events=True,
                                    key="jak3/tex",
                                )
                            ],
                            [sg.VPush()],
                            [
                                sg.Btn(
                                    button_text="View iso_data Folder",
                                    key="-VIEWISOFOLDER-",
                                    expand_x=True,
                                )
                            ],
                            [
                                sg.Btn(
                                    button_text="jakmods.dev",
                                    key="-JAKMODSWEB-",
                                    expand_x=True,
                                )
                            ],
                        ],
                        expand_y=True,
                    ),
                    sg.VerticalSeparator(),
                    sg.Column(
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
                                        [
                                            sg.Text(
                                                "",
                                                key="-SELECTEDMODDESC-",
                                                size=(45, 7),
                                            )
                                        ],
                                        [sg.Text("Tags:", key="-SELECTEDMODTAGS-")],
                                        [sg.Text("Contributors:", key="-SELECTEDMODCONTRIBUTORS-")],
                                        [sg.Text("Release Date:", key="-SELECTEDMODRELEASEDATE-")],
                                        [
                                            sg.Btn(
                                                button_text="Launch",
                                                key="-LAUNCH-",
                                                expand_x=True,
                                            ),
                                            sg.Btn(
                                                button_text="Re-extract",
                                                key="-REEXTRACT-",
                                                expand_x=True,
                                            ),
                                            sg.Btn(
                                                button_text="Recompile",
                                                key="-RECOMPILE-",
                                                expand_x=True,
                                            ),
                                            sg.Btn(
                                                button_text="Uninstall",
                                                key="-UNINSTALL-",
                                                expand_x=True,
                                            ),
                                        ],
                                        [
                                            sg.Btn(
                                                button_text="View Folder",
                                                key="-VIEWFOLDER-",
                                                expand_x=True,
                                            ),
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
                                            # sg.Btn(
                                            #     button_text="Photo(s)",
                                            #     key="-PHOTOS-",
                                            #     expand_x=True,
                                            #     metadata={"url": ""},
                                            # ),
                                        ],
                                    ],
                                    size=(200, 300),
                                    expand_x=True,
                                    expand_y=True,
                                ),
                                sg.Frame(
                                    title="",
                                    element_justification="center",
                                    vertical_alignment="center",
                                    border_width=0,
                                    layout=[
                                        [
                                            sg.Image(
                                                key="-SELECTEDMODIMAGE-", expand_y=True
                                            )
                                        ]
                                    ],
                                    size=(450, 300),
                                ),
                            ],
                            [sg.HorizontalSeparator()],
                            [
                                sg.Text("Search"),
                                sg.Input(
                                    expand_x=True, enable_events=True, key="-FILTER-"
                                ),
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
                        ]
                    ),
                ]
            ],
        )
    ],
]

window = sg.Window(
    "OpenGOAL Mod Launcher", layout, icon=iconfile, border_depth=0, finalize=True
)


def handleModTableSelection(row):
    global LATEST_TABLE_DATA
    mod = LATEST_TABLE_DATA[row]
    # print(mod)

    mod_id = mod[ColumnEnum.ID]
    mod_name = mod[ColumnEnum.NAME]
    mod_desc = mod[ColumnEnum.DESC]
    mod_tags = mod[ColumnEnum.TAGS]
    mod_contributors = mod[ColumnEnum.CONTRIBUTORS]
    mod_release_date = mod[ColumnEnum.RELEASE_DATE]
    mod_install_date = mod[ColumnEnum.INSTALL_DATE]
    mod_access_date = mod[ColumnEnum.LAUNCH_DATE]
    mod_url = mod[ColumnEnum.INSTALL_URL]
    mod_website_url = mod[ColumnEnum.WEBSITE_URL]
    mod_videos_url = mod[ColumnEnum.VIDEOS_URL]
    mod_photos_url = mod[ColumnEnum.PHOTOS_URL]
    mod_image_override_url = mod[ColumnEnum.THUMBNAIL_URL]
    mod_game = mod[ColumnEnum.GAME]

    # update text and metadata
    window["-LAUNCH-"].update(
        "Install" if mod_access_date == "Not Installed" else "Launch"
    )
    window["-SELECTEDMODNAME-"].update(mod_name)
    window["-SELECTEDMODNAME-"].metadata["id"] = mod_id
    window["-SELECTEDMODNAME-"].metadata["url"] = mod_url
    window["-SELECTEDMODNAME-"].metadata["image_override_url"] = mod_image_override_url
    window["-SELECTEDMODNAME-"].metadata["game"] = mod_game
    window["-SELECTEDMODDESC-"].update(mod_desc)
    window["-SELECTEDMODTAGS-"].update(f"Tags: {mod_tags}")
    window["-SELECTEDMODCONTRIBUTORS-"].update(f"Contributors: {mod_contributors}")
    window["-SELECTEDMODRELEASEDATE-"].update(f"Release Date: {mod_release_date}")
    window["-VIEWFOLDER-"].update(disabled=(mod_access_date == "Not Installed"))
    window["-REEXTRACT-"].update(disabled=(mod_access_date == "Not Installed"))
    window["-RECOMPILE-"].update(disabled=(mod_access_date == "Not Installed"))
    window["-UNINSTALL-"].update(disabled=(mod_access_date == "Not Installed"))
    window["-WEBSITE-"].update(disabled=(mod_website_url == ""))
    window["-WEBSITE-"].metadata["url"] = mod_website_url
    window["-VIDEOS-"].update(disabled=(mod_videos_url == ""))
    window["-VIDEOS-"].metadata["url"] = mod_videos_url
    # window["-PHOTOS-"].update(disabled=(mod_photos_url == ""))
    # window["-PHOTOS-"].metadata["url"] = mod_photos_url

    # load mod image
    try:
        mod_image_url = (
            mod_image_override_url
            if mod_image_override_url != ""
            else githubUtils.returnModImageURL(mod_url)
        )

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
        window["-SELECTEDMODIMAGE-"].update(
            githubUtils.resize_image(png_data, 450.0, 300.0)
        )

    except Exception as e:
        print("Failed to download mod image for ", mod_name, "error", e)
        window["-SELECTEDMODIMAGE-"].update(
            githubUtils.resize_image(noimagefile, 450.0, 300.0)
        )

windowstatus = "main"

def launch_mod(tmpModURL):
    [linkType, tmpModURL] = githubUtils.identifyLinkType(tmpModURL)

    launcherUtils.update_and_launch(tmpModURL, tmpModSelected, tmpModName, linkType, tmpGame)

def reset():
    global LATEST_TABLE_DATA
    if window is not None:
        LATEST_TABLE_DATA = getRefreshedTableData(None)
        window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
        for i in range(len(sorted_table_headings)):
            window["-MODTABLE-"].Widget.heading(i, text=sorted_table_headings[i])

        if len(LATEST_TABLE_DATA) > 0:
            window["-MODTABLE-"].update(select_rows=[0])
            handleModTableSelection(0)
    else:
        print("Window is closed. Cannot reset.")

LOADING_IMAGE_URLS = [
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-0.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-1.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-2.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-3.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-4.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-5.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-6.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-7.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-8.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-9.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-10.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-11.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-12.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-13.png",
    "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlauncher-loading-14.png"
]

def loading_screen_with_thread(thread):
    windowstatus = "loading"

    # hide all the buttons and display a window showing that it is installing
    loadingimage = getPNGFromURL(LOADING_IMAGE_URLS[random.randint(0, len(LOADING_IMAGE_URLS)-1)])
    if loadingimage is not None:
      window["-LOADINGIMAGE-"].update(source=githubUtils.resize_image(loadingimage, 970, 607), visible=True)
      window["-LOADINGBACKUP-"].update(visible=False)
    else:
      window["-LOADINGIMAGE-"].update(visible=False)
      window["-LOADINGBACKUP-"].update(visible=True)
      
    window["-LOADINGFRAME-"].update(visible=True)
    window["-LOADINGFRAME-"].unhide_row()
    window["-MAINFRAME-"].update(visible=False)
    window["-MAINFRAME-"].hide_row()
    window.refresh()

    # online launch
    window["-LAUNCH-"].update(disabled=True)
    window["-LAUNCH-"].update("Updating...")
    thread.start()

    # Continue processing events while the background thread runs
    while thread.is_alive():
        event, values = window.read(timeout=100)

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        # Handle other events here...

    # Reset windowstatus back to "main"
    windowstatus = "main"

    reset()

# this is the main event loop where we handle user input
reset()
bootstart = time.time()
while True:
    if windowstatus == "main" and window["-LOADINGFRAME-"].visible:
        # turn the button back on
        window["-LAUNCH-"].update("Launch")
        window["-LAUNCH-"].update(disabled=False)

        # We are done installing show the main menu again
        window["-MAINFRAME-"].update(visible=True)
        window["-MAINFRAME-"].unhide_row()
        window["-LOADINGFRAME-"].update(visible=False)
        window["-LOADINGFRAME-"].hide_row()

        # refresh table in case a new mod is installed
        reset()

    event, values = window.read(timeout=100)

    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "__TIMEOUT__":
        if bootstart is not None:
            curtime = time.time()
            if curtime - bootstart > 2:
                # switch from splash screen to main screen after 2s
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
            if row == None:
                # empty row, do nothing
                continue
            elif row == -1:
                # heading row, sort by col
                LATEST_TABLE_DATA = getRefreshedTableData(col)
                window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
                for i in range(len(sorted_table_headings)):
                    window["-MODTABLE-"].Widget.heading(
                        i, text=sorted_table_headings[i]
                    )
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
        tmpGame = window["-SELECTEDMODNAME-"].metadata["game"]


        selected_mod_tags = window["-SELECTEDMODTAGS-"].get()
        if "external" in selected_mod_tags:
            ans = sg.popup_ok_cancel(tmpModName + " is an external mod that can be found at " + tmpModURL + " would you like to go there now?", icon=iconfile, image=iconfile)
            if ans == "OK":
                webbrowser.open(tmpModURL)
                reset()
        else:
            launch_thread = threading.Thread(target=launch_mod, args=(tmpModURL,))

            loading_screen_with_thread(launch_thread)


    elif event == "-VIEWFOLDER-":
        tmpModSelected = window["-SELECTEDMODNAME-"].metadata["id"]
        subfolders = [f.name for f in os.scandir(ModFolderPATH) if f.is_dir()]

        if tmpModSelected in subfolders:
            dir = dirs.user_data_dir + "\\OpenGOAL-Mods\\" + tmpModSelected
            launcherUtils.openFolder(dir)
        else:
            sg.Popup("Selected mod is not installed", keep_on_top=True, icon=iconfile)
    elif event == "-REEXTRACT-":
        tmpModName = window["-SELECTEDMODNAME-"].get()
        tmpModSelected = window["-SELECTEDMODNAME-"].metadata["id"]
        tmpModURL = window["-SELECTEDMODNAME-"].metadata["url"]
        tmpGame = window["-SELECTEDMODNAME-"].metadata["game"]
        [linkType, tmpModURL] = githubUtils.identifyLinkType(tmpModURL)
        subfolders = [f.name for f in os.scandir(ModFolderPATH) if f.is_dir()]
        if tmpModSelected in subfolders:
            dir = dirs.user_data_dir + "\\OpenGOAL-Mods\\" + tmpModSelected
            ans = sg.popup_ok_cancel(
                "Confirm: re-extracting "
                + dir,
                icon=iconfile,
            )
            if ans == "OK":
                rebuild_thread = threading.Thread(target=launcherUtils.rebuild, args=(tmpModURL, tmpModSelected, tmpModName, linkType, tmpGame, True))

                loading_screen_with_thread(rebuild_thread)
        else:
            sg.Popup("Selected mod is not installed", keep_on_top=True, icon=iconfile)
    elif event == "-RECOMPILE-":
        tmpModName = window["-SELECTEDMODNAME-"].get()
        tmpModSelected = window["-SELECTEDMODNAME-"].metadata["id"]
        tmpModURL = window["-SELECTEDMODNAME-"].metadata["url"]
        tmpGame = window["-SELECTEDMODNAME-"].metadata["game"]
        [linkType, tmpModURL] = githubUtils.identifyLinkType(tmpModURL)
        subfolders = [f.name for f in os.scandir(ModFolderPATH) if f.is_dir()]
        if tmpModSelected in subfolders:
            dir = dirs.user_data_dir + "\\OpenGOAL-Mods\\" + tmpModSelected
            ans = sg.popup_ok_cancel(
                "Confirm: recompiling "
                + dir,
                icon=iconfile,
            )
            if ans == "OK":
                rebuild_thread = threading.Thread(target=launcherUtils.rebuild, args=(tmpModURL, tmpModSelected, tmpModName, linkType, tmpGame, False))

                loading_screen_with_thread(rebuild_thread)
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
    # elif event == "-PHOTOS-":
    #     window = window.refresh()
    #     url = window["-PHOTOS-"].metadata["url"]
    #     if url:
    #         webbrowser.open(url)
    # nav siderbar events
    elif event == "jak1/mods":
        FILTER_GAME = "jak1"
        FILTER_CAT = "mods"
        LATEST_TABLE_DATA = getRefreshedTableData(None)
        window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
    elif event == "jak1/tex":
        FILTER_GAME = "jak1"
        FILTER_CAT = "tex"
        LATEST_TABLE_DATA = getRefreshedTableData(None)
        window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
    elif event == "jak2/mods":
        FILTER_GAME = "jak2"
        FILTER_CAT = "mods"
        LATEST_TABLE_DATA = getRefreshedTableData(None)
        window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
    elif event == "jak2/tex":
        FILTER_GAME = "jak2"
        FILTER_CAT = "tex"
        LATEST_TABLE_DATA = getRefreshedTableData(None)
        window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
    elif event == "jak3/mods":
        FILTER_GAME = "jak3"
        FILTER_CAT = "mods"
        LATEST_TABLE_DATA = getRefreshedTableData(None)
        window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
    elif event == "jak3/tex":
        FILTER_GAME = "jak3"
        FILTER_CAT = "tex"
        LATEST_TABLE_DATA = getRefreshedTableData(None)
        window["-MODTABLE-"].update(values=LATEST_TABLE_DATA)
    elif event == "-VIEWISOFOLDER-":
        dir = dirs.user_data_dir + "\\OpenGOAL-Mods\\_iso_data"
        launcherUtils.ensure_jak_folders_exist()
        launcherUtils.openFolder(dir)
    elif event == "-JAKMODSWEB-":
        openLauncherWebsite()
    else:
        print("unhandled event:", event, values)

window.close()
