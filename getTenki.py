import requests
import json
import sqlite3
import datetime
import pprint
import time

# Open Weather
# https://openweathermap.org/
# https://qiita.com/noritakaIzumi/items/34f16e383f59f9c5d8cf

def get_tenki():
    latitude, longitude = 35.02625391921756, 137.0370839873832
    api_key = "3b241d7361b50161806f04c7b40d3452"
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": str(latitude),
        "lon": str(longitude),
        "appid": api_key,
        "units": "metric",
        "lang": "ja",
        "exclude": "current",
    }
    proxies = {"http":"http://proxy.tns.toyota-body.co.jp:8080",
            "https":"http://proxy.tns.toyota-body.co.jp:8080"}              # プロキシ

    i=0
    while True:
        try:
            i += 1
            print(f"データ取得 {i}回目")
#            response = requests.get(url, params=params, proxies=proxies)
            response = requests.get(url, params=params)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"エラー:{e}につき10秒待ちます")
            time.sleep(10)
        else:
            json_data = json.loads(response.text)
            print("正常に処理されました")
            break


    return json_data

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
    tenki = get_tenki(proxies=None)
    dict = json2db(tenki)
