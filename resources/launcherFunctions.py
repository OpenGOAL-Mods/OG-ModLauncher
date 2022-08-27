# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 18:13:55 2022

@author: Zed
"""
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


def link_type(link_path): #image_path: "C:User/Image/img.jpg"
    if '/tree/' in link_path:
        print("branch detected")
        branch = 1
        return 1
    else:
        if '/releases' in link_path:
            print("release detected")
            release = 1
            return 2
        else:
            print("nothing detected, assuming its main github page")
            link_path = link_path + "tree/main"
            print("changing it to branch main and recalling")
            link_type(link_path)

            
            mainpage = 1
            return 3
        
def installedlist(PATH):
    print(PATH)
    scanDir = PATH
    directories = [d for d in os.listdir(scanDir) if os.path.isdir(os.path.join(os.path.abspath(scanDir), d))]
    print(directories)
    for i in directories:
        print(i)
    print(os.path.dirname(os.path.dirname(PATH)))
    
        
def homepageToMainBranchURL(URL):
    if link_type(URL) == 3:
        URL = URL + "tree/main"
        print(URL)
        return URL
    
    
def returnModImageURL (URL):
    if link_type(URL) == 1:
        print("image url branch detected method starting")
        URL = str(URL).replace('https://github.com/','https://raw.githubusercontent.com/').replace('tree/','') + '/ModImage.png'
        return URL
    
    
    
    
    
def resize_image(image_path, resize=None): #image_path: "C:User/Image/img.jpg"
    if isinstance(image_path, str):
        img = PIL.Image.open(image_path)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(image_path)))
        except Exception as e:
            data_bytes_io = io.BytesIO(image_path)
            img = PIL.Image.open(data_bytes_io)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.Resampling.LANCZOS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()