from .model import model
import sqlite3

DB_FILE = 'weather.db'    # Database file

class Model(model):
    
    def __init__(self):
        """
        Manages interactions for the SQLite3 database.
        """
        self.kind = "weather"
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        try:
            cursor.execute("select count(rowid) from weather")
        except sqlite3.OperationalError:
            cursor.execute("CREATE TABLE weather (lat_long TEXT, date DATE, max_temp FLOAT, min_temp FLOAT)")
        cursor.close()


    def select(self, lat_long: str, date: str = None):
        """
        Gets all entities from the database matching the latitude,longitude and date.
        Each entity contains: lat_long: str, date: str, max_temp: float, min_temp: float
        :param: lat_long: String
        :param: date: String, default is None
        :return: List of tuples containing all matching entities from database.
        """
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        params = {'lat_long': lat_long, 'date': date}
        if date is None:
            cursor.execute("SELECT * FROM weather WHERE lat_long = :lat_long", params)
        else:
            cursor.execute("SELECT * FROM weather WHERE lat_long = :lat_long AND date = :date", params)

        items = cursor.fetchall()
        cursor.close()
        return items


    def insert(self, month_temps: list):
        """
        Inserts entities into database.
        :param month_temps: list[(lat_long: str, date: str, max_temp: float, min_temp: float), ...]
        :return: True
        """
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        for (lat_long, date, max_temp, min_temp) in month_temps:
            params = {'lat_long': lat_long, 'date': date, 'max_temp': max_temp, 'min_temp': min_temp}
            cursor.execute("INSERT INTO weather (lat_long, date, max_temp, min_temp) VALUES (:lat_long, :date, :max_temp, :min_temp)", params)

        connection.commit()
        cursor.close()
        return True


    def update(self, month_temp: tuple) -> bool:
        """
        Updates entities in database. They must already exist.
        :param month_temps: list[(lat_long: str, date: str, max_temp: float, min_temp: float), ...]
        :return: True
        """
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()

        (lat_long, date, max_temp, min_temp) = month_temp
        params = {'lat_long': lat_long, 'date': date, 'max_temp': max_temp, 'min_temp': min_temp, 'lat_long': lat_long, 'date': date}
        cursor.execute("UPDATE weather SET max_temp = :max_temp, min_temp = :min_temp WHERE lat_long = :lat_long and date = :date", params)

        connection.commit()
        cursor.close()
        return True
