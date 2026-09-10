import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 데이터를 이용하여 영화와 시간의 관계를 그래프로 살펴봅니다.")


# =========================================================
# 데이터 불러오기
# =========================================================

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # 숫자형 변환
    numeric_columns = [
        "순위",
        "영화코드",
        "일관객",
        "누적관객",
        "스크린수",
        "상영횟수"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()


# =========================================================
# 데이터 기본 정보
# =========================================================

st.info(
    f"총 {len(df):,}개의 기록이 있으며, "
    f"{df['날짜'].min().strftime('%Y-%m-%d')}부터 "
    f"{df['날짜'].max().strftime('%Y-%m-%d')}까지의 데이터를 사용합니다."
)


# =========================================================
# 그래프 1
# 영화별 시간에 따른 일관객 변화
# =========================================================

st.header("1. 영화별 시간에 따른 일관객 변화")

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list
)

movie_df = (
    df[df["영화명"] == selected_movie]
    .sort_values("날짜")
    .copy()
)

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객"
    }
)

fig1.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,.0f}명"
    "<extra></extra>"
)

fig1.update_layout(
    hovermode="x unified"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "그래프 1에서 알 수 있는 점을 입력하세요.",
    key="graph1_answer",
    placeholder="예: 영화의 일관객은 날짜에 따라 증가하거나 감소하는 모습을 보인다."
)


# =========================================================
# 그래프 2
# 일관객 합계가 가장 큰 영화 TOP 5
# =========================================================

st.divider()

st.header("2. 일관객 합계가 가장 큰 영화 TOP 5")

top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)
)

top5_names = top5_movies["영화명"].tolist()

top5_df = (
    df[df["영화명"].isin(top5_names)]
    .sort_values(["영화명", "날짜"])
    .copy()
)

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계가 가장 큰 영화 TOP 5의 날짜별 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객",
        "영화명": "영화"
    }
)

fig2.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,.0f}명"
    "<extra></extra>"
)

fig2.update_layout(
    hovermode="x unified",
    legend=dict(
        itemclick="toggle",
        itemdoubleclick="toggleothers"
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.caption("범례의 영화를 클릭하면 해당 영화의 그래프를 켜거나 끌 수 있습니다.")

st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "그래프 2에서 알 수 있는 점을 입력하세요.",
    key="graph2_answer",
    placeholder="예: 인기 영화도 날짜에 따라 일관객의 변화 폭이 다르게 나타난다."
)


# =========================================================
# 그래프 3
# 날짜별 10위권 일관객 합계
# =========================================================

st.divider()

st.header("3. 날짜별 10위권 일관객 합계")

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

# 일관객 합계가 가장 높은 날짜 TOP 3
top3_days = (
    daily_total
    .nlargest(3, "일관객")
    .sort_values("날짜")
)

fig3 = go.Figure()

# 전체 영역 그래프
fig3.add_trace(
    go.Scatter(
        x=daily_total["날짜"],
        y=daily_total["일관객"],
        mode="lines",
        fill="tozeroy",
        name="10위권 일관객 합계",
        hovertemplate=
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,.0f}명"
        "<extra></extra>"
    )
)

# TOP 3 표시
fig3.add_trace(
    go.Scatter(
        x=top3_days["날짜"],
        y=top3_days["일관객"],
        mode="markers+text",
        name="일관객 합계 TOP 3",
        text=[
            f"{date.strftime('%m/%d')}<br>{value:,.0f}명"
            for date, value in zip(
                top3_days["날짜"],
                top3_days["일관객"]
            )
        ],
        textposition="top center",
        marker=dict(size=10),
        hovertemplate=
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig3.update_layout(
    title="날짜별 영화 TOP 10의 일관객 합계",
    xaxis_title="날짜",
    yaxis_title="일관객 합계",
    hovermode="x unified"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "그래프 3에서 알 수 있는 점을 입력하세요.",
    key="graph3_answer",
    placeholder="예: 특정 날짜에는 영화관을 찾은 관객이 평소보다 크게 증가했다."
)


# =========================================================
# 그래프 4
# 영화별 일관객 합계 TOP 10
# =========================================================

st.divider()

st.header("4. 영화별 일관객 합계 TOP 10")

movie_summary = (
    df.groupby("영화명")
    .agg(
        일관객합계=("일관객", "sum"),
        기록일수=("날짜", "nunique")
    )
    .reset_index()
)

top10_movies = (
    movie_summary
    .sort_values("일관객합계", ascending=False)
    .head(10)
    .copy()
)

# 그래프에서 가장 큰 값이 위에 오도록 역순 정렬
top10_movies = top10_movies.sort_values(
    "일관객합계",
    ascending=True
)

fig4 = px.bar(
    top10_movies,
    x="일관객합계",
    y="영화명",
    orientation="h",
    title="영화별 일관객 합계 TOP 10",
    labels={
        "일관객합계": "기간 내 일관객 합계",
        "영화명": "영화"
    },
    custom_data=["기록일수"]
)

fig4.update_traces(
    hovertemplate=
    "영화: %{y}<br>"
    "일관객 합계: %{x:,.0f}명<br>"
    "10위권 기록 일수: %{customdata[0]}일"
    "<extra></extra>"
)

fig4.update_layout(
    yaxis=dict(
        categoryorder="total ascending"
    )
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "그래프 4에서 알 수 있는 점을 입력하세요.",
    key="graph4_answer",
    placeholder="예: 기간 전체에서 일관객 합계가 높은 영화와 그 차이를 비교할 수 있다."
)


# =========================================================
# 그래프 5
# 월 × 요일별 10위권 일관객 합계
# =========================================================

st.divider()

st.header("5. 월 × 요일별 10위권 일관객 합계")

heatmap_df = df.copy()

# 월 추출
heatmap_df["월"] = heatmap_df["날짜"].dt.month

# 요일 이름 변환
weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일"
]

weekday_map = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일"
}

heatmap_df["요일"] = (
    heatmap_df["날짜"]
    .dt.weekday
    .map(weekday_map)
)

# 월 × 요일별 일관객 합계
monthly_weekday = (
    heatmap_df
    .groupby(["월", "요일"], as_index=False)["일관객"]
    .sum()
)

# 피벗 테이블 생성
heatmap_pivot = (
    monthly_weekday
    .pivot(
        index="월",
        columns="요일",
        values="일관객"
    )
    .reindex(columns=weekday_order)
)

# 월 순서 정리
heatmap_pivot = heatmap_pivot.sort_index()

# 숫자가 없는 부분은 0
heatmap_pivot = heatmap_pivot.fillna(0)

fig5 = px.imshow(
    heatmap_pivot,
    labels={
        "x": "요일",
        "y": "월",
        "color": "일관객 합계"
    },
    x=weekday_order,
    y=[f"{month}월" for month in heatmap_pivot.index],
    aspect="auto",
    text_auto=".0f",
    title="월 × 요일별 10위권 일관객 합계"
)

fig5.update_traces(
    hovertemplate=
    "월: %{y}<br>"
    "요일: %{x}<br>"
    "일관객 합계: %{z:,.0f}명"
    "<extra></extra>"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.subheader("이 그래프로 알 수 있는 것")

st.text_input(
    "그래프 5에서 알 수 있는 점을 입력하세요.",
    key="graph5_answer",
    placeholder="예: 월과 요일에 따라 10위권 영화의 전체 관객 규모가 다르게 나타난다."
)


# =========================================================
# 다음 그래프 추가 공간
# =========================================================

st.divider()

st.header("6. 다음 그래프")

st.write("여기에 새로운 그래프를 추가할 수 있습니다.")
