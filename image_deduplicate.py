import os
import argparse
import shutil
import scipy.fftpack
from PIL import Image
import numpy

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
    hash_bucket = []

    pics = os.listdir(folder)
    for pic in pics:
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
            hash_bucket.append([hash_result, image_path])

    return hash_bucket

def image_deduplication(hash_bucket):
    os.makedirs('./trash', exist_ok=True)
    compared_bucket = set()
    for i, vi in enumerate(hash_bucket):
        for j, vj in enumerate(hash_bucket):
            if j <= i:
                continue
            # remove the last one and record the compared pair
            if hamming_distance(vi[0], vj[0]) < 4 and vi[1] not in compared_bucket and vj[1] not in compared_bucket:
                shutil.move(vj[1], './trash')
                compared_bucket.add(vj[1])
                print (vi[1] + ' --> ' + os.path.join('./trash', os.path.split(vj[1])[-1]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--folder', type = str, required = True, help = 'path to folder which contains the images')
    args = parser.parse_args()

    hash_bucket = get_hash_bucket(args.folder)
    image_deduplication(hash_bucket)