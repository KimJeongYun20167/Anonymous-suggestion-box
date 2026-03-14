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
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 820px;
}

.main-card {
    background-color: #ffffff;
    padding: 1.4rem 1.2rem;
    border-radius: 18px;
    border: 1px solid #e9ecef;
    box-shadow: 0 4px 14px rgba(0,0,0,0.04);
    margin-bottom: 1rem;
}

.section-title {
    font-size: 1.8rem;
    font-weight: 800;
    margin-bottom: 0.3rem;
}

.section-sub {
    color: #6b7280;
    font-size: 0.98rem;
    margin-bottom: 0.2rem;
}

.small-note {
    font-size: 0.88rem;
    color: #6b7280;
}

div[data-testid="stForm"] {
    border: 1px solid #ececec;
    border-radius: 16px;
    padding: 1rem 1rem 0.6rem 1rem;
    background-color: #fcfcfc;
}

div[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

hr {
    margin-top: 1rem;
    margin-bottom: 1rem;
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

    return df


# -----------------------
# 사이드바
# -----------------------
mode = st.sidebar.radio("탭", ["건의사항 제출", "관리자 페이지"])

# -----------------------
# 학생용 페이지
# -----------------------
if mode == "건의사항 제출":
    st.markdown("""
    <div class="main-card">
        <div class="section-title">📮 2-8 익명 건의함</div>
        <div class="section-sub">
            하고 싶은 말, 바라는 점, 불편했던 점을 자유롭게 남겨줘.
        </div>
        <div class="small-note">
            익명으로 제출되며, 제목과 내용을 모두 입력해야 제출돼.
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("suggestion_form"):
        title = st.text_input("제목", placeholder="예: 급식 건의, 교실 환경, 수업 의견")
        content = st.text_area(
            "내용",
            height=220,
            placeholder="하고 싶은 말을 자유롭게 적어줘."
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
                st.success("제출 완료! 의견이 잘 전달됐어.")
                st.balloons()
            except requests.HTTPError as e:
                st.error("제출 요청이 실패했어.")
                st.exception(e)
            except requests.RequestException as e:
                st.error("네트워크 요청 중 오류가 발생했어.")
                st.exception(e)
            except Exception as e:
                st.error("제출 중 오류가 발생했어.")
                st.exception(e)

# -----------------------
# 관리자 페이지
# -----------------------
else:
    st.markdown("""
    <div class="main-card">
        <div class="section-title">🔐 관리자 페이지</div>
        <div class="section-sub">
            제출된 건의사항을 확인하는 공간이야.
        </div>
        <div class="small-note">
            관리자 비밀번호를 입력하면 목록을 볼 수 있어.
        </div>
    </div>
    """, unsafe_allow_html=True)

    admin_password = st.text_input("관리자 비밀번호", type="password", placeholder="비밀번호 입력")

    if admin_password == ADMIN_PASSWORD:
        st.success("인증 완료")
        st.snow()

        try:
            df = load_submissions()

            if df.empty:
                st.info("제출된 글이 아직 없어.")
            else:
                st.markdown("### 제출 목록")
                st.caption("오래된 순서부터 표시돼.")
                st.dataframe(df, use_container_width=True, hide_index=True)

        except requests.HTTPError as e:
            st.error("관리자 데이터 조회 요청이 실패했어.")
            st.exception(e)
        except requests.RequestException as e:
            st.error("네트워크 요청 중 오류가 발생했어.")
            st.exception(e)
        except Exception as e:
            st.error("관리자 데이터 조회 중 오류가 발생했어.")
            st.exception(e)

    else:
        if admin_password:
            st.error("비밀번호가 올바르지 않아!")
        else:
            st.info("비밀번호를 입력해줘.")
