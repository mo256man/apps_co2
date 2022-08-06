import cv2
import numpy as np
import datetime
import csv
import random
from cv2 import aruco
from my_segment import *
import pandas as pd
import base64
import json

def img2base64(imgCV):
    _, imgEnc = cv2.imencode(".png", imgCV)                             # エンコードされたオブジェクト
    imgB64 = base64.b64encode(imgEnc)                                   # byte
    strB64 = str(imgB64, "utf-8")                                       # string
    return strB64


class Camera():
    def __init__(self):
        # カメラ初期設定
        self.cam = cv2.VideoCapture(0)
        self.dic_aruco = aruco.Dictionary_get(aruco.DICT_4X4_50)
        self.frameW, self.frameH = 640, 480                                     # カメラサイズ定義
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.frameW)                     # カメラサイズ指定
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frameH)

        # マーカー四角形の指定
        self.preset_ids = [0, 1, 2, 3]                                          # 現実世界で貼るマーカーのid　左上から時計回り
        self.preset_corner_ids = [1, 0, 3, 2]                                   # 各マーカーのどの頂点の座標を取得するか
        self.rectW, self.rectH = 270+5, 90                                      # 長方形の実サイズ（単位はmm）
        self.rectH = int(self.rectH*self.frameW/self.rectW)                     # 長方形の高さを実サイズの縦横比に合わせて拡大する
        self.rectW = self.frameW                                                # 長方形の幅をカメラサイズと同じにする
        self.pts2 = np.float32(
            [(0,0), (self.rectW,0), (self.rectW, self.rectH), (0,self.rectH)])  # 長方形座標

        # 一つ前の有効画像の初期値　画像取得できなかったときに使う
        self.last_frame = np.zeros((self.frameH, self.frameW, 3), np.uint8)
        self.last_rect = np.zeros((self.rectH, self.rectW, 3), np.uint8)


    def get_rect(self):
        # カメラ映像取得
        ret, frame = self.cam.read()                                            # カメラ映像を取得する
        if ret:                                                                 # 映像を正しく取得できたら  
            self.last_frame = cv2.rectangle(frame.copy(), (0,0), (self.frameW, self.frameH), (0,0,0), 3)     # 一つ前のフレームとしても覚えておく
        else:                                                                   # 映像を正しく取得できなかったら
            frame = self.last_frame                                             # 前のフレームを使う

        # マーカー検出
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)                          # グレースケールにする
        corners, ids, _ = aruco.detectMarkers(gray, self.dic_aruco)             # マーカー検出
        image1 = aruco.drawDetectedMarkers(frame.copy(), corners, ids)          # 検出結果を重ね書き

        # 4個のマーカーから四角形を得る
        list_ids = np.ravel(ids)                                                # idsを一次元化する
        if set(self.preset_ids) <= set(list_ids):                               # 検出結果に4個のidが含まれていたら
            pt = {}
            for id, corner in zip(list_ids, corners):                           # まずは検出結果について
                pt[id] = corner[0]                                              # idとcornerを紐づける
            pts = []
            for id, corner_id in zip(self.preset_ids, self.preset_corner_ids):  # 次に事前登録した4個のidについて
                pts.append(pt[id][corner_id])                                   # 特定の頂点の座標を順にリストに追加する
            pts1 = np.float32(pts)                                              # 投影変換する前の四角形

            M = cv2.getPerspectiveTransform(pts1, self.pts2)                    # 投影行列
            rect = cv2.warpPerspective(frame, M, (self.rectW, self.rectH))      # 長方形画像を得る

            pts1 = np.int32(pts1)                                               # 今度は整数にして
            image1 = cv2.polylines(image1, [pts1], True, (0,0,255), 2)          # 各頂点を線で結ぶ  
            self.image2 = rect                                                  # 投影変換で得られた長方形画像
            # self.last_rect = rect                                               # 一つ前の長方形画像としても覚えておく

        else:                                                                   # 検出結果に4個のidが含まれていなかったら
            self.image2 = self.last_rect                                        # 前の長方形画像を使う

        self.image1 = image1


def main():
    cam = Camera()

    while True:
        cam.get_rect()
        cv2.imshow("image1", cam.image1)
        cv2.imshow("image2", cam.image2)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

if __name__ == "__main__":
    main()