import csv
import re
from io import StringIO
import requests
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import niid


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
    df = niid.get_data()

    return df

dfs = load_data()
df = dfs[desease]

# Plotly
colors = px.colors.qualitative.Plotly
x = pd.date_range(start = '2020-1-1', end = '2020-12-31', freq = '7d')
fig = go.Figure()
# past 10 years
for c, color in zip(df.columns[:-1], colors):
    fig.add_trace(go.Scatter(x=x, y=df[c], mode='lines', name=c, line=dict(color=color)))
# this year
c = df.columns[-1]
color = '#444'
fig.add_trace(go.Scatter(x=x, y=df[c], mode='lines+markers', name=c, line=dict(color=color), marker=dict(color=color)))
# setting
fig.update_layout(xaxis=dict(tickformat="%b %d"), title=desease)

st.plotly_chart(fig, use_container_width=True)

st.text("出典: https://www.niid.go.jp/niid/ja/data.html")
