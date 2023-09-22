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
from datetime import datetime
import sys
import webbrowser
import os
from os.path import exists
import shutil
import tkinter
from appdirs import AppDirs
from appdirs import AppDirs
import platform
import stat
from datetime import datetime
from pathlib import Path
import openGOALModLauncher2


splashfile = openGOALModLauncher2.getPNGFromURL("https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/modlaunchersplash.png")

noimagefile = openGOALModLauncher2.getPNGFromURL("https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/noRepoImageERROR.png")

iconfile = openGOALModLauncher2.getPNGFromURL("https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/appicon.ico")


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
                          button_text="View ISO Folder", key="-VIEWISOFOLDER-", expand_x=True
                      ),
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