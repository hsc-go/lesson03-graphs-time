import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 데이터(최근 1년, 10위권)를 활용한 시간 관련 그래프 모음")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    # 날짜(예: 20250901) -> datetime으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
    return df


df = load_data()

st.divider()

# ----------------------------------------------------------------------------
# 1. 영화별 날짜에 따른 일일 관객수 변화
# ----------------------------------------------------------------------------
st.header("1. 영화별 일일 관객수 변화")

movie_list = sorted(df["영화명"].unique())
selected_movie = st.selectbox("영화를 선택하세요", movie_list)

movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"'{selected_movie}' 일별 관객수 변화",
    labels={"날짜": "날짜", "일관객": "일일 관객수"},
)
fig1.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일일 관객수: %{y:,}명<extra></extra>"
)
fig1.update_layout(hovermode="x unified")

st.plotly_chart(fig1, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 문구를 입력하세요)")

st.divider()

# ----------------------------------------------------------------------------
# 2. 일관객 합계 상위 5편의 날짜별 일일 관객수 비교
# ----------------------------------------------------------------------------
st.header("2. 상위 5편 일일 관객수 비교")

# 기간 내 일관객 합계 기준 상위 5편 선정
top5_movies = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).head(5).index
)
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 상위 5편의 날짜별 일일 관객수",
    labels={"날짜": "날짜", "일관객": "일일 관객수", "영화명": "영화"},
)
fig2.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일일 관객수: %{y:,}명<extra>%{fullData.name}</extra>"
)
fig2.update_layout(hovermode="x unified", legend_title_text="영화 (클릭해서 켜고 끄기)")

st.plotly_chart(fig2, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 문구를 입력하세요)")

st.divider()

# ----------------------------------------------------------------------------
# 3. 날짜별 10위권 일관객 합계 (영역 그래프)
# ----------------------------------------------------------------------------
st.header("3. 날짜별 박스오피스 합계 추이")

daily_sum_df = df.groupby("날짜")["일관객"].sum().reset_index()
daily_sum_df.columns = ["날짜", "합계관객"]

# 합계가 가장 컸던 상위 3일
top3_days = daily_sum_df.sort_values("합계관객", ascending=False).head(3)

fig3 = px.area(
    daily_sum_df,
    x="날짜",
    y="합계관객",
    title="날짜별 10위권 일관객 합계",
    labels={"날짜": "날짜", "합계관객": "10위권 일관객 합계"},
)
fig3.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계 관객수: %{y:,}명<extra></extra>"
)

# 상위 3일 표시 (점 + 날짜 라벨)
fig3.add_scatter(
    x=top3_days["날짜"],
    y=top3_days["합계관객"],
    mode="markers+text",
    text=top3_days["날짜"].dt.strftime("%Y-%m-%d"),
    textposition="top center",
    marker=dict(size=10, color="red", symbol="star"),
    name="합계 상위 3일",
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계 관객수: %{y:,}명<extra>상위 3일</extra>",
)

st.plotly_chart(fig3, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 문구를 입력하세요)")

st.divider()

# ----------------------------------------------------------------------------
# 4. 일관객 합계 TOP 10 (가로 막대그래프)
# ----------------------------------------------------------------------------
st.header("4. 일관객 합계 TOP 10")

movie_summary = (
    df.groupby("영화명")
    .agg(합계관객=("일관객", "sum"), 등장일수=("날짜", "count"))
    .reset_index()
)
top10_summary = movie_summary.sort_values("합계관객", ascending=False).head(10)
# 가로 막대그래프는 데이터 순서상 아래에서 위로 그려지므로,
# 관객이 많은 영화가 위에 오도록 오름차순으로 정렬해 전달한다.
top10_summary = top10_summary.sort_values("합계관객", ascending=True)

fig4 = px.bar(
    top10_summary,
    x="합계관객",
    y="영화명",
    orientation="h",
    title="이 기간 일관객 합계 TOP 10",
    labels={"합계관객": "일관객 합계", "영화명": "영화"},
    custom_data=["등장일수"],
)
fig4.update_traces(
    hovertemplate=(
        "영화: %{y}<br>"
        "일관객 합계: %{x:,}명<br>"
        "10위권에 든 날수: %{customdata[0]}일<extra></extra>"
    )
)
fig4.update_layout(yaxis_title=None)

st.plotly_chart(fig4, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 문구를 입력하세요)")
