# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 18:33:45 2022

@author: Zed
"""

# img_viewer.py

import PySimpleGUI as sg
import os.path
import json
import time
from PIL import Image
import PIL.Image
import io
import base64
import sys
import cloudscraper
import launcherFunctions



# Folder where script is placed, It looks in this for the Exectuable
if getattr(sys, 'frozen', False):
    LauncherDir = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    LauncherDir = os.path.dirname(__file__)

installpath = str(LauncherDir + "\\")



  
# Opening JSON file
f = open(installpath + 'data.json')
  
# returns JSON object as 
# a dictionary
moddersAndModsJSON = json.load(f)
f.close()

j_file = json.dumps(moddersAndModsJSON)
print(moddersAndModsJSON["Modding Community"][0]["name"])
print(moddersAndModsJSON["Modding Community"][0]["URL"])


# First the window layout in 2 columns

file_list_column = [
	[sg.Text("Mod Creator")],
	[sg.Combo(list(moddersAndModsJSON.keys()), enable_events=True, key='pick_modder', size=(30, 0),default_value="Modding Community")],
    [sg.Text("Their Mods")],
	[
        sg.Combo([], key='pick_mod', size=(30, 0),default_value="Randomizer",enable_events=True)  # there must be values of selected item
        
    ],
]



# For now will only show the name of the file that was chosen
image_viewer_column = [
    [sg.Text("Choose an mod from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],

]

installed_mods_column = [
    [sg.Text("Installed mods")],
	[sg.Listbox(values=["Randomizer", "MicroTransactions"],size=(60,5))],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-IMvAGE-")],

]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
		[sg.Column(installed_mods_column)],
		[sg.Btn(button_text="Launch!")],
		[sg.Btn(button_text="Uninstall")]
    ]
]

window = sg.Window('OpenGOAL Mod Launcher v0.01', layout, icon= installpath + 'appicon.ico')

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            f
            for f in file_list
            if os.path.isfile(os.path.join(folder, f))
            and f.lower().endswith((".png", ".gif"))
        ]
        window["-FILE LIST-"].update(fnames)
    elif event == "-FILE LIST-":  # A file was chosen from the listbox
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-TOUT-"].update(filename)
            window["-IMAGE-"].update(filename=filename)

        except:
            pass
    elif event =='pick_modder':
        window['-IMAGE-'].update(launcherFunctions.resize_image(installpath + "QezJKtyZ_400x400.png" ,resize=(250,250)))
        item = values[event]
        title_list = [i["name"] for i in moddersAndModsJSON[item]]
        window['pick_mod'].update(value=title_list[0], values=title_list)
    elif event =='pick_mod':
        #TODO generate this URL automatically
        url = "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/opengoal-randomizer-mod-pack/main/ModImage.png"
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
        png_data = png_bio.getvalue()
        print("image changed")
        window['-IMAGE-'].update(launcherFunctions.resize_image(png_data ,resize=(250,250)))
    

window.close()