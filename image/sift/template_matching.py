import numpy as np
import cv2
from image.sift.sift import SIFT
from matplotlib import pyplot as plt
import yaml
import os

def extract_keypoints(img,param_dict):
    img_sift = SIFT(img, param_dict)
    kp, des = img_sift.compute()
    return kp,des

def match_des(des1,des2):
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1, des2, k=2)

    good = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)
    return good

def plot_template_matches(good,kp,imgs):
    kp1,kp2=kp
    img1, img2=imgs
    # Estimate homography between template and scene
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

    M = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)[0]

    # Draw detected template in scene image
    h, w = img1.shape
    pts = np.float32([[0, 0],
                      [0, h - 1],
                      [w - 1, h - 1],
                      [w - 1, 0]]).reshape(-1, 1, 2)
    dst = cv2.perspectiveTransform(pts, M)

    img2 = cv2.polylines(img2, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)

    h1, w1 = img1.shape
    h2, w2 = img2.shape
    nWidth = w1 + w2
    nHeight = max(h1, h2)
    hdif = int((h2 - h1) / 2)
    newimg = np.zeros((nHeight, nWidth, 3), np.uint8)

    for i in range(3):
        newimg[hdif:hdif + h1, :w1, i] = img1
        newimg[:h2, w1:w1 + w2, i] = img2

    # Draw SIFT keypoint matches
    for m in good:
        pt1 = (int(kp1[m.queryIdx].pt[0]), int(kp1[m.queryIdx].pt[1] + hdif))
        pt2 = (int(kp2[m.trainIdx].pt[0] + w1), int(kp2[m.trainIdx].pt[1]))
        cv2.line(newimg, pt1, pt2, (255, 0, 0))

    plt.imshow(newimg)
    plt.show()

def kp_from_file(fin):
    points=[]
    kp_info=yaml.load(fin)
    for info in kp_info:
        keypoint = cv2.KeyPoint()
        keypoint.pt = info['pt']
        keypoint.octave = info['octave']
        keypoint.size =info['size']
        keypoint.response = info['response']
        points.append(keypoint)
    return points

def kp_to_file(kp,stream):
    points=[]
    for point in kp:
        points.append(
            {
                'pt':point.pt,
                'octave':point.octave,
                'size':point.size,
                'response':point.response,
            }
        )
    yaml.dump(points,stream)

def save_kp_n_des(kp,des,name,dir):
    os.makedirs(dir,exist_ok=True)
    np.save(f'{dir}/{name}.npy', des)
    with open(f'{dir}/{name}.yaml','w') as fout:
        kp_to_file(kp,fout)

def load_kp_n_des(name,dir):
    des=np.load(f'{dir}/{name}.npy')
    with open(f'{dir}/{name}.yaml','r') as fin:
        kp=kp_from_file(fin)
    return kp,des

if __name__=='__main__':
    img1=cv2.imread('tshirt.bmp', 0)
    img2=cv2.imread('tshirt_in_scene.bmp', 0)
    param_dict={
        'sigma':1.6,
        'assumed_blur':0.5,
        'num_intervals':3,
        'image_border_width':5,
        'contrast_threshold':0.04,
    }
    # kp1,des1=extract_keypoints(img1,param_dict)
    # save_kp_n_des(kp1,des1,'tshirt','tshirt') # save template to file
    kp1,des1=load_kp_n_des('tshirt','tshirt') # read template from file. For speedup.

    kp2,des2=extract_keypoints(img2,param_dict)
    matches=match_des(des1,des2)
    print(matches)
    plot_template_matches(matches,(kp1,kp2),(img1,img2))
