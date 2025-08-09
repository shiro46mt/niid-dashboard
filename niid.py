import csv
import re
from io import StringIO
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import requests


deseases = [
    'インフルエンザ','COVID-19','咽頭結膜熱','Ａ群溶血性レンサ球菌咽頭炎','感染性胃腸炎',
    '水痘','手足口病','伝染性紅斑','突発性発しん','百日咳',
    'ヘルパンギーナ','流行性耳下腺炎','急性出血性結膜炎','流行性角結膜炎','細菌性髄膜炎',
    '無菌性髄膜炎','マイコプラズマ肺炎','クラミジア肺炎','感染性胃腸炎（ロタウイルス）','RSウイルス（定点あたり報告数）',
]


def get_data():
    index_url = "https://id-info.jihs.go.jp/surveillance/idwr/index.html"

    # IDWR速報データ
    response = requests.get(index_url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')

    # 最新週へのリンク
    elem = soup.find('a', href=re.compile('idwr/jp/rapid'))
    latest_page_url = urljoin(index_url, elem.attrs['href'])

    # 最新週のページ
    response = requests.get(latest_page_url)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')

    # csvファイルのリンク: 疾病毎定点当たり報告数　～過去10年間との比較～
    elem = soup.find('a', href=re.compile(r"trend\.csv"))
    csv_url = urljoin(latest_page_url, elem.attrs['href'])

    # csvファイルの読み込み
    response = requests.get(csv_url)
    response.encoding = response.apparent_encoding
    reader = csv.reader(StringIO(response.text))

    # csvファイルの読み込み
    data = {}
    _desease = ''
    for row in reader:
        # 疾患名の行 -> 初期化
        if row[0] in deseases:
            _desease = row[0]
            data[_desease] = []
        # ヘッダー行 -> スキップ
        elif _desease == '':
            continue
        # データ行 -> 追加
        elif row[0] != '':
            data[_desease].append(row)

    # 疾患別にDataFrameに格納
    cols = ['年'] + list(range(1, 54))
    dfs = {}
    for desease in deseases:
        df = pd.DataFrame(data[desease], columns=cols)
        df['年'] = df['年'].apply(lambda x: '20' + x)
        dfs[desease] = df.set_index('年').T.replace(['', '-'], np.nan).astype(float)

    return dfs


if __name__ == "__main__":
    df = get_data()
    print(df)
