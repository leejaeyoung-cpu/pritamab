# 🧬 AI-based Anticancer Drug Discovery System (ADDS)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 📋 소개

**AI 기반 항암제 칵테일 추론 프로그램**은 환자 맞춤형 항암제 조합을 추천하는 첨단 의료 AI 시스템입니다.

### 주요 기능

- 🤖 **AI 기반 약물 조합 추천**: 환자 데이터를 기반으로 최적의 항암제 조합 추론
- 🔬 **Cellpose 세포 분석**: GPU 가속 기반 종양 세포 자동 검출 및 정량 분석
- 📊 **종합 점수 시스템**: 효능, 시너지, 독성을 통합한 과학적 평가
- 📈 **3D 신호전달 경로 시각화**: 암 종별 분자 신호 경로 인터랙티브 3D 그래프
- 👤 **환자 관리 시스템**: KRAS 변이 추적, 병기별 통계 분석

## 🚀 빠른 시작

### 온라인 데모
[🌐 웹에서 바로 사용하기](https://your-app-url.streamlit.app)

### 로컬 실행

```bash
# 저장소 클론
git clone https://github.com/yourusername/anticancer-drug-system.git
cd anticancer-drug-system

# 의존성 설치
pip install -r requirements.txt

# 앱 실행
streamlit run AI_Anticancer_Drug_System.py
```

## 💡 핵심 기술

### 1. AI 추천 엔진
- **효능 예측**: 환자 나이, 병기, ECOG 점수 기반 맞춤형 효능 계산
- **시너지 분석**: 약물 간 상호작용 정량화
- **독성 평가**: 환자 특성 반영 독성 프로파일링

### 2. Cellpose 이미지 분석
- RTX GPU 가속 지원
- 세포 수, 면적, 위치 자동 정량화
- 배치 분석으로 여러 이미지 동시 처리

### 3. Pritamab 우수성 평가
- 프리온 단백질 표적 치료제
- 효능 +15%, 시너지 +20% 향상
- 낮은 독성 프로파일 (2.0/10)

## 📁 프로젝트 구조

```
anticancer-drug-system/
├── AI_Anticancer_Drug_System.py   # 메인 Streamlit 앱
├── src/
│   ├── recommendation_engine.py    # AI 추천 엔진
│   ├── cellpose_analyzer.py       # 세포 이미지 분석
│   └── inference_dataset_manager.py
├── data/                           # 환자 데이터
├── dataset/                        # 학습 데이터셋
├── docs/                          # 문서
└── requirements.txt               # Python 의존성
```

## 🏥 사용 사례

1. **환자 등록**: 기본 정보, KRAS 변이 상태 입력
2. **Cellpose 분석**: 종양 조직 이미지 업로드 및 자동 분석
3. **AI 추천 받기**: 암 종류와 치료 요법(1제/2제/3제) 선택
4. **조합 비교**: AI 추천 vs 사용자 선택 정량적 비교
5. **3D 시각화**: 신호전달 경로 및 약물 타겟 확인

## 📊 지원 암 종류

- 🎯 대장암 (Colorectal Cancer)
- 🫁 폐암 (Lung Cancer)
- 🎀 유방암 (Breast Cancer)

## 🔬 기술 스택

- **Frontend**: Streamlit
- **AI/ML**: PyTorch, scikit-learn, Cellpose
- **시각화**: Plotly, Matplotlib
- **데이터**: Pandas, NumPy

## 📄 라이선스

이 프로젝트는 연구 및 교육 목적으로 제공됩니다.

**⚠️ 의료 면책**: 이 시스템은 연구 도구이며, 실제 임상 결정에 사용하기 전 전문가의 검토가 필요합니다.

## 👥 개발

**인하대학교병원 AI 항암제 연구팀**

© 2024 Inha University Hospital
