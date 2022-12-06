"""
A Weather History Web App to observe monthly temperature changes across the global.
"""
import flask
from weather import Weather

app = flask.Flask(__name__) 

app.add_url_rule('/',
                 view_func=Weather.as_view('weather'),
                 methods=['GET', 'POST'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
