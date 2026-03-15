import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="📮 2-5 익명 건의함",
    page_icon="📮",
    layout="centered"
)

# -----------------------
# 기본 스타일
# -----------------------
st.markdown("""
<style>
/* 전체 배경 */
.stApp {
    background:
        linear-gradient(rgba(248,247,242,0.7), rgba(248,247,242,0.7)),
        url("https://raw.githubusercontent.com/KimJeongYun20167/Anonymous-suggestion-box/main/clover_bg.jpg");
    background-size: 320px auto;
    background-repeat: repeat;
    background-attachment: fixed;
}

/* 메인 컨테이너 */
.block-container {
    padding-top: 2.2rem;
    padding-bottom: 2rem;
    max-width: 860px;
}

/* 카드 */
.main-card {
    background: rgba(255, 255, 255, 0.90);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    padding: 1.45rem 1.2rem;
    border-radius: 24px;
    border: 1px solid rgba(170, 190, 170, 0.22);
    box-shadow: 0 10px 30px rgba(80, 90, 80, 0.08);
    margin-bottom: 1rem;
}

/* 제목/서브텍스트 */
.section-title {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #36553b;
    margin-bottom: 0.35rem;
}

.section-sub {
    color: #5f6b60;
    font-size: 1rem;
    line-height: 1.6;
    margin-bottom: 0.25rem;
}

.small-note {
    font-size: 0.88rem;
    color: #7d877d;
    line-height: 1.5;
}

/* 폼 */
div[data-testid="stForm"] {
    border: 1px solid rgba(160, 180, 160, 0.22);
    border-radius: 22px;
    padding: 1.1rem 1.1rem 0.8rem 1.1rem;
    background: rgba(255,255,255,0.92);
    box-shadow: 0 8px 24px rgba(0,0,0,0.04);
}

/* 입력창 */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    border-radius: 16px !important;
    border: 1px solid #dfe6dc !important;
    background-color: #fcfcf8 !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="textarea"] > div:focus-within {
    border: 1px solid #9cc6a3 !important;
    box-shadow: 0 0 0 1px #9cc6a3 !important;
}

/* 라벨 */
label, .stTextInput label, .stTextArea label {
    color: #49604d !important;
    font-weight: 600 !important;
}

/* 버튼 */
.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 999px !important;
    border: none !important;
    background: linear-gradient(135deg, #5fa86d 0%, #4f9960 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    padding: 0.6rem 1.2rem !important;
    box-shadow: 0 8px 18px rgba(79, 153, 96, 0.28) !important;
}

/* 데이터프레임 */
div[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    border: 1px solid rgba(170, 185, 170, 0.18);
    background: rgba(255,255,255,0.92);
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: rgba(246,245,239,0.94);
    border-right: 1px solid rgba(120, 140, 120, 0.10);
}

section[data-testid="stSidebar"] .stRadio label {
    color: #4e5f51 !important;
    font-weight: 600;
}

/* 알림 박스 */
div[data-testid="stAlert"] {
    border-radius: 16px;
}

/* 캡션 */
[data-testid="stCaptionContainer"] {
    color: #6f786f !important;
}

/* 구분선 */
hr {
    margin-top: 1rem;
    margin-bottom: 1rem;
    border: none;
    height: 1px;
    background: rgba(120,140,120,0.12);
}

/* 배지 */
.soft-badge {
    display: inline-block;
    padding: 0.35rem 0.7rem;
    border-radius: 999px;
    background: #eef5ee;
    color: #52705a;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 0.7rem;
}

.tomato {
    color: #d86d5c;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Secrets
# -----------------------
POST_URL = st.secrets["sheetdb"]["post_url"].strip()
GET_URL = st.secrets["sheetdb"]["get_url"].strip()
ADMIN_PASSWORD = st.secrets["admin"]["password"].strip()

# -----------------------
# 데이터 함수
# -----------------------
def save_submission(title: str, content: str):
    now = "'" + datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "data": [
            {
                "created_at": now,
                "title": title,
                "content": content
            }
        ]
    }

    response = requests.post(POST_URL, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def load_submissions() -> pd.DataFrame:
    response = requests.get(
        GET_URL,
        params={
            "sort_by": "created_at",
            "sort_order": "asc"
        },
        timeout=10
    )
    response.raise_for_status()

    data = response.json()

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    wanted_cols = ["created_at", "title", "content"]
    existing_cols = [col for col in wanted_cols if col in df.columns]

    if existing_cols:
        df = df[existing_cols]

    # 1부터 시작하는 인덱스
    df = df.reset_index(drop=True)
    df.index = df.index + 1

    return df


# -----------------------
# 사이드바
# -----------------------
st.sidebar.markdown("### 🍀 메뉴")
mode = st.sidebar.radio("", ["건의사항 제출", "관리자 페이지"])

# -----------------------
# 학생용 페이지
# -----------------------
if mode == "건의사항 제출":
    st.markdown("""
    <div class="main-card">
        <div class="soft-badge">*¨*•.¸¸♪*¨*•.¸¸♪</div>
        <div class="section-title">📮 2-5 익명 건의함</div>
        <div class="section-sub">
            하고 싶은 말, 바라는 점, 불편했던 점을 편하게 남겨줘.
        </div>
        <div class="small-note">
            익명으로 제출되며, 제목과 내용을 모두 입력해야 등록돼.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("suggestion_form", clear_on_submit=True):
        title = st.text_input(
            "제목",
            placeholder=""
        )
        content = st.text_area(
            "내용",
            height=220,
            placeholder="하고 싶은 말을 자유롭게 적어줘!"
        )
        submitted = st.form_submit_button("제출하기", use_container_width=True)

    if submitted:
        title = title.strip()
        content = content.strip()

        if not title or not content:
            st.error("제목과 내용을 모두 입력해줘.")
        else:
            try:
                save_submission(title, content)
                st.toast("제출 완료")
                st.balloons()
            except requests.HTTPError as e:
                st.error("제출 요청 실패")
                st.exception(e)
            except requests.RequestException as e:
                st.error("네트워크 요청 중 오류 발생")
                st.exception(e)
            except Exception as e:
                st.error("제출 중 오류 발생.")
                st.exception(e)
# -----------------------
# 관리자 페이지
# -----------------------
else:
    st.markdown("""
    <div class="main-card">
        <div class="soft-badge">admin only</div>
        <div class="section-title"><span class="tomato">🍅</span> 관리자 페이지</div>
        <div class="section-sub">
            제출된 건의사항을 확인하는 공간
        </div>
        <div class="small-note">
            관리자 비밀번호를 입력하면 목록을 볼 수 있어.
        </div>
    </div>
    """, unsafe_allow_html=True)

    admin_password = st.text_input(
        "관리자 비밀번호",
        type="password",
        placeholder="비밀번호 입력"
    )

    if admin_password == ADMIN_PASSWORD:
        st.success("인증 완료")

        try:
            df = load_submissions()

            if df.empty:
                st.info("제출된 글이 아직 없어.")
            else:
                st.markdown("### 제출 목록")
                st.dataframe(df, use_container_width=True)

        except requests.HTTPError as e:
            st.error("관리자 데이터 조회 요청 실패")
            st.exception(e)
        except requests.RequestException as e:
            st.error("네트워크 요청 중 오류가 발생")
            st.exception(e)
        except Exception as e:
            st.error("관리자 데이터 조회 중 오류 발생")
            st.exception(e)

    else:
        if admin_password:
            st.error("올바르지 않은 비밀번호")
        else:
            st.info("로그인")
