import csv
import re
from io import StringIO
import requests
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
import streamlit as st

deseases = [
    'インフルエンザ','COVID-19','咽頭結膜熱','Ａ群溶血性レンサ球菌咽頭炎','感染性胃腸炎',
    '水痘','手足口病','伝染性紅斑','突発性発しん','百日咳',
    'ヘルパンギーナ','流行性耳下腺炎','急性出血性結膜炎','流行性角結膜炎','細菌性髄膜炎',
    '無菌性髄膜炎','マイコプラズマ肺炎','クラミジア肺炎','感染性胃腸炎（ロタウイルス）','RSウイルス（定点あたり報告数）',
]


### ページ設定
st.set_page_config(
    page_title="国立感染症研究所 速報データ",
    page_icon="🧫", # 🧪
    layout="wide"
)

st.title('国立感染症研究所 速報データ')
st.subheader('疾病毎定点当たり報告数　～過去10年間との比較～')

desease = st.selectbox('疾患:', deseases)

@st.cache_data
def load_data():
    base_url = "https://www.niid.go.jp"
    url = base_url + "/niid/ja/data.html"

    # IDWR速報データ
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    # csvファイルのリンク: 疾病毎定点当たり報告数　～過去10年間との比較～
    elem = soup.find(href=re.compile("trend.csv"))

    response = requests.get(base_url + elem.attrs['href'])
    response.encoding = 'shift-jis'
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

dfs = load_data()
df = dfs[desease]

color = ["#4E79A7CC","#F28E2BCC","#E15759CC","#76B7B2CC","#59A14FCC","#EDC948CC","#B07AA1CC","#FF9DA7CC","#9C755FCC","#BAB0ACCC", "#222f"]
st.line_chart(df, color=color)

st.text("出典: https://www.niid.go.jp/niid/ja/data.html")
