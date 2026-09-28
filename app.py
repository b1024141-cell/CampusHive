import streamlit as st
from supabase import create_client, Client
import random

# =========================
# ページ設定
# =========================

st.set_page_config(
    page_title="Campus Hive",
    page_icon="🐝",
    layout="centered"
)


# =========================
# Supabase接続
# =========================

@st.cache_resource
def init_connection() -> Client:

    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]

    return create_client(url, key)


supabase = init_connection()


# =========================
# タイトル
# =========================

st.title("🐝 Campus Hive")

st.write(
    "蜂の群知能を利用した大学生向けマッチングアプリ"
)

st.divider()


# ==================================================
# プロフィール登録
# ==================================================

st.header("🌸 プロフィールを登録")


with st.form("profile_form"):

    name = st.text_input(
        "名前・ニックネーム",
        placeholder="例：あずみ"
    )

    grade = st.selectbox(
        "学年",
        [
            "1年",
            "2年",
            "3年",
            "4年",
            "大学院生"
        ]
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


# =========================
# プロフィール登録処理
# =========================

if submitted:

    if name.strip() == "":

        st.warning(
            "名前・ニックネームを入力してください。"
        )

    elif len(purpose) == 0:

        st.warning(
            "探したい相手を1つ以上選択してください。"
        )

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

            st.error(
                "プロフィールの登録に失敗しました。"
            )

            st.code(str(e))


st.divider()


# ==================================================
# プロフィール取得
# ==================================================

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

    st.error(
        "プロフィールを読み込めませんでした。"
    )

    st.code(str(e))

    profiles = []


# ==================================================
# 探索機能
# ==================================================

if len(profiles) >= 2:

    st.write(
        "あなたのプロフィールを選択して、"
        "他のメンバーを探索してみましょう。"
    )


    # -------------------------
    # 自分を選択
    # -------------------------

    profile_names = [
        person["name"]
        for person in profiles
    ]


    my_name = st.selectbox(
        "🐝 あなたは誰ですか？",
        profile_names
    )


    my_profile = next(
        person
        for person in profiles
        if person["name"] == my_name
    )


    # -------------------------
    # 探索候補
    # -------------------------

    candidates = [

        person
        for person in profiles
        if person["id"] != my_profile["id"]

    ]


    # ==================================================
    # 群れの経験データ取得
    # ==================================================

    try:

        experience_response = (
            supabase
            .table("experiences")
            .select("*")
            .execute()
        )

        experiences = experience_response.data

    except Exception as e:

        st.error(
            "交流データを読み込めませんでした。"
        )

        st.code(str(e))

        experiences = []


    # ==================================================
    # 群れスコア計算
    # ==================================================

    swarm_scores = {}


    for person in candidates:

        # この人に対する過去の評価
        person_experiences = [

            experience
            for experience in experiences

            if experience["flower_id"] == person["id"]

        ]


        # 評価が存在する場合
        if len(person_experiences) > 0:

            average = (

                sum(
                    experience["satisfaction"]
                    for experience in person_experiences
                )

                / len(person_experiences)

            )

        # 評価がない場合
        else:

            average = 0


        swarm_scores[person["id"]] = average


    # ==================================================
    # 探索ボタン
    # ==================================================

    if st.button(
        "🌼 群れの情報を使って探索する"
    ):

        # 評価された候補
        evaluated_candidates = [

            person
            for person in candidates

            if swarm_scores[person["id"]] > 0

        ]


        # 評価がある場合
        if evaluated_candidates:

            # 現在は最も評価が高い人を選ぶ
            target = max(

                evaluated_candidates,

                key=lambda person:
                swarm_scores[person["id"]]

            )


        # 評価がない場合
        else:

            # ランダム探索
            target = random.choice(
                candidates
            )


        st.session_state.target = target


    # ==================================================
    # 探索結果
    # ==================================================

    if "target" in st.session_state:

        target = st.session_state.target


        st.divider()


        st.subheader(
            f"🌸 {target['name']}さんを発見しました！"
        )


        # -------------------------
        # プロフィール表示
        # -------------------------

        st.write(
            f"🎓 {target['grade']} / "
            f"{target['department']}"
        )


        st.write(
            f"🔎 探している相手："
            f"{target['purpose']}"
        )


        if target["strength"]:

            st.write(
                f"💪 得意：{target['strength']}"
            )


        if target["weakness"]:

            st.write(
                f"📚 教えてほしい："
                f"{target['weakness']}"
            )


        if target["hobby"]:

            st.write(
                f"🎮 趣味：{target['hobby']}"
            )


        if target["introduction"]:

            st.write(
                f"💬 {target['introduction']}"
            )


        # -------------------------
        # 群れスコア
        # -------------------------

        score = swarm_scores[
            target["id"]
        ]


        if score > 0:

            st.info(
                f"🐝 群れからの平均評価："
                f"{score:.1f} / 5"
            )

        else:

            st.info(
                "🐝 まだ群れからの評価はありません。"
            )


        st.divider()


        # ==================================================
        # 交流評価
        # ==================================================

        st.subheader(
            "🍯 この人との交流を評価"
        )


        satisfaction = st.slider(
            "満足度",
            min_value=1,
            max_value=5,
            value=3
        )


        comment = st.text_area(
            "感想（任意）",
            placeholder=(
                "例：Pythonについて話せて楽しかった！"
            )
        )


        # -------------------------
        # 評価保存
        # -------------------------

        if st.button(
            "🍯 評価を保存する"
        ):

            try:

                supabase.table(
                    "experiences"
                ).insert({

                    "bee_id":
                        my_profile["id"],

                    "flower_id":
                        target["id"],

                    "satisfaction":
                        satisfaction,

                    "comment":
                        comment

                }).execute()


                st.success(
                    "🐝 交流経験を記録しました！"
                )


                st.rerun()


            except Exception as e:

                st.error(
                    "評価の保存に失敗しました。"
                )

                st.code(str(e))


else:

    st.info(
        "探索するには、2人以上のプロフィール登録が必要です。"
    )


st.divider()


# ==================================================
# メンバー一覧
# ==================================================

st.header(
    "🌼 Campus Hive のメンバー"
)


for person in profiles:

    with st.container(
        border=True
    ):

        st.subheader(
            f"🌸 {person['name']}"
        )


        st.write(
            f"🎓 {person['grade']} / "
            f"{person['department']}"
        )


        st.write(
            f"🔎 探している相手："
            f"{person['purpose']}"
        )


        if person["strength"]:

            st.write(
                f"💪 得意："
                f"{person['strength']}"
            )


        if person["weakness"]:

            st.write(
                f"📚 教えてほしい："
                f"{person['weakness']}"
            )


        if person["hobby"]:

            st.write(
                f"🎮 趣味："
                f"{person['hobby']}"
            )


        if person["introduction"]:

            st.write(
                f"💬 {person['introduction']}"
            )
            # ==================================================
# マッチ機能
# ==================================================

st.subheader("💛 この人とつながる")


if st.button("💛 マッチする"):

    try:

        # 自分と相手のID
        my_id = my_profile["id"]
        target_id = target["id"]

        # IDの順番を統一
        user1_id = min(my_id, target_id)
        user2_id = max(my_id, target_id)

        # すでにマッチしているか確認
        existing_match = (
            supabase
            .table("matches")
            .select("*")
            .eq("user1_id", user1_id)
            .eq("user2_id", user2_id)
            .execute()
        )

        if existing_match.data:

            st.info(
                "💛 すでにマッチしています！"
            )

        else:

            # マッチを保存
            supabase.table("matches").insert({

                "user1_id": user1_id,
                "user2_id": user2_id

            }).execute()

            st.success(
                f"💕 {target['name']}さんとマッチしました！"
            )

            st.rerun()

    except Exception as e:

        st.error(
            "マッチの保存に失敗しました。"
        )

        st.code(str(e))
        # ==================================================
# マッチした人一覧
# ==================================================

st.divider()

st.header("💕 マッチした人")


try:

    match_response = (
        supabase
        .table("matches")
        .select("*")
        .execute()
    )

    matches = match_response.data


    my_matches = []

    for match in matches:

        if match["user1_id"] == my_profile["id"]:

            matched_id = match["user2_id"]

        elif match["user2_id"] == my_profile["id"]:

            matched_id = match["user1_id"]

        else:

            continue


        matched_person = next(

            (
                person
                for person in profiles
                if person["id"] == matched_id
            ),

            None

        )


        if matched_person:

            my_matches.append(
                matched_person
            )


    # -------------------------
    # マッチがない場合
    # -------------------------

    if len(my_matches) == 0:

        st.info(
            "まだマッチした人はいません。"
        )


    # -------------------------
    # マッチした人を表示
    # -------------------------

    else:

        for person in my_matches:

            with st.container(
                border=True
            ):

                st.subheader(
                    f"💕 {person['name']}"
                )

                st.write(
                    f"🎓 {person['grade']} / "
                    f"{person['department']}"
                )

                st.write(
                    f"🎮 趣味：{person['hobby']}"
                )

                st.button(
                    "💬 チャットする",
                    key=f"chat_{person['id']}"
                )


except Exception as e:

    st.error(
        "マッチ情報を読み込めませんでした。"
    )

    st.code(str(e))
