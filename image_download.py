import requests
import os
import threading
import queue
import argparse

parser = argparse.ArgumentParser()
# parser.add_argument('-i', '--in_path', type = str, required = True, help = 'path to urls file')
parser.add_argument('-o', '--out_path', type = str, required = True, help = 'path to store the download images')
parser.add_argument('-t', '--thread', type = int, help = 'download thread number', default = 10)
args = parser.parse_args()

def fetch_img_func(q):
    while True:
        try:
            # unblock read from queue
            url = q.get_nowait() # https://example.com/example.jpg
        except:
            break
        else:
            try:
                url = url.strip()
                # download and save
                filename = os.path.basename(url)
                r = requests.get(url, timeout=(5, 20))
                with open('%s/%s' % (args.out_path, filename), 'wb') as f:
                    f.write(r.content)
            except:
                pass
            else:
                pass

if __name__ == "__main__":
    q = queue.Queue()

    '''
    Put the urls into queue here.
    eg:
        url = https://example.com/example.jpg
        q.put(url)
    '''

    # It depends on your net speed and the image size, too big is a disaster to your net.
    threads = []
    for i in range(args.thread):
        thread = threading.Thread(target=fetch_img_func, args=(q, ))
        threads.append(thread)
        thread.start()
    for i in threads:
        i.join()