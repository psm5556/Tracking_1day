import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import requests
import time

st.set_page_config(page_title="Stock Price Chart", layout="wide")

st.title("📈 5분 단위 주식 등락률 차트")

# 티커 리스트
tickers = ['XLF', 'XLE', 'V', 'QTUM', 'SMH', 'UFO', 'ARKG', 'LVMHF', 'NLR']

# 미국 동부 시간대 설정
et_tz = pytz.timezone('America/New_York')
now = datetime.now(et_tz)

# 사이드바에서 날짜 선택 옵션 추가
with st.sidebar:
    date_option = st.radio(
        "날짜 선택:",
        ["최근 5일", "최근 3일", "최근 1일"],
        index=0  # 기본값: 최근 5일
    )
    
    if date_option == "최근 1일":
        days_back = 5  # 충분한 데이터를 위해 5일 요청
        days_to_show = 1
    elif date_option == "최근 3일":
        days_back = 5
        days_to_show = 3
    else:  # 최근 5일
        days_back = 5
        days_to_show = 5

# 날짜 표시
st.markdown(f"**기간**: {date_option} | **간격**: 5분")

@st.cache_data(ttl=300)  # 5분 캐시
def fetch_stock_data_api(ticker, days_back, days_to_show):
    """
    Yahoo Finance Chart API를 직접 호출하여 주식 데이터 가져오기
    첨부 코드의 get_stock_data 함수와 동일한 방식
    """
    try:
        # 날짜 범위 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # timestamp 변환
        start_timestamp = int(start_date.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        end_timestamp = int(end_date.replace(hour=23, minute=59, second=59, microsecond=999000).timestamp())
        
        # Yahoo Finance Chart API 호출
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {
            'period1': start_timestamp,
            'period2': end_timestamp,
            'interval': '5m'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=20)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # 응답 데이터 검증
        if not data.get('chart') or not data['chart'].get('result') or len(data['chart']['result']) == 0:
            return None
        
        result = data['chart']['result'][0]
        timestamps = result.get('timestamp', [])
        
        if not timestamps:
            return None
        
        # 가격 데이터 추출
        indicators_list = result.get('indicators', {}).get('quote', [])
        if not indicators_list or len(indicators_list) == 0:
            return None
        
        indicators = indicators_list[0]
        opens = indicators.get('open', [])
        highs = indicators.get('high', [])
        lows = indicators.get('low', [])
        closes = indicators.get('close', [])
        volumes = indicators.get('volume', [])
        
        # DataFrame 생성
        data_list = []
        for i in range(len(timestamps)):
            if closes[i] is not None and opens[i] is not None and highs[i] is not None and lows[i] is not None:
                date = datetime.fromtimestamp(timestamps[i])
                data_list.append({
                    'Date': date,
                    'Open': float(opens[i]),
                    'High': float(highs[i]),
                    'Low': float(lows[i]),
                    'Close': float(closes[i]),
                    'Volume': int(volumes[i]) if volumes[i] is not None else 0
                })
        
        if not data_list:
            return None
        
        df = pd.DataFrame(data_list)
        df = df.set_index('Date')
        df = df.sort_index()
        
        # 최근 N일 데이터만 필터링
        if days_to_show < days_back and len(df) > 0:
            cutoff_date = df.index[-1] - timedelta(days=days_to_show)
            df = df[df.index >= cutoff_date]
        
        if df.empty:
            return None
        
        # 시작 가격을 0%로 정규화
        start_price = df['Close'].iloc[0]
        df['Return'] = ((df['Close'] - start_price) / start_price) * 100
        
        return df
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

# 데이터 로딩
with st.spinner('데이터를 불러오는 중...'):
    all_data = {}
    progress_bar = st.progress(0)
    
    for idx, ticker in enumerate(tickers):
        data = fetch_stock_data_api(ticker, days_back, days_to_show)
        if data is not None and len(data) > 0:
            all_data[ticker] = data
        # API rate limiting
        time.sleep(0.1)
        progress_bar.progress((idx + 1) / len(tickers))
    
    progress_bar.empty()

if not all_data:
    st.error("⚠️ 데이터를 불러올 수 없습니다.")
    st.info("💡 Yahoo Finance API에 일시적인 문제가 있을 수 있습니다. 잠시 후 다시 시도해주세요.")
    st.stop()

# 차트 생성
fig = go.Figure()

# 각 티커의 등락률 라인 추가
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
          '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']

for idx, (ticker, df) in enumerate(all_data.items()):
    color = colors[idx % len(colors)]
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Return'],
        mode='lines',
        name=ticker,
        line=dict(width=2, color=color),
        hovertemplate='<b>%{fullData.name}</b><br>' +
                      '시간: %{x}<br>' +
                      '등락률: %{y:.2f}%<br>' +
                      '<extra></extra>'
    ))

# 0% 기준선 추가
fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

# 레이아웃 설정
chart_title = f"주식 등락률 (5분 단위) - {date_option}"

fig.update_layout(
    title={
        'text': chart_title,
        'x': 0.5,
        'xanchor': 'center',
        'font': {'size': 20}
    },
    xaxis_title='시간',
    yaxis_title='등락률 (%)',
    hovermode='x unified',
    legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1.01
    ),
    height=600,
    template='plotly_white',
    yaxis=dict(
        zeroline=True,
        zerolinewidth=2,
        zerolinecolor='gray',
        ticksuffix='%'
    )
)

st.plotly_chart(fig, use_container_width=True)

# 통계 정보
st.subheader("📊 등락률 통계")

stats_data = []
for ticker, df in all_data.items():
    if len(df) > 0:
        stats_data.append({
            '티커': ticker,
            '시작가': f"${df['Close'].iloc[0]:.2f}",
            '현재가': f"${df['Close'].iloc[-1]:.2f}",
            '등락률': f"{df['Return'].iloc[-1]:.2f}%",
            '최고': f"{df['Return'].max():.2f}%",
            '최저': f"{df['Return'].min():.2f}%",
            '데이터 개수': len(df)
        })

stats_df = pd.DataFrame(stats_data)
st.dataframe(stats_df, use_container_width=True, hide_index=True)

# 사이드바 정보
with st.sidebar:
    st.divider()
    st.header("ℹ️ 정보")
    st.markdown("""
    **티커 목록:**
    - XLF: Financial Select Sector SPDR Fund
    - XLE: Energy Select Sector SPDR Fund
    - V: Visa Inc.
    - QTUM: Defiance Quantum ETF
    - SMH: VanEck Semiconductor ETF
    - UFO: Procure Space ETF
    - ARKG: ARK Genomic Revolution ETF
    - LVMHF: LVMH Moët Hennessy
    - NLR: VanEck Uranium+Nuclear Energy ETF
    
    **데이터 소스**: Yahoo Finance Chart API
    
    **업데이트**: 5분 간격 (5분 캐시)
    """)
    
    st.info("💡 차트를 확대/축소하려면 드래그하거나 더블클릭하세요.")
    
    st.divider()
    
    # 성공적으로 로드된 티커 표시
    if all_data:
        st.success(f"✅ {len(all_data)}/{len(tickers)} 종목 로드 완료")
        loaded_tickers = list(all_data.keys())
        failed_tickers = [t for t in tickers if t not in loaded_tickers]
        
        if failed_tickers:
            st.warning(f"⚠️ 로드 실패: {', '.join(failed_tickers)}")
    
    st.divider()
    
    # 사용 팁
    st.markdown("""
    ### 💡 사용 팁
    
    **5분 데이터 특성:**
    - 장중 시간대에만 데이터 생성
    - 미국 동부시간 기준 9:30 AM ~ 4:00 PM
    - 한국시간 기준 밤 11:30 PM ~ 새벽 6:00 AM
    
    **데이터 로드 실패 시:**
    - 페이지 새로고침 (F5)
    - 잠시 후 다시 시도
    - 다른 기간 옵션 선택
    
    **참고:**
    - Yahoo Finance Chart API 직접 사용
    - yfinance 라이브러리 미사용
    """)
