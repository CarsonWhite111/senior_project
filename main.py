# PIL for image handling
from PIL import Image
# Random for key creation
import random
# So multiple files can be downloaded at once
import zipfile
# Web server imports
from http.server import BaseHTTPRequestHandler, HTTPServer
# Get form fields
import cgi
# For os operations
import os

# Define the hostname and port
hostName = "localhost"
serverPort = 8080


# Server functionality
class Server(BaseHTTPRequestHandler):

    # Handle client requests
    def do_GET(self):
        # Ensure connection
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        # Home page
        if self.path == "/":
            # Page that lists encode and decode links
            self.wfile.write(bytes("<html><head><title>Image encrypter & decrypter web serverr</title></head>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<h1>Encode & Decode Images Here</h1>", "utf-8"))
            self.wfile.write(bytes("<p><a href='/encode'>encode</a></p>", "utf-8"))
            self.wfile.write(bytes("<p><a href='/decode'>decode</a></p>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
        # Encode page
        elif self.path == "/encode":
            # Lists a file input and upload button
            self.wfile.write(bytes("<html><head><title>Encode</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Encode Page</h1>", "utf-8"))
            self.wfile.write(b"<form method='POST' enctype='multipart/form-data'>")
            self.wfile.write(b"<input type='file' name='img_file'><br><p>Image</p>")
            self.wfile.write(b"<input type='submit' value='Upload'>")
            self.wfile.write(b"</form>")
            self.wfile.write(bytes("</body></html>", "utf-8"))
        elif self.path == "/decode":
            # Lists two file inputs for image and key and upload button
            self.wfile.write(bytes("<html><head><title>Decode</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Decode Page</h1>", "utf-8"))
            self.wfile.write(b"<form method='POST' enctype='multipart/form-data'>")
            self.wfile.write(b"<input type='file' name='img_file'><p>Image</p><br>")
            self.wfile.write(b"<input type='file' name='key_file'><p>Key</p><br>")
            self.wfile.write(b"<input type='submit' value='Upload'>")
            self.wfile.write(b"</form>")
            self.wfile.write(bytes("</body></html>", "utf-8"))
        else:
            # If navigated to incorrect location
            self.wfile.write(bytes("<html><head><title>Not Found</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><p>404 - Page not found.</p></body></html>", "utf-8"))

    # Handle client actions
    def do_POST(self):
        # Decode client actions
        if self.path == "/decode":
            # Get form fields
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST"}
            )
            # Get files
            img_file = form["img_file"]
            key_file = form['key_file']
            if img_file.filename:
                # Find file locations
                img_path = os.path.join(os.getcwd(), img_file.filename)
                key_path = os.path.join(os.getcwd(), key_file.filename)
                # Write to disk
                with open(img_path, "wb") as f:
                    f.write(img_file.file.read())
                with open(key_path, "wb") as f:
                    f.write(key_file.file.read())
                # Decrypt and return possible errors
                png_e, key_e = decrypt_image(img_path, key_path)
                # If client submits an incorrect file for image
                if png_e is not None:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(bytes("You inputted either a non png file or a png file with incorrect format",
                                           "utf8"))
                # If client submits an incorrect key size for image
                elif key_e is not None:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(bytes("The given key does not match the dimensions of the given image", 'utf8'))
                # Fine path
                else:
                    # Write and download decrypted image
                    with open(img_path, "rb") as f:
                        self.send_response(200)
                        self.send_header("Content-type", "application/zip")
                        self.send_header("Content-Disposition", "attachment; filename=" + img_file.filename)
                        self.end_headers()
                        self.wfile.write(f.read())
                # Remove files after execution
                os.remove(key_path)
                os.remove(img_path)
            # Generic uploading error path
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body>")
                self.wfile.write(b"<p>Error uploading file.</p>")
                self.wfile.write(b"</body></html>")
        # Encode client actions
        elif self.path == "/encode":
            # Get fields
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST"}
            )
            # Get image
            img_file = form["img_file"]
            if img_file.filename:
                # Save file
                img_path = os.path.join(os.getcwd(), img_file.filename)
                with open(img_path, "wb") as f:
                    f.write(img_file.file.read())
                # Encode image if no error with format
                error = encode_image(img_path, 'key.txt')
                # Tell user of error
                if error is not None:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(bytes("You inputted either a non png file or a png file with incorrect format",
                                           "utf8"))
                # Zip and download files
                else:
                    file_names = [img_file.filename, "key.txt"]
                    with zipfile.ZipFile("key_img.zip", "w") as zipf:
                        for file_name in file_names:
                            file_path = os.path.join(os.getcwd(), file_name)
                            if os.path.exists(file_path):
                                zipf.write(file_path, file_name)
                    # Download file to client
                    with open("key_img.zip", "rb") as f:
                        self.send_response(200)
                        self.send_header("Content-type", "application/zip")
                        self.send_header("Content-Disposition", "attachment; filename=test.zip")
                        self.end_headers()
                        self.wfile.write(f.read())
                    # Remove local files
                    os.remove('key.txt')
                    os.remove('key_img.zip')
                # Remove image
                os.remove(img_path)
        # File not found error
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><p>404 - Page not found.</p></body></html>")


# Takes an image path and a path to place the key
def encode_image(path, key_path):
    # Error variables
    png_exception = None
    input = None
    try:
        # Get source image and pixels
        input = Image.open(path)
        pixels = input.load()
    except:
        # No png = error
        png_exception = True
    # Continue if png
    if input is not None:
        width, height = input.size
        # Create a list of all possible byte values for xor operation
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
    # Return possible error
    return png_exception


# Decrypts an image from a key file and the original image using one-time-pad strategy
def decrypt_image(path, key_path):
    # Get key and turn into bytearray
    key_file = open(key_path, 'rb')
    key = key_file.read()
    key_file.close()
    key = bytearray(key)
    # Get source image pixel map
    input = None
    # Exceptions
    png_exception = None
    key_exception = None
    try:
        # Test if loading the image is fine
        input = Image.open(path)
        pixels = input.load()
    except:
        # If not changer error var
        png_exception = True
    # If fine continue
    if png_exception is None:
        # Get dimensions
        width, height = input.size
        if len(key) != (width * height * 3):
            key_exception = True
        else:
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
    # Return possible errors
    return png_exception, key_exception


if __name__ == "__main__":
    # Setup webserver
    hostName = "localhost"
    serverPort = 8080
    webServer = HTTPServer((hostName, serverPort), Server)
    print(f"Server started at http://{hostName}:{serverPort}")
    # Exit if interrupted
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")
