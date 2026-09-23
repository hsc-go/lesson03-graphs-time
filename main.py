import io

import requests
import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", layout="wide")
st.title("영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 데이터(최근 1년, 10위권)를 활용한 시간 관련 그래프 모음")

# raw.githubusercontent.com이 배포 환경 IP에서 간헐적으로 요청을 막는 경우가 있어,
# 캐싱이 되어 더 안정적인 jsDelivr CDN 미러를 우선 시도하고, 실패하면 원본 주소로 재시도한다.
DATA_URLS = [
    "https://cdn.jsdelivr.net/gh/greatsong/modudata@main/data/kobis_daily.csv",
    "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv",
]


@st.cache_data
def load_data():
    headers = {"User-Agent": "Mozilla/5.0"}
    last_error = None
    for url in DATA_URLS:
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            df = pd.read_csv(io.StringIO(response.text))
            # 날짜(예: 20250901) -> datetime으로 변환
            df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")
            return df
        except Exception as e:  # noqa: BLE001
            last_error = e
            continue
    raise RuntimeError(f"데이터를 불러오지 못했습니다: {last_error}")


try:
    df = load_data()
except Exception as e:  # noqa: BLE001
    st.error(
        "데이터를 불러오는 데 실패했습니다. 잠시 후 앱을 새로고침(우측 상단 메뉴 > Rerun)해 주세요.\n\n"
        f"오류 내용: {e}"
    )
    st.stop()

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

st.divider()

# ----------------------------------------------------------------------------
# 5. 월 x 요일별 일관객 합계 (히트맵)
# ----------------------------------------------------------------------------
st.header("5. 월 x 요일별 일관객 합계")

weekday_labels = ["월", "화", "수", "목", "금", "토", "일"]

heatmap_src = df.copy()
heatmap_src["월"] = heatmap_src["날짜"].dt.month
heatmap_src["요일번호"] = heatmap_src["날짜"].dt.weekday  # 0=월요일 ... 6=일요일

heatmap_grouped = (
    heatmap_src.groupby(["요일번호", "월"])["일관객"].sum().reset_index()
)

pivot = heatmap_grouped.pivot(index="요일번호", columns="월", values="일관객")
pivot = pivot.reindex(index=range(7), columns=sorted(heatmap_src["월"].unique()))
pivot.index = weekday_labels  # 월요일부터 일요일 순서로 라벨링

fig5 = px.imshow(
    pivot,
    color_continuous_scale="Reds",
    aspect="auto",
    labels=dict(x="월", y="요일", color="일관객 합계"),
    title="월 x 요일별 일관객 합계 (진할수록 관객 많음)",
)
fig5.update_xaxes(dtick=1, title="월")
fig5.update_yaxes(title="요일")
fig5.update_traces(
    hovertemplate="월: %{x}월<br>요일: %{y}<br>일관객 합계: %{z:,}명<extra></extra>"
)

st.plotly_chart(fig5, use_container_width=True)

st.info("**이 그래프로 알 수 있는 것:** (여기에 문구를 입력하세요)")
