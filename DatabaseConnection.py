import sqlite3 as sqlite
import time


class DatabaseHandler:
    databasename = None
    connection = None
    cursor = None

    def __init__(self, databasename):
        self.databasename = databasename
        try:
            self.connection = sqlite.connect(self.databasename)
            self.cursor = self.connection.cursor()

        except sqlite.Error as e:
            print(e)

        finally:
            self.connection.close()

    def adddata(self, tablename, **data):
        self.connection = sqlite.connect(self.databasename)
        self.cursor = self.connection.cursor()

        if tablename == 'image_data':
            self.cursor.execute('INSERT INTO image_data (image, ratio, angle, fingertip, nailbed, joint, timestamp) '
                                'VALUES (?,?,?,?,?,?,?)',
                                (data['image'], data['ratio'], data['angle'], data['fingertip'],
                                 data['nailbed'], data['joint'], time.time()))

        if tablename == 'events':
            self.cursor.execute("INSERT INTO events (event, timestamp) VALUES (?,?)",
                                (data['event'], time.time()))

        self.connection.commit()
        self.connection.close()
