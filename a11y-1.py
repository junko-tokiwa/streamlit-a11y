import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# Streamlitタイトル
st.title("WCAG2.2 AA アクセシビリティ自動チェックツール")

# URL入力欄
url = st.text_input("診断したいWebページのURLを入力してください")

# 診断開始ボタン
if st.button("診断開始"):
    # 結果表示用リスト
    results = []

    # URLからHTML取得
    try:
        res = requests.get(url)
        res.raise_for_status()
        html = res.text
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        st.error(f"ページの取得に失敗しました: {e}")
        st.stop()

    # コントラストチェック（簡易版）
    # すべてのテキスト要素を抽出
    for tag in soup.find_all(text=True):
        parent = tag.parent
        # style属性から色を抽出（本格的にはCSS解析が必要）
        style = parent.get("style", "")
        fg_match = re.search(r"color:\s*([^;]+);", style)
        bg_match = re.search(r"background(-color)?:\s*([^;]+);", style)
        fg = fg_match.group(1) if fg_match else "#000"
        bg = bg_match.group(2) if bg_match else "#fff"
        # コントラスト比計算（簡易: 実際は色変換・比率計算が必要）
        if fg != "#000" or bg != "#fff":
            # ここでコントラスト比を計算し、4.5:1未満なら指摘
            # 本格的にはcolormath等のライブラリを使う
            results.append({
                "問題点": f"⽂字⾊({fg})と背景⾊({bg})のコントラスト⽐が4.5:1未満の可能性があります。",
                "修正方法": "コントラスト⽐を4.5:1以上にしてください。",
                "達成基準": "1.4.3 コントラスト（最低限）（レベルAA）",
                "参考": "https://waic.jp/docs/WCAG21/Understanding/contrast-minimum.html"
            })

    # 結果表示
    if results:
        for r in results:
            st.markdown(f"### 問題点\n{r['問題点']}")
            st.markdown(f"### 修正方法（案）\n{r['修正方法']}")
            st.markdown(f"### 関連する達成基準\n{r['達成基準']}")
            st.markdown(f"### 参考\n{r['参考']}")
    else:
        st.success("問題は検出されませんでした！")
