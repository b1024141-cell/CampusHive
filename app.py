import streamlit as st
import pandas as pd
import random
from supabase import create_client


# =========================================================
# ページ設定
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

supabase = create_client(
    url,
    key
)
# =========================================================
# セッション管理
# =========================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None


# =========================================================
# ログイン画面
# =========================================================

def login_page():

    st.title("🐝 CampusHive")

    st.subheader("大学生のための新しいマッチング")

    st.write(
        "あなたを「蜂」、他の学生を「花」として、"
        "交流経験を次の出会いに活かします。"
    )

    st.divider()

    tab1, tab2 = st.tabs(
        ["🔐 ログイン", "🆕 新規登録"]
    )


    # -----------------------------------------------------
    # ログイン
    # -----------------------------------------------------

    with tab1:

        st.subheader("ログイン")

        with st.form("login_form"):

            email = st.text_input(
                "メールアドレス"
            )

            password = st.text_input(
                "パスワード",
                type="password"
            )

            login_button = st.form_submit_button(
                "ログイン",
                type="primary"
            )


        if login_button:

            if not email or not password:

                st.error(
                    "メールアドレスとパスワードを入力してください。"
                )

            else:

                try:

                    response = supabase.auth.sign_in_with_password(
                        {
                            "email": email,
                            "password": password
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

                        st.success(
                            "ログインしました！"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "ログインセッションを取得できませんでした。"
                        )

                except Exception as e:

                    st.error(
                        "ログインに失敗しました。"
                    )

                    st.caption(str(e))


    # -----------------------------------------------------
    # 新規登録
    # -----------------------------------------------------

    with tab2:

        st.subheader("新規登録")

        with st.form("signup_form"):

            signup_email = st.text_input(
                "メールアドレス",
                key="signup_email"
            )

            signup_password = st.text_input(
                "パスワード",
                type="password",
                key="signup_password"
            )

            signup_password2 = st.text_input(
                "パスワード（確認）",
                type="password",
                key="signup_password2"
            )

            signup_button = st.form_submit_button(
                "アカウントを作成"
            )


        if signup_button:

            if not signup_email or not signup_password:

                st.error(
                    "メールアドレスとパスワードを入力してください。"
                )

            elif signup_password != signup_password2:

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

                    # Confirm emailがOFFの場合
                    if response.session:

                        st.session_state.access_token = (
                            response.session.access_token
                        )

                        st.session_state.refresh_token = (
                            response.session.refresh_token
                        )

                        st.success(
                            "アカウントを作成しました！"
                        )

                        st.rerun()

                    else:

                        st.success(
                            "アカウントを作成しました！"
                        )

                        st.info(
                            "確認メールが届いている場合は、"
                            "メールアドレスを確認してからログインしてください。"
                        )

                except Exception as e:

                    st.error(
                        "アカウント作成に失敗しました。"
                    )

                    st.caption(str(e))


# =========================================================
# セッションをSupabaseに設定
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


# =========================================================
# 現在のユーザー取得
# =========================================================

try:

    user_response = supabase.auth.get_user()

    user = user_response.user

except Exception:

    user = None


# =========================================================
# ログインしていなければログイン画面
# =========================================================

if user is None:

    login_page()

    st.stop()


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

        st.rerun()


# =========================================================
# プロフィール未登録の場合
# =========================================================

if my_profile is None:

    st.title("🐝 CampusHive")

    st.header("🌸 プロフィールを登録")

    st.write(
        "まずはあなたの情報を登録してください。"
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

        if not name:

            st.error(
                "名前を入力してください。"
            )

        else:

            try:

                data = {
                    "auth_id": user_id,
                    "name": name,
                    "grade": grade,
                    "department": department,
                    "purpose": ", ".join(purpose),
                    "strength": ", ".join(strength),
                    "weakness": ", ".join(weakness),
                    "hobby": ", ".join(hobby),
                    "introduction": introduction
                }

                supabase.table(
                    "profiles"
                ).insert(data).execute()

                st.success(
                    "プロフィールを登録しました！"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "プロフィール登録に失敗しました。"
                )

                st.code(str(e))

    st.stop()
# =========================================================
# メイン画面
# =========================================================

st.title("🐝 CampusHive")

st.write(
    f"こんにちは、{my_profile['name']}さん！"
)

st.write(
    "あなたは🐝、他の学生は🌸です。"
)

st.divider()


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
# 全プロフィール取得
# =========================================================

try:

    profiles_response = (
        supabase
        .table("profiles")
        .select("*")
        .neq("id", my_profile["id"])
        .execute()
    )

    profiles = profiles_response.data or []

except Exception as e:

    st.error(
        "プロフィール情報を取得できませんでした。"
    )

    profiles = []


# =========================================================
# 経験データ取得
# =========================================================

try:

    experiences_response = (
        supabase
        .table("experiences")
        .select("*")
        .execute()
    )

    experiences = experiences_response.data or []

except Exception:

    experiences = []


# =========================================================
# マッチング
# =========================================================

with tab_match:

    st.header("🌸 あなたにおすすめの学生")

    if not profiles:

        st.info(
            "まだ他の学生が登録されていません。"
        )

    else:

        # -------------------------------------------------
        # 群れ全体の評価を計算
        # -------------------------------------------------

        swarm_scores = {}

        for experience in experiences:

            flower_id = experience.get(
                "flower_id"
            )

            satisfaction = experience.get(
                "satisfaction"
            )

            if flower_id is None:
                continue

            if flower_id not in swarm_scores:

                swarm_scores[flower_id] = []

            swarm_scores[flower_id].append(
                satisfaction
            )


        swarm_average = {}

        for flower_id, scores in swarm_scores.items():

            if scores:

                swarm_average[flower_id] = (
                    sum(scores) / len(scores)
                )


        # -------------------------------------------------
        # 探索 / 活用
        # -------------------------------------------------

        exploration_rate = 0.3

        if random.random() < exploration_rate:

            mode = "🔍 探索"

            unexplored = [
                p for p in profiles
                if p["id"] not in swarm_average
            ]

            if unexplored:

                candidate = random.choice(
                    unexplored
                )

            else:

                candidate = random.choice(
                    profiles
                )

        else:

            mode = "🧠 活用"

            scored_profiles = [
                p for p in profiles
                if p["id"] in swarm_average
            ]

            if scored_profiles:

                candidate = max(
                    scored_profiles,
                    key=lambda p:
                        swarm_average[p["id"]]
                )

            else:

                candidate = random.choice(
                    profiles
                )


        # -------------------------------------------------
        # 選ばれた学生
        # -------------------------------------------------

        st.info(
            f"今回の行動モード：{mode}"
        )

        st.subheader(
            "🌸 あなたが出会った候補"
        )

        st.markdown(
            f"## {candidate['name']}"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"🎓 学年：{candidate.get('grade', '')}"
            )

            st.write(
                f"🏫 学科：{candidate.get('department', '')}"
            )

            st.write(
                f"🎯 目的：{candidate.get('purpose', '')}"
            )

        with col2:

            st.write(
                f"💪 得意：{candidate.get('strength', '')}"
            )

            st.write(
                f"📚 苦手：{candidate.get('weakness', '')}"
            )

            st.write(
                f"🎮 趣味：{candidate.get('hobby', '')}"
            )


        if candidate.get("introduction"):

            st.write(
                "💬 自己紹介"
            )

            st.write(
                candidate["introduction"]
            )


        # -------------------------------------------------
        # 群れの評価
        # -------------------------------------------------

        if candidate["id"] in swarm_average:

            score = swarm_average[
                candidate["id"]
            ]

            st.metric(
                "🐝 群れの平均満足度",
                f"{score:.1f} / 5"
            )

        else:

            st.caption(
                "🐝 まだ群れの経験がありません。"
            )


        st.divider()


        # -------------------------------------------------
        # マッチ申請
        # -------------------------------------------------

        st.subheader(
            "🤝 この人とつながる"
        )

        if st.button(
            "💛 マッチ申請する",
            type="primary",
            use_container_width=True
        ):

            try:

                # 既に逆方向で登録されていないか確認
                existing1 = (
                    supabase
                    .table("matches")
                    .select("id")
                    .eq(
                        "user1_id",
                        my_profile["id"]
                    )
                    .eq(
                        "user2_id",
                        candidate["id"]
                    )
                    .execute()
                )

                existing2 = (
                    supabase
                    .table("matches")
                    .select("id")
                    .eq(
                        "user1_id",
                        candidate["id"]
                    )
                    .eq(
                        "user2_id",
                        my_profile["id"]
                    )
                    .execute()
                )


                if existing1.data or existing2.data:

                    st.info(
                        "この人とはすでにマッチしています。"
                    )

                else:

                    supabase.table(
                        "matches"
                    ).insert(
                        {
                            "user1_id": my_profile["id"],
                            "user2_id": candidate["id"]
                        }
                    ).execute()

                    st.success(
                        f"{candidate['name']}さんにマッチ申請しました！"
                    )

                    st.rerun()


            except Exception as e:

                st.error(
                    "マッチ申請に失敗しました。"
                )

                st.code(str(e))


        st.divider()


        # -------------------------------------------------
        # 他の学生一覧
        # -------------------------------------------------

        st.subheader(
            "🌼 他の学生"
        )

        for profile in profiles:

            if profile["id"] == candidate["id"]:
                continue

            with st.expander(
                f"🌸 {profile['name']}"
            ):

                st.write(
                    f"🎓 {profile.get('grade', '')}"
                )

                st.write(
                    f"🏫 {profile.get('department', '')}"
                )

                st.write(
                    f"🎯 {profile.get('purpose', '')}"
                )

                st.write(
                    f"💪 得意：{profile.get('strength', '')}"
                )

                st.write(
                    f"📚 苦手：{profile.get('weakness', '')}"
                )

                st.write(
                    f"🎮 趣味：{profile.get('hobby', '')}"
                )

                st.write(
                    profile.get('introduction', '')
                )


# =========================================================
# マイプロフィール
# =========================================================

with tab_profile:

    st.header("👤 マイプロフィール")

    st.write(
        f"**名前：** {my_profile['name']}"
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
        f"**自己紹介：** {my_profile.get('introduction', '')}"
    )


# =========================================================
# 交流経験
# =========================================================

with tab_experience:

    st.header("⭐ 交流経験を記録")

    st.write(
        "実際に交流した相手との経験を記録すると、"
        "今後の🐝マッチングに活用できます。"
    )


    # -----------------------------------------------------
    # マッチ一覧
    # -----------------------------------------------------

    try:

        matches1 = (
            supabase
            .table("matches")
            .select("*")
            .eq(
                "user1_id",
                my_profile["id"]
            )
            .execute()
        )

        matches2 = (
            supabase
            .table("matches")
            .select("*")
            .eq(
                "user2_id",
                my_profile["id"]
            )
            .execute()
        )

        my_matches = (
            (matches1.data or [])
            + (matches2.data or [])
        )

    except Exception:

        my_matches = []


    if not my_matches:

        st.info(
            "まだマッチした相手はいません。"
        )

    else:

        # 相手プロフィール取得
        other_profiles = []

        for match in my_matches:

            if match["user1_id"] == my_profile["id"]:

                other_id = match["user2_id"]

            else:

                other_id = match["user1_id"]


            try:

                response = (
                    supabase
                    .table("profiles")
                    .select("*")
                    .eq("id", other_id)
                    .single()
                    .execute()
                )

                if response.data:

                    other_profiles.append(
                        response.data
                    )

            except Exception:

                pass


        if other_profiles:

            selected_name = st.selectbox(
                "交流した相手",
                [
                    p["name"]
                    for p in other_profiles
                ]
            )


            selected_profile = next(
                p for p in other_profiles
                if p["name"] == selected_name
            )


            satisfaction = st.slider(
                "満足度",
                min_value=1,
                max_value=5,
                value=3
            )


            comment = st.text_area(
                "交流についてのコメント",
                placeholder="例：一緒に勉強できてよかった"
            )


            if st.button(
                "⭐ 経験を記録",
                type="primary"
            ):

                try:

                    supabase.table(
                        "experiences"
                    ).insert(
                        {
                            "bee_id": my_profile["id"],
                            "flower_id": selected_profile["id"],
                            "satisfaction": satisfaction,
                            "comment": comment
                        }
                    ).execute()

                    st.success(
                        "交流経験を記録しました！🐝"
                    )

                    st.info(
                        "この経験は今後のマッチングに活用されます。"
                    )

                    st.rerun()


                except Exception as e:

                    st.error(
                        "経験の記録に失敗しました。"
                    )

                    st.code(str(e))
                    # =========================================================
# チャット
# =========================================================

with tab_chat:

    st.header("💬 チャット")

    st.write(
        "マッチした相手と1対1でメッセージを送ることができます。"
    )

    # -----------------------------------------------------
    # 自分のマッチ一覧を取得
    # -----------------------------------------------------

    try:

        matches1 = (
            supabase
            .table("matches")
            .select("*")
            .eq(
                "user1_id",
                my_profile["id"]
            )
            .execute()
        )

        matches2 = (
            supabase
            .table("matches")
            .select("*")
            .eq(
                "user2_id",
                my_profile["id"]
            )
            .execute()
        )

        my_matches = (
            (matches1.data or [])
            + (matches2.data or [])
        )

    except Exception as e:

        st.error(
            "マッチ情報を取得できませんでした。"
        )

        st.code(str(e))

        my_matches = []


    # -----------------------------------------------------
    # マッチした相手を取得
    # -----------------------------------------------------

    chat_partners = []

    for match in my_matches:

        if match["user1_id"] == my_profile["id"]:

            partner_id = match["user2_id"]

        else:

            partner_id = match["user1_id"]


        try:

            partner_response = (
                supabase
                .table("profiles")
                .select("*")
                .eq(
                    "id",
                    partner_id
                )
                .single()
                .execute()
            )

            partner = partner_response.data

            if partner:

                chat_partners.append(partner)

        except Exception:

            pass


    # -----------------------------------------------------
    # マッチ相手がいない場合
    # -----------------------------------------------------

    if not chat_partners:

        st.info(
            "まだマッチした相手がいません。"
        )

        st.write(
            "🐝 マッチング画面から気になる学生とつながってみましょう！"
        )


    # -----------------------------------------------------
    # チャット相手を選択
    # -----------------------------------------------------

    else:

        partner_names = [
            partner["name"]
            for partner in chat_partners
        ]

        selected_name = st.selectbox(
            "💬 チャットする相手",
            partner_names
        )


        selected_partner = next(
            partner
            for partner in chat_partners
            if partner["name"] == selected_name
        )

        partner_id = selected_partner["id"]


        st.divider()

        st.subheader(
            f"🌸 {selected_partner['name']}さん"
        )


        # -------------------------------------------------
        # メッセージ取得
        # -------------------------------------------------

        try:

            sent_messages_response = (
                supabase
                .table("messages")
                .select("*")
                .eq(
                    "sender_id",
                    my_profile["id"]
                )
                .eq(
                    "receiver_id",
                    partner_id
                )
                .execute()
            )

            received_messages_response = (
                supabase
                .table("messages")
                .select("*")
                .eq(
                    "sender_id",
                    partner_id
                )
                .eq(
                    "receiver_id",
                    my_profile["id"]
                )
                .execute()
            )


            sent_messages = (
                sent_messages_response.data or []
            )

            received_messages = (
                received_messages_response.data or []
            )


            # 送信・受信をまとめる
            all_messages = (
                sent_messages
                + received_messages
            )


            # 時系列順に並べる
            all_messages.sort(
                key=lambda x: x["created_at"]
            )


        except Exception as e:

            st.error(
                "メッセージを取得できませんでした。"
            )

            st.code(str(e))

            all_messages = []


        # -------------------------------------------------
        # メッセージ表示
        # -------------------------------------------------

        if not all_messages:

            st.info(
                "まだメッセージはありません。"
            )

            st.write(
                f"{selected_partner['name']}さんに最初のメッセージを送ってみましょう！"
            )


        else:

            for message in all_messages:

                if message["sender_id"] == my_profile["id"]:

                    # 自分のメッセージ
                    with st.chat_message("user"):

                        st.write(
                            message["message"]
                        )

                else:

                    # 相手のメッセージ
                    with st.chat_message("assistant"):

                        st.write(
                            message["message"]
                        )


        # -------------------------------------------------
        # メッセージ送信
        # -------------------------------------------------

        new_message = st.chat_input(
            f"{selected_partner['name']}さんにメッセージを送る"
        )


        if new_message:

            new_message = new_message.strip()


            if new_message:

                try:

                    supabase.table(
                        "messages"
                    ).insert(
                        {
                            "sender_id": my_profile["id"],
                            "receiver_id": partner_id,
                            "message": new_message
                        }
                    ).execute()


                    st.rerun()


                except Exception as e:

                    st.error(
                        "メッセージを送信できませんでした。"
                    )

                    st.code(str(e))
