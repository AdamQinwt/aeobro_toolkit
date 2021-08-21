import cv2
import numpy as np
import argparse

def recolor(c,colors:dict):
    '''
    Recolor a pixxel according to its value. Parameter definitions are described in redraw_pic
    :param c:
    :param colors:
    :return:
    '''
    for color_name,color_detail in colors.items():
        rl=color_detail['range']
        for r in rl:
            mini=r[0]
            maxi=r[1]
            if mini[0]<c[0] and mini[1]<c[1] and mini[2]<c[2] and maxi[0]>c[0] and maxi[1]>c[1] and maxi[2]>c[2]:
                return color_detail['rgb']
    return (255,255,255)

def get_colors(fname=''):
    colors={
        'red':{'range':[((0,16,0),(10,255,255)),((130,16,0),(180,255,255))],'rgb':(255,0,0)},
        #'red':{'range':[((0,128,46),(5,255,255)),((156,128,46),(180,255,255))],'rgb':(255,0,0)},
        #'green':{'range':[((35,128,46),(77,255,255))],'rgb':(0,255,0)},
        #'blue':{'range':[((100,128,46),(124,255,255))],'rgb':(0,0,255)},
        #'yellow':{'range':[((15,128,46),(34,255,255))],'rgb':(255,255,0)},
        #'black':{'range':[((0,0,0),(180,255,10))],'rgb':(0,0,0)},
        'white':{'range':[((0,0,70),(180,30,255))],'rgb':(255,255,255)},
    }
    return colors

def redraw_pic(img,colors):
    '''
    Redraw a picture in a pixel-to-pixel manner.
    Each pixel is converted according to its value and color ranges.
    :param img: Input image.
    :param colors: Color ranges. A dictionary of color name->dictionary('range'->hsv min-max value, 'rgb'->resulting rgb.) Examples are given in get_colors. Note that ranges come in HSV while output values come in RGB.
    :return: Converte image
    '''
    img= cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h,w,c=img.shape
    print(h,w,c)
    for i in range(h):
        for j in range(w):
            img[i][j]=recolor(img[i][j],colors)
    return img

def parse_pic(img_name,tgt):
    '''
    Parse a source picture to a bi-color picture as preparation for waterprint/signature.
    :param img_name: Source picture name
    :param tgt: Target signature name
    :return: None
    '''
    img=redraw_pic(cv2.imread(img_name),get_colors())
    img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    cv2.imwrite(tgt,img)