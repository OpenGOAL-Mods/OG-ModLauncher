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
from enum import Enum

class LinkTypes(Enum):
    BRANCH = 1
    RELEASE = 2

def identifyLinkType(link_path): #image_path: "C:User/Image/img.jpg"
    if '/tree/' in link_path:
        print("branch detected")
        return [LinkTypes.BRANCH, link_path]
    elif '/releases' in link_path:
        print("release detected")
        return [LinkTypes.RELEASE, releaseToApiURL(link_path)]
    #else:
    print("nothing detected, assuming its main github page")
    print("changing it to branch main and recalling")
    return [LinkTypes.BRANCH, homepageToMainBranchURL(link_path) ]
    
        
def homepageToMainBranchURL(URL):
    # adding leading / is safe even if URL already ends in /
    URL = URL + "/tree/main"
    print(URL)
    return URL
    
    
def returnModImageURL (URL):
    [linkType, URL] = identifyLinkType(URL)
    if linkType == LinkTypes.BRANCH:
        print("image url branch detected method starting")
        return str(URL).replace('https://github.com/','https://raw.githubusercontent.com/').replace('/tree/','/') + '/ModImage.png'
    elif linkType == LinkTypes.RELEASE:
        return str(URL).replace('https://github.com/','https://raw.githubusercontent.com/').replace('https://api.github.com/repos/','https://raw.githubusercontent.com/').replace('/releases','/main') + '/ModImage.png'

def releaseToApiURL(URL):
    return str(URL).replace('https://github.com/','https://api.github.com/repos/')

def branchToApiURL(URL):
    return str(URL).replace('https://github.com/','https://api.github.com/repos/').replace('/tree/','/branches/')

def branchToArchiveURL(URL):
    return str(URL).replace('/tree/','/archive/') + ".zip"
    
    
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