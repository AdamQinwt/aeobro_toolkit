import numpy as np
from random import randint
from nntrainer.trainer.max_min_stat import MinRecord
import cv2
from skimage.measure import marching_cubes_classic,marching_cubes_lewiner

def euclidean(a,b):
    '''Distance'''
    return ((a[0]-b[0])**2)+((a[1]-b[1])**2)

def area2mesh2(area):
    '''
    convert an area to mesh with marching cubes
    :param area: 2D(h*w) array of foreground/background flags. 0 for background and non-0 for foreground
    :return: (vertex,face) that make a mesh which looks like the area.
    '''
    zero=np.zeros(area.shape)
    area=np.array(np.stack([zero]+[area]+[zero],0),dtype=np.float)
    res = marching_cubes_classic(area,.1,spacing=(.01,.01,.01))
    return res

def enumerable2string(enu,split=' '):
    '''
    conver something enumerable(list,tuple,1D-array,...) to string
    :param enu: something enumerable(list,tuple,1D-array,...)
    :param split: splitting symbol. ' ' as default.
    :return: string
    '''
    if enu is None: return ''
    l=len(enu)
    if l==0: return ''
    if l==1: return str(l)
    s=str(enu[0])
    for itm in enu[1:]:
        s+=f'{split}{itm}'
    return s

def writemesh(mesh,fname):
    '''
    Wrte a Mesh to an obj file
    :param mesh: dictionary like {'v': (vertex list),'f': (face list)}. line heads are determined by the key.
    :param fname: object file name
    '''
    with open(fname,'w') as fout:
        for kmain,vmain in mesh.items():
            for itm in vmain:
                fout.write(f'{enumerable2string(itm)}\n')

def gen_area(filename,func_isforeground):
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)<254
    up=scan_up(gray)
    down=scan_down(gray)
    left=scan_left(gray)
    right=scan_right(gray)
    e=up*down*left*right
    return e

def scan_up(a):
    h,w=a.shape
    r=np.zeros([h,w],dtype=np.float32)
    flags=np.zeros([w],dtype=np.bool)
    for y in range(h):
        flags[a[y]]=True
        r[y,flags]=1
    return r

def scan_down(a):
    h,w=a.shape
    r=np.zeros([h,w],dtype=np.float32)
    flags=np.zeros([w],dtype=np.bool)
    for y in range(h-1,-1,-1):
        flags[a[y]]=True
        r[y,flags]=1
    return r

def scan_left(a):
    h,w=a.shape
    r=np.zeros([h,w],dtype=np.float32)
    flags=np.zeros([h],dtype=np.bool)
    for x in range(w):
        flags[a[:,x]]=True
        r[flags,x]=1
    return r

def scan_right(a):
    h,w=a.shape
    r=np.zeros([h,w],dtype=np.float32)
    flags=np.zeros([h],dtype=np.bool)
    for x in range(w-1,-1,-1):
        flags[a[:,x]]=True
        r[flags,x]=1
    return r

if __name__=='__main__':
    area=gen_area('t6.bmp')
    res=area2mesh2(area)
    print(res)
    v,f=res
    writemesh({'v':-v,'f':f+1},'front.obj')