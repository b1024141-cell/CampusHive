import streamlit as st
from supabase import create_client, Client
import random

st.set_page_config(
    page_title="Campus Hive",
    page_icon="🐝",
    layout="centered"
)

# -------------------------
# Supabase接続
# -------------------------
@st.cache_resource
def init_connection() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()


# -------------------------
# タイトル
# -------------------------
st.title("🐝 Campus Hive")
st.write("蜂の群知能を利用した大学生向けマッチングアプリ")

st.divider()


# -------------------------
# プロフィール登録
# -------------------------
st.header("🌸 プロフィールを登録")

with st.form("profile_form"):

    name = st.text_input(
        "名前・ニックネーム",
        placeholder="例：あずみ"
    )

    grade = st.selectbox(
        "学年",
        ["1年", "2年", "3年", "4年", "大学院生"]
    )

    department = st.text_input(
        "学科",
        placeholder="例：複雑系知能学科"
    )

    purpose = st.multiselect(
        "探したい相手",
        [
            "友達",
            "勉強仲間",
            "プロジェクト仲間",
            "ゲーム仲間",
            "旅行仲間",
            "趣味仲間",
            "就活仲間"
        ]
    )

    strength = st.text_input(
        "得意なこと",
        placeholder="例：Python、数学、AI"
    )

    weakness = st.text_input(
        "苦手・教えてほしいこと",
        placeholder="例：英語、プレゼン"
    )

    hobby = st.text_input(
        "趣味",
        placeholder="例：ゲーム、旅行、カフェ巡り"
    )

    introduction = st.text_area(
        "自己紹介",
        placeholder="自分について自由に書いてください"
    )

    submitted = st.form_submit_button(
        "🐝 プロフィールを登録する"
    )


if submitted:

    if name.strip() == "":
        st.warning("名前・ニックネームを入力してください。")

    elif len(purpose) == 0:
        st.warning("探したい相手を1つ以上選択してください。")

    else:

        try:

            supabase.table("profiles").insert({
                "name": name,
                "grade": grade,
                "department": department,
                "purpose": ", ".join(purpose),
                "strength": strength,
                "weakness": weakness,
                "hobby": hobby,
                "introduction": introduction
            }).execute()

            st.success(
                f"🐝 {name}さんのプロフィールを登録しました！"
            )

            st.rerun()

        except Exception as e:

            st.error("プロフィールの登録に失敗しました。")
            st.code(str(e))


st.divider()


# -------------------------
# 登録メンバー取得
# -------------------------
st.header("🐝 探索")

try:

    response = (
        supabase
        .table("profiles")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    profiles = response.data

except Exception as e:

    st.error("プロフィールを読み込めませんでした。")
    st.code(str(e))
    profiles = []


# -------------------------
# 探索機能
# -------------------------
if len(profiles) >= 2:

    st.write(
        "あなたのプロフィールを選択して、他のメンバーを探索してみましょう。"
    )

    profile_names = [
        person["name"]
        for person in profiles
    ]

    my_name = st.selectbox(
        "🐝 あなたは誰ですか？",
        profile_names
    )

    my_profile = next(
        person for person in profiles
        if person["name"] == my_name
    )

    candidates = [
        person
        for person in profiles
        if person["id"] != my_profile["id"]
    ]

    if "target" not in st.session_state:

        st.session_state.target = random.choice(candidates)

    if st.button("🌼 新しい相手を探索する"):

        st.session_state.target = random.choice(candidates)

    target = st.session_state.target

    st.divider()

    st.subheader(
        f"🌸 {target['name']}さんを発見しました！"
    )

    st.write(
        f"🎓 {target['grade']} / {target['department']}"
    )

    st.write(
        f"🔎 探している相手：{target['purpose']}"
    )

    if target["strength"]:
        st.write(
            f"💪 得意：{target['strength']}"
        )

    if target["weakness"]:
        st.write(
            f"📚 教えてほしい：{target['weakness']}"
        )

    if target["hobby"]:
        st.write(
            f"🎮 趣味：{target['hobby']}"
        )

    if target["introduction"]:
        st.write(
            f"💬 {target['introduction']}"
        )

    st.divider()

    # -------------------------
    # 交流評価
    # -------------------------

    st.subheader("🍯 この人との交流を評価")

    satisfaction = st.slider(
        "満足度",
        min_value=1,
        max_value=5,
        value=3
    )

    comment = st.text_area(
        "感想（任意）",
        placeholder="例：Pythonについて話せて楽しかった！"
    )

    if st.button("🍯 評価を保存する"):

        try:

            supabase.table("experiences").insert({
                "bee_id": my_profile["id"],
                "flower_id": target["id"],
                "satisfaction": satisfaction,
                "comment": comment
            }).execute()

            st.success(
                "🐝 交流経験を記録しました！"
            )

        except Exception as e:

            st.error("評価の保存に失敗しました。")
            st.code(str(e))

else:

    st.info(
        "探索するには、2人以上のプロフィール登録が必要です。"
    )


st.divider()


# -------------------------
# メンバー一覧
# -------------------------
st.header("🌼 Campus Hive のメンバー")

for person in profiles:

    with st.container(border=True):

        st.subheader(
            f"🌸 {person['name']}"
        )

        st.write(
            f"🎓 {person['grade']} / {person['department']}"
        )

        st.write(
            f"🔎 探している相手：{person['purpose']}"
        )

        if person["strength"]:
            st.write(
                f"💪 得意：{person['strength']}"
            )

        if person["weakness"]:
            st.write(
                f"📚 教えてほしい：{person['weakness']}"
            )

        if person["hobby"]:
            st.write(
                f"🎮 趣味：{person['hobby']}"
            )

        if person["introduction"]:
            st.write(
                f"💬 {person['introduction']}"
            )
