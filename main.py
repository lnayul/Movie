import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption("1년치 일별 박스오피스 데이터를 시간의 흐름에 따라 살펴봅니다.")

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜를 실제 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d"
    )

    # 숫자형으로 변환
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

except Exception:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()


# --------------------------------------------------
# 데이터 기본 정보
# --------------------------------------------------
st.info(
    f"📊 총 {len(df):,}개의 기록을 불러왔습니다. "
    f"기간: {df['날짜'].min().strftime('%Y-%m-%d')} ~ "
    f"{df['날짜'].max().strftime('%Y-%m-%d')}"
)


# ==================================================
# 그래프 1. 영화별 시간에 따른 일관객 변화
# ==================================================
st.header("1. 영화별 시간에 따른 일관객 변화")

st.write(
    "영화를 하나 선택하면 해당 영화의 날짜별 일관객 변화를 "
    "선 그래프로 확인할 수 있습니다."
)

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list
)

movie_df = df[df["영화명"] == selected_movie].copy()
movie_df = movie_df.sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"「{selected_movie}」의 날짜별 일관객 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수"
    }
)

fig1.update_traces(
    hovertemplate=
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,.0f}명"
    "<extra></extra>"
)

fig1.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    height=500
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_input(
    "그래프를 보고 알 수 있는 점을 한 문장으로 적어 보세요.",
    placeholder="예: 개봉 초기에 관객이 많았지만 시간이 지나면서 일관객 수가 감소하는 경향을 보인다.",
    key="graph1_comment"
)


# ==================================================
# 그래프 2. 일관객 합계 TOP 5 영화의 시간별 변화
# ==================================================
st.divider()

st.header("2. 일관객 합계가 가장 큰 영화 TOP 5")

st.write(
    "전체 기간 동안의 일관객을 합산하여 관객 수가 가장 많았던 "
    "5편의 날짜별 일관객 변화를 비교합니다."
)

top5_movies = (
    df.groupby("영화명", as_index=False)["일관객"]
    .sum()
    .sort_values("일관객", ascending=False)
    .head(5)["영화명"]
    .tolist()
)

top5_df = df[
    df["영화명"].isin(top5_movies)
].copy()

top5_df = top5_df.sort_values(
    ["날짜", "영화명"]
)

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 TOP 5 영화의 날짜별 변화",
    labels={
        "날짜": "날짜",
        "일관객": "일관객 수",
        "영화명": "영화"
    }
)

fig2.update_traces(
    hovertemplate=
    "영화: %{fullData.name}<br>"
    "날짜: %{x|%Y-%m-%d}<br>"
    "일관객: %{y:,.0f}명"
    "<extra></extra>"
)

fig2.update_layout(
    hovermode="x unified",
    xaxis_title="날짜",
    yaxis_title="일관객 수(명)",
    height=600,
    legend_title="영화",
    legend=dict(
        itemclick="toggle",
        itemdoubleclick="toggleothers"
    )
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_input(
    "그래프를 보고 알 수 있는 점을 한 문장으로 적어 보세요.",
    placeholder="예: 영화마다 일관객이 가장 높아지는 시점과 감소하는 속도에 차이가 나타난다.",
    key="graph2_comment"
)


# ==================================================
# 그래프 3. 날짜별 10위권 일관객 합계
# ==================================================
st.divider()

st.header("3. 날짜별 10위권 일관객 합계")

st.write(
    "각 날짜의 박스오피스 10위권 영화들의 일관객을 모두 합산하여 "
    "하루 동안 10위권 영화가 기록한 전체 관객 규모를 살펴봅니다."
)

daily_audience = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = (
    daily_audience
    .nlargest(3, "일관객")
    .sort_values("날짜")
)

fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(
        x=daily_audience["날짜"],
        y=daily_audience["일관객"],
        mode="lines",
        fill="tozeroy",
        name="10위권 일관객 합계",
        hovertemplate=
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig3.add_trace(
    go.Scatter(
        x=top3_days["날짜"],
        y=top3_days["일관객"],
        mode="markers+text",
        marker=dict(
            size=10
        ),
        text=[
            date.strftime("%Y-%m-%d")
            for date in top3_days["날짜"]
        ],
        textposition="top center",
        name="일관객 합계 TOP 3",
        hovertemplate=
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig3.update_layout(
    title="날짜별 10위권 일관객 합계",
    xaxis_title="날짜",
    yaxis_title="10위권 일관객 합계(명)",
    height=550,
    hovermode="x unified",
    showlegend=True
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_input(
    "그래프를 보고 알 수 있는 점을 한 문장으로 적어 보세요.",
    placeholder="예: 특정 날짜에는 10위권 영화 전체의 일관객 합계가 크게 증가하는 모습을 확인할 수 있다.",
    key="graph3_comment"
)


# ==================================================
# 그래프 4. 영화별 일관객 합계 TOP 10
# ==================================================
st.divider()

st.header("4. 영화별 일관객 합계 TOP 10")

st.write(
    "전체 기간 동안 각 영화의 일관객을 모두 더해 "
    "관객 수가 가장 많은 영화 10편을 비교합니다."
)

movie_summary = (
    df.groupby("영화명")
    .agg(
        일관객합계=("일관객", "sum"),
        10위권_기록일수=("날짜", "nunique")
    )
    .reset_index()
)

top10_movies = (
    movie_summary
    .sort_values("일관객합계", ascending=False)
    .head(10)
    .copy()
)

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
    custom_data=["10위권_기록일수"]
)

fig4.update_traces(
    hovertemplate=
    "영화: %{y}<br>"
    "일관객 합계: %{x:,.0f}명<br>"
    "10위권 기록 일수: %{customdata[0]}일"
    "<extra></extra>"
)

fig4.update_layout(
    xaxis_title="기간 내 일관객 합계(명)",
    yaxis_title="영화",
    height=600
)

st.plotly_chart(
    fig4,
    use_container_width=True
)

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_input(
    "그래프를 보고 알 수 있는 점을 한 문장으로 적어 보세요.",
    placeholder="예: 전체 기간의 관객 규모가 큰 영화일수록 10위권에 머문 기간도 긴 경향이 나타나는지 비교할 수 있다.",
    key="graph4_comment"
)


# ==================================================
# 그래프 5. 월 × 요일별 일관객 합계 히트맵
# ==================================================
st.divider()

st.header("5. 월 × 요일별 일관객 합계")

st.write(
    "날짜에서 월과 요일을 추출하여, 각 월의 각 요일에 "
    "10위권 영화들이 기록한 일관객 합계를 히트맵으로 나타냅니다."
)

# --------------------------------------------------
# 월과 요일 추출
# --------------------------------------------------
heatmap_df = df.copy()

heatmap_df["월"] = heatmap_df["날짜"].dt.month

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

heatmap_df["요일"] = heatmap_df["날짜"].dt.weekday.map(weekday_map)

# --------------------------------------------------
# 월 × 요일별 일관객 합계
# --------------------------------------------------
monthly_weekday = (
    heatmap_df
    .groupby(["월", "요일"], as_index=False)["일관객"]
    .sum()
)

# 월 × 요일 형태로 변환
heatmap_pivot = (
    monthly_weekday
    .pivot(
        index="월",
        columns="요일",
        values="일관객"
    )
    .reindex(columns=weekday_order)
)

# --------------------------------------------------
# 히트맵
# --------------------------------------------------
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

fig5.update_layout(
    height=600,
    xaxis_title="요일",
    yaxis_title="월"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)

st.markdown("**이 그래프로 알 수 있는 것**")

st.text_input(
    "그래프를 보고 알 수 있는 점을 한 문장으로 적어 보세요.",
    placeholder="예: 월과 요일에 따라 10위권 영화의 일관객 합계에 차이가 나타나는 것을 확인할 수 있다.",
    key="graph5_comment"
)


# ==================================================
# 그래프 6. 앞으로 추가할 그래프
# ==================================================
st.divider()

st.header("6. 다음 그래프")
st.caption("앞으로 새로운 그래프를 이 구역에 추가할 예정입니다.")
