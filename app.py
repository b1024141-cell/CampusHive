import streamlit as st
import pandas as pd
import random
import extra_streamlit_components as stx
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

# cache_resourceは使わない
# ユーザーごとの認証状態が混ざるのを防ぐ
supabase = create_client(url, key)

# =========================================================
# Cookie
# =========================================================

cookie_manager = stx.CookieManager(
    key="campushive_cookie_manager"
)

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None

# 保存済みセッションを読み込む
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
# ログイン・新規登録
# =========================================================

def save_session(session):
    st.session_state.access_token = session.access_token
    st.session_state.refresh_token = session.refresh_token

    cookie_manager.set(
        "campushive_access_token",
        session.access_token,
        max_age=60 * 60 * 24 * 30,
        secure=True,
        same_site="lax"
    )

    cookie_manager.set(
        "campushive_refresh_token",
        session.refresh_token,
        max_age=60 * 60 * 24 * 30,
        secure=True,
        same_site="lax"
    )


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

            email = st.text_input("メールアドレス")

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

                    response = (
                        supabase.auth.sign_in_with_password(
                            {
                                "email": email,
                                "password": password
                            }
                        )
                    )

                    session = response.session

                    if session:

                        save_session(session)

                        st.success("ログインしました！")
                        st.rerun()

                    else:

                        st.error(
                            "ログインセッションを取得できませんでした。"
                        )

                except Exception as e:

                    st.error("ログインに失敗しました。")
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

                    if response.session:

                        save_session(response.session)

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
# Supabaseにセッションを設定
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
# 選択肢
# =========================================================

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


def split_values(value):
    if not value:
        return []
    return [
        x.strip()
        for x in value.split(",")
        if x.strip()
    ]


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

        name = st.text_input("名前")

        grade = st.selectbox(
            "学年",
            GRADE_OPTIONS
        )

        department = st.text_input(
            "学部・学科"
        )

        purpose = st.multiselect(
            "🎯 CampusHiveを使う目的",
            PURPOSE_OPTIONS
        )

        hobby = st.multiselect(
            "🎮 趣味",
            HOBBY_OPTIONS
        )

        strength = st.multiselect(
            "💪 得意なこと",
            SKILL_OPTIONS
        )

        weakness = st.multiselect(
            "📚 苦手・伸ばしたいこと",
            SKILL_OPTIONS
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
                    "department": department,
                    "purpose": ", ".join(purpose),
                    "strength": ", ".join(strength),
                    "weakness": ", ".join(weakness),
                    "hobby": ", ".join(hobby),
                    "introduction": introduction.strip()
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
        # 群れ全体の評価
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

            if satisfaction is not None:
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
        # 候補表示
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

            st.write("💬 自己紹介")

            st.write(
                candidate["introduction"]
            )

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
                    profile.get(
                        "introduction",
                        ""
                    )
                )


# =========================================================
# マイプロフィール
# =========================================================

with tab_profile:

    st.header("👤 マイプロフィール")

    # -----------------------------------------------------
    # 表示
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # 編集
    # -----------------------------------------------------

    st.subheader("✏️ プロフィールを編集")

    current_purpose = split_values(
        my_profile.get("purpose", "")
    )

    current_hobby = split_values(
        my_profile.get("hobby", "")
    )

    current_strength = split_values(
        my_profile.get("strength", "")
    )

    current_weakness = split_values(
        my_profile.get("weakness", "")
    )

    # selectbox / multiselect の初期値が
    # 選択肢に存在するか確認
    current_grade = my_profile.get(
        "grade",
        GRADE_OPTIONS[0]
    )

    if current_grade not in GRADE_OPTIONS:
        current_grade = GRADE_OPTIONS[0]

    current_purpose = [
        x for x in current_purpose
        if x in PURPOSE_OPTIONS
    ]

    current_hobby = [
        x for x in current_hobby
        if x in HOBBY_OPTIONS
    ]

    current_strength = [
        x for x in current_strength
        if x in SKILL_OPTIONS
    ]

    current_weakness = [
        x for x in current_weakness
        if x in SKILL_OPTIONS
    ]

    with st.form("edit_profile_form"):

        edit_name = st.text_input(
            "名前",
            value=my_profile.get("name", "")
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

    if save_profile:

        if not edit_name.strip():

            st.error(
                "名前を入力してください。"
            )

        else:

            try:

                update_data = {
                    "name": edit_name.strip(),
                    "grade": edit_grade,
                    "department": edit_department.strip(),
                    "purpose": ", ".join(
                        edit_purpose
                    ),
                    "strength": ", ".join(
                        edit_strength
                    ),
                    "weakness": ", ".join(
                        edit_weakness
                    ),
                    "hobby": ", ".join(
                        edit_hobby
                    ),
                    "introduction": (
                        edit_introduction.strip()
                    )
                }

                update_response = (
    supabase
    .table("profiles")
    .update(update_data)
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

if not update_response.data:
    st.error(
        "プロフィールを更新できませんでした。"
        "SupabaseのRLSポリシーを確認してください。"
    )
else:
    st.success(
        "プロフィールを更新しました！🐝"
    )

    st.info(
        "変更内容を反映しました。"
    )

    st.rerun()
                st.success(
                    "プロフィールを更新しました！🐝"
                )

                st.info(
                    "変更内容は次回のマッチングから反映されます。"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    "プロフィールの更新に失敗しました。"
                )

                st.code(str(e))


# =========================================================
# 交流経験
# =========================================================

with tab_experience:

    st.header("⭐ 交流経験を記録")

    st.write(
        "実際に交流した相手との経験を記録すると、"
        "今後の🐝マッチングに活用できます。"
    )

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
                    .eq(
                        "id",
                        other_id
                    )
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

    @st.fragment(run_every="3s")
    def chat_fragment():

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

        if not chat_partners:

            st.info(
                "まだマッチした相手がいません。"
            )

            st.write(
                "🐝 マッチング画面から気になる学生とつながってみましょう！"
            )

            return

        partner_names = [
            partner["name"]
            for partner in chat_partners
        ]

        selected_name = st.selectbox(
            "💬 チャットする相手",
            partner_names,
            key="chat_partner_select"
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

            all_messages = (
                sent_messages
                + received_messages
            )

            all_messages.sort(
                key=lambda x: x["created_at"]
            )

        except Exception as e:

            st.error(
                "メッセージを取得できませんでした。"
            )

            st.code(str(e))
            all_messages = []

        if not all_messages:

            st.info(
                "まだメッセージはありません。"
            )

            st.write(
                f"{selected_partner['name']}さんに"
                "最初のメッセージを送ってみましょう！"
            )

        else:

            for message in all_messages:

                if message["sender_id"] == my_profile["id"]:

                    with st.chat_message("user"):

                        st.write(
                            message["message"]
                        )

                else:

                    with st.chat_message("assistant"):

                        st.write(
                            message["message"]
                        )

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

                    st.rerun(scope="fragment")

                except Exception as e:

                    st.error(
                        "メッセージを送信できませんでした。"
                    )

                    st.code(str(e))

    chat_fragment()
