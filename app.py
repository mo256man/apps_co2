"""
起動するときはF5ではなく
streamlit run app.py
"""

import cv2
import streamlit as st
import streamlit.components.v1 as stc
import time
import datetime

from my_camera import *
from my_segment import *
from my_database import *

camera = Camera()
co2 = Co2()
tmp = Temperature()
hum = Humidity()
db = DB()

def main():
    last_date, last_time = db.get_last_datetime()                           # 直近のデータの日付と時刻
    last_datetime = f"{last_date} {last_time}"                              # 日付と時刻を合体したもの
    cap = cv2.VideoCapture(0)

    st_title = st.empty()
    column1, column2 = st.columns(2)
    with column1:
        st.markdown("##### カメラ画像")
        st_image1 = st.empty()
    with column2:
        st.markdown("##### 画像処理後")
        st_image2 = st.empty()
        st_co2 = st.empty()
        st_tmp = st.empty()
        st_hum = st.empty()
    st.write("")
    st.write("##### CO2グラフ")
    st_graph_co2 = st.empty()
    data = db.get_todays_data()
    st_graph_co2.line_chart(data["co2"])


    while True:
        now = datetime.datetime.now()                                       # 現在日時
        str_now = now.strftime("%Y/%m/%d %H:%M")                            # 現在日時を文字列にする
        camera.get_rect()
        ret, value_co2, value_tmp, value_hum = read_value_in_image(camera.image2, [co2, tmp, hum])
#        print(ret, value_co2, value_tmp, value_hum )
        image1 = camera.image1[:, :, ::-1]                                  # RGB -> BGR
        image2 = camera.image2[:, :, ::-1]
        st_image1.image(image1)
        st_image2.image(image2)
        st_co2.write(f"##### CO2濃度：{value_co2}ppm")
        st_tmp.write(f"##### 温度：{value_tmp}%")
        st_hum.write(f"##### 湿度：{value_hum}%")
        st_title.write(f"#### 環境自動記録システム　　　　{str_now}")
        time.sleep(1)
        # 10分に1回データを更新する
        if str_now[:-1] != last_datetime[:-1] and ret:                      # 分の十の位が変わり、データが有効ならば
            last_datetime = str_now                                         # 前回の分を更新する
            str_date = now.strftime("%Y/%m/%d")
            str_time = now.strftime("%H:%M")
            print(str_time, "データ追加")
            sql = f"INSERT INTO sensor VALUES('{str_date}', '{str_time}', {value_co2}, {value_tmp}, {value_hum});" 
            db.execute(sql)

            data = db.get_todays_data()
            st_graph_co2.line_chart(data["co2"])


if __name__ == "__main__":
    main()

cv2.destroyAllWindows()
