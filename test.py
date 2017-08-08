from PIL import Image, ImageTk
import sqlite3 as sqlite
import os
import io


dirPath = os.path.dirname(os.path.realpath(__file__))
connection = sqlite.connect(dirPath + '/database/testDB.db')
cursor = connection.cursor()

cursor.execute('SELECT image FROM image_data')
image = cursor.fetchall()[0][0]
img = Image.frombytes(data=image, size=(672, 504), mode="RGB")
img.show()