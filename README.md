# 🧬 AI-based Anticancer Drug Discovery System (ADDS)

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://github.com/leejaeyoung-cpu/ADDS)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Cellpose](https://img.shields.io/badge/Cellpose-2.0-green.svg)](https://www.cellpose.org/)

## 📋 시스템 소개 (Introduction)

**AI 기반 항암제 칵테일 추론 프로그램 (ADDS)**은 환자의 임상 데이터와 종양 세포 이미지를 분석하여 최적의 맞춤형 항암제 조합을 추천하는 통합 의료 AI 플랫폼입니다.

본 시스템은 **Pritamab** (프리온 단백질 표적 치료제)을 포함한 다양한 약물 조합의 효능, 시너지, 독성을 예측하고, **Cellpose** 딥러닝 모델을 활용한 정밀 세포 분석 기능을 제공합니다.

---

## 🏗️ 시스템 아키텍처 (System Architecture)

본 프로젝트는 두 개의 주요 모듈로 구성되어 있습니다:

### 1. 🏥 메인 임상 시스템 (Main Clinical System)
- **Port**: `8501`
- **기능**: 환자 관리, AI 약물 추천, 3D 신호전달 경로 시각화
- **실행 파일**: `AI_Anticancer_Drug_System.py`

### 2. 🔬 Cellpose 데이터 센터 (Cellpose Data Center)
- **Port**: `8505` (기본)
- **기능**: 고성능 세포 이미지 분석, 정밀 형태학적 분석, 파인튜닝 데이터 수집
- **실행 파일**: `데이터센터/app.py`

---

## 💡 주요 기능 (Key Features)

### 1. 🤖 AI 약물 추천 엔진 (AI Drug Recommendation)
- **항암제 칵테일 최적화 (Anticancer Cocktail Optimization)**:
    - 단일 약물의 한계를 극복하기 위한 **다제 병용 요법(Combination Therapy)** 자동 설계
    - **시너지 효과(Synergy Effect)** 극대화: 약물 간 상호작용을 분석하여 1+1 > 2가 되는 조합 발굴
    - **내성 억제**: 서로 다른 기전의 약물을 조합하여 암세포의 약물 내성 획득 차단
- **다차원 분석**: 효능(Efficacy), 시너지(Synergy), 독성(Toxicity)을 종합적으로 평가
- **개인화 추천**: 환자의 나이, 성별, 암 종류(대장암/폐암/유방암), 병기, ECOG 점수 반영
- **Pritamab 통합**: 차세대 표적 치료제 Pritamab의 병용 요법 효과 시뮬레이션

### 2. 🔬 Cellpose 데이터 센터 (New!)
최신 딥러닝 기술을 활용한 심층 세포 분석 환경입니다.

- **🔍 정밀 객체 인식**: Cellpose 2.0/3.0 모델(Cyto, Nuclei) 기반 자동 세포 분할
- **🔭 인터랙티브 줌 (Interactive Zoom)**: 고해상도 이미지의 세밀한 확대/축소 및 이동 검사
- **⚙️ 고급 전처리 (Advanced Preprocessing)**:
    - **Upscaling**: 1.5x ~ 3.0x 이미지 확대로 미세 세포 검출력 향상
    - **CLAHE**: 적응형 히스토그램 평활화로 저대비 이미지 분석 성능 강화
- **📊 형태학적 분석**: 세포 크기, 원형도, 밝기, 이질성(Heterogeneity) 자동 계산
- **🚦 세포 상태 분류**: 정상 / 스트레스 / 사멸(Apoptosis) 세포 자동 분류 및 시각화
- **🔧 파인튜닝 지원**: 분석 결과를 학습 데이터로 저장하여 모델 성능 지속적 개선

### 3. 📈 3D 시각화 및 리포트
- **Pathway 3D**: 암종별 주요 신호전달 경로(MAPK, PI3K 등)의 3D 인터랙티브 시각화
- **종합 리포트**: 환자별 분석 결과 및 AI 추천 사유가 포함된 상세 리포트 생성

---

## 🚀 설치 및 실행 (Installation & Usage)

### 1. 환경 설정
```bash
# 저장소 복제
git clone https://github.com/leejaeyoung-cpu/ADDS.git
cd ADDS

# 가상환경 생성 (권장)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. GPU 설정 (선택사항)
Cellpose의 고속 분석을 위해 NVIDIA GPU 사용을 권장합니다.
- [PyTorch CUDA 설치 가이드](https://pytorch.org/get-started/locally/)를 참고하여 호환되는 버전을 설치하세요.

### 3. 프로그램 실행

**A. 메인 시스템 실행 (임상/추천)**
```bash
streamlit run AI_Anticancer_Drug_System.py
```
👉 접속: `http://localhost:8501`

**B. Cellpose 데이터 센터 실행 (이미지 분석)**
```bash
streamlit run 데이터센터/app.py --server.port 8505
```
👉 접속: `http://localhost:8505`

---

## 📁 프로젝트 구조 (Directory Structure)

```
ADDS/
├── AI_Anticancer_Drug_System.py   # [Main] 임상 의사결정 지원 시스템
├── 데이터센터/
│   └── app.py                     # [Sub] Cellpose 정밀 분석 및 데이터 수집
├── src/
│   ├── recommendation_engine.py    # AI 약물 추천 로직
│   ├── cellpose_analyzer.py       # Cellpose 분석 엔진 (전처리/Upscaling 포함)
│   ├── ai_analysis_annotator.py   # 분석 결과 텍스트 생성
│   └── ...
├── modules/
│   └── cellpose_page.py           # 메인 시스템 내장 간편 분석 모듈
├── data/                           # 환자 및 약물 데이터베이스
├── dataset/                        # 학습 및 파인튜닝 데이터 저장소
└── requirements.txt               # 프로젝트 의존성 목록
```

---

## 👥 기여 및 문의 (Contact)

**인하대학교병원 AI 항암제 연구팀**
- **GitHub**: [leejaeyoung-cpu](https://github.com/leejaeyoung-cpu)
- **Project**: ADDS (AI-based Anticancer Drug System)

---

**⚠️ Disclaimer**: 본 시스템은 연구 및 교육 목적으로 개발되었으며, 실제 임상 현장에서의 사용은 전문가의 검토와 승인이 필요합니다.
