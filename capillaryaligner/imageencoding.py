import numpy as np
import zlib

def decodeimage(imagestring:bytes):
    metastring = imagestring.split(b';end;')[0].decode()
    arraystring = zlib.decompress(imagestring.split(b';end;')[1].replace(imageendstring,b''))
    metadata = {}
    for item in metastring.split(';'):
        if item == 'end':
            break
        isplit = item.split('_')
        metadata[isplit[0]] = isplit[1]
    d1 = int(metadata['d1'])
    d2 = int(metadata['d2'])
    d3 = int(metadata['d3'])
    image = np.frombuffer(arraystring,dtype=np.uint8)
    image = image.reshape(d1,d2,d3)
    return image


def encodeimage(array:np.ndarray):
    if len(array.shape) < 3:
        d3 = 1
    else:
        d3 = array.shape[2]
    d1 = array.shape[0]
    d2 = array.shape[1]
    bstring = array.tobytes()
    bstring = zlib.compress(bstring)
    startstring = f'send_;d1_{d1};d2_{d2};d3_{d3};end;'

    bstring = bytes(startstring,encoding='utf-8') + bstring + imageendstring
    return bstring


imageendstring = b'!!!end!!!'