import cv2
import os
import argparse
import shutil

pic_suffix = set()
pic_suffix.update(['.BMP', '.DIB', '.JPEG', '.JPG', '.JPE', '.PNG', '.PBM', '.PGM', '.PPM', '.SR', '.RAS', '.TIFF', '.TIF', '.EXR', '.JP2'])

def phash(image):
    # image to 32*32 & rgb to gray
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = cv2.resize(img, (32, 32), interpolation=cv2.INTER_CUBIC)

    # int to float32
    img = img.astype('float32')

    # dct
    vis = cv2.dct(cv2.dct(img))
    # left up corner 8 * 8
    vis = vis[0:8, 0:8]

    # two dimension to one
    img_list = []
    for i in vis:
        img_list.extend(i)
    
    # calculate mean
    avg = sum(img_list) * 1. / len(img_list)
    avg_list = ['0' if i < avg else '1' for i in img_list]

    # get hash
    # return ''.join(['%x' % int(''.join(avg_list[x:x + 4]), 2) for x in range(0, 8 * 8, 4)])
    return ''.join(str(i) for i in avg_list)

def hamming_distance(s0, s1):
    if len(s0) != len(s1):
        raise ValueError("Length must be the same!")
    return sum(el1 != el2 for el1, el2 in zip(s0, s1))

def get_hash_bucket(folder):
    hash_bucket = {}

    pics = os.listdir(folder)
    for pic in pics:
        image_path = os.path.join(folder, pic)
        try:
            # not image
            if os.path.splitext(image_path)[-1].upper() not in pic_suffix:
                print ('Not image %s' % (image_path))
                continue
            
            # image is none
            image = cv2.imread(image_path)
            if image is None:
                print ('Image none: %s' % (image_path))
                continue
        except:
            # catch except
            print ('Image read except %s' % (image_path))
        else:
            # split into 4 bucket
            hash_result = phash(image)
            bucket0 = hash_result[0:16]
            bucket1 = hash_result[16:32]
            bucket2 = hash_result[32:48]
            bucket3 = hash_result[48:64]

            # +'_0' is uses to compare the same location
            # eg: 123 456 789 and 789 123 456 should be different
            if bucket0+'_0' in hash_bucket:
                hash_bucket[bucket0+'_0'].append([hash_result, image_path])
            else:
                hash_bucket[bucket0+'_0'] = [[hash_result, image_path]]

            if bucket1+'_1' in hash_bucket:
                hash_bucket[bucket1+'_1'].append([hash_result, image_path])
            else:
                hash_bucket[bucket1+'_1'] = [[hash_result, image_path]]

            if bucket2+'_2' in hash_bucket:
                hash_bucket[bucket2+'_2'].append([hash_result, image_path])
            else:
                hash_bucket[bucket2+'_2'] = [[hash_result, image_path]]

            if bucket3+'_3' in hash_bucket:
                hash_bucket[bucket3+'_3'].append([hash_result, image_path])
            else:
                hash_bucket[bucket3+'_3'] = [[hash_result, image_path]]

    return hash_bucket

def image_deduplication(hash_bucket):
    os.makedirs('./trash', exist_ok=True)
    compared_bucket = set()
    for key in hash_bucket:
        array_2d = hash_bucket[key]
        for index_i, i in enumerate(array_2d):
            for index_j, j in enumerate(array_2d):

                # get the image_path pair to avoid comparing again
                if i[1] <= j[1]:
                    pair = (i[1], j[1])
                else:
                    pair = (j[1], i[1])

                if index_j <= index_i or pair in compared_bucket:
                    continue
                
                # remove the last one and record the compared pair
                if hamming_distance(i[0], j[0]) < 4:
                    shutil.move(j[1], './trash')
                    compared_bucket.add(pair)
                    print (i[1] + ' --> ' + os.path.join('./trash', os.path.split(j[1])[-1]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type = str, required = True, help = 'path to folder which contains the images')
    args = parser.parse_args()

    hash_bucket = get_hash_bucket(args.folder)
    image_deduplication(hash_bucket)