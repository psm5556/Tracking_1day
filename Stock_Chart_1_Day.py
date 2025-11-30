import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="Stock Price Chart", layout="wide")

st.title("📈 5분 단위 주식 등락률 차트")

# 티커 리스트
tickers = ['XLF', 'XLE', 'V', 'QTUM', 'SMH', 'UFO', 'ARKG', 'LVMHF', 'NLR']

# 미국 동부 시간대 설정
et_tz = pytz.timezone('America/New_York')

# 현재 시간 기준으로 최근 거래일 데이터 가져오기
now = datetime.now(et_tz)

# 사이드바에서 날짜 선택 옵션 추가
with st.sidebar:
    date_option = st.radio(
        "날짜 선택:",
        ["오늘", "어제", "최근 5일", "사용자 지정"],
        index=1  # 기본값: 어제
    )
    
    if date_option == "사용자 지정":
        selected_date = st.date_input(
            "날짜 선택:",
            value=now.date() - timedelta(days=1),
            max_value=now.date()
        )
        period = "1d"
    elif date_option == "오늘":
        selected_date = now.date()
        period = "1d"
    elif date_option == "어제":
        selected_date = now.date() - timedelta(days=1)
        period = "1d"
    else:  # 최근 5일
        selected_date = None
        period = "5d"

# 날짜 표시
if selected_date:
    st.markdown(f"**날짜**: {selected_date.strftime('%Y년 %m월 %d일')} | **기간**: 1일")
else:
    st.markdown(f"**기간**: 최근 5일")

@st.cache_data(ttl=300)  # 5분 캐시
def fetch_stock_data(ticker, period='1d'):
    """5분 단위 주식 데이터 가져오기"""
    try:
        stock = yf.Ticker(ticker)
        # period 파라미터 사용 (1d, 5d 등)
        df = stock.history(period=period, interval='5m')
        
        if df.empty:
            return None
        
        # 시작 가격을 0%로 정규화
        if len(df) > 0:
            start_price = df['Close'].iloc[0]
            df['Return'] = ((df['Close'] - start_price) / start_price) * 100
            return df
        return None
    except Exception as e:
        st.warning(f"{ticker}: {str(e)}")
        return None

# 데이터 로딩
with st.spinner('데이터를 불러오는 중...'):
    all_data = {}
    progress_bar = st.progress(0)
    
    for idx, ticker in enumerate(tickers):
        data = fetch_stock_data(ticker, period)
        if data is not None and len(data) > 0:
            all_data[ticker] = data
        progress_bar.progress((idx + 1) / len(tickers))
    
    progress_bar.empty()

if not all_data:
    st.error("⚠️ 데이터를 불러올 수 없습니다. 다른 날짜를 선택해보세요.")
    st.info("💡 주말이나 공휴일에는 데이터가 없을 수 있습니다. '어제' 또는 '최근 5일'을 선택해보세요.")
    st.stop()

# 차트 생성
if all_data:
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
    chart_title = f"주식 등락률 (5분 단위)"
    if selected_date:
        chart_title = f"{selected_date.strftime('%Y년 %m월 %d일')} " + chart_title
    else:
        chart_title = "최근 5일 " + chart_title
    
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
                '종가': f"${df['Close'].iloc[-1]:.2f}",
                '일일 등락률': f"{df['Return'].iloc[-1]:.2f}%",
                '최고': f"{df['Return'].max():.2f}%",
                '최저': f"{df['Return'].min():.2f}%"
            })
    
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

# 사이드바 정보
with st.sidebar:
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
    
    **데이터 소스**: Yahoo Finance
    
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
