import requests
import json
import sqlite3
import datetime
import pprint
import time

# Open Weather
# https://openweathermap.org/
# https://qiita.com/noritakaIzumi/items/34f16e383f59f9c5d8cf

class Weather():
    def __init__(self, proxies=False):
        latitude, longitude = 35.02625391921756, 137.0370839873832
        api_key = "3b241d7361b50161806f04c7b40d3452"
        self.url = "https://api.openweathermap.org/data/2.5/weather"
        self.params = {
            "lat": str(latitude),
            "lon": str(longitude),
            "appid": api_key,
            "units": "metric",
            "lang": "ja",
            "exclude": "current",
        }

        if proxies:
            self.proxies = {
                "http":"http://proxy.tns.toyota-body.co.jp:8080",
                "https":"http://proxy.tns.toyota-body.co.jp:8080"}              # プロキシ
        else:
            self.proxies = {
                "http": None,
                "https": None}

    def get_weather(self):
        cnt = 0
        while True:
            cnt += 1
            try:
                response = requests.get(self.url, params=self.params, proxies=self.proxies)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"エラー:{e}につき10秒待ちます")
                time.sleep(10)
            else:
                json_data = json.loads(response.text)
                print(f"{cnt}回でデータ取得できました")
                break
        dict = json2dict(json_data)
        return dict
    
def json2dict(json_data):
    dt = datetime.datetime.now()
    date = dt.strftime("%Y/%m/%d")
    time = dt.strftime("%H:%M")
    hour = dt.hour
    weather = json_data["weather"][0]["description"]
    temp = json_data["main"]["temp"]
    humidity = json_data["main"]["humidity"]
    rain = 1
    wind_speed = json_data["wind"]["speed"]
    icon = json_data["weather"][0]["icon"]
    if "rain" in json_data.keys():
        rain = json_data["rain"]["1h"]
    elif "snow" in json_data.keys():
        rain = json_data["snow"]["1h"]
    else:
        rain = 0    
    dict = {
        "date": date, 
        "time":time, 
        "hour":hour, 
        "weather":weather, 
        "rain":rain, 
        "temp":temp, 
        "humidity":humidity, 
        "wind_speed":wind_speed, 
        "icon":icon}
    return dict


def json2db(tenki):
    dt = datetime.datetime.now()
    date = dt.strftime("%Y/%m/%d")
    time = dt.strftime("%H:%M")
    hour = dt.hour
    weather = tenki["weather"][0]["description"]
    temp = tenki["main"]["temp"]
    humidity = tenki["main"]["humidity"]
    rain = 1
    wind_speed = tenki["wind"]["speed"]
    icon = tenki["weather"][0]["icon"]
    if "rain" in tenki.keys():
        rain = tenki["rain"]["1h"]
    elif "snow" in tenki.keys():
        rain = tenki["snow"]["1h"]
    else:
        rain = 0

    dbpath = ".\\static\\"
    dbname = "co2.db"
    conn = sqlite3.connect(dbpath + dbname)
    cur = conn.cursor()
    sql = f"INSERT INTO weather VALUES('{date}','{time}','{hour}','{weather}', {temp}, {humidity}, {rain}, {wind_speed}, '{icon}');" 
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()
    dict = {"date": date, "time":time, "hour":hour, "weather":weather, "rain":rain, "temp":temp, "humidity":humidity, "wind_speed":wind_speed, "icon":icon}
    pprint.pprint(dict)
    return json.dumps(dict)


def get_daily_tenki(date=None):
    if date is None:
        date = datetime.datetime.now().strftime("%Y/%m/%d")
    dbpath = ".\\static\\"
    dbname = "co2.db"
    conn = sqlite3.connect(dbpath + dbname)
    cur = conn.cursor()
    sql = f"SELECT * FROM weather WHERE date='{date}';" 
    cur.execute(sql)
    data_dict = {}
    for i, row in enumerate(cur.fetchall()):
        date, time, hour, weather, temp, humidity, rain, wind_speed, icon = row
        dict = {"date": date, "time":time, "hour":hour, "weather":weather, "rain":rain, "temp":temp, "humidity":humidity, "wind_speed":wind_speed, "icon":icon}
        data_dict[i] = dict
    cur.close()
    conn.close()
    return json.dumps(data_dict)


if __name__ == "__main__":
    w = Weather(proxies=False)
    weather = w.get_weather()
    print(weather)

#    tenki = get_tenki(proxies=None)
#    dict = json2db(tenki)
