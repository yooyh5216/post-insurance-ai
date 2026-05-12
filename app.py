import streamlit as st
import pandas as pd

st.title("보험 추천 시스템")

file_name = "업무툴만들기.xlsx"

info = pd.read_excel(file_name, sheet_name="상품기본정보")
cover = pd.read_excel(file_name, sheet_name="보장정보")
score = pd.read_excel(file_name, sheet_name="점수정보")
detail = pd.read_excel(file_name, sheet_name="상세정보")

info.columns = info.columns.str.strip()
cover.columns = cover.columns.str.strip()
score.columns = score.columns.str.strip()
detail.columns = detail.columns.str.strip()

df = pd.merge(info, cover, on="상품ID", how="left")
df = pd.merge(df, score, on="상품ID", how="left")
df = pd.merge(df, detail, on="상품ID", how="left")

if "상품명_x" in df.columns:
    df.rename(columns={"상품명_x": "상품명"}, inplace=True)

# 입력
age = st.number_input("나이", 0, 100, 30)

customer_type = st.selectbox("고객 유형", ["일반", "유병자", "장애인"])
purpose = st.selectbox("보험 목적", ["건강보장", "암보장", "연금/노후", "저축/목돈", "사망/가족보장"])
style = st.selectbox("추천 성향", ["보장 중심", "가성비 중심", "균형 추천"])
interest = st.selectbox("관심 보장", ["사망", "암", "뇌/심장", "입원/수술", "간병", "없음"])

if st.button("추천 받기"):

    temp = df.copy()

    # 기본 필터
    temp = temp[(temp["가입최소나이"] <= age) & (temp["가입최대나이"] >= age)]

    if "판매여부" in temp.columns:
        temp = temp[temp["판매여부"].astype(str).str.strip() == "판매중"]

    if "추천제외여부" in temp.columns:
        temp = temp[temp["추천제외여부"].astype(str).str.strip().str.upper() == "N"]

    temp["추천점수"] = temp["최종점수"]

    # 🔥 고객 유형 (정상 핵심)
    if customer_type == "일반":
        temp = temp[temp["유병자여부"].astype(str).str.strip().str.upper().isin(["N", "B"])]
        temp = temp[temp["장애인여부"].astype(str).str.strip().str.upper() != "Y"]

    elif customer_type == "유병자":
        temp = temp[temp["유병자여부"].astype(str).str.strip().str.upper().isin(["Y", "B"])]

    elif customer_type == "장애인":
        temp = temp[temp["장애인여부"].astype(str).str.strip().str.upper() == "Y"]

    # 보험 목적
    if purpose == "연금/노후":
        temp = temp[temp["연금상품여부"].astype(str).str.strip().str.upper() == "Y"]

    elif purpose == "저축/목돈":
        temp = temp[temp["저축성상품여부"].astype(str).str.strip().str.upper() == "Y"]

    elif purpose == "사망/가족보장":
        temp = temp[temp["사망보장"].isin(["Y", "특약"])]

    # 🔥 관심보장 (재해 제거)
    if interest == "간병":
        temp = temp[temp["간병비보장"].astype(str).str.strip().str.upper().isin(["Y", "특약"])]

    elif interest == "암":
        temp = temp[temp["암보장"].astype(str).str.strip().str.upper().isin(["Y", "특약"])]

    elif interest == "뇌/심장":
        temp = temp[
            temp["뇌보장"].astype(str).str.strip().str.upper().isin(["Y", "특약"]) &
            temp["심장보장"].astype(str).str.strip().str.upper().isin(["Y", "특약"])
        ]

    elif interest == "입원/수술":
        temp = temp[temp["입원수술비보장"].astype(str).str.strip().str.upper().isin(["Y", "특약"])]

    # 점수
    if style == "보장 중심":
        temp["추천점수"] += temp.get("보장점수", 0) * 2

    elif style == "가성비 중심":
        temp["추천점수"] += temp.get("가성비점수", 0) * 2

    else:
        temp["추천점수"] += temp.get("보장점수", 0)
        temp["추천점수"] += temp.get("가성비점수", 0)

    # 결과
    result = temp.sort_values(by="추천점수", ascending=False)

    if result.empty:
        st.warning("조건에 맞는 상품이 없습니다.")
    else:
        st.subheader("추천 상품 TOP 3")

        for _, row in result.head(3).iterrows():
            st.markdown(f"### {row['상품명']}")
            st.write("▶ 설명:", row.get("상품상세내역", ""))
            st.write("▶ 주의:", row.get("주의사항", ""))
            st.write("▶ 포인트:", row.get("상담포인트", ""))
            st.markdown("---")