from pathlib import Path
import struct

from collections import OrderedDict

folder = Path("C:/Users/georg/motherlode/UMass/cs590K")
filename = folder / "gettysburg-lz.txt"

with open(filename, 'rb') as f:
    buffer = f.read()  # load all the content into memory

    # cleanup angle brackets and whitespaces
    splits = buffer.decode().split('<')
    new_splits = []
    for s in splits:
        s = s.split('>')[0]
        if len(s) > 0:
            new_splits.append(s)
    splits = []
    for s in new_splits:
        s = s.split(', ')
        splits.append(s)

    # print(splits)

    # cleanup done!
    final_string = ""
    for item in splits:
        if len(item)==2:
            # this is a non-redundant item
            final_string += item[1]
        elif len(item)==3:
            # this is a back pointer
            go_back = int(item[1])
            to_copy = int(item[2])
            temp_string = final_string[-go_back:][:to_copy]
            final_string += temp_string

    # print(final_string)
    # while writing the string to file,
    # use (newline='\n') so that unix newline is used instead of windows
    # this is just a minor nit so that gettysburg can match exactly with
    # my output file during sha1sum check
    out_file = open("decompressed.txt", "w", newline='\n')
    out_file.write(final_string)
    out_file.close()