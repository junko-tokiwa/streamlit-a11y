import streamlit as st
import requests
from bs4 import BeautifulSoup
from color_contrast_calc import Color, ratio
import re
# Playwright関連は必要に応じて加筆

def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.error(f"ページ取得に失敗しました: {e}")
        return None

def get_styles(soup):
    # 簡易にインラインstyleやstyle属性を抽出
    styles = {}
    for tag in soup.find_all(True):
        color = tag.get('color') or tag.get('style')
        bg = tag.get('background-color') or tag.get('style')
        text = tag.get_text(strip=True)
        if color or bg:
            styles[text] = (color, bg)
    return styles

def parse_style(style_str):
    # styleから色情報取得
    color_match = re.search(r'color:\s*([^;]+)', style_str or '', re.I)
    bg_match = re.search(r'background-color:\s*([^;]+)', style_str or '', re.I)
    return (color_match.group(1).strip() if color_match else None,
            bg_match.group(1).strip() if bg_match else None)

def check_contrast(text_color, bg_color):
    if not text_color or not bg_color:
        return None
    try:
        col1 = Color(text_color)
        col2 = Color(bg_color)
        ratio_val = ratio(col1, col2)
        return ratio_val
    except Exception:
        return None

def analyze_contrast(soup):
    results = []
    for tag in soup.find_all(True):
        text = tag.get_text(strip=True)
        if not text:
            continue
        style = tag.get('style')
        if style:
            text_color, bg_color = parse_style(style)
            contr = check_contrast(text_color, bg_color)
            if contr and contr < 4.5:
                # 以下でフォーマットする
                results.append({
                    "problem": f"⽂字「{text}」の⽂字⾊({text_color})と背景⾊({bg_color})のコントラスト⽐が4.5:1未満です（{contr:.2f}:1）",
                    "solution": "⽂字⾊や背景⾊を調整し、コントラスト⽐を4.5:1以上にしてください。",
                    "criteria": "1.4.3 コントラスト（最小値）",
                    "reference": "https://waic.jp/docs/WCAG21/Understanding/contrast-minimum.html"
                })
    return results

def render_results(results):
    for res in results:
        st.markdown(f"""
        ### 問題点
        {res.get('problem')}
        ### 修正方法（案）
        {res.get('solution')}
        ### 関連する達成基準
        {res.get('criteria')}
        ### 参考
        {res.get('reference')}
        """)

st.title("WCAG2.2 AA アクセシビリティ自動チェックツール")
url = st.text_input("診断したいサイトのURLを入力してください")
if st.button("診断開始"):
    html = fetch_html(url)
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        results = analyze_contrast(soup)
        if results:
            render_results(results)
        else:
            st.success("主なコントラスト問題は見つかりませんでした")