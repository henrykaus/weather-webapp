class model():
    
    def select(self, lat_long: str, date: str) -> list:
        """
        Gets all entries from the database matching the latitude,longitude and date.
        Each entry contains: lat_long: str, date: str, max_temp: float, min_temp: float
        :param: lat_long: String
        :param: date: String, default is None
        :return: List of lists containing all matching entries of database.
        """
        pass


    def insert(self, month_temps: list) -> bool:
        """
        Puts entries into database.
        :param: month_temps: list [(lat_long: str, date: str, max_temp: float, min_temp: float), ...]
        :return: True
        """
        pass


    def update(self, month_temp: tuple) -> bool:
        """
        Updates entries in database.
        :param: month_temp: tuple (lat_long: str, date: str, max_temp: float, min_temp: float)
        :return: True
        """
        pass
    