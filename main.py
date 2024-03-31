# PIL for image handling
from PIL import Image
# Random for key creation
import random
import zipfile

# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi
import os

# Define the hostname and port
hostName = "localhost"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Send a 200 OK response
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Check the requested path and respond accordingly
        if self.path == "/":
            # UI with a link to the About page
            self.wfile.write(bytes("<html><head><title>Image encrypter & decrypter web serverr</title></head>", "utf-8"))
            self.wfile.write(bytes("<body>", "utf-8"))
            self.wfile.write(bytes("<h1>Encode & Decode Images Here</h1>", "utf-8"))
            self.wfile.write(bytes("<p><a href='/encode'>encode</a></p>", "utf-8"))
            self.wfile.write(bytes("<p><a href='/decode'>decode</a></p>", "utf-8"))
            self.wfile.write(bytes("</body></html>", "utf-8"))
        elif self.path == "/encode":
            # About page
            self.wfile.write(bytes("<html><head><title>Encode</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Encode Page</h1>", "utf-8"))
            self.wfile.write(b"<form method='POST' enctype='multipart/form-data'>")
            self.wfile.write(b"<input type='file' name='img_file'><br><p>Image</p>")
            self.wfile.write(b"<input type='submit' value='Upload'>")
            self.wfile.write(b"</form>")
            self.wfile.write(bytes("</body></html>", "utf-8"))
        elif self.path == "/decode":
            # About page
            self.wfile.write(bytes("<html><head><title>Decode</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><h1>Decode Page</h1>", "utf-8"))
            self.wfile.write(b"<form method='POST' enctype='multipart/form-data'>")
            self.wfile.write(b"<input type='file' name='img_file'><p>Image</p><br>")
            self.wfile.write(b"<input type='file' name='key_file'><p>Key</p><br>")
            self.wfile.write(b"<input type='submit' value='Upload'>")
            self.wfile.write(b"</form>")
            self.wfile.write(bytes("</body></html>", "utf-8"))
        else:
            # 404 - Page not found
            self.wfile.write(bytes("<html><head><title>Not Found</title></head>", "utf-8"))
            self.wfile.write(bytes("<body><p>404 - Page not found.</p></body></html>", "utf-8"))

    def do_POST(self):
        # Handle POST requests (file upload)
        if self.path == "/decode":
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST"}
            )
            img_file = form["img_file"]
            key_file = form['key_file']
            if img_file.filename:
                # Save the uploaded file (customize the path as needed)
                img_path = os.path.join(os.getcwd(), img_file.filename)
                key_path = os.path.join(os.getcwd(), key_file.filename)
                with open(img_path, "wb") as f:
                    f.write(img_file.file.read())
                with open(key_path, "wb") as f:
                    f.write(key_file.file.read())
                decrypt_image(img_path, key_path)
                with open(img_path, "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-type", "application/zip")
                    self.send_header("Content-Disposition", "attachment; filename=" + img_file.filename)
                    self.end_headers()
                    self.wfile.write(f.read())
                os.remove(key_path)
                os.remove(img_path)
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<html><body>")
                self.wfile.write(b"<p>Error uploading file.</p>")
                self.wfile.write(b"</body></html>")
        elif self.path == "/encode":
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={"REQUEST_METHOD": "POST"}
            )
            img_file = form["img_file"]
            if img_file.filename:
                # Save the uploaded file (customize the path as needed)
                img_path = os.path.join(os.getcwd(), img_file.filename)
                with open(img_path, "wb") as f:
                    f.write(img_file.file.read())
                encode_image(img_path, 'key.txt')
                file_names = [img_file.filename, "key.txt"]  # Customize with your file names
                with zipfile.ZipFile("key_img.zip", "w") as zipf:
                    for file_name in file_names:
                        file_path = os.path.join(os.getcwd(), file_name)
                        if os.path.exists(file_path):
                            zipf.write(file_path, file_name)
                with open("key_img.zip", "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-type", "application/zip")
                    self.send_header("Content-Disposition", "attachment; filename=test.zip")
                    self.end_headers()
                    self.wfile.write(f.read())
                os.remove(img_path)
                os.remove('key.txt')
                os.remove('key_img.zip')
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><p>404 - Page not found.</p></body></html>")


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


if __name__ == "__main__":
    hostName = "localhost"
    serverPort = 8080
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f"Server started at http://{hostName}:{serverPort}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")