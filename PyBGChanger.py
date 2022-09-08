import os
from threading import Thread

import PySimpleGUI as sg
import cv2
import pyvirtualcam
from cvzone.SelfiSegmentationModule import SelfiSegmentation
from pyvirtualcam import PixelFormat

segmentor = SelfiSegmentation()

vc = cv2.VideoCapture(0)

if not vc.isOpened():
    raise RuntimeError('Could not open video source')

pref_width = 1280
pref_height = 720
pref_fps = 30
vc.set(cv2.CAP_PROP_FRAME_WIDTH, pref_width)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, pref_height)
vc.set(cv2.CAP_PROP_FPS, pref_fps)

width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = vc.get(cv2.CAP_PROP_FPS)

count = [0]


def task(indexImage, isActive):
    while True:
        event, values = window.read()
        if event == "Next BG":
            indexImage[0] += 1
            if indexImage[0] >= count[0]:
                indexImage[0] = 0
        if event == "Pre BG":
            indexImage[0] -= 1
            if indexImage[0] < 0:
                indexImage[0] = count[0] - 1
        if event == sg.WIN_CLOSED or event == "End":
            break
    isActive[0] = False
    window.close()


with pyvirtualcam.Camera(width, height, fps, fmt=PixelFormat.BGR) as cam:
    cam_name = f'Virtual camera device: {cam.device}'
    print('Virtual camera device: ' + cam.device)
    listImg = os.listdir("BG Images")
    imgList = []
    count[0] = len(listImg)
    for imgPath in listImg:
        img = cv2.imread(f'BG Images/{imgPath}')
        imgList.append(img)

    indexImg = [0]
    layout = [[sg.Text("Py BG Changer - By Matin Ghanbari", background_color='black', text_color='gold',
                       size=(36, 1), justification='center')],
              [sg.Text(cam_name, background_color='black', text_color='gold',
                       key='fps', size=(36, 1), justification='center')],
              [sg.Button("Pre BG", button_color='orange', size=(12, 1)),
               sg.Button("Next BG", button_color='green', size=(12, 1)),
               sg.Button("End", button_color='red', size=(6, 1))]]
    window = sg.Window("Py BG Changer", layout=layout, margins=(50, 10), icon=r'icon.ico',
                       font=['Bahnschrift SemiLight', 10], button_color='black', background_color='black',
                       auto_size_buttons=True, auto_size_text=True, titlebar_background_color='black',
                       no_titlebar=False, titlebar_icon=r'icon.ico')
    isActive = [True]
    thread = Thread(target=task, args=(indexImg, isActive,), name='Thread#1').start()
    while isActive[0]:
        _, frame = vc.read()

        imgOut = segmentor.removeBG(frame, imgList[indexImg[0]], threshold=0.7)
        imgOut = cv2.flip(imgOut, 1)
        cam.send(imgOut)
        cam.sleep_until_next_frame()
