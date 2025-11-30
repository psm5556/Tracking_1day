# 📈 5분 단위 주식 등락률 차트

2025년 11월 29일 미국 주식 9종목의 5분 단위 등락률을 실시간으로 시각화하는 Streamlit 애플리케이션입니다.

## 📊 추적 종목

- **XLF**: Financial Select Sector SPDR Fund
- **XLE**: Energy Select Sector SPDR Fund
- **V**: Visa Inc.
- **QTUM**: Defiance Quantum ETF
- **SMH**: VanEck Semiconductor ETF
- **UFO**: Procure Space ETF
- **ARKG**: ARK Genomic Revolution ETF
- **LVMHF**: LVMH Moët Hennessy
- **NLR**: VanEck Uranium+Nuclear Energy ETF

## 🚀 Streamlit Cloud 배포 방법

### 1. GitHub 저장소 생성

1. GitHub에 로그인
2. 새 저장소 생성 (예: `stock-chart-5min`)
3. 이 파일들을 저장소에 업로드:
   - `stock_chart_app.py`
   - `requirements.txt`
   - `README.md`

### 2. Streamlit Cloud 배포

1. [Streamlit Cloud](https://streamlit.io/cloud)에 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택:
   - Repository: `your-username/stock-chart-5min`
   - Branch: `main`
   - Main file path: `stock_chart_app.py`
5. "Deploy!" 클릭

### 3. 앱 실행 확인

배포 후 몇 분 내에 앱이 실행됩니다. Streamlit Cloud가 제공하는 URL로 접속 가능합니다.

## 💻 로컬 실행 방법

```bash
# 의존성 설치
pip install -r requirements.txt

# 앱 실행
streamlit run stock_chart_app.py
```

## 📝 기능

- ✅ 5분 단위 실시간 데이터
- ✅ 시작 시간 0% 기준 등락률 표시
- ✅ 9개 종목 동시 비교
- ✅ 인터랙티브 차트 (확대/축소/호버)
- ✅ 통계 정보 제공

## 🔧 주의사항

- 2025년 11월 29일은 토요일이므로, 실제로는 가장 최근 거래일(11월 28일 금요일) 데이터를 표시합니다.
- Yahoo Finance API를 사용하므로 실시간 데이터는 약 15분 지연될 수 있습니다.
- 장외 거래 시간에는 데이터가 없을 수 있습니다.

## 📄 라이선스

MIT License

## 🙋‍♂️ 문의

이슈나 개선 사항이 있으면 GitHub Issues를 통해 제보해주세요.
