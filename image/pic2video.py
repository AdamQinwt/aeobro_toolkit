import os
import cv2

def convert(file_list,save_path,fmt,img_size,fps=12):
    '''
    Connect a series of pictures to a video.
    :param file_list: A list of picture file names.
    :param save_path: Video path
    :param fmt: format. 'mp4' now supported.
    :param img_size: image size.
    :param fps: frame/s
    :return: None
    '''
    if fmt=='mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    elif fmt=='avi':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    else:
        raise ValueError
    video_writer = cv2.VideoWriter(save_path, fourcc, fps, img_size)
    for file_name in file_list:
        try:
            img = cv2.imread(file_name)
            video_writer.write(img)
        except:
            print(f'Unable to load {file_name}!')
            break

    video_writer.release()