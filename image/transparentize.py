import cv2
import numpy as np
import PIL.Image as im

def transparentize(in_name,out_name,a,is_background=None):
    '''
    make a picture transparent
    :param in_name: name of the source picture
    :param out_name: name of the target picture
    :param a: alpha.0(totally transparent)-1(non-transparent)
    :param is_background: * a function to tell whether a pixel is background(with pixel as input) E.g. IsColor can be used to create a family of such functions.
    :return:
    '''
    pic=cv2.imread(in_name,cv2.IMREAD_UNCHANGED)
    h,w,c=pic.shape
    alpha_value=int(a*255)
    tr=np.ones([h,w,1])*alpha_value
    if is_background:
        for i in range(h):
            for j in range(w):
                if is_background(pic[i,j]):
                    tr[i,j]=0
    pic=np.concatenate([pic,tr],-1)
    cv2.imwrite(out_name,pic)

class IsColor:
    def __init__(self,color):
        self.c=color
    def __call__(self, pix):
        for i,c in enumerate(self.c):
            if c!=pix[i]:
                return False
        return True