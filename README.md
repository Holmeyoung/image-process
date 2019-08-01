# Image process script

## [image_deduplicate](https://github.com/Holmeyoung/image-process/blob/master/image_deduplicate.py)

Use `multi process` to calculate the image hash value.

Use `phash` to judge whether two images are the same or not.

Use `Pigeon nest principle` to accelerate calculation.



## [image_valid](https://github.com/Holmeyoung/image-process/blob/master/image_valid.py)

Used to judge whether a image is valid or not. I use `multi process` to deal with it, so it's very fast.



## [image_download](https://github.com/Holmeyoung/image-process/blob/master/image_download.py)

Use `multi thread` to download image from Internet. Take care not to set the thread too big, or it will be a disaster to your net.