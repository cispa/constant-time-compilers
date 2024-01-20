import struct
import random
import sys

def write_random_unsigned_ints(filename, count):
    # Open the file in binary write mode
    with open(filename, 'wb') as f:
        # Generate and write random unsigned integers
        for _ in range(count):
            random_uint = random.randint(0, 2**32 - 1)
            packed_data = struct.pack('I', random_uint)
            f.write(packed_data)

if __name__ == "__main__":
    # Call the function to write 34 random unsigned integers to 'key.dat'
    key_filename = sys.argv[1]
    write_random_unsigned_ints(key_filename, 34)
