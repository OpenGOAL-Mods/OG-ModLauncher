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
    if tree in link_path:
        branch = 1
        return
    else:
        if releases in link_path:
            release = 1
            return
        else:
             mainpage = 1
             return
         
            
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