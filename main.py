import datetime
import requests
import string
from flask import Flask, render_template, request, redirect, url_for


OWM_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"
OWM_FORECAST_ENDPOINT = "https://api.openweathermap.org/data/2.5/forecast"
GEOCODING_API_ENDPOINT = "http://api.openweathermap.org/geo/1.0/direct"

api_key = "27e15b0805a28f7ffa546b57b51f108c"

app = Flask(__name__)


def get_weather_data(city_name):
    try:
   
        location_params = {"q": city_name, "appid": api_key}
        location_response = requests.get(GEOCODING_API_ENDPOINT, params=location_params)
        location_response.raise_for_status()
        location_data = location_response.json()

     
        if location_data:
            lat = location_data[0]['lat']
            lon = location_data[0]['lon']
        else:
            raise ValueError("City coordinates not found")

        weather_params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
        weather_response = requests.get(OWM_ENDPOINT, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()


        forecast_response = requests.get(OWM_FORECAST_ENDPOINT, params=weather_params)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        return weather_data, forecast_data

    except requests.exceptions.RequestException as e:
      
        return None, None
    except ValueError as ve:
     
        return None, None


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        city = request.form.get("search")
        return redirect(url_for("get_weather", city=city))
    return render_template("index.html")


@app.route("/<city>", methods=["GET", "POST"])
def get_weather(city):

    city_name = string.capwords(city)
    today = datetime.datetime.now()
    current_date = today.strftime("%A, %B %d")


    weather_data, forecast_data = get_weather_data(city_name)

    if weather_data and forecast_data:
  
        current_temp = round(weather_data['main']['temp'])
        current_weather = weather_data['weather'][0]['main']
        min_temp = round(weather_data['main']['temp_min'])
        max_temp = round(weather_data['main']['temp_max'])
        wind_speed = weather_data['wind']['speed']

   
        five_day_temp_list = [round(item['main']['temp']) for item in forecast_data['list'] if '12:00:00' in item['dt_txt']]
        five_day_weather_list = [item['weather'][0]['main'] for item in forecast_data['list'] if '12:00:00' in item['dt_txt']]
        five_day_unformatted = [today + datetime.timedelta(days=i) for i in range(5)]
        five_day_dates_list = [date.strftime("%a") for date in five_day_unformatted]

        return render_template("city.html", city_name=city_name, current_date=current_date, current_temp=current_temp,
                               current_weather=current_weather, min_temp=min_temp, max_temp=max_temp, wind_speed=wind_speed,
                               five_day_temp_list=five_day_temp_list, five_day_weather_list=five_day_weather_list,
                               five_day_dates_list=five_day_dates_list)
    else:
  
        return redirect(url_for("error"))


@app.route("/error")
def error():
    return render_template("error.html")

if __name__ == "__main__":
    app.run(debug=True)
