import os
import cv2
import shutil
from multiprocessing import Pool
import argparse

pic_suffix = set()
pic_suffix.update(['.BMP', '.DIB', '.JPEG', '.JPG', '.JPE', '.PNG', '.PBM', '.PGM', '.PPM', '.SR', '.RAS', '.TIFF', '.TIF', '.EXR', '.JP2'])

def image_judge(image_path):
    try:
        new_path = os.path.join('./trash', os.path.split(image_path)[-1])
        # not image
        if os.path.splitext(image_path)[-1].upper() not in pic_suffix:
            print ('Not image %s' % (new_path))
            shutil.move(image_path, './trash')
            return
        
        # image is none
        image = cv2.imread(image_path)
        if image is None:
            print ('Image none: %s' % (new_path))
            shutil.move(image_path, './trash')
            return
    except:
        # catch except                                            
        print ('Image error: %s' % (new_path))
        shutil.move(image_path, './trash')
        return

def entry_function(folder):
    os.makedirs('./trash', exist_ok=True)
    pic_list = []
    pics = os.listdir(folder)
    for pic in pics:
        pic_list.append(os.path.join(folder, pic))
    pool = Pool()
    pool.map(image_judge, pic_list)
    pool.close()
    pool.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type = str, required = True, help = 'path to folder which contains the images')
    args = parser.parse_args()

    entry_function(args.folder)