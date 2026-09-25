import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection


# =========================
# ページ設定
# =========================

st.set_page_config(
    page_title="Campus Hive",
    page_icon="🐝",
    layout="centered"
)


# =========================
# Google Sheets 接続
# =========================

conn = st.connection(
    "gsheets",
    type=GSheetsConnection
)


# =========================
# タイトル
# =========================

st.title("🐝 Campus Hive")

st.write(
    "蜂の群知能を利用した大学生向けマッチングアプリ"
)

st.divider()


# =========================
# プロフィール登録
# =========================

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
# プロフィール保存
# =========================

if submitted:

    if name.strip() == "":
        st.warning("名前・ニックネームを入力してください。")

    elif len(purpose) == 0:
        st.warning("探したい相手を1つ以上選択してください。")

    else:

        try:

            # 現在のデータを取得
            df = conn.read(
                worksheet="Profiles",
                ttl=0
            )

            # 空のシートだった場合
            if df.empty:
                df = pd.DataFrame(
                    columns=[
                        "id",
                        "name",
                        "grade",
                        "department",
                        "purpose",
                        "strength",
                        "weakness",
                        "hobby",
                        "introduction",
                        "created_at"
                    ]
                )

            # 新しいプロフィール
            new_profile = pd.DataFrame([
                {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                    "name": name,
                    "grade": grade,
                    "department": department,
                    "purpose": ", ".join(purpose),
                    "strength": strength,
                    "weakness": weakness,
                    "hobby": hobby,
                    "introduction": introduction,
                    "created_at": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                }
            ])

            # データを追加
            df = pd.concat(
                [df, new_profile],
                ignore_index=True
            )

            # Google Sheetsを更新
            conn.update(
                worksheet="Profiles",
                data=df
            )

            # キャッシュを削除
            st.cache_data.clear()

            st.success(
                f"🐝 {name}さんのプロフィールを登録しました！"
            )

            st.rerun()

        except Exception as e:

            st.error(
                "プロフィールの登録に失敗しました。"
            )

            st.code(str(e))


# =========================
# 登録済みプロフィール
# =========================

st.divider()

st.header("🌼 Campus Hive のメンバー")


try:

    profiles = conn.read(
        worksheet="Profiles",
        ttl=0
    )

    if profiles.empty:

        st.info(
            "まだ登録されているメンバーはいません。"
        )

    else:

        # 新しい人から表示
        profiles = profiles.iloc[::-1]

        for _, person in profiles.iterrows():

            with st.container(border=True):

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
                        f"💪 得意：{person['strength']}"
                    )

                if person["weakness"]:
                    st.write(
                        f"📚 教えてほしい："
                        f"{person['weakness']}"
                    )

                if person["hobby"]:
                    st.write(
                        f"🎮 趣味：{person['hobby']}"
                    )

                if person["introduction"]:
                    st.write(
                        f"💬 {person['introduction']}"
                    )


except Exception as e:

    st.error(
        "プロフィールを読み込めませんでした。"
    )

    st.code(str(e))