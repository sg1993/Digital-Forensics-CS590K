import io
from pathlib import Path
import PIL
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

import binascii

folder = Path("C:/Users/georg/motherlode/UMass/cs590K")
filename = folder / "dfrws-2006-challenge.raw"
with open(filename, 'rb') as f:
    hexdata = f.read()
    #print(hexdata)
    if isinstance(hexdata, bytes):
        print("hello!")

    # all hex data is in memory now
    header_index = []  # stores the index/byte-position of each header (i.e. FFD8FFE0) in the raw file
    print(len(hexdata))
    count = 0
    for i in range(0, len(hexdata)):
        slice = hexdata[i:i+4].hex()
        #print(len(slice))
        if(slice=='ffd8ffe0'):
            #print (slice, i)
            header_index.append(i)
        elif(slice[0:4]=='ffd9'):
            count+=1
            # for every footer, match it with every header possible
            num = 0
            for header in reversed(header_index):
                image_bytes = io.BytesIO(hexdata[header:i+2])
                # print(image_bytes)
                try:
                    img = Image.open(image_bytes)
                    # img.show()
                    print(img.size, i+2, header)
                    img.save(folder / (str(header)+"_"+str(i+2) + ".jpeg"))
                    header_index.pop(-num) # remove this header since it has been matched with a footer
                except PIL.UnidentifiedImageError:
                    print("PILUIE")
                num += 1

    print(header_index)
    print(len(header_index))
    print(count)
