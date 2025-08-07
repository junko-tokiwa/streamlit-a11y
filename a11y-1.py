import streamlit as st
import requests
from bs4 import BeautifulSoup

st.title("シンプルWCAGチェックツール")

url = st.text_input("診断したいサイトのURLを入力してください")
if st.button("診断開始"):
    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        title = soup.title.string if soup.title else "タイトルが見つかりません"
        st.success(f"サイト名: {title}")
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")