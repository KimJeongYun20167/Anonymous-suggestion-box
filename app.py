import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(
    page_title="📮 2-5 익명 건의함",
    page_icon="📮",
    layout="centered"
)

# -----------------------
# Secrets 불러오기
# -----------------------
POST_URL = st.secrets["sheetdb"]["post_url"].strip()
GET_URL = st.secrets["sheetdb"]["get_url"].strip()
ADMIN_PASSWORD = st.secrets["admin"]["password"].strip()

# -----------------------
# SheetDB 함수
# -----------------------
def save_submission(title: str, content: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    payload = {
        "data": [
            {
                "created_at": now,
                "title": title,
                "content": content,
                "status": "미처리"
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
            "sort_order": "desc"
        },
        timeout=10
    )
    response.raise_for_status()

    data = response.json()

    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)

    wanted_cols = ["created_at", "title", "content", "status"]
    existing_cols = [col for col in wanted_cols if col in df.columns]

    if existing_cols:
        df = df[existing_cols]

    return df


# -----------------------
# 사이드바 메뉴
# -----------------------
mode = st.sidebar.radio("메뉴", ["학생용 제출", "관리자 페이지"])

# -----------------------
# 학생용 페이지
# -----------------------
if mode == "학생용 제출":
    st.title("📮 2-5 익명 건의함")
    st.write("건의사항은 익명으로 보이니 자유롭게 남겨줘!")

    with st.form("suggestion_form"):
        title = st.text_input("제목")
        content = st.text_area("내용", height=220)
        submitted = st.form_submit_button("제출")

    if submitted:
        title = title.strip()
        content = content.strip()

        if not title or not content:
            st.error("제목과 내용을 모두 입력해줘.")
        else:
            try:
                save_submission(title, content)
                st.success("제출 완료!")
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
    st.title("🔐 관리자 페이지")
    admin_password = st.text_input("관리자 비밀번호", type="password")

    if admin_password == ADMIN_PASSWORD:
        st.success("관리자 인증 완료")

        try:
            df = load_submissions()

            if df.empty:
                st.info("제출된 글이 아직 없어.")
            else:
                st.dataframe(df, use_container_width=True)
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
            st.info("관리자 비밀번호를 입력해줘.")
