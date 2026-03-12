import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="익명 건의함", page_icon="📮")

# ----------------------------
# Google Sheets 연결
# ----------------------------
def connect_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)

    sheet_url = st.secrets["google_sheet"]["url"]
    spreadsheet = client.open_by_url(sheet_url)
    worksheet = spreadsheet.sheet1
    return worksheet

def save_submission(title, content):
    worksheet = connect_sheet()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    worksheet.append_row([now, title, content, "미처리"])

def load_submissions():
    worksheet = connect_sheet()
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

# ----------------------------
# 화면 모드 선택
# ----------------------------
mode = st.sidebar.radio("메뉴", ["학생용 제출", "관리자 페이지"])

# ----------------------------
# 학생용 제출 페이지
# ----------------------------
if mode == "학생용 제출":
    st.title("📮 익명 건의함")
    st.write("이름 없이 자유롭게 건의사항을 남겨줘.")

    with st.form("suggestion_form"):
        title = st.text_input("제목")
        content = st.text_area("내용", height=200)
        submitted = st.form_submit_button("제출")

        if submitted:
            if not title.strip() or not content.strip():
                st.error("제목과 내용을 모두 입력해줘.")
            else:
                save_submission(title.strip(), content.strip())
                st.success("제출이 완료되었어.")

# ----------------------------
# 관리자 페이지
# ----------------------------
else:
    st.title("🔐 관리자 페이지")

    admin_password = st.text_input("관리자 비밀번호", type="password")

    if admin_password == st.secrets["admin"]["password"]:
        st.success("관리자 인증 완료")

        df = load_submissions()

        if df.empty:
            st.info("아직 제출된 글이 없어.")
        else:
            st.subheader("제출 목록")
            st.dataframe(df, use_container_width=True)
    else:
        if admin_password:
            st.error("비밀번호가 올바르지 않아.")
        else:
            st.info("관리자 비밀번호를 입력해줘.")
