from data_manager import DataManager
from flask import request, render_template
from flask.views import MethodView

class Weather(MethodView):

    def __init__(self):
        """
        Manages requests to the '/' page of the web app.
        """
        self.data_manager = DataManager()
    

    def get(self):
        """
        Accepts GET requests, and loads the empty weather page.
        """
        return render_template('weather.html', maxtemp='-', mintemp='-', address='None', month='Month')


    def post(self):
        """
        Accepts POST requests, processes the form, and reloads the page with
        weather data from a particular location if appropriate.
        """
        text_input = request.form['location']
        select_input = request.form['preset']
        location = select_input if select_input != 'none' else text_input

        db_items = self.data_manager.update_location_in_db(location)
        if db_items == []:
            return self.get()

        widget_data = self.data_manager.get_widget_data(db_items)
        graph_items = self.data_manager.get_graph_data(db_items)
        address = self.data_manager.get_location_address(location)
        month = self.data_manager.get_month_from_number(int(db_items[-1][1][5:]))

        return render_template('weather.html', max_temp=widget_data["max_temp"], min_temp=widget_data["min_temp"], percent=widget_data["percent_diff"], location=location, address=address, month=month, graph_maxes=graph_items["max_temps"], graph_mins=graph_items["min_temps"], graph_labels=graph_items["dates"])
        