from datetime import date
import gbmodel
from geopy.geocoders import Nominatim
import requests

class DataManager():

    def __init__(self):
        """
        Manages interactions between DB and APIs -- Nominatim and Open-Meteo 
        Historical Weather.
        """
        self.geolocator = Nominatim(user_agent="User")
        self.model = gbmodel.get_model()


    def update_location_in_db(self, location: str) -> list:
        """
        Updates monthly entries for location in the database using its latitude and
        longitude coordinates. If location does not exist in DB, then it is created,
        and all entries are added. If location does not exist globally, then no
        changes are made.

        IMPORTANT: This SHOULD be run before getting widget or graph data to get
        API data.

        :param: location: String
        :return: List of tuples with all month entries for the city.
        """
        lat_long = self.get_location_lat_long(location)
        todays_date = self.get_current_date("%Y-%m-%d")
        if lat_long is None:
            return []

        db_items = self.model.select(lat_long)

        if db_items == []:
            # Calculate all month's highs and lows
            api_items = self.get_weatherapi_data(lat_long, "2000-01-01", todays_date)
            self.model.insert(self.calculate_monthly_temps(api_items, lat_long))
        else:
            # Calculate all recent month's highs and lows
            most_recent_date = db_items[-1][1]

            api_items = self.get_weatherapi_data(lat_long, most_recent_date + "-01", todays_date)
            month_items_for_db = self.calculate_monthly_temps(api_items, lat_long)

            self.model.update(month_items_for_db[0])
            month_items_for_db.pop(0)

            self.model.insert(month_items_for_db)

        # Return updated DB items for location
        return self.model.select(lat_long)


    def get_widget_data(self, db_items: list) -> dict:
        """
        Uses DB data for a location to find the max/min temp for the current
        month and percent difference from the year prior.
        :param: db_items: list of items returned from update_location_in_db()
        :return: Dictionary {"max_temp": float, "min_temp": float, "percent_diff": float}
        """
        max_temp = db_items[-1][2]        
        min_temp = db_items[-1][3]      

        # If less than one year of data in DB, then let percent_difference be infinite  
        try:
            last_year_weather_item = db_items[-13]
            percent_difference = round(max_temp / last_year_weather_item[2] * 100 - 100, 2)
        except IndexError:
            percent_difference = float("inf")

        return {"max_temp": max_temp, "min_temp": min_temp, "percent_diff": percent_difference}


    def get_graph_data(self, db_items: list) -> dict:
        """
        Reformats the db_items into three lists in a dictionary to be read by the
        HTML/JavaScript.
        :param: db_items: List of items returned from update_location_in_db()
        :return: Dictionary {"dates": list, "max_temps": list, "min_temps": list}
        """
        months = []
        max_temps = []
        min_temps = []
        for item in db_items:
            months.append(item[1])
            max_temps.append(item[2])
            min_temps.append(item[3])

        return {"dates": months, "max_temps": max_temps, "min_temps": min_temps}


    def calculate_monthly_temps(self, daily_temps: list, lat_long: str) -> list:
        """
        Condenses daily temperature data from a given location into monthly mins
        and maxes.
        :param: daily_temps: List
        :param: lat_long: String
        :return: List of monthly temperature items ready for DB
        """
        if daily_temps == []:
            return []

        curr_max = float("-inf")
        curr_min = float("inf")
        monthly_data = []
        prev_month = curr_month = daily_temps[0][0][0:7]

        # Find min and max for each month given daily temperatures
        for (date, max, min) in daily_temps:
            prev_month = curr_month
            curr_month = date[0:7]
            # Append current min and max for a month after reaching next month
            if prev_month != curr_month:
                monthly_data.append((lat_long, prev_month, curr_max, curr_min))
                curr_max = float("-inf")
                curr_min = float("inf")

            curr_max = max if max > curr_max else curr_max
            curr_min = min if min < curr_min else curr_min

        monthly_data.append((lat_long, curr_month, curr_max, curr_min))

        return monthly_data


    def get_weatherapi_data(self, lat_long: str, start: str, end: str) -> list:
        """
        Sends request to the Weather API for daily weather temperatures between
        beginning and end date. Sorts response to move any null values returned.
        :param: lat_long: String
        :param: beginning: String
        :param: end: String
        :return: List containing valid daily weather items 
        """
        url = 'https://archive-api.open-meteo.com/v1/era5'
        coords = lat_long.split(',')
        response = requests.get(f'{url}?latitude={coords[0]}&longitude={coords[1]}&start_date={start}&end_date={end}&daily=temperature_2m_max,temperature_2m_min&timezone=America%2FLos_Angeles&temperature_unit=fahrenheit').json()["daily"]
        return self.filter_weatherapi_data(response)


    def filter_weatherapi_data(self, api_items: dict) -> list:
        """
        Sorts through the raw API data and removes any null items it sent back.
        :param: api_items: Dictionary from API
        :return: List of tuples containing the days, max temps and min temps.
        """
        filtered_items = []

        dates = api_items["time"]
        mins = api_items["temperature_2m_min"]
        maxes = api_items["temperature_2m_max"]
        
        for (date, max, min) in zip(dates, maxes, mins):
            if max is not None:
                filtered_items.append((date, max, min))
        
        return filtered_items


    def get_location_lat_long(self, location_name: str) -> str:
        """
        Uses the Nominatim API to turn a location name into a lat/long coordinates.
        :param: location_name: String
        :return: String of coordinations "lat,long"
        """
        location = self.geolocator.geocode(location_name)
        return None if location is None else str(location.latitude)+','+str(location.longitude)


    def get_location_address(self, location_name: str) -> str:
        """
        Uses Nominatim API to turn location name into the location used by Nominatim.
        :param: location_name: String
        :return: String of formal location name
        """
        location = self.geolocator.geocode(location_name)
        return None if location is None else location.address


    def get_current_date(self, format: str = "%Y-%m") -> str:
        """
        Gets current formatted date.
        :param: format: String
        :return: String of date
        """
        return date.today().strftime(format)
    

    def get_month_from_number(self, number: int) -> str:
        """
        Gets the month from month number.
        :param: number: Integer
        :return: String of month name
        """
        if number < 1 or number > 12:
            return "Month"
        
        requested_date = date(2000, number, 1)
        return requested_date.strftime("%B")
