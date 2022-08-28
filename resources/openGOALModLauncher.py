# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 18:33:45 2022

@author: Zed
"""

# img_viewer.py

# we will clean these up later but for now even leave unused imports
#we are not in cleanup phase yet
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
import launcherUtils
import githubUtils
import requests



# Folder where script is placed, It looks in this for the Exectuable
if getattr(sys, 'frozen', False):
    LauncherDir = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    LauncherDir = os.path.dirname(__file__)

installpath = str(LauncherDir + "\\")

#intialize default variables so they are never null
currentModderSelected = "not selected"
currentModSelected = "not selected"
currentModURL = "not selected"
currentModImage = "not selected"


launcherUtils.installedlist(installpath)
# Opening JSON file
f = open(installpath + 'data.json')
  
# returns JSON object as 
# a dictionary
moddersAndModsJSON = json.load(f)
f.close()

j_file = json.dumps(moddersAndModsJSON)
#print(moddersAndModsJSON["Modding Community"][0]["name"])
#print(moddersAndModsJSON["Modding Community"][0]["URL"])


# First the window layout in 2 columns

mod_list_column = [
	[sg.Text("Mod Creator")],
    #would be nice to add default_value="Modding Community", below, but if we do that it doesnt trigger the update event currently
	[sg.Combo(list(moddersAndModsJSON.keys()), enable_events=True, key='pick_modder', size=(30, 0))],
    [sg.Text("Their Mods")],
    #would be nice to add default_value="Randomizer", below, but if we do that it doesnt trigger the update event currently
	[
        sg.Combo([], key='pick_mod', size=(30, 0),enable_events=True )  # there must be values of selected item
        
    ],
]



# For now will only show the name of the file that was chosen
mod_details_column = [
    [sg.Text("Choose an mod from list on left:")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(key="-SELECTEDMODIMAGE-")],

]

installed_mods_column = [
    [sg.Text("Installed mods")],
	[sg.Listbox(values=["Randomizer", "MicroTransactions"],size=(60,5))],
    [sg.Text(size=(40, 1), key="-TOUT-")],

]

# ----- Full layout -----
layout = [
    [
        sg.Column(mod_list_column),
        sg.VSeperator(),
        sg.Column(mod_details_column),
		[sg.Column(installed_mods_column)],
		[sg.Btn(button_text="Launch!")],
		[sg.Btn(button_text="Uninstall", disabled=True)]
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
            window["-SELECTEDMODIMAGE-"].update(filename=filename)

        except:
            pass
    elif event =='pick_modder':
        window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(installpath + "noRepoImageERROR.png" ,resize=(1,1)))
        item = values[event]
        title_list = [i["name"] for i in moddersAndModsJSON[item]]
        window['pick_mod'].update(value=title_list[0], values=title_list)
    elif event =='pick_mod':
        #TODO generate this URL automatically
        #https://github.com/OpenGOAL-Unofficial-Mods/opengoal-randomizer-mod-pack/blob/main/ModImage.png?raw=true

        currentModderSelected = window['pick_modder'].get()
        currentModSelected = window['pick_mod'].get()
        
        
        #print(moddersAndModsJSON[currentModderSelected][0]["URL"])
        for i in range(len(moddersAndModsJSON[currentModderSelected])):
            if moddersAndModsJSON[currentModderSelected][i]["name"] == currentModSelected:
                currentModURL = moddersAndModsJSON[currentModderSelected][i]["URL"]
        
        currentModImage = githubUtils.returnModImageURL(currentModURL)
        print("Current modder is " + currentModderSelected)
        print("Current mod is " + currentModSelected)
        print("Current mod URL is " + currentModURL)
        print("Current mod image is " + str(currentModImage))
        
        url = currentModImage
        try:
            r = requests.head(currentModImage).status_code
            print(str(r))
            if r == 200:
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
                window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(png_data ,resize=(250,250)))
                # prints the int of the status code. Find more at httpstatusrappers.com :)    
            if r != 200:
                window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(installpath + "noRepoImageERROR.png" ,resize=(250,250)))

        except requests.exceptions.MissingSchema:
            window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(installpath + "noRepoImageERROR.png" ,resize=(250,250)))
    elif event == "Launch!":
        print(" ")
        window['Launch!'].update(disabled=True)
        print("Launch button hit!")
        print("Printing avalible information below for debug purposes, remove these later")
        print(currentModderSelected)
        print(currentModSelected)
        print(currentModURL)
        print(currentModImage)

        [linkType, currentModURL] = githubUtils.identifyLinkType(currentModURL)
        launcherUtils.launch(currentModURL, currentModderSelected, currentModSelected, linkType)
        
        #turn the button back on
        window['Launch!'].update(disabled=False)
    elif event == "Uninstall":
        print("")
        print("uninstallButton hit!")
        print("Do things here")

            
    

window.close()