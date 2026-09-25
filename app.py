import streamlit as st
import pandas as pd
import random

# =========================
# ページ設定
# =========================

st.set_page_config(
    page_title="Campus Hive",
    page_icon="🐝",
    layout="centered"
)

st.title("🐝 Campus Hive")
st.write("蜂の群知能を利用した大学内マッチング実験")

# =========================
# 学生データ
# =========================

students = pd.DataFrame({
    "name": ["田中", "佐藤", "鈴木", "高橋", "伊藤", "山田"],
    "AI": [5, 2, 4, 1, 3, 5],
    "Python": [5, 1, 4, 2, 3, 5],
    "数学": [4, 2, 5, 1, 3, 4],
    "英語": [2, 5, 3, 4, 1, 2],
    "ゲーム": [1, 5, 4, 2, 5, 1],
    "旅行": [5, 3, 2, 4, 5, 2],
    "目的": [
        "勉強仲間",
        "友達",
        "ゲーム仲間",
        "勉強仲間",
        "旅行仲間",
        "プロジェクト仲間"
    ]
})

# =========================
# セッション状態
# =========================

if "target" not in st.session_state:
    st.session_state.target = None

if "memory" not in st.session_state:
    st.session_state.memory = {}

# =========================
# プロフィール
# =========================

st.header("👤 あなた")

name = st.text_input(
    "名前",
    placeholder="名前を入力"
)

purpose = st.selectbox(
    "探したい相手",
    [
        "友達",
        "勉強仲間",
        "プロジェクト仲間",
        "ゲーム仲間",
        "旅行仲間"
    ]
)

# =========================
# 探索
# =========================

st.header("🐝 探索")

if st.button("🐝 花を探索する", use_container_width=True):

    candidates = students[
        students["目的"] == purpose
    ]

    if len(candidates) > 0:

        target = candidates.sample(1).iloc[0]

        st.session_state.target = target

    else:
        st.warning("条件に合う相手が見つかりませんでした。")

# =========================
# 発見した相手
# =========================

if st.session_state.target is not None:

    target = st.session_state.target

    st.divider()

    st.header("🌸 発見した学生")

    st.subheader(target["name"])

    st.write(
        f"目的：{target['目的']}"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"AI：{'★' * target['AI']}")
        st.write(f"Python：{'★' * target['Python']}")
        st.write(f"数学：{'★' * target['数学']}")

    with col2:
        st.write(f"英語：{'★' * target['英語']}")
        st.write(f"ゲーム：{'★' * target['ゲーム']}")
        st.write(f"旅行：{'★' * target['旅行']}")

    st.divider()

    st.write("🤝 実際に交流したら、満足度を入力してください。")

    satisfaction = st.slider(
        "🍯 交流の満足度",
        min_value=1,
        max_value=5,
        value=3
    )

    if st.button(
        "🍯 経験を記録する",
        use_container_width=True
    ):

        target_name = target["name"]

        st.session_state.memory[target_name] = satisfaction

        st.success(
            f"🐝 {target_name}さんとの経験を記録しました！"
        )

        st.write(
            f"満足度：{'🍯' * satisfaction}"
        )

# =========================
# 自分の記憶
# =========================

if len(st.session_state.memory) > 0:

    st.divider()

    st.header("🧠 あなたの記憶")

    for person, score in st.session_state.memory.items():

        st.write(
            f"🌸 {person}：{'🍯' * score}"
        )