# PIL for image handling
from PIL import Image
# Random for key creation
import random


# Takes an image path and a path to place the key
def encode_image(path, key_path):
    # Get source image and pixels as well as height/width
    input = Image.open(path)
    pixels = input.load()
    width, height = input.size
    # Create a list of all possible byte vaues for xor operation
    bytes = []
    for i in range(256):
        bytes.insert(0, 255 - i)
    # Create an all zero bytearray for key
    key = bytearray(width * height * 3)
    # Iterate through pixels and modify them while storing key values
    index = 0
    for i in range(width):
        for j in range(height):
            r, g, b, _p = input.getpixel((i, j))
            # Generate random byte for xor, store it, and modify pixel value with it
            key[index] = random.choice(bytes)
            r = r ^ key[index]
            index = index + 1
            key[index] = random.choice(bytes)
            g = g ^ key[index]
            index = index + 1
            key[index] = random.choice(bytes)
            b = b ^ key[index]
            index = index + 1
            pixels[i, j] = (r, g, b)
    # Save encrypted image in original place
    input.save(path, format='png')
    # Save key to key's path
    key_file = open(key_path, 'wb')
    key_file.write(key)
    key_file.close()


# Decrypts an image from a key file and the original image using one-time-pad strategy
def decrypt_image(path, key_path):
    # Get key and turn into bytearray
    key_file = open(key_path, 'rb')
    key = key_file.read()
    key_file.close()
    key = bytearray(key)
    # Get source image pixel map and height
    input = Image.open(path)
    pixels = input.load()
    width, height = input.size
    # Iterate through pixels and modify them based on key
    index = 0
    for i in range(width):
        for j in range(height):
            # Get pixels
            r, g, b, _p = input.getpixel((i, j))
            # Change pixel values back to original
            r = r ^ key[index]
            index = index + 1
            g = g ^ key[index]
            index = index + 1
            b = b ^ key[index]
            index = index + 1
            pixels[i, j] = (r, g, b)
    # Save decoded image back in its original place
    input.save(path, format='png')


# Main
if __name__ == '__main__':
    # Menu loop
    while(True):
        # Choices
        i = input('1. encrypt 2. decrypt 3. quit\n')
        match i:
            # Encrypt
            case '1':
                path = input('Enter path of unencrypted image: ')
                key = input('Enter key location: ')
                encode_image(path, key)
            # Decrypt
            case '2':
                path = input('Enter path of encrypted image: ')
                key = input('Enter key location: ')
                decrypt_image(path, key)
            # Exit
            case '3':
                break
