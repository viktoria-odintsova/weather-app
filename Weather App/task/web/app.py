from flask import Flask, request, render_template, redirect, flash
from json import loads
from flask_sqlalchemy import SQLAlchemy
import sys
import requests

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        return self.name


db.create_all()


def get_weather_info(city_name):
    params = {'q': city_name, 'appid': 'your openweather API key', 'units': 'metric'}
    r = requests.get("http://api.openweathermap.org/data/2.5/weather", params=params)
    data = loads(r.text)
    weather_state = data["weather"][0]["main"]
    temp = data["main"]["temp"]
    city = City.query.filter_by(name=city_name.name).first()
    return {'city': city_name, 'temp': temp, 'state': weather_state, 'id': city.id}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city_name = request.form['city_name']
        params = {'q': city_name, 'appid': 'aa53684ca290cddd3fadf90f05c75270', 'units': 'metric'}
        r = requests.get("http://api.openweathermap.org/data/2.5/weather", params=params)
        if r.status_code == 404:
            flash("The city doesn't exist!")
        else:
            new_city = City(name=city_name)
            if db.session.query(City).filter_by(name=city_name).count() < 1:
                db.session.add(new_city)
                db.session.commit()
            else:
                flash("The city has already been added to the list!")
    cities = City.query.all()
    weather_info = []
    for city in cities:
        weather_info.append(get_weather_info(city))
    return render_template('index.html', weather=weather_info)


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


@app.route('/profile')
def profile():
    return 'This is profile page'


@app.route('/login')
def log_in():
    return 'This is login page'


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
