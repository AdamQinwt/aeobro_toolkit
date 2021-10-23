import numpy as np
import cv2
from skimage.measure import marching_cubes_classic,marching_cubes_lewiner

def euclidean(a,b):
    '''Distance'''
    return ((a[0]-b[0])**2)+((a[1]-b[1])**2)

def area2mesh2_classic(area,*args,**kwargs):
    '''
    convert an area to mesh with marching cubes with classic
    DEPRECATED!!
    area2mesh_postprocess strongly recommended!!!
    :param area: 2D(h*w) array of foreground/background flags. 0 for background and non-0 for foreground
    :param args: Extra arguments may include level, spacing, gradient_direction
    :param kwargs: Extra arguments may include level, spacing, gradient_direction
    :return: (vertex,face) that make a mesh which looks like the area.
    '''
    zero=np.zeros(area.shape)
    area=np.array(np.stack([zero,area,zero],0),dtype=np.float)
    res = marching_cubes_classic(area,*args,**kwargs)
    return res

def area2mesh2(area,*args,**kwargs):
    '''
    convert an area to mesh with marching cubes
    area2mesh_postprocess strongly recommended!!!
    :param area: 2D(h*w) array of foreground/background flags. 0 for background and non-0 for foreground
    :param args: Extra arguments may include level, spacing, gradient_direction, step_size, allow_degenerate
    :param kwargs: Extra arguments may include level, spacing, gradient_direction, step_size, allow_degenerate
    :return: (vertex,face,vertex normal,local maximum) that make a mesh which looks like the area.
    '''
    zero=np.zeros(area.shape)
    area=np.array(np.stack([zero,area,zero],0),dtype=np.float)
    res = marching_cubes_lewiner(area,*args,**kwargs)
    return res

def area2mesh_postprocess(res,axis=0,thresh=.01,is_short=False):
    '''
    area2mesh2 outputs a closed mesh, and this function turns into a single plane.
    :param res: a closed mesh made up of vertices and faces(in np arrays)
    :param axis: index of eliminated axis. Could change if you change the axis(in the np.stack line in area2mesh2).
    :param thresh: Threshold of the value on the axis. Only SMALLER ones are reserved.
    :param is_short: whether the res is short(vertices,faces) or not(vertices,faces,normals,local maxima)
    :return: short(vertices,faces) or not(vertices,faces,normals,local maxima) of the processed version
    '''
    if is_short:
        v,f=res
    else:
        v, f, vn, val = res
    mask = v[:, axis] < thresh
    v0 = v[mask]
    if not is_short:
        vn0=vn[mask]
        val0=val[mask]
    v0[:, axis] = 0
    print(f'Points left: {v0.shape}')
    remap_idx = {}
    current_idx = 0
    for i, m in enumerate(mask):
        if m:
            remap_idx[i] = current_idx
            current_idx += 1

    newf = []
    for a, b, c in f:
        flag = mask[a] & mask[b] & mask[c]
        if flag:
            newf.append([remap_idx[a], remap_idx[b], remap_idx[c]])
    f0 = np.array(newf, dtype=np.int)
    return (v0,f0) if is_short else (v0,f0,vn0,val0)

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
                fout.write(f'{kmain} {enumerable2string(itm)}\n')

def gen_area(filename,func_isforeground=lambda x:x<254):
    '''
    Generate an area flag with 4-direction scanning.
    Note that 4-direction scanning may result in inaccurate area estimations in many cases.
    :param filename: source  image file
    :param func_isforeground: A function to tell whether a pixel is foreground. The function should take a number(int/byte/float) as input and output a flag showing whether the pixel belongs to the foreground.
    :return: an array of True/False flags.
    '''
    img = cv2.imread(filename)
    gray = func_isforeground(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
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
    root='E:/data/clothes/'
    name='sleeve_close'
    # sleeve:46.57,front:50.5,back:50.5
    target_length=46.57
    area=gen_area(root+name+'.bmp',lambda x:x>0)
    res=area2mesh2(area)
    v, f, vn, val = res
    x,y,z=v[:,0],v[:,1],v[:,2]
    print(x.max(),x.min())
    print(y.max(),y.min())
    print(z.max(),z.min())
    margin=z.max()-z.min()
    res=area2mesh_postprocess(res,thresh=1)
    v,f,vn,val=res
    v=v/margin*target_length
    writemesh({'v':v,'vn':vn,'f':f+1},root+name+'.obj')
