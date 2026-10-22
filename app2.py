import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static

# 앱 제목 설정 및 기본 부산 중심 좌표
st.title("Busan Subway Map Analysis App")

# [1. 파일 업로드]
uploaded_file = st.file_uploader("busan_subway.csv 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # CSV 데이터 불러오기
    df = pd.read_csv(uploaded_file)

    # 데이터 테이블로 표시
    st.subheader("Raw Subway Data")
    st.dataframe(df)

    # ==========================================
    # [3. 호선 필터 및 데이터 선택]
    # ==========================================
    # 데이터에서 호선 목록 추출
    lines = sorted(df['호선'].unique())
    # 멀티셀렉트로 호선 선택
    selected_lines = st.multiselect("보여줄 호선을 선택하세요", lines, default=lines)

    # 선택된 호선만 데이터 필터링
    df_filtered = df[df['호선'].isin(selected_lines)]

    # ==========================================
    # [2. 지도 설정 및 호선별 색상]
    # ==========================================
    # 필터링된 데이터가 없으면 기본 부산 중심 좌표로 지도 생성
    center = [35.179558, 129.075642]  # 부산 중심
    if not df_filtered.empty:
        # 필터링된 역들의 평균 좌표로 지도 중심 설정
        center = [df_filtered['위도'].mean(), df_filtered['경도'].mean()]

    m = folium.Map(location=center, zoom_start=11)

    # 호선별 색상 매핑 (딕셔너리)
    line_colors = {
        '1호선': 'orange',
        '2호선': 'green',
        '3호선': 'brown',
        '4호선': 'blue'
    }

    # ==========================================
    # [4. 대화형 지도 레이어 (마커 추가)]
    # ==========================================
    # 필터링된 데이터 루프 돌며 CircleMarker 추가
    for idx, row in df_filtered.iterrows():
        # 면적이 이용객 수에 비례하도록 반지름 계산 (이용객수의 제곱근 사용)
        radius = np.sqrt(row['이용객수']) * 0.1

        # 호선별 색상 적용 (정의 안 된 호선은 회색)
        marker_color = line_colors.get(row['호선'], 'gray')

        folium.CircleMarker(
            location=[row['위도'], row['경도']],
            radius=radius,
            color=marker_color,  # 선 색상
            fill=True,
            fill_color=marker_color,  # 채우기 색상
            fill_opacity=0.6,
            tooltip=row['역명'],  # 마우스 올렸을 때: 역명 표시
            popup=f"{row['역명']} ({row['호선']}): {row['이용객수']:,}명"  # 클릭했을 때: 상세 정보 표시
        ).add_to(m)

    # Streamlit 화면에 지도 출력
    st.subheader("🗺️ 지도 분석")
    if not df_filtered.empty:
        folium_static(m)
    else:
        st.warning("선택된 호선이 없습니다.")

    # ==========================================
    # [5. 이용객 상위 5개 역 표 표시]
    # ==========================================
    st.subheader("🏆 이용객 상위 5개 역")
    # 필터링된 데이터 기준 nlargest로 상위 5개 추출
    top5_df = df_filtered.nlargest(5, '이용객수')[['호선', '역명', '이용객수']]
    st.table(top5_df)  # index 제외하고 보기 좋게 표로 출력

else:
    # 파일 미업로드 시 안내 메시지
    st.info("CSV 파일을 업로드하면 분석 결과가 표시됩니다.")