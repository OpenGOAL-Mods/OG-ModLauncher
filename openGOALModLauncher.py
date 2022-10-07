# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 18:33:45 2022

@author: Zed
"""

# img_viewer.py

# we will clean these up later but for now even leave unused imports
#we are not in cleanup phase yet
from PIL import Image 
from utils import launcherUtils, githubUtils
import PySimpleGUI as sg
import cloudscraper
import io
import json
import os.path
import requests
import sys
import webbrowser

import os
from os.path import exists
import urllib.request
import shutil

# Folder where script is placed, It looks in this for the Exectuable
if getattr(sys, 'frozen', False):
    LauncherDir = os.path.dirname(os.path.realpath(sys.executable))
elif __file__:
    LauncherDir = os.path.dirname(__file__)

installpath = str(LauncherDir + "\\resources\\")

#intialize default variables so they are never null
currentModderSelected = None
currentModSelected = None
currentModURL = None
currentModImage = None
steamDIR = None
AppdataPATH = os.getenv('APPDATA')


#comment this out if you want to test with a local file
moddersAndModsJSON = requests.get("https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/ListOfMods.json").json()

j_file = json.dumps(moddersAndModsJSON)
#print(moddersAndModsJSON["Modding Community"][0]["name"])
#print(moddersAndModsJSON["Modding Community"][0]["URL"])


# First the window layout in 2 columns

installed_mods_column = [
    [sg.Text("Installed Mods", font=("Helvetica", 14))],
    [sg.Listbox(values=["This List is not", "Classic+"],size=(40,5),key="InstalledModListBox",enable_events=True)],
    [
        sg.Btn(button_text="Refresh"),
        sg.Btn(button_text="Uninstall"),
        sg.Btn(button_text="Add to Steam",key='AddToSteam',enable_events=True)
    ],
]

mod_list_column = [
	[sg.Text("Available Mods", font=("Helvetica", 14))],
	[sg.Text("Mod Creator")], 
    [sg.Combo(list(moddersAndModsJSON.keys()), enable_events=True, key='pick_modder', size=(40, 0))],
    [sg.Text("Their Mods")], 
    [sg.Combo([], key='pick_mod', size=(40, 0),enable_events=True)],
    [sg.Btn(button_text="Search Available mods",key='mod_search')]
]

mod_details_column = [
    [sg.Text("Selected Mod", font=("Helvetica", 14))], 
    [
        sg.Text("", key="-SELECTEDMOD-"),
        sg.Text("", key="-SELECTEDMODURL-", visible=False)
    ],
    [sg.Text("", key="-SELECTEDMODDESC-")],
    [sg.Image(key="-SELECTEDMODIMAGE-")],
    [
        sg.Btn(button_text="Launch!"),
        sg.Btn(button_text="View Folder",key="ViewFolder_1"),
        sg.Btn(button_text="Reinstall",key="Reinstall_1"),
        sg.Btn(button_text="Uninstall",key="Uninstall_1"),
        sg.Btn(button_text="View mod on github!",key="-GITHUB-_1")
    ]
]

# ----- Full layout -----
layout = [
    [sg.Column([
        [sg.Column(installed_mods_column)],
        [sg.HSeparator()],
        [sg.Column(mod_list_column)],
        ]),
    sg.VSeparator(),
    sg.Column(mod_details_column)]
]
sg.theme('Python')
url= "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/appicon.ico"
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

url= "https://raw.githubusercontent.com/OpenGOAL-Unofficial-Mods/OpenGoal-ModLauncher-dev/main/resources/noRepoImageERROR.png"
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

window = sg.Window('OpenGOAL Mod Launcher v0.03', layout, icon = iconfile, finalize=True)
window.Element('AddToSteam').Update(visible = False)
def bootup():
    #print("BOOT")
    
    #installed mods
    if not os.path.exists(AppdataPATH + "/OpenGOAL-Mods"):
        print("Creating Mod dir: " + AppdataPATH)
        os.makedirs(AppdataPATH + "/OpenGOAL-Mods")
    subfolders = [ f.name for f in os.scandir(os.getenv('APPDATA') + "\\OpenGOAL-Mods") if f.is_dir() ]
    if subfolders == []:
        subfolders = ["No Mods Installed"]
    #print(subfolders)
    window["InstalledModListBox"].update(subfolders)
    print()
  
    if subfolders == [] or subfolders[0] == "No Mods Installed":
    #default mod selection on boot
        window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(1,1)))
        item = "Modding Community"
        window['pick_modder'].update(item)
        title_list = [i["name"] for i in moddersAndModsJSON[item]]
        window['pick_mod'].update(value=title_list[0], values=title_list)
        currentModderSelected = "Modding Community"
        currentModSelected = "Randomizer"
        currentModURL = "https://github.com/OpenGOAL-Unofficial-Mods/opengoal-randomizer-mod-pack/tree/main"
        currentModImage = None
        [currentModderSelected, currentModSelected, currentModURL, currentModImage] = handleModSelected()
    
    if subfolders != [] and subfolders[0] != "No Mods Installed":
    #if there is a mod installed, use the first one in the list on boot.
    
        for modder in moddersAndModsJSON.keys():
                for mod in moddersAndModsJSON[modder]:
                    if mod["name"] == subfolders[0]:
                        currentMOD = modder
        print(currentMOD)
        window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(1,1)))
        item = currentMOD
        window['pick_modder'].update(item)
        title_list = [i["name"] for i in moddersAndModsJSON[item]]
        #below is not correct but it does work.
        window['pick_mod'].update(value=subfolders[0], values=title_list)
        
        currentModderSelected = modder
        currentModSelected = subfolders[0]
        currentModURL = "https://github.com/OpenGOAL-Unofficial-Mods/opengoal-randomizer-mod-pack/tree/main"
        currentModImage = None
        [currentModderSelected, currentModSelected, currentModURL, currentModImage] = handleModSelected()
    if window['-SELECTEDMOD-'].get().lower() == "local multiplayer (beta) + randomizer":
            window.Element('AddToSteam').Update(visible = True)
    else:
            window.Element('AddToSteam').Update(visible = False)

def handleModSelected():
    tmpModderSelected = window['pick_modder'].get()
    tmpModSelected = window['pick_mod'].get()
    tmpModURL = None
    tmpModDesc = "<No description available>"
    tmpModImage = None
    print("\nLoading new mod selection one moment...")
    for mod in moddersAndModsJSON[tmpModderSelected]:
        if mod["name"] == tmpModSelected:
            tmpModURL = mod["URL"]
            if mod.get("desc"):
                tmpModDesc = mod["desc"]
    
    tmpModImage = githubUtils.returnModImageURL(tmpModURL)
    
    url = tmpModImage
    try:
        r = requests.head(tmpModImage).status_code
        if r != 200:
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
        else:
            window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(250,250)))
        print("Done Loading new mod selection")
        changePlayInstallButtonText()

    except requests.exceptions.MissingSchema:
        window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(250,250)))

    window['-SELECTEDMOD-'].update(tmpModSelected)
    window['-SELECTEDMODDESC-'].update(tmpModDesc)
    window['-SELECTEDMODURL-'].update(tmpModURL)
    
    if tmpModSelected.lower() == "local multiplayer (beta) + randomizer":
        window.Element('AddToSteam').Update(visible = True)
    else:
        window.Element('AddToSteam').Update(visible = False)

    return [tmpModderSelected, tmpModSelected, tmpModURL, tmpModImage]

def handleInstalledModSelected():
    if len(window['InstalledModListBox'].get()) == 0:
        return [None, None]
        
    tmpModSelected = window['InstalledModListBox'].get()[0]
    tmpModderSelected = None

    for modder in moddersAndModsJSON.keys():
        if not tmpModderSelected:
            for mod in moddersAndModsJSON[modder]:
                if mod["name"] == tmpModSelected:
                    tmpModderSelected = modder
                    break

    return [tmpModderSelected, tmpModSelected]

def changePlayInstallButtonText():
    subfolders = [ f.name for f in os.scandir(os.getenv('APPDATA') + "\\OpenGOAL-Mods") if f.is_dir() ]
    if not window['pick_mod'].get() in subfolders:
            window['Launch!'].update('Install')
            window['Uninstall'].update(disabled=True)
            window['ViewFolder_1'].update(disabled=True)
            window['Reinstall_1'].update(disabled=True)
            window['Uninstall_1'].update(disabled=True)
    else:
        window['Launch!'].update('Launch!')
        window['Uninstall'].update(disabled=False)
        window['ViewFolder_1'].update(disabled=False)
        window['Reinstall_1'].update(disabled=False)
        window['Uninstall_1'].update(disabled=False)
        

def refreshInstalledList():
    subfolders = [ f.name for f in os.scandir(os.getenv('APPDATA') + "\\OpenGOAL-Mods") if f.is_dir() ]
    window["InstalledModListBox"].update(subfolders)

def open_steamPrompt():
    filelayout = [ [sg.FolderBrowse("Select Steam Directory",enable_events=True,key="PICKSTEAMDIR")]]
    filewindow = sg.Window('Search for offered mods', filelayout, keep_on_top=True,icon = iconfile, size=window.size,location = window.CurrentLocation())
    
    # Event Loop
    while True:
            event, values = filewindow.read()
            print(event)
            print(values[event])
            if event in (sg.WIN_CLOSED, 'Exit'):                # always check for closed window
                break
            if exists(values[event]+"/steam.exe"):
                print("FOUND STEAM DIR")
                print(values[event])
                steamDIR = values[event]
                print(steamDIR)
                filewindow.close()
                return steamDIR
            else:
                sg.popup("Did not find Steam install Directory try again",keep_on_top=True)
            
            
            
    else:
        filewindow.close()



def open_search():
    names = []

    for modder in moddersAndModsJSON.keys():
        for mod in moddersAndModsJSON[modder]:
            if not mod["name"] in names:
                names.append(mod["name"])    



    layout = [[sg.Text('Search for offered mods')],
          [sg.Input(size=window.size, enable_events=True, key='-INPUT-')],
          [sg.Listbox(names, size=window.size, enable_events=True, key='-LIST-')],
          [sg.Button('Chrome'), sg.Button('Exit')]]

    window2 = sg.Window('Search for offered mods', layout, keep_on_top=True,icon = iconfile, size=window.size,location = window.CurrentLocation())
# Event Loop
    while True:
        event, values = window2.read()
        if event in (sg.WIN_CLOSED, 'Exit'):                # always check for closed window
            break
        if values['-INPUT-'] != '':                         # if a keystroke entered in search field
            search = values['-INPUT-'].lower()
            new_values = [x for x in names if search.lower() in x.lower()]  # do the filtering
            window2['-LIST-'].update(new_values)     # display in the listbox
            
            
            print(len(values['-LIST-']))
            if event == '-LIST-':
                print(values['-LIST-'][0])
                print("was CLICKED!")
                currentMOD = "unkown"
                p=0
                for modder in moddersAndModsJSON.keys():
                      
                        for mod in moddersAndModsJSON[modder]:
                           
                            print(mod["name"])
                            print(values['-LIST-'][0])
                            if mod["name"].lower() == values['-LIST-'][0].lower():
                                print("MATCH")
                                indexOfMod = p
                                currentMOD = modder
                            
                print(currentMOD)
                item = currentMOD
                window['pick_modder'].update(item)
                
                title_list = [i["name"] for i in moddersAndModsJSON[item]]
                p=-1
                for title in title_list:
                    p=p+1
          
                    if title == values['-LIST-'][0]:
                        print("MATCH")
                        indexOfMod = p
     
                window['pick_mod'].update(value=title_list[indexOfMod], values=title_list)
                handleModSelected()
                window2.close()
                #sg.popup('Selected ', values['-LIST-'], keep_on_top=True,icon = iconfile)


            
        else:
            # display original unfiltered list
            window2['-LIST-'].update(names)
            # if a list item is chosen
            print(len(values['-LIST-']))
            if event == '-LIST-':
                print(values['-LIST-'][0])
                print("was CLICKED!")
                currentMOD = "unkown"
                for modder in moddersAndModsJSON.keys():
                        for mod in moddersAndModsJSON[modder]:
                            print(mod["name"])
                            print(values['-LIST-'][0])
                            if mod["name"].lower() == values['-LIST-'][0].lower():
                                print("MATCH")
                                currentMOD = modder
                print(currentMOD)
                item = currentMOD
                window['pick_modder'].update(item)
                
                title_list = [i["name"] for i in moddersAndModsJSON[item]]
                p=-1
                for title in title_list:
                    p=p+1
          
                    if title == values['-LIST-'][0]:
                        print("MATCH")
                        indexOfMod = p
     
                window['pick_mod'].update(value=title_list[indexOfMod], values=title_list)
                handleModSelected()
                window2.close()
                #sg.popup('Selected ', values['-LIST-'], keep_on_top=True,icon = iconfile)

    window2.close()


bootupcount = 0
# Run the Event Loop
if bootupcount == 0:
    bootup()
while True:
    event, values = window.read()

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    
    # Folder name was filled in, make a list of files in the folder
    if event == "InstalledModListBox" and not window["InstalledModListBox"].get() == ['No Mods Installed']:
        [tmpModderSelected, tmpModSelected] = handleInstalledModSelected()

        if not tmpModderSelected:
            sg.Popup('Installed mod not found in available mods!', keep_on_top=True, icon = iconfile)
            window['-SELECTEDMOD-'].update(tmpModSelected)
            window['-SELECTEDMODDESC-'].update("<No description available>")
            window['-SELECTEDMODURL-'].update("")
            local_img = launcherUtils.local_mod_image(tmpModSelected)
            if local_img:
                window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(local_img ,resize=(250,250)))
            else:
                window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(250,250)))
        else:
            window['pick_modder'].update(tmpModderSelected)
            title_list = [i["name"] for i in moddersAndModsJSON[tmpModderSelected]]
            window['pick_mod'].update(value=tmpModSelected, values=title_list)
            
            handleModSelected()
    elif event == "Refresh":
        refreshInstalledList()
        if (len(window['InstalledModListBox'].get())) == 0:
            bootup()
    elif event =='pick_modder':
        window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(1,1)))
        item = values[event]
        print("\nChaning to this modder")
        print(item)
        print("Done!")
        title_list = [i["name"] for i in moddersAndModsJSON[item]]
        window['pick_mod'].update(value=title_list[0], values=title_list)
        handleModSelected()
    elif event =='pick_mod':
        handleModSelected()

    elif event == 'mod_search':
        open_search()
        
    elif event == "Launch!":
        tmpModSelected = window['-SELECTEDMOD-'].get()
        tmpModURL = window['-SELECTEDMODURL-'].get()

        if tmpModURL:
            # online launch
            window['Launch!'].update(disabled=True)
            window['Launch!'].update('Updating...')
            [linkType, tmpModURL] = githubUtils.identifyLinkType(tmpModURL)
            launcherUtils.launch(tmpModURL, tmpModSelected, linkType)
            #turn the button back on
            window['Launch!'].update('Launch!')
            window['Launch!'].update(disabled=False)
            #may have installed new mod, update list
            refreshInstalledList()
        elif tmpModSelected:
            # local launch
            window['Launch!'].update(disabled=True)
            err = launcherUtils.launch_local(tmpModSelected)
            if err:
                sg.popup("Error: " + err, icon = iconfile)
            #turn the button back on
            window['Launch!'].update(disabled=False)
        else:
            bootup()
            sg.Popup('No mod selected', keep_on_top=True, icon = iconfile)
    elif event == "ViewFolder_1":
        tmpModSelected = window['-SELECTEDMOD-'].get()
        tmpModURL = window['-SELECTEDMODURL-'].get()
        subfolders = [ f.name for f in os.scandir(os.getenv('APPDATA') + "\\OpenGOAL-Mods") if f.is_dir() ]
        if subfolders == []:
            subfolders = ["No Mods Installed"]
            
        if tmpModSelected and not tmpModSelected == "No Mods Installed" and tmpModSelected in subfolders:
            print(tmpModSelected)
            dir = os.getenv('APPDATA') + "\\OpenGOAL-Mods\\" + tmpModSelected
            launcherUtils.openFolder(dir)
        else:
            if (len(window['InstalledModListBox'].get())) == 0:
                bootup()
            sg.Popup('No installed mod selected', keep_on_top=True,icon = iconfile)
    elif event == "Reinstall_1":
        tmpModSelected = window['-SELECTEDMOD-'].get()
        tmpModURL = window['-SELECTEDMODURL-'].get()
        subfolders = [ f.name for f in os.scandir(os.getenv('APPDATA') + "\\OpenGOAL-Mods") if f.is_dir() ]
        if subfolders == []:
            subfolders = ["No Mods Installed"]
            
        if tmpModSelected and not tmpModSelected == "No Mods Installed" and tmpModSelected in subfolders:
            print(tmpModSelected)
            dir = os.getenv('APPDATA') + "\\OpenGOAL-Mods\\" + tmpModSelected
            ans = sg.popup_ok_cancel('Confirm: reinstalling ' + dir + " \n\nNote: this will re-extract texture_replacements too",icon = iconfile)
            if ans == 'OK':
                launcherUtils.reinstall(tmpModSelected)
                refreshInstalledList()
                if (len(window['InstalledModListBox'].get())) == 0:
                    bootup()
        else:
            if (len(window['InstalledModListBox'].get())) == 0:
                bootup()
            sg.Popup('No installed mod selected', keep_on_top=True,icon = iconfile)
    elif event == "Uninstall" or event =="Uninstall_1":
        tmpModSelected = window['-SELECTEDMOD-'].get()
        tmpModURL = window['-SELECTEDMODURL-'].get()
        subfolders = [ f.name for f in os.scandir(os.getenv('APPDATA') + "\\OpenGOAL-Mods") if f.is_dir() ]
        if subfolders == []:
            subfolders = ["No Mods Installed"]
            
        if tmpModSelected and not tmpModSelected == "No Mods Installed" and tmpModSelected in subfolders:
            print(tmpModSelected)
            dir = os.getenv('APPDATA') + "\\OpenGOAL-Mods\\" + tmpModSelected
            ans = sg.popup_ok_cancel('Confirm: uninstalling ' + dir ,icon = iconfile)
            if ans == 'OK':
                launcherUtils.try_remove_dir(dir)
                refreshInstalledList()
                if (len(window['InstalledModListBox'].get())) == 0:
                    bootup()
                window['-SELECTEDMOD-'].update("")
                window['-SELECTEDMODDESC-'].update("")
                window['-SELECTEDMODURL-'].update("")
                window['-SELECTEDMODIMAGE-'].update(githubUtils.resize_image(noimagefile ,resize=(1,1)))
                sg.popup('Uninstalled ' + tmpModSelected,icon = iconfile)
                if (len(window['InstalledModListBox'].get())) == 0:
                    bootup()
        else:
            if (len(window['InstalledModListBox'].get())) == 0:
                bootup()
            sg.Popup('No installed mod selected', keep_on_top=True,icon = iconfile)
    elif event == "-GITHUB-_1":
        window = window.refresh()
        url = window['-SELECTEDMODURL-'].get()
        if url:
            webbrowser.open(url)
    elif event == "AddToSteam":
        print("STEAM BUTTON HIT")
        if exists(r"C:\Program Files (x86)\Steam"):
            steamDIR = r"C:\Program Files (x86)\Steam"
            print("FOUND STEAM DIR")
        else:
            print("trying to find it")
            steamDIR = open_steamPrompt()
            
        if exists(steamDIR + "\steamapps\common\Play With Gilbert"):
            print("FOUND GILBERT")
            if sg.PopupYesNo('Do you want to replace Play With Gilbert with the unoffical Mod Launcher?') == "Yes":
                print("Preparing to replace Gilbert")
                launcherUtils.try_remove_file(steamDIR + "\steamapps\common\Play With Gilbert\PlayWithGilbert.exe")
                autoUpdaterURL = "https://github.com/OpenGOAL-Unofficial-Mods/OpenGOAL-Unofficial-Mods.github.io/raw/main/Launcher%20with%20autoupdater.exe"
                print("Downloading update from " + autoUpdaterURL)
                file = urllib.request.urlopen(autoUpdaterURL)
                print()
                print(str("File size is ") + str(file.length))
                urllib.request.urlretrieve(autoUpdaterURL, "PlaywithGilbert.exe", launcherUtils.show_progress)
                print("Done downloading")
                print("moving to steam")
                shutil.move("PlaywithGilbert.exe", steamDIR + "\steamapps\common\Play With Gilbert\\")
                if sg.PopupYesNo('Do you ever want to play the real Play with Gilbert') == "Yes":
                    sg.Popup("Ok we will leave the Play with Gilbert files")
                else:
                    sg.Popup("Ok removing the play with gilbert game files to save space. ( :( )")
                    launcherUtils.try_remove_dir(steamDIR + "\steamapps\common\Play With Gilbert\Engine")
                    launcherUtils.try_remove_dir(steamDIR + "\steamapps\common\Play With Gilbert\PWG_2020")
                sg.Popup("Mod Launcher added to steam, launch by playing \"Play with Gilbert\" in Steam.")
            else:
                sg.Popup("Understandable")
            
        else:
            sg.Popup("Did not find play with gilbert please download from " + "https://store.steampowered.com/app/1359630/Play_With_Gilbert__A_Small_Tail" , keep_on_top=True,icon = iconfile)
       

window.close()