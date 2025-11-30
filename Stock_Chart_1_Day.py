import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="Stock Price Chart", layout="wide")

st.title("📈 5분 단위 주식 등락률 차트")
st.markdown("**날짜**: 2025년 11월 29일 | **기간**: 1일")

# 티커 리스트
tickers = ['XLF', 'XLE', 'V', 'QTUM', 'SMH', 'UFO', 'ARKG', 'LVMHF', 'NLR']

# 미국 동부 시간대 설정
et_tz = pytz.timezone('America/New_York')

# 2025년 11월 29일 (토요일이므로 이전 금요일 데이터 사용)
# 실제로는 11월 28일(금요일) 데이터를 가져옴
target_date = datetime(2025, 11, 28)
start_date = target_date
end_date = target_date + timedelta(days=1)

@st.cache_data
def fetch_stock_data(ticker, start, end):
    """5분 단위 주식 데이터 가져오기"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start, end=end, interval='5m')
        
        if df.empty:
            st.warning(f"{ticker}: 데이터가 없습니다.")
            return None
        
        # 시작 가격을 0%로 정규화
        if len(df) > 0:
            start_price = df['Close'].iloc[0]
            df['Return'] = ((df['Close'] - start_price) / start_price) * 100
            return df
        return None
    except Exception as e:
        st.error(f"{ticker} 데이터 로드 오류: {str(e)}")
        return None

# 데이터 로딩
with st.spinner('데이터를 불러오는 중...'):
    all_data = {}
    for ticker in tickers:
        data = fetch_stock_data(ticker, start_date, end_date)
        if data is not None:
            all_data[ticker] = data

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
    fig.update_layout(
        title={
            'text': '2025년 11월 29일 주식 등락률 (5분 단위)',
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
    
else:
    st.error("데이터를 불러올 수 없습니다. 날짜를 확인해주세요.")

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
    
    **업데이트**: 5분 간격
    """)
    
    st.info("💡 차트를 확대/축소하려면 드래그하거나 더블클릭하세요.")
