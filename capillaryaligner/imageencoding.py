import numpy as np


def decodeimage(imagestring:bytes):
    imagestring = imagestring.replace(b'!',b'')
    stringsplit = imagestring.split(b';')
    metadata = {}
    for item in stringsplit:
        i = item.decode()
        if i == 'end':
            break
        isplit = i.split('_')
        metadata[isplit[0]] = isplit[1]
    d1 = int(metadata['d1'])
    d2 = int(metadata['d2'])
    d3 = int(metadata['d3'])
    image = np.frombuffer(stringsplit[-1],dtype=np.uint8)
    image = image.reshape(d1,d2,d3)
    return image


def encodeimage(array:np.ndarray):
    if len(array.shape) < 3:
        d3 = 1
    else:
        d3 = array.shape[2]
    d1 = array.shape[0]
    d2 = array.shape[1]
    bstring = f'send_;d1_{d1};d2_{d2};d3_{d3};end;'
    bstring = bytes(bstring, encoding='utf-8')
    bstring += array.tobytes()
    bstring += b'!'
    return bstring
