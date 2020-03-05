from pathlib import Path
import struct

from collections import OrderedDict

folder = Path("C:/Users/georg/motherlode/UMass/cs590K/songs")
filename = folder / "chunk10.tar.gz"

# this discriminator is only for MPEG-1 Layer 3
# I found the other versions (MPEG 2 or 2.5 and their layers)
# a bit complex
# Here's the bitrate table for MPEG 1, layer 3 (the original MP3)
bitrate_table = {
    1: 32,
    2: 40,
    3: 48,
    4: 56,
    5: 64,
    6: 80,
    7: 96,
    8: 112,
    9: 128,
    10: 160,
    11: 192,
    12: 224,
    13: 256,
    14: 320,
}

# Here's the sample rate table for MPEG 1, Layer 3
sample_rate_table = {
    0: 44100,
    1: 48000,
    2: 32000,
}

# this dict records the start_offset of a potential MP3 frame
# and its "probable" frame-size
start_offset_and_frame_size = OrderedDict()

with open(filename, 'rb') as f:
    buffer = f.read()  # load all the content into memory

    i = 0
    while i < (len(buffer) - 4):
        # read 4 bytes
        data = struct.unpack("BBBB", buffer[i:i + 4])

        i += 1  # move to next byte for next iteration

        if data[0] != 255:
            continue

        #  the first 8 bits are all 1
        # mp3 has all of the first 12 bits set to 1s
        # (as per the Garfinkel paper, this is what they observed in their corpus)
        # also since we support only layer 3 of MPEG 1,
        # we just check for the the first 7 bits of the 2nd byte:
        # it should be '1111101'
        # (http://www.mp3-tech.org/programmer/frame_header.html for the header structure)
        mpeg_version = (data[1] & 0b11111110)

        if mpeg_version != 0b11111010:
            continue

        # the first 12 bits are set!

        # find the bitrate
        # they are the first 4 bits of the 3rd byte
        bit_rate_index = ((data[2] & 0b11110000) >> 4)

        # check whether padding bit is set or not
        # its the 23rd bit from the beginning i.e. 7th bit of the 3rd byte
        padded = bool(data[2] & 0b10)

        # sampling rate index (to the table declared at the beginning)
        # its the 5th and 6th bits of the 3rd byte
        sampling_rate_index = ((data[2] & 0x0c) >> 2)
        # print(type(sampling_rate_index))

        '''if i < 100:
            print(sampling_rate_index)
            print(i, data[2], next_four, bitrate_table[bitrate], sample_rate_table,
                  sample_rate_table[sampling_rate_index])
            print(sampling_rate_index)'''

        # sanity checks on the bit-rate and sample-rate
        # bit-rate-index must be between 1 and 14
        if bit_rate_index < 1 or bit_rate_index > 14:
            continue

        # sample-rate-index must be 0, 1 or 2
        if sampling_rate_index < 0 or sampling_rate_index > 2:
            continue

        # print(i, bit_rate_index, sampling_rate_index)

        # calculate frame size
        frame_size = int(144 * (1000 * bitrate_table[bit_rate_index]) / sample_rate_table[sampling_rate_index])

        if padded:
            frame_size += 1

        # record the start-offset and the frame-size
        start_offset_and_frame_size[i] = frame_size  # 4 for the header and then the frame

offset = []
fsize = []
for entry in start_offset_and_frame_size:
    print(entry, start_offset_and_frame_size[entry])
    offset.append(entry)
    fsize.append(start_offset_and_frame_size[entry])

max_chain_length = 0
i = 0
while i < len(offset):
    # print(offset[i], fsize[i])
    start = i
    i += 1
    # print(offset[start])
    while i < len(offset):
        if offset[i - 1] + fsize[i - 1] == offset[i]:
            # print(offset[i])
            i += 1
        else:
            break
    chain_length = i - start
    # print(offset[i])
    # print("chain length=", chain_length)
    max_chain_length = max(max_chain_length, chain_length)

print("The maximum length chain of frame headers found in this is: ", max_chain_length)

# as used in the paper, I am choosing the chain length of 4 to be the deciding factor
# if there is a chain of 4 (or more) contigous frames, this is an MP3 else not!
if (max_chain_length >= 4):
    print("This is an MP3 file!")
else:
    print("This isn't an MP3 file..")
