import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# 1. 데이터 불러오기 함수
def load_data():
    sheet_id = "1t1reQUHfw0K7BEzPcaxOaCtP8x--ATip7tGhGy11NTU"
    gid = "0"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    # header=None으로 읽어와서 모든 행을 포함시킨 후, 수동으로 컬럼명 지정
    df = pd.read_csv(url, header=None)
    
    # 사용자 요청 기반 컬럼명 설정 (A열: 날짜, B: 담당자, C: 회사, D: 상품, E: 결과)
    df.columns = ['날짜', '담당자명', '회사명', '가입(예정) 상품명', '조치 사항 및 방문결과']
    
    # 날짜 데이터 변환 (에러 발생 시 해당 행은 건너뜀)
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    df = df.dropna(subset=['날짜']) # 날짜 형식이 아닌 행(헤더 등) 제거
    
    return df

# 2. 주 단위 텍스트 생성 (매주 목요일 ~ 다음주 수요일 기준)
def get_custom_week_range(date):
    # 요일 계산 (월=0, 화=1, 수=2, 목=3, 금=4, 토=5, 일=6)
    # 목요일(3)을 기준으로 시작일을 찾음
    days_to_subtract = (date.weekday() - 3) % 7
    start = date - timedelta(days=days_to_subtract)
    end = start + timedelta(days=6)
    return f"{start.month}월{start.day}일 ~ {end.month}월{end.day}일"

try:
    st.set_page_config(page_title="주간 업무 보고서", layout="wide")
    st.title("📊 주간 업무 보고 시스템 (목~수 기준)")

    data = load_data()

    # 맞춤형 주차 컬럼 추가
    data['주차'] = data['날짜'].apply(get_custom_week_range)

    # 사이드바: 주차 선택 (최신 주차가 위로 오도록 정렬)
    weeks = sorted(data['주차'].unique(), reverse=True)
    selected_week = st.sidebar.selectbox("보고서 주차를 선택하세요", weeks)

    st.subheader(f"📅 보고 기간: {selected_week}")

    # 선택된 주차의 데이터 필터링
    filtered_data = data[data['주차'] == selected_week]

    if filtered_data.empty:
        st.info("선택한 기간에 해당하는 데이터가 없습니다.")
    else:
        # 담당자별 취합 및 출력
        managers = filtered_data['담당자명'].unique()

        for manager in managers:
            with st.expander(f"👤 담당자: {manager}", expanded=True):
                m_data = filtered_data[filtered_data['담당자명'] == manager]
                # B, C, D, E열 데이터 출력
                display_cols = ['회사명', '가입(예정) 상품명', '조치 사항 및 방문결과']
                st.table(m_data[display_cols])

except Exception as e:
    st.error(f"오류가 발생했습니다. 스프레드시트 공유 설정을 확인해주세요.")
    st.info(f"에러 내용: {e}")