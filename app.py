import streamlit as st
import pandas as pd
import random
import extra_streamlit_components as stx
from supabase import create_client


# =========================================================
# 基本設定
# =========================================================

st.set_page_config(
    page_title="CampusHive",
    page_icon="🐝",
    layout="wide"
)


# =========================================================
# Supabase接続
# =========================================================

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

# セッションごとにクライアントを作る
# cache_resourceは使用しない
supabase = create_client(url, key)


# =========================================================
# Cookie
# =========================================================

cookie_manager = stx.CookieManager(
    key="campushive_cookie_manager"
)


# =========================================================
# Session State
# =========================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None


# =========================================================
# Cookieからログイン状態を復元
# =========================================================

if (
    st.session_state.access_token is None
    or st.session_state.refresh_token is None
):

    saved_access_token = cookie_manager.get(
        "campushive_access_token"
    )

    saved_refresh_token = cookie_manager.get(
        "campushive_refresh_token"
    )

    if saved_access_token and saved_refresh_token:
        st.session_state.access_token = saved_access_token
        st.session_state.refresh_token = saved_refresh_token


# =========================================================
# ログイン状態をSupabaseにセット
# =========================================================

if (
    st.session_state.access_token
    and st.session_state.refresh_token
):

    try:

        supabase.auth.set_session(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

    except Exception:

        st.session_state.access_token = None
        st.session_state.refresh_token = None

        try:
            cookie_manager.delete(
                "campushive_access_token"
            )

            cookie_manager.delete(
                "campushive_refresh_token"
            )

        except Exception:
            pass


# =========================================================
# 現在のユーザー取得
# =========================================================

try:

    user_response = supabase.auth.get_user()

    user = user_response.user

except Exception:

    user = None


# =========================================================
# ログイン画面
# =========================================================

def login_page():

    st.title("🐝 CampusHive")

    st.subheader("大学生のための交流・マッチングアプリ")

    st.write(
        "友達、勉強仲間、プロジェクト仲間、趣味仲間などを探せます。"
    )

    st.divider()

    tab_login, tab_signup = st.tabs(
        [
            "🔑 ログイン",
            "📝 新規登録"
        ]
    )


    # -----------------------------------------------------
    # ログイン
    # -----------------------------------------------------

    with tab_login:

        st.subheader("ログイン")

        login_email = st.text_input(
            "メールアドレス",
            key="login_email"
        )

        login_password = st.text_input(
            "パスワード",
            type="password",
            key="login_password"
        )

        if st.button(
            "ログイン",
            type="primary",
            use_container_width=True
        ):

            if not login_email or not login_password:

                st.error(
                    "メールアドレスとパスワードを入力してください。"
                )

            else:

                try:

                    response = supabase.auth.sign_in_with_password(
                        {
                            "email": login_email,
                            "password": login_password
                        }
                    )

                    session = response.session

                    if session:

                        st.session_state.access_token = (
                            session.access_token
                        )

                        st.session_state.refresh_token = (
                            session.refresh_token
                        )

                        # Cookieに保存
                        cookie_manager.set(
                            "campushive_access_token",
                            session.access_token,
                            max_age=60 * 60 * 24 * 30
                        )

                        cookie_manager.set(
                            "campushive_refresh_token",
                            session.refresh_token,
                            max_age=60 * 60 * 24 * 30
                        )

                        st.success(
                            "ログインしました！🐝"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "ログインに失敗しました。"
                        )

                except Exception as e:

                    st.error(
                        "ログインに失敗しました。"
                    )

                    st.code(str(e))


    # -----------------------------------------------------
    # 新規登録
    # -----------------------------------------------------

    with tab_signup:

        st.subheader("新規登録")

        signup_email = st.text_input(
            "メールアドレス",
            key="signup_email"
        )

        signup_password = st.text_input(
            "パスワード",
            type="password",
            key="signup_password"
        )

        signup_password_confirm = st.text_input(
            "パスワード（確認）",
            type="password",
            key="signup_password_confirm"
        )

        if st.button(
            "アカウントを作成",
            type="primary",
            use_container_width=True
        ):

            if not signup_email or not signup_password:

                st.error(
                    "メールアドレスとパスワードを入力してください。"
                )

            elif signup_password != signup_password_confirm:

                st.error(
                    "パスワードが一致していません。"
                )

            elif len(signup_password) < 6:

                st.error(
                    "パスワードは6文字以上にしてください。"
                )

            else:

                try:

                    response = supabase.auth.sign_up(
                        {
                            "email": signup_email,
                            "password": signup_password
                        }
                    )

                    if response.user:

                        st.success(
                            "アカウントを作成しました！🐝"
                        )

                        if response.session:

                            st.session_state.access_token = (
                                response.session.access_token
                            )

                            st.session_state.refresh_token = (
                                response.session.refresh_token
                            )

                            cookie_manager.set(
                                "campushive_access_token",
                                response.session.access_token,
                                max_age=60 * 60 * 24 * 30
                            )

                            cookie_manager.set(
                                "campushive_refresh_token",
                                response.session.refresh_token,
                                max_age=60 * 60 * 24 * 30
                            )

                            st.rerun()

                        else:

                            st.info(
                                "確認メールが届いている場合は、"
                                "メール内のリンクから確認してください。"
                            )

                except Exception as e:

                    st.error(
                        "アカウント作成に失敗しました。"
                    )

                    st.code(str(e))


# =========================================================
# ログインしていない場合
# =========================================================

if user is None:

    login_page()

    st.stop()


# =========================================================
# User ID
# =========================================================

user_id = user.id


# =========================================================
# 自分のプロフィール取得
# =========================================================

try:

    my_profile_response = (
        supabase
        .table("profiles")
        .select("*")
        .eq("auth_id", user_id)
        .maybe_single()
        .execute()
    )

    my_profile = my_profile_response.data

except Exception:

    my_profile = None


# =========================================================
# プロフィール登録
# =========================================================

if my_profile is None:

    st.title("🐝 CampusHive")

    st.header("🌸 プロフィールを登録")

    st.write(
        "CampusHiveを利用するためにプロフィールを登録してください。"
    )

    with st.form("profile_form"):

        name = st.text_input(
            "名前"
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
            "学部・学科"
        )

        purpose = st.multiselect(
            "🎯 CampusHiveを使う目的",
            [
                "友達探し",
                "勉強仲間探し",
                "プロジェクト仲間探し",
                "趣味仲間探し",
                "ゲーム仲間探し",
                "旅行仲間探し",
                "就活仲間探し"
            ]
        )

        hobby = st.multiselect(
            "🎮 趣味",
            [
                "ゲーム",
                "アニメ・漫画",
                "音楽",
                "映画・ドラマ",
                "スポーツ",
                "旅行",
                "カフェ・グルメ",
                "読書",
                "ファッション",
                "写真",
                "プログラミング",
                "その他"
            ]
        )

        strength = st.multiselect(
            "💪 得意なこと",
            [
                "プログラミング",
                "数学",
                "英語",
                "プレゼン",
                "デザイン",
                "文章作成",
                "コミュニケーション",
                "リーダーシップ",
                "調査・情報収集",
                "スポーツ",
                "その他"
            ]
        )

        weakness = st.multiselect(
            "📚 苦手・伸ばしたいこと",
            [
                "プログラミング",
                "数学",
                "英語",
                "プレゼン",
                "デザイン",
                "文章作成",
                "コミュニケーション",
                "リーダーシップ",
                "調査・情報収集",
                "スポーツ",
                "その他"
            ]
        )

        introduction = st.text_area(
            "自己紹介"
        )

        submit_profile = st.form_submit_button(
            "プロフィールを登録",
            type="primary"
        )


    if submit_profile:

        if not name.strip():

            st.error(
                "名前を入力してください。"
            )

        else:

            try:

                data = {

                    "auth_id": user_id,

                    "name": name.strip(),

                    "grade": grade,

                    "department": department.strip(),

                    "purpose": ", ".join(purpose),

                    "strength": ", ".join(strength),

                    "weakness": ", ".join(weakness),

                    "hobby": ", ".join(hobby),

                    "introduction": introduction.strip()
                }

                response = (
                    supabase
                    .table("profiles")
                    .insert(data)
                    .execute()
                )

                if response.data:

                    st.success(
                        "プロフィールを登録しました！🐝"
                    )

                    st.rerun()

                else:

                    st.error(
                        "プロフィールの登録に失敗しました。"
                    )

            except Exception as e:

                st.error(
                    "プロフィール登録に失敗しました。"
                )

                st.code(str(e))


    st.stop()


# =========================================================
# ユーティリティ
# =========================================================

def split_values(value):

    if not value:
        return []

    return [
        x.strip()
        for x in str(value).split(",")
        if x.strip()
    ]


def calculate_compatibility(me, other):

    my_purpose = set(
        split_values(me.get("purpose", ""))
    )

    other_purpose = set(
        split_values(other.get("purpose", ""))
    )

    my_hobby = set(
        split_values(me.get("hobby", ""))
    )

    other_hobby = set(
        split_values(other.get("hobby", ""))
    )

    my_strength = set(
        split_values(me.get("strength", ""))
    )

    other_strength = set(
        split_values(other.get("strength", ""))
    )

    my_weakness = set(
        split_values(me.get("weakness", ""))
    )

    other_weakness = set(
        split_values(other.get("weakness", ""))
    )


    # 目的の一致
    purpose_score = (
        len(my_purpose & other_purpose)
        /
        max(
            len(my_purpose | other_purpose),
            1
        )
    )


    # 趣味の一致
    hobby_score = (
        len(my_hobby & other_hobby)
        /
        max(
            len(my_hobby | other_hobby),
            1
        )
    )


    # 得意・苦手の補完関係
    complement_count = (

        len(
            my_strength
            &
            other_weakness
        )

        +

        len(
            other_strength
            &
            my_weakness
        )
    )


    total_possible = (

        len(
            my_strength
            |
            other_weakness
        )

        +

        len(
            other_strength
            |
            my_weakness
        )
    )


    complement_score = (
        complement_count
        /
        max(
            total_possible,
            1
        )
    )


    compatibility = (

        purpose_score * 0.30

        +

        hobby_score * 0.25

        +

        complement_score * 0.45
    )


    return compatibility


# =========================================================
# サイドバー
# =========================================================

with st.sidebar:

    st.title("🐝 CampusHive")

    st.write(
        f"ログイン中：{user.email}"
    )

    st.divider()


    if st.button(
        "🚪 ログアウト",
        use_container_width=True
    ):

        try:

            supabase.auth.sign_out()

        except Exception:

            pass


        st.session_state.access_token = None
        st.session_state.refresh_token = None


        try:

            cookie_manager.delete(
                "campushive_access_token"
            )

            cookie_manager.delete(
                "campushive_refresh_token"
            )

        except Exception:

            pass


        st.rerun()


# =========================================================
# 最新プロフィールを取得
# =========================================================

try:

    latest_profile_response = (
        supabase
        .table("profiles")
        .select("*")
        .eq("auth_id", user_id)
        .maybe_single()
        .execute()
    )

    if latest_profile_response.data:

        my_profile = latest_profile_response.data

except Exception:

    pass


my_profile_id = my_profile["id"]


# =========================================================
# 他のプロフィール取得
# =========================================================

try:

    profiles_response = (
        supabase
        .table("profiles")
        .select("*")
        .neq("id", my_profile_id)
        .execute()
    )

    profiles = profiles_response.data or []

except Exception:

    profiles = []


# =========================================================
# 交流経験取得
# =========================================================

try:

    experiences_response = (
        supabase
        .table("experiences")
        .select("*")
        .execute()
    )

    experiences = (
        experiences_response.data
        or []
    )

except Exception:

    experiences = []


# =========================================================
# タブ
# =========================================================

tab_match, tab_chat, tab_profile, tab_experience = st.tabs(
    [
        "🐝 マッチング",
        "💬 チャット",
        "👤 マイプロフィール",
        "⭐ 交流経験"
    ]
)


# =========================================================
# マッチング
# =========================================================

with tab_match:

    st.header("🐝 マッチング")

    st.write(
        "あなたに合いそうな学生を探します。"
    )


    if not profiles:

        st.info(
            "まだ他のユーザーが登録されていません。"
        )

    else:

        # ---------------------------------------------
        # 交流経験から候補者ごとの平均評価を計算
        # ---------------------------------------------

        swarm_scores = {}

        for profile in profiles:

            profile_id = profile["id"]

            related = [

                e
                for e in experiences

                if (
                    e.get("flower_id") == profile_id
                    or
                    e.get("bee_id") == profile_id
                )
            ]


            if related:

                swarm_scores[profile_id] = (

                    sum(
                        e.get("satisfaction", 0)
                        for e in related
                    )
                    /
                    len(related)
                )

            else:

                swarm_scores[profile_id] = 0


        # ---------------------------------------------
        # 未交流ユーザー
        # ---------------------------------------------

        experienced_ids = set()

        for e in experiences:

            if e.get("bee_id") == my_profile_id:

                experienced_ids.add(
                    e.get("flower_id")
                )

            if e.get("flower_id") == my_profile_id:

                experienced_ids.add(
                    e.get("bee_id")
                )


        unexplored = [

            p
            for p in profiles

            if p["id"] not in experienced_ids
        ]


        # ---------------------------------------------
        # 探索 / 活用
        # ---------------------------------------------

        exploration_rate = 0.3

        if random.random() < exploration_rate:

            # 探索
            if unexplored:

                candidate = random.choice(
                    unexplored
                )

                mode = "🔍 探索"

            else:

                candidate = random.choice(
                    profiles
                )

                mode = "🔍 探索"


        else:

            # 活用
            candidate = max(

                profiles,

                key=lambda p:
                    swarm_scores.get(
                        p["id"],
                        0
                    )
            )

            mode = "🧠 経験を活用"


        # ---------------------------------------------
        # 候補者
        # ---------------------------------------------

        st.subheader(
            f"{mode}：おすすめの相手"
        )

        compatibility = calculate_compatibility(
            my_profile,
            candidate
        )


        st.markdown(
            f"""
            ### 🌸 {candidate.get('name', '')}

            **学年：** {candidate.get('grade', '')}

            **学科：** {candidate.get('department', '')}

            **利用目的：** {candidate.get('purpose', '')}

            **得意：** {candidate.get('strength', '')}

            **苦手・伸ばしたいこと：**
            {candidate.get('weakness', '')}

            **趣味：** {candidate.get('hobby', '')}

            **自己紹介：**
            {candidate.get('introduction', '')}
            """
        )


        st.metric(
            "プロフィール上の相性",
            f"{compatibility * 100:.0f}%"
        )


        swarm_score = swarm_scores.get(
            candidate["id"],
            0
        )


        if swarm_score > 0:

            st.metric(
                "🐝 群れの平均満足度",
                f"{swarm_score:.1f} / 5"
            )

        else:

            st.info(
                "まだ交流経験がありません。"
            )


        # ---------------------------------------------
        # マッチング申請
        # ---------------------------------------------

        st.divider()

        if st.button(
            "💛 この人とつながる",
            type="primary",
            use_container_width=True
        ):

            try:

                # 重複確認
                existing = (
                    supabase
                    .table("matches")
                    .select("*")
                    .or_(
                        f"and(user1_id.eq.{my_profile_id},"
                        f"user2_id.eq.{candidate['id']}),"
                        f"and(user1_id.eq.{candidate['id']},"
                        f"user2_id.eq.{my_profile_id})"
                    )
                    .execute()
                )


                if existing.data:

                    st.info(
                        "すでにつながっています！🐝"
                    )

                else:

                    insert_response = (
                        supabase
                        .table("matches")
                        .insert(
                            {
                                "user1_id": my_profile_id,
                                "user2_id": candidate["id"]
                            }
                        )
                        .execute()
                    )


                    if insert_response.data:

                        st.success(
                            "つながりを作りました！💛"
                        )

                    else:

                        st.error(
                            "つながりの作成に失敗しました。"
                        )

            except Exception as e:

                st.error(
                    "つながりの作成に失敗しました。"
                )

                st.code(str(e))


        # ---------------------------------------------
        # 他の候補者
        # ---------------------------------------------

        st.divider()

        st.subheader(
            "🌸 他の学生"
        )


        for profile in profiles:

            with st.expander(
                f"🌸 {profile.get('name', '')}"
            ):

                st.write(
                    f"**学年：** {profile.get('grade', '')}"
                )

                st.write(
                    f"**学科：** {profile.get('department', '')}"
                )

                st.write(
                    f"**利用目的：** {profile.get('purpose', '')}"
                )

                st.write(
                    f"**得意：** {profile.get('strength', '')}"
                )

                st.write(
                    f"**苦手：** {profile.get('weakness', '')}"
                )

                st.write(
                    f"**趣味：** {profile.get('hobby', '')}"
                )

                st.write(
                    f"**自己紹介：** "
                    f"{profile.get('introduction', '')}"
                )


# =========================================================
# チャット
# =========================================================

with tab_chat:

    st.header("💬 チャット")


    @st.fragment(run_every="3s")
    def chat_fragment():

        # ---------------------------------------------
        # 最新プロフィールを再取得
        # ---------------------------------------------

        try:

            current_profile_response = (
                supabase
                .table("profiles")
                .select("*")
                .eq("auth_id", user_id)
                .maybe_single()
                .execute()
            )

            current_profile = (
                current_profile_response.data
            )

        except Exception:

            current_profile = my_profile


        if not current_profile:

            st.warning(
                "プロフィールが見つかりません。"
            )

            return


        current_profile_id = current_profile["id"]


        # ---------------------------------------------
        # 自分のマッチ一覧
        # ---------------------------------------------

        try:

            matches_response = (
                supabase
                .table("matches")
                .select("*")
                .or_(
                    f"user1_id.eq.{current_profile_id},"
                    f"user2_id.eq.{current_profile_id}"
                )
                .execute()
            )

            matches = matches_response.data or []

        except Exception:

            matches = []


        if not matches:

            st.info(
                "まだつながっている相手がいません。"
            )

            return


        # ---------------------------------------------
        # 相手一覧
        # ---------------------------------------------

        partner_ids = []

        for match in matches:

            if match["user1_id"] == current_profile_id:

                partner_ids.append(
                    match["user2_id"]
                )

            else:

                partner_ids.append(
                    match["user1_id"]
                )


        try:

            partners_response = (
                supabase
                .table("profiles")
                .select("*")
                .in_(
                    "id",
                    partner_ids
                )
                .execute()
            )

            partners = (
                partners_response.data
                or []
            )

        except Exception:

            partners = []


        if not partners:

            st.info(
                "チャット相手が見つかりません。"
            )

            return


        partner_dict = {

            p["id"]: p

            for p in partners
        }


        partner_options = {

            p["id"]:
            p.get("name", "名前未設定")

            for p in partners
        }


        selected_partner_id = st.selectbox(

            "チャット相手",

            options=list(
                partner_options.keys()
            ),

            format_func=lambda x:
                partner_options[x]
        )


        selected_partner = partner_dict[
            selected_partner_id
        ]


        st.subheader(
            f"💬 {selected_partner.get('name', '')}"
        )


        # ---------------------------------------------
        # メッセージ取得
        # ---------------------------------------------

        try:

            messages_response = (
                supabase
                .table("messages")
                .select("*")
                .or_(
                    f"and(sender_id.eq.{current_profile_id},"
                    f"receiver_id.eq.{selected_partner_id}),"
                    f"and(sender_id.eq.{selected_partner_id},"
                    f"receiver_id.eq.{current_profile_id})"
                )
                .order(
                    "created_at",
                    desc=False
                )
                .execute()
            )

            messages = (
                messages_response.data
                or []
            )

        except Exception as e:

            st.error(
                "メッセージの取得に失敗しました。"
            )

            st.code(str(e))

            messages = []


        # ---------------------------------------------
        # メッセージ表示
        # ---------------------------------------------

        for message in messages:

            if message["sender_id"] == current_profile_id:

                st.chat_message(
                    "user"
                ).write(
                    message["message"]
                )

            else:

                st.chat_message(
                    "assistant"
                ).write(
                    message["message"]
                )


        # ---------------------------------------------
        # メッセージ送信
        # ---------------------------------------------

        new_message = st.chat_input(
            "メッセージを入力..."
        )


        if new_message:

            try:

                response = (
                    supabase
                    .table("messages")
                    .insert(
                        {
                            "sender_id":
                                current_profile_id,

                            "receiver_id":
                                selected_partner_id,

                            "message":
                                new_message
                        }
                    )
                    .execute()
                )


                if response.data:

                    st.rerun(
                        scope="fragment"
                    )

                else:

                    st.error(
                        "メッセージを送信できませんでした。"
                    )

            except Exception as e:

                st.error(
                    "メッセージ送信に失敗しました。"
                )

                st.code(str(e))


    chat_fragment()


# =========================================================
# マイプロフィール
# =========================================================

with tab_profile:

    st.header("👤 マイプロフィール")


    # ---------------------------------------------
    # 最新データを取得
    # ---------------------------------------------

    try:

        profile_response = (
            supabase
            .table("profiles")
            .select("*")
            .eq("auth_id", user_id)
            .maybe_single()
            .execute()
        )

        my_profile = profile_response.data

    except Exception:

        pass


    if my_profile:

        # -----------------------------------------
        # 現在のプロフィール
        # -----------------------------------------

        st.subheader("現在のプロフィール")

        st.write(
            f"**名前：** {my_profile.get('name', '')}"
        )

        st.write(
            f"**学年：** {my_profile.get('grade', '')}"
        )

        st.write(
            f"**学科：** {my_profile.get('department', '')}"
        )

        st.write(
            f"**利用目的：** {my_profile.get('purpose', '')}"
        )

        st.write(
            f"**得意：** {my_profile.get('strength', '')}"
        )

        st.write(
            f"**苦手：** {my_profile.get('weakness', '')}"
        )

        st.write(
            f"**趣味：** {my_profile.get('hobby', '')}"
        )

        st.write(
            f"**自己紹介：** "
            f"{my_profile.get('introduction', '')}"
        )


        st.divider()

        st.subheader(
            "✏️ プロフィールを編集"
        )


        # -----------------------------------------
        # 選択肢
        # -----------------------------------------

        GRADE_OPTIONS = [

            "1年",
            "2年",
            "3年",
            "4年",
            "大学院生"
        ]


        PURPOSE_OPTIONS = [

            "友達探し",
            "勉強仲間探し",
            "プロジェクト仲間探し",
            "趣味仲間探し",
            "ゲーム仲間探し",
            "旅行仲間探し",
            "就活仲間探し"
        ]


        HOBBY_OPTIONS = [

            "ゲーム",
            "アニメ・漫画",
            "音楽",
            "映画・ドラマ",
            "スポーツ",
            "旅行",
            "カフェ・グルメ",
            "読書",
            "ファッション",
            "写真",
            "プログラミング",
            "その他"
        ]


        SKILL_OPTIONS = [

            "プログラミング",
            "数学",
            "英語",
            "プレゼン",
            "デザイン",
            "文章作成",
            "コミュニケーション",
            "リーダーシップ",
            "調査・情報収集",
            "スポーツ",
            "その他"
        ]


        current_purpose = split_values(
            my_profile.get(
                "purpose",
                ""
            )
        )


        current_hobby = split_values(
            my_profile.get(
                "hobby",
                ""
            )
        )


        current_strength = split_values(
            my_profile.get(
                "strength",
                ""
            )
        )


        current_weakness = split_values(
            my_profile.get(
                "weakness",
                ""
            )
        )


        current_grade = my_profile.get(
            "grade",
            GRADE_OPTIONS[0]
        )


        if current_grade not in GRADE_OPTIONS:

            current_grade = GRADE_OPTIONS[0]


        current_purpose = [

            x

            for x in current_purpose

            if x in PURPOSE_OPTIONS
        ]


        current_hobby = [

            x

            for x in current_hobby

            if x in HOBBY_OPTIONS
        ]


        current_strength = [

            x

            for x in current_strength

            if x in SKILL_OPTIONS
        ]


        current_weakness = [

            x

            for x in current_weakness

            if x in SKILL_OPTIONS
        ]


        # -----------------------------------------
        # 編集フォーム
        # -----------------------------------------

        with st.form(
            "edit_profile_form"
        ):

            edit_name = st.text_input(

                "名前",

                value=my_profile.get(
                    "name",
                    ""
                )
            )


            edit_grade = st.selectbox(

                "学年",

                GRADE_OPTIONS,

                index=GRADE_OPTIONS.index(
                    current_grade
                )
            )


            edit_department = st.text_input(

                "学部・学科",

                value=my_profile.get(
                    "department",
                    ""
                )
            )


            edit_purpose = st.multiselect(

                "🎯 CampusHiveを使う目的",

                PURPOSE_OPTIONS,

                default=current_purpose
            )


            edit_hobby = st.multiselect(

                "🎮 趣味",

                HOBBY_OPTIONS,

                default=current_hobby
            )


            edit_strength = st.multiselect(

                "💪 得意なこと",

                SKILL_OPTIONS,

                default=current_strength
            )


            edit_weakness = st.multiselect(

                "📚 苦手・伸ばしたいこと",

                SKILL_OPTIONS,

                default=current_weakness
            )


            edit_introduction = st.text_area(

                "自己紹介",

                value=my_profile.get(
                    "introduction",
                    ""
                )
            )


            save_profile = st.form_submit_button(

                "💾 プロフィールを保存",

                type="primary"
            )


        # -----------------------------------------
        # 保存処理
        # -----------------------------------------

        if save_profile:

            if not edit_name.strip():

                st.error(
                    "名前を入力してください。"
                )

            else:

                try:

                    update_data = {

                        "name":
                            edit_name.strip(),

                        "grade":
                            edit_grade,

                        "department":
                            edit_department.strip(),

                        "purpose":
                            ", ".join(
                                edit_purpose
                            ),

                        "strength":
                            ", ".join(
                                edit_strength
                            ),

                        "weakness":
                            ", ".join(
                                edit_weakness
                            ),

                        "hobby":
                            ", ".join(
                                edit_hobby
                            ),

                        "introduction":
                            edit_introduction.strip()
                    }


                    # ★ 重要
                    # auth_idが自分のユーザーIDと一致する
                    # プロフィールだけを更新する

                    update_response = (

                        supabase

                        .table("profiles")

                        .update(
                            update_data
                        )

                        .eq(
                            "id",
                            my_profile["id"]
                        )

                        .eq(
                            "auth_id",
                            user_id
                        )

                        .execute()
                    )


                    # ---------------------------------
                    # 更新できたか確認
                    # ---------------------------------

                    if not update_response.data:

                        st.error(

                            "プロフィールを更新できませんでした。"

                        )

                        st.warning(

                            "SupabaseのRLS設定を確認してください。"

                        )

                    else:

                        st.success(

                            "プロフィールを更新しました！🐝"

                        )

                        st.info(

                            "変更内容を保存しました。"

                        )

                        st.rerun()


                except Exception as e:

                    st.error(

                        "プロフィールの更新に失敗しました。"

                    )

                    st.code(
                        str(e)
                    )


# =========================================================
# 交流経験
# =========================================================

with tab_experience:

    st.header("⭐ 交流経験")

    st.write(
        "実際に交流した相手への満足度を記録します。"
    )


    if not profiles:

        st.info(
            "交流できる相手がいません。"
        )

    else:

        # ---------------------------------------------
        # マッチ相手取得
        # ---------------------------------------------

        try:

            matches_response = (
                supabase
                .table("matches")
                .select("*")
                .or_(
                    f"user1_id.eq.{my_profile_id},"
                    f"user2_id.eq.{my_profile_id}"
                )
                .execute()
            )

            matches = (
                matches_response.data
                or []
            )

        except Exception:

            matches = []


        partner_ids = []

        for match in matches:

            if match["user1_id"] == my_profile_id:

                partner_ids.append(
                    match["user2_id"]
                )

            else:

                partner_ids.append(
                    match["user1_id"]
                )


        if not partner_ids:

            st.info(
                "まずは誰かとつながってみましょう！🐝"
            )

        else:

            try:

                partners_response = (
                    supabase
                    .table("profiles")
                    .select("*")
                    .in_(
                        "id",
                        partner_ids
                    )
                    .execute()
                )

                partners = (
                    partners_response.data
                    or []
                )

            except Exception:

                partners = []


            if partners:

                partner_dict = {

                    p["id"]:
                        p

                    for p in partners
                }


                selected_partner_id = st.selectbox(

                    "交流した相手",

                    options=list(
                        partner_dict.keys()
                    ),

                    format_func=lambda x:
                        partner_dict[x].get(
                            "name",
                            "名前未設定"
                        )
                )


                satisfaction = st.slider(

                    "満足度",

                    min_value=1,

                    max_value=5,

                    value=5
                )


                comment = st.text_area(

                    "コメント",

                    placeholder=
                    "どんな交流だったか記録できます。"
                )


                if st.button(

                    "⭐ 交流経験を保存",

                    type="primary"
                ):

                    try:

                        response = (

                            supabase

                            .table("experiences")

                            .insert(
                                {
                                    "bee_id":
                                        my_profile_id,

                                    "flower_id":
                                        selected_partner_id,

                                    "satisfaction":
                                        satisfaction,

                                    "comment":
                                        comment.strip()
                                }
                            )

                            .execute()
                        )


                        if response.data:

                            st.success(

                                "交流経験を保存しました！🐝⭐"

                            )

                            st.rerun()

                        else:

                            st.error(

                                "保存できませんでした。"

                            )


                    except Exception as e:

                        st.error(

                            "交流経験の保存に失敗しました。"

                        )

                        st.code(
                            str(e)
                        )


                # -------------------------------------
                # 自分の過去の交流
                # -------------------------------------

                st.divider()

                st.subheader(
                    "📚 自分の交流履歴"
                )


                try:

                    my_experiences_response = (

                        supabase

                        .table("experiences")

                        .select("*")

                        .eq(
                            "bee_id",
                            my_profile_id
                        )

                        .order(
                            "created_at",
                            desc=True
                        )

                        .execute()
                    )


                    my_experiences = (

                        my_experiences_response.data

                        or []
                    )


                except Exception:

                    my_experiences = []


                for experience in my_experiences:

                    partner = partner_dict.get(

                        experience.get(
                            "flower_id"
                        ),

                        {}
                    )


                    partner_name = partner.get(

                        "name",

                        "名前未設定"
                    )


                    st.markdown(

                        f"""
                        **🌸 {partner_name}**

                        満足度：
                        {"⭐" * experience.get("satisfaction", 0)}

                        コメント：
                        {experience.get("comment", "")}
                        """
                    )

                    st.divider()
