import os
import argparse
import shutil
import scipy.fftpack
from PIL import Image
import numpy
from tqdm import tqdm

pic_suffix = set()
pic_suffix.update(['.BMP', '.DIB', '.JPEG', '.JPG', '.JPE', '.PNG', '.PBM', '.PGM', '.PPM', '.SR', '.RAS', '.TIFF', '.TIF', '.EXR', '.JP2'])

def _binary_array_to_hex(arr):
	"""
	internal function to make a hex string out of a binary array.
	"""
	bit_string = ''.join(str(b) for b in 1 * arr.flatten())
	width = int(numpy.ceil(len(bit_string)/4))
	return '{:0>{width}x}'.format(int(bit_string, 2), width=width)

def phash(image, hash_size=8, highfreq_factor=4):
    img_size = hash_size * highfreq_factor
    image = image.convert("L").resize((img_size, img_size), Image.ANTIALIAS)
    pixels = numpy.asarray(image)
    dct = scipy.fftpack.dct(scipy.fftpack.dct(pixels, axis=0), axis=1)
    dctlowfreq = dct[:hash_size, :hash_size]
    med = numpy.median(dctlowfreq)
    diff = dctlowfreq > med
    return _binary_array_to_hex(diff.flatten())

def hamming_distance(s0, s1):
    if len(s0) != len(s1):
        raise ValueError("Length must be the same!")
    return sum(el1 != el2 for el1, el2 in zip(s0, s1))

def get_hash_bucket(folder):
    hash_bucket0 = {}
    hash_bucket1 = {}
    hash_bucket2 = {}
    hash_bucket3 = {}
    image_bucket = {}
    pics = os.listdir(folder)
    for pic in tqdm(pics):
        image_path = os.path.join(folder, pic)
        try:
            # not image
            if os.path.splitext(image_path)[-1].upper() not in pic_suffix:
                print ('Not image %s' % (image_path))
                continue
            
            # image is none
            image = Image.open(image_path)
            if image is None:
                print ('Image none: %s' % (image_path))
                continue
        except:
            # catch except
            print ('Image read except %s' % (image_path))
        else:
            # split into 4 bucket
            hash_result = phash(image)
            hash0 = hash_result[0:4]
            hash1 = hash_result[4:8]
            hash2 = hash_result[8:12]
            hash3 = hash_result[12:16]

            if hash0 in hash_bucket0:
                hash_bucket0[hash0].append(image_path)
            else:
                hash_bucket0[hash0] = [image_path]

            if hash1 in hash_bucket1:
                hash_bucket1[hash1].append(image_path)
            else:
                hash_bucket1[hash1] = [image_path]

            if hash2 in hash_bucket2:
                hash_bucket2[hash2].append(image_path)
            else:
                hash_bucket2[hash2] = [image_path]

            if hash3 in hash_bucket3:
                hash_bucket3[hash3].append(image_path)
            else:
                hash_bucket3[hash3] = [image_path]
            
            image_bucket[image_path] = [hash_result, [hash0, hash1, hash2, hash3]]

    return image_bucket, hash_bucket0, hash_bucket1, hash_bucket2, hash_bucket3

def image_deduplication(image_bucket, hash_bucket0, hash_bucket1, hash_bucket2, hash_bucket3):
    os.makedirs('./trash', exist_ok=True)
    compared_bucket = set()
    trash_bucket = set()
    for image_i, hash_set in tqdm(image_bucket.items()):
        # if in trash_bucket, no need to compare
        if image_i in trash_bucket:
            continue

        hash0 = hash_set[1][0]
        hash1 = hash_set[1][1]
        hash2 = hash_set[1][2]
        hash3 = hash_set[1][3]

        sim_list = set()
        if hash0 in hash_bucket0:
            sim_list.update(hash_bucket0[hash0])
        if hash1 in hash_bucket1:
            sim_list.update(hash_bucket1[hash1])
        if hash2 in hash_bucket2:
            sim_list.update(hash_bucket2[hash2])
        if hash3 in hash_bucket3:
            sim_list.update(hash_bucket3[hash3])
        
        # discard itself
        sim_list.discard(image_i)
        for image_j in sim_list:
            # if in trash_bucket, no need to compare
            # after sorted, tuple become list
            if image_j in trash_bucket or tuple(sorted((image_i, image_j))) in compared_bucket: 
                continue

            if hamming_distance(image_bucket[image_i][0], image_bucket[image_j][0]) < 4:
                shutil.move(image_j, './trash')
                trash_bucket.add(image_j)
                print (image_i + ' --> ' + os.path.join('./trash', os.path.split(image_j)[-1]))
            
            compared_bucket.add(tuple(sorted((image_i, image_j))))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type = str, required = True, help = 'path to folder which contains the images')
    args = parser.parse_args()

    image_bucket, hash_bucket0, hash_bucket1, hash_bucket2, hash_bucket3 = get_hash_bucket(args.folder)
    image_deduplication(image_bucket, hash_bucket0, hash_bucket1, hash_bucket2, hash_bucket3)