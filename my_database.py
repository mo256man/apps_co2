import sqlite3
import datetime
import pprint
import pandas as pd
import time

class DB():
    def __init__(self, has_proxy=False):
        self.dbname = "co2.db"

    def execute(self, sql, ret=0):
        """
        sqlを実行する
        ret　0:戻り値なし/ 1:fetchone / 2:fetchall
        """
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute(sql)
        if ret == 1:
            result = cur.fetchone()
        elif ret == 2:
            result = cur.fetchall()
        else:
            conn.commit()
            result = None
        cur.close()
        conn.close()
        return result


    def get_last_datetime(self):
        """
        最新データの日時を取得する
        """
        sql = "SELECT date, MAX(time) FROM sensor WHERE date=(SELECT MAX(date) FROM sensor);"
        return self.execute(sql, 1)


    def get_todays_data(self):
        """
        今日のデータを取得する
        """
        today = datetime.datetime.now().strftime("%Y/%m/%d")
        sql = f"SELECT * FROM sensor WHERE date='{today}';"
        data = self.execute(sql, 2)

        # df定義
        times = [[f"{h:0=2}:{10*m:0=2}" for m in range(6)] for h in range(7, 20)]   # 二重の内包表記でhh:m0を作る
        times = sum(times, [])                                                      # 二重のリストを平坦化
        nulls = [None for i in range(len(times))]                                   # timesと同数のNone
        dict = {"co2":nulls, "tmp":nulls, "hum":nulls}                              # 辞書化
        df = pd.DataFrame(data=dict, index=times)                                   # データフレーム定義

        # dfにデータを追記する
        for row in data:
            tim = row[1][:-1] + "0"                                                 # 時刻をhh:m0分にする
            if tim in times:                                                        # その時刻がtimesの中にあったら
                df.at[tim, "co2"] = row[2]
                df.at[tim, "tmp"] = row[3]
                df.at[tim, "hum"] = row[4]

        return df

