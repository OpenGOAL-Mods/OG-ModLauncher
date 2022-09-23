# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 18:13:55 2022

@author: Zed
"""

import PIL.Image
import io
import base64
from enum import Enum
import json
import requests
import datetime

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
        #print("image url branch detected method starting")
        #print(str(URL).replace('https://github.com/','https://raw.githubusercontent.com/').replace('/tree/','/') + '/ModImage.png')
        return str(URL).replace('https://github.com/','https://raw.githubusercontent.com/').replace('/tree/','/') + '/ModImage.png'
    elif linkType == LinkTypes.RELEASE:
        print("Printing URL")

        apiURL = str(URL).replace('https://github.com/','https://raw.githubusercontent.com/').replace('/releases','')
        launchUrl = apiURL
        r = json.loads(json.dumps(requests.get(url = launchUrl, params = {'address':"yolo"}).json()))
        defaultBranch = r.get("default_branch")
        

        imageURL = apiURL.replace('https://api.github.com/', 'https://raw.githubusercontent.com/').replace("repos/", "") + "/" + defaultBranch + "/" + "ModImage.png"
        
       
       # LatestRelAssetsURL = (json.loads(json.dumps(requests.get(url = r[0].get("assets_url"), params = {'address':"yolo"}).json())))[0].get("browser_download_url")
        
        
        return imageURL
    
def returnDefaultBranch (URL):
    [linkType, URL] = identifyLinkType(URL)
    if linkType == LinkTypes.RELEASE:
        print("Printing URL")
        print(str(URL))
        apiURL = str(URL).replace('https://github.com/','https://raw.githubusercontent.com/').replace('/releases','')
        print(str(apiURL))
        
        
        launchUrl = apiURL
        r = json.loads(json.dumps(requests.get(url = launchUrl, params = {'address':"yolo"}).json()))
        defaultBranch = r.get("default_branch")
        

        imageURL = apiURL.replace('https://api.github.com/', 'https://raw.githubusercontent.com/').replace("repos/", "") + "/" + defaultBranch + "/" + "ModImage.png"
    
       
       # LatestRelAssetsURL = (json.loads(json.dumps(requests.get(url = r[0].get("assets_url"), params = {'address':"yolo"}).json())))[0].get("browser_download_url")
        
        
        return imageURL

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
  
    while cur_width == 400:
        print("Too wide fixing it.")
        img = img.resize((int(cur_width*0.95), int(cur_height*0.95)), PIL.Image.Resampling.LANCZOS)
        cur_width, cur_height = img.size
        print(img.size)
    while cur_height == 250:
        print("Too high fixing it.")
        img = img.resize((int(cur_width*0.95), int(cur_height*0.95)), PIL.Image.Resampling.LANCZOS)
        cur_width, cur_height = img.size
        print(img.size)

    img= img.resize(((426, 240)),PIL.Image.Resampling.LANCZOS)

    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()