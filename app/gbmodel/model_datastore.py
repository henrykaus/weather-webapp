import datetime
from google.cloud import datastore
from .model import model

CLIENT = 'project-kaus-hkaus'   # GCP Project

def from_datastore(entity) -> list:
    """
    Translates datastore results into the format expected by the application.

    Datastore typically returns:
        [Entity{key: (kind, id), prop: val, ...}]

    :param: entity
    :return: [ lat_long, date, max_temp, min_temp ] where lat_long and date are strings, and max_temp and min_temp are floats.
    """
    if not entity:
        return None
    if isinstance(entity, list):
        entity = entity.pop()
    
    return [ entity['lat_long'], entity['date'], entity['max_temp'], entity['min_temp'] ]


class Model(model):

    def __init__(self):
        """
        Manages interactions with the datastore client.
        """
        self.client = datastore.Client(CLIENT)
        self.kind = 'weather'


    def select(self, lat_long: str, date: str = None) -> bool:
        """
        Gets all entities from the datastore matching the latitude,longitude and date.
        Each entity contains: lat_long: str, date: str, max_temp: float, min_temp: float
        :param: lat_long: String
        :param: date: String, default is None
        :return: List of lists containing all matching entities of datastore.
        """
        limit = self.diff_months(datetime.date(2000, 1, 1), datetime.date.today()) + 1

        # Construct the query
        query = self.client.query(kind = self.kind)
        query.add_filter("lat_long", "=", lat_long)
        if date is not None:
            query.add_filter("date", "=", date)
        query.order = ["date"]

        entities = list(map(from_datastore, query.fetch(limit=limit)))
        return entities


    def insert(self, month_temps: list) -> bool:
        """
        Puts entities into datastore.
        :param: month_temps: List [(lat_long: str, date: str, max_temp: float, min_temp: float), ...]
        :return: True
        """
        items_to_put = []
        
        for (lat_long, date, max_temp, min_temp) in month_temps:
            key = self.client.key(self.kind)
            rev = datastore.Entity(key)
            rev.update({
                'lat_long': lat_long,
                'date' : date,
                'max_temp' : max_temp,
                'min_temp' : min_temp
            })
            items_to_put.append(rev)
        
        self.client.put_multi(items_to_put)
        
        return True


    def update(self, month_temp: tuple) -> bool:
        """
        Updates entity in datastore.
        :param: month_temp: tuple (lat_long: str, date: str, max_temp: float, min_temp: float)
        :return: True
        """

        # Get key for month item to replace
        (lat_long, date, max_temp, min_temp) = month_temp
        query = self.client.query(kind = self.kind)
        query.add_filter("lat_long", "=", lat_long)
        query.add_filter("date", "=", date)
        query.keys_only()
        entities = query.fetch(limit=1)
        complete_key = entities.__next__().key.id

        # Replace item in DB
        key = self.client.key(self.kind, complete_key)
        rev = datastore.Entity(key)
        rev.update({
            'lat_long': lat_long,
            'date' : date,
            'max_temp' : max_temp,
            'min_temp' : min_temp
        })
        
        self.client.put(rev)

        return True


    def diff_months(self, beginning, end) -> int:
        """
        Finds difference in months between two dates.
        :param: beginning: datetime.date
        :param: end: datetime.date
        :return: Integer
        """
        return (end.year - beginning.year) * 12 + end.month - beginning.month
