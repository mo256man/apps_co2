import cv2

class Co2():
    # この機種のCO2はまるでデジタル時計のように2桁と2桁の間に隙間があり、4桁として扱うことができない
    def __init__(self):
        self.name = "CO2"                               # クラスオブジェクトの名前
        self.value = ""                                 # 値
        self.is_readable = False                        # 読み取ることができたかどうか
        self.width, self.height = 78, 132               # 7セグ文字の幅、高さ
        self.thickness, self.space = 18, 13             # セグメントの幅、文字間の隙間
        self.areas = [(31, 63), (225, 63)]              # 7セグ文字エリアの左上座標
        self.cnt = 2                                    # エリアの中に格納されている文字数
        self.pos = getPos(self)                         # 7セグ文字の各セグメントの座標
        self.lastminute = -1                            # データベースにUPDATEした時間の分

class Temperature():
    def __init__(self):
        self.name = "Temperature"
        self.value = ""
        self.is_readable = False
        self.width, self.height = 32, 54
        self.thickness, self.space = 8, 5
        self.areas = [(509, 58)]
        self.cnt = 2
        self.pos = getPos(self)
        self.lastminute = -1

class Humidity():
    def __init__(self):
        self.name = "Humidity"
        self.value = ""
        self.is_readable = False
        self.width, self.height = 32, 54
        self.thickness, self.space = 8, 5
        self.areas = [(511, 147)]
        self.cnt = 2
        self.pos = getPos(self)
        self.lastminute = -1

def getPos(obj):
    width = obj.width                                # 7セグ文字の幅
    height = obj.height                              # 7セグ文字の高さ
    thickness = obj.thickness                        # セグメントの幅
    
    # 7個のセグメントの座標
    xa, ya = width//2, thickness//2                     # 上
    xb, yb = width-thickness//2, height//4              # 右上
    xc, yc = xb, 3*yb                                   # 右下
    xd, yd = xa, height-thickness//2                    # 下
    xe, ye = thickness//2, yc                           # 左下
    xf, yf = xe, yb                                     # 左上
    xg, yg = xa, height//2                              # 中
    return [(xa,ya), (xb,yb), (xc,yc), (xd,yd), (xe,ye), (xf,yf), (xg,yg)]


DIGIT = {"0": [1,1,1,1,1,1,0],
         "1": [0,1,1,0,0,0,0],
         "2": [1,1,0,1,1,0,1],
         "3": [1,1,1,1,0,0,1],
         "4": [0,1,1,0,0,1,1],
         "5": [1,0,1,1,0,1,1],
         "6": [1,0,1,1,1,1,1],
         "7": [1,1,1,0,0,0,0],
         "8": [1,1,1,1,1,1,1],
         "9": [1,1,1,1,0,1,1],
         "-": [0,0,0,0,0,0,1],
         "_": [0,0,0,1,0,0,0],
         " ": [0,0,0,0,0,0,0],
         }


def read_7segs(image, obj):
    str_num = ""                                            # 読み取った数字が入る変数
    ret = True                                              # 正しく読み取れたかどうかの初期値はTrue
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)          # グレー化
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)  # 二値化
    for i in range(obj.cnt):                                # 7セグ数字の数だけループ
        x1 = i*(obj.width + obj.space)                      # 文字の左座標
        x2 = x1 + obj.width                                 # 右座標（左座標＋文字幅）
        roi = gray[:, x1:x2]                                # 1文字の画像
        seg = []                                            # セグメントオンオフ状況の初期値
        for pos in obj.pos:                                 # 1文字の中の各セグメント
            x, y = pos                                      # 注目する場所
            val = 1 if roi[y][x]==255 else 0                # そこの値によって1か0を取る
            seg.append(val)                                 # 配列変数に追加する
            image = cv2.circle(image, (x1+x,y), 3, (0,0,255), 1)       # 注目する場所を丸で囲む
        for key, value in DIGIT.items():                    # 数字辞書で
            if seg == value:                                # セグメントのオンオフ状況が一致したら
                str_num += key                              # そのキーの値を追加する
                break                                       # ループを抜ける
        else:                                               # ループを完走しなかったら　つまり数字辞書になかったら
            ret = False                                     # 結果をFalseにする
            str_num += "?"                                  # ?を追加する
    return ret, str_num, image


def readROI(image, obj):
    is_readable = True                                          # 全部正しく読み取れたかどうかの初期値
    str_value = ""                                              # 読み取り結果の初期値
    for x1, y1 in obj.areas:                                    # 各エリアの左上座標について
        x2 = x1 + obj.cnt*obj.width + (obj.cnt-1)*obj.space     # 右座標
        y2 = y1 + obj.height                                    # 下座標
        roi = image[y1:y2, x1:x2]                               # 7セグ文字があるエリア
        ret, val, roi = read_7segs(roi, obj)                    # エリア内の7セグ数字を読み取ると共に注目ポイントを丸で囲む
        image[y1:y2, x1:x2] = roi                               # 変更したROIを元画像に織り込む
        str_value += val                                        # それを結果に追加する
        if (not ret) or val.strip() == "":                      # 正しく読み取れていなかったら　もしくは　読み取り結果が全部" "で中身なしだったら
            is_readable = False                                 # 総合結果をFalseにする
        cv2.rectangle(image, (x1,y1), (x2,y2), (0,0,255), 1)
    obj.is_readable = is_readable
    obj.value = str_value.strip()                               # この時点ではまだ文字列


def read_value_in_image(image, objs):
    result = [True]                                             # 戻り値の初期値
    for obj in objs:
        readROI(image, obj)
        result.append(obj.value)
        if not obj.is_readable:
            result[0] = False
    return result

if __name__=="__main__":
    filename = "co2.jpeg"
    image = cv2.imread(filename)
    co2 = Co2()
    tmp = Temperature()
    hum = Humidity()

    ret, value_co2, value_tmp, value_hum = read_value_in_image(image, [co2, tmp, hum])
    print(ret, value_co2, value_tmp, value_hum)

    cv2.imshow("co2", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
