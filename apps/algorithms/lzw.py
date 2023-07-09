from io import StringIO
from struct import *


class LZW_TEXT:
    def __init__(self, path=""):
        pass

    def compress(self, data, maximum_table_size=15000):
        dictionary_size = 9000
        dictionary = {chr(i): i for i in range(dictionary_size)}
        string = ""
        compressed_data = []

        for symbol in data:
            string_plus_symbol = string + symbol
            if string_plus_symbol in dictionary:
                string = string_plus_symbol
            else:
                compressed_data.append(dictionary[string])
                if (len(dictionary) <= maximum_table_size):
                    dictionary[string_plus_symbol] = dictionary_size
                    dictionary_size += 1
                string = symbol

        if string in dictionary:
            compressed_data.append(dictionary[string])

        return compressed_data

    def decompress(self, compressed_data):
        dictionary_size = 9000
        dictionary = dict([(x, chr(x)) for x in range(dictionary_size)])

        next_code = dictionary_size
        decompressed_data = ""
        string = ""
        for code in compressed_data:
            if not (code in dictionary):
                dictionary[code] = string + (string[0])
            decompressed_data += dictionary[code]
            if not (len(string) == 0):
                dictionary[next_code] = string + (dictionary[code][0])
                next_code += 1
            string = dictionary[code]
        return decompressed_data

    def save(compressed_data, input_file):
        out = input_file.split(".")[0]
        output_file = open("CompressedFiles" + out + ".lzw", "wb")
        for data in compressed_data:
            output_file.write(pack('>H', int(data)))

        output_file.close()

    def compress_text(self, text):
        compressed_text = self.compress(text)
        compressed_text = ''.join(chr(code) for code in compressed_text)
        return compressed_text

    def decompress_text(self, compressed_text):
        dictionary = {i: chr(i) for i in range(256)}
        compressed_text = [ord(char) for char in compressed_text]
        return self.decompress(compressed_text)


from PIL import Image
import os
import numpy as np


class LZW_IMG:
    def __init__(self, file=None, path=''):
        self.path = path
        if file != None:
            self.file = StringIO(file.getvalue().decode("utf-8"))
        self.compressionDictionary, self.compressionIndex = self.createCompressionDict()
        self.decompressionDictionary, self.decompressionIndex = self.createDecompressionDict()

    ''''''
    ''' --------------------- Compression of the Image --------------------- '''
    ''''''

    def compress(self):
        self.initCompress()
        compressedcColors = []
        print("Compressing Image ...")
        compressedcColors.append(self.compressColor(self.red))
        print("Compressing Image ...")
        compressedcColors.append(self.compressColor(self.green))
        print("Compressing Image ...")
        compressedcColors.append(self.compressColor(self.blue))
        print("Image Compressed --------- Writing to File")

        compressed_data = ""
        for color in compressedcColors:
            for row in color:
                compressed_data += row
                compressed_data += "\n"
        return compressed_data

    def compressColor(self, colorList):
        compressedColor = []
        i = 0
        for currentRow in colorList:
            currentString = currentRow[0]
            compressedRow = ""
            i += 1
            for charIndex in range(1, len(currentRow)):
                currentChar = currentRow[charIndex]
                if currentString + currentChar in self.compressionDictionary:
                    currentString = currentString + currentChar
                else:
                    compressedRow = compressedRow + str(self.compressionDictionary[currentString]) + ","
                    self.compressionDictionary[currentString + currentChar] = self.compressionIndex
                    self.compressionIndex += 1
                    currentString = currentChar
            compressedRow = compressedRow + str(self.compressionDictionary[currentString])
            compressedColor.append(compressedRow)
        return compressedColor

    ''''''
    ''' --------------------- Deompression of the Image --------------------- '''
    ''''''

    def decompress(self):
        print("Decompressing File ...")
        image = []
        # with open("CompressedFiles\C.txt","r") as file:
        for line in self.file:
            decodedRow = self.decompressRow(str(line))
            image.append(np.array(decodedRow))

        image = np.array(image)
        shapeTup = image.shape
        image = image.reshape((3, shapeTup[0] // 3, shapeTup[1]))

        imagelist, imagesize = self.makeImageData(image[0], image[1], image[2])
        imagenew = Image.new('RGB', imagesize)
        imagenew.putdata(imagelist)

        return imagenew

    def decompressRow(self, line):
        currentRow = line.split(",")
        currentRow[-1] = currentRow[-1][:-1]
        decodedRow = ""
        decodedRow = decodedRow + self.decompressionDictionary[int(currentRow[0])]
        word = self.decompressionDictionary[int(currentRow[0])]
        for i in range(1, len(currentRow)):
            new = int(currentRow[i])
            if new in self.decompressionDictionary:
                entry = self.decompressionDictionary[new]
                decodedRow += entry
                add = word + entry[0]
                word = entry
            else:
                entry = word + word[0]
                decodedRow += entry
                add = entry
                word = entry
            self.decompressionDictionary[self.decompressionIndex] = add
            self.decompressionIndex += 1
        newRow = decodedRow.split(',')
        decodedRow = [int(x) for x in newRow]
        return decodedRow

    ''''''
    ''' ---------------------- Class Helper Functions ---------------------- '''
    ''''''
    '''
    Used For: Compression of Image
    Function: This function breaks down the image into the three constituting
              image chanels - Red, Green and Blue.
    '''

    def initCompress(self):
        self.image = Image.open(self.path)
        self.height, self.width = self.image.size
        self.red, self.green, self.blue = self.processImage()

    '''
    Used For: Compression of Image
    Function: This function breaks down the image into the three constituting
              image chanels - Red, Green and Blue.
    '''

    def processImage(self):
        image = self.image.convert('RGB')
        red, green, blue = [], [], []
        pixel_values = list(image.getdata())
        iterator = 0
        for height_index in range(self.height):
            R, G, B = "", "", ""
            for width_index in range(self.width):
                RGB = pixel_values[iterator]
                R = R + str(RGB[0]) + ","
                G = G + str(RGB[1]) + ","
                B = B + str(RGB[2]) + ","
                iterator += 1
            red.append(R[:-1])
            green.append(G[:-1])
            blue.append(B[:-1])
        return red, green, blue

    '''
    Used For: Decompression of Image
    Function: This function will save the decompressed image as <name>.tif
    '''

    def saveImage(self, image):
        print("Saving Decompressed File...")
        filesplit = str(os.path.basename(self.path)).split('_LZWCompressed.txt')
        filename = filesplit[0] + "_LZWDecompressed.jpg"
        savingDirectory = os.path.join(os.getcwd(), 'DecompressedFiles')
        if not os.path.isdir(savingDirectory):
            os.makedirs(savingDirectory)
        imagelist, imagesize = self.makeImageData(image[0], image[1], image[2])
        imagenew = Image.new('RGB', imagesize)
        imagenew.putdata(imagelist)
        imagenew.save(os.path.join(savingDirectory, filename))

    '''
    Used For: Decompression of Image
    Function: This function will convert and return the image in the (r,g,b) format
              to save the image.
    '''

    def makeImageData(self, r, g, b):
        imagelist = []
        for i in range(len(r)):
            for j in range(len(r[0])):
                imagelist.append((r[i][j], g[i][j], b[i][j]))
        return imagelist, (len(r), len(r[0]))

    '''
    Used For: Compression of Image
    Function: This function will initialise the compression dictionary
    '''

    def createCompressionDict(self):
        dictionary = {}
        for i in range(10):
            dictionary[str(i)] = i
        dictionary[','] = 10
        return dictionary, 11

    '''
    Used For: Compression of Image
    Function: This function will initialise the decompression dictionary
    '''

    def createDecompressionDict(self):
        dictionary = {}
        for i in range(10):
            dictionary[i] = str(i)
        dictionary[10] = ','
        return dictionary, 11
