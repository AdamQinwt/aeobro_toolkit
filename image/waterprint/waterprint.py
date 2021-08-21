import cv2
import numpy as np
import argparse
import matplotlib.pyplot as plt
from copy import deepcopy
import os
from tqdm import tqdm
from .average import AverageMeter

def add_wp(a,b,wa,color_flag):
    l=len(a)
    c=deepcopy(a)
    wb=1-wa
    b=(255,255,255) if color_flag else b
    for i in range(l):
        c[i]=a[i]*wa+b[i]*wb
    return c

def add_waterprint(orig,wp,size=.1,position=(.98,.98),brightness_threshold=127,p=.5):
    '''
    Add a waterprint to a picture.
    Color automatically adjusted according to the color in the target area.
    :param orig: Original picture.
    :param wp: waterprint picture.
    :param size: Signature size.(recommended: 0.1)
    :param position: Position of the right-bottom corner. E.g., (0.9,0.88) means the right-bottom corner is at (0.9*height,0.88*width). (recommended: (0.98,0.98))
    :param brightness_threshold: Brightness threshold. If the average brightness(avg(r,g,b)) is smaller, a pure white waterprint is used instead of the original color. threshold<0(>255) means never(always) using the alternative color..
    :param p: How much the original picture is used. 0(purely from waterprint)-1(purely from original image)
    :return: output image
    '''

    # get position
    h,w,c=orig.shape
    ph,pw,cw=wp.shape
    hw=int(h*size) #waterprint size depends on heig# ht
    ww=int(hw*pw/ph)
    strideH,strideW=ph//hw,pw//ww
    strideH+=1
    strideW+=1
    right=int(w*position[1])
    left = right - ww
    bottom=int(h*position[0])
    top=bottom-hw
    i0=0

    # Get average brightness of the area.
    if brightness_threshold<0:
        color_flag=False
    elif brightness_threshold>255:
        color_flag=True
    else:
        avg=AverageMeter()
        for i in range(top,bottom):
            for j in range(left,right):
                x=sum(orig[i][j])/3
                avg.update(x)
        color_flag=avg.avg<brightness_threshold

    for i in range(top,bottom):
        j0=0
        for j in range(left,right):
            if wp[i0][j0][0]!=255 or wp[i0][j0][1]!=255 or wp[i0][j0][2]!=255:
                orig[i][j]=add_wp(orig[i][j],wp[i0][j0],p,color_flag)
            j0+=strideW
            if j0>=pw:
                break
        i0 += strideH
        if i0 >= ph:
            break
    return orig

def waterprint(waterprint,name,newname,*args,**kwargs):
    '''
    Add a waterprint to a picture.
    :param waterprint: waterprint filename.
    :param name: Source image name.
    :param newname: Output image name.
    :param args: Extra arguments may include: size, position, brightness_threshold, p
    :param kwargs: Extra arguments may include: size, position, brightness_threshold, p
    :return: Output image
    '''
    wp = cv2.imread(waterprint)
    img=add_waterprint(cv2.imread(name),wp,*args,**kwargs)
    cv2.imwrite(newname,img)
    return img

def walk_and_waterprint(waterprint,dir,newdir,*args,**kwargs):
    '''
    Add a waterprint to all pictures in the directory..
    :param waterprint: waterprint filename.
    :param dir: Source directory name.
    :param newdir: Output directory name.
    :param args: Extra arguments may include: size, position, brightness_threshold, p
    :param kwargs: Extra arguments may include: size, position, brightness_threshold, p
    :return: None
    '''
    r=dir
    wp = read_waterprint(waterprint)
    for root,dirs,files in os.walk(r):
        f=tqdm(files)
        for img in f:
            if not img.lower().endswith('.jpg'): continue
            in_path=os.path.join(dir,img)
            out_path=os.path.join(newdir,img)
            img = add_waterprint(cv2.imread(in_path), wp,*args,**kwargs)
            cv2.imwrite(out_path, img)