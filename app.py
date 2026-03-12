import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(page_title="익명 건의함", page_icon="📮", layout="centered")

# -----------------------
# Supabase 연결
# -----------------------
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_supabase()

# -----------------------
# DB 함수
# -----------------------
def save_submission(title: str, content: str):
    data = {
        "title": title,
        "content": content,
        "status": "미처리"
    }
    supabase.table("suggestions").insert(data).execute()

def load_submissions():
    response = (
        supabase
        .table("suggestions")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return pd.DataFrame(response.data)

# -----------------------
# 사이드바 메뉴
# -----------------------
mode = st.sidebar.radio("메뉴", ["학생용 제출", "관리자 페이지"])

# -----------------------
# 학생용 페이지
# -----------------------
if mode == "학생용 제출":
    st.title("📮 익명 건의함")
    st.write("익명으로 자유롭게 의견을 남겨줘.")

    with st.form("suggestion_form"):
        title = st.text_input("제목")
        content = st.text_area("내용", height=220)
        submitted = st.form_submit_button("제출")

    if submitted:
        if not title.strip() or not content.strip():
            st.error("제목과 내용을 모두 입력해줘.")
        else:
            save_submission(title.strip(), content.strip())
            st.success("제출이 완료되었어.")

# -----------------------
# 관리자 페이지
# -----------------------
else:
    st.title("🔐 관리자 페이지")
    admin_password = st.text_input("관리자 비밀번호", type="password")

    if admin_password == st.secrets["admin"]["password"]:
        st.success("관리자 인증 완료")
        df = load_submissions()

        if df.empty:
            st.info("제출된 글이 아직 없어.")
        else:
            df = df[["id", "created_at", "title", "content", "status"]]
            st.dataframe(df, use_container_width=True)
    else:
        if admin_password:
            st.error("비밀번호가 올바르지 않아.")
        else:
            st.info("관리자 비밀번호를 입력해줘.")
