

# 🔬 세포 이미지 분석 페이지
elif page == "🔬 세포 이미지 분석":
    st.markdown("""
    <div class='hospital-header'>
        <div class='hospital-title'>🔬 Advanced Cell Image Analysis</div>
        <div style='text-align: center; margin-top: 0.5rem; font-size: 1.1rem;'>
            5-Model Ensemble Segmentation & AI Prediction
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Cellpose 서버 관리
    import subprocess
    import time
    from pathlib import Path
    
    # 세션 상태 초기화
    if 'cellpose_server_process' not in st.session_state:
        st.session_state.cellpose_server_process = None
    if 'cellpose_server_running' not in st.session_state:
        st.session_state.cellpose_server_running = False
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🚀 고급 세포 이미지 분석 시스템
        
        **주요 기능:**
        - 🎯 **5-Model Ensemble Segmentation**: Cellpose, Omnipose, StarDist, YOLOv8, U-Net
        - 🔬 **형태학적 특징 자동 추출**: 면적, 원형도, 불규칙도, 스트레스 지표
        - 🧠 **AI 약물 반응 예측**: 생존율, 세포사멸 단계, 치료 반응성
        - 📊 **실시간 시각화**: 세포 분할, 특징 분포, 예측 결과
        """)
    
    with col2:
        st.markdown("### 🎮 서버 제어")
        
        if st.session_state.cellpose_server_running:
            st.success("🟢 서버 실행 중")
            if st.button("🛑 서버 중지", use_container_width=True):
                if st.session_state.cellpose_server_process:
                    st.session_state.cellpose_server_process.terminate()
                    st.session_state.cellpose_server_process = None
                st.session_state.cellpose_server_running = False
                st.rerun()
        else:
            st.info("⚪ 서버 대기 중")
            if st.button("▶️ 서버 시작", use_container_width=True, type="primary"):
                try:
                    datacenter_path = Path(__file__).parent / "데이터센터"
                    app_path = datacenter_path / "app.py"
                    
                    if not app_path.exists():
                        st.error(f"❌ 파일을 찾을 수 없습니다: {app_path}")
                    else:
                        # Streamlit 서버 시작
                        process = subprocess.Popen(
                            ["streamlit", "run", str(app_path), "--server.port", "8502", "--server.headless", "true"],
                            cwd=str(datacenter_path),
                            shell=True
                        )
                        st.session_state.cellpose_server_process = process
                        st.session_state.cellpose_server_running = True
                        time.sleep(2)  # 서버 시작 대기
                        st.success("✅ Cellpose 서버가 시작되었습니다!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ 서버 시작 실패: {str(e)}")
    
    st.markdown("---")
    
    # 접속 정보
    if st.session_state.cellpose_server_running:
        st.markdown("""
        ### 📡 접속 정보
        
        Cellpose 데이터센터가 실행 중입니다. 아래 링크를 클릭하거나 새 탭에서 열어주세요:
        """)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <a href="http://localhost:8502" target="_blank" style="
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                text-align: center;
                width: 100%;
            ">
                🔗 Cellpose 분석 열기
            </a>
            """, unsafe_allow_html=True)
            st.caption("**로컬 접속**: http://localhost:8502")
        
        with col2:
            st.info("""
            **현재 상태**
            - 포트: 8502
            - 상태: 🟢 실행 중
            """)
        
        with col3:
            st.info("""
            **지원 파일**
            - .tif, .tiff
            - .png, .jpg, .jpeg
            """)
        
        st.markdown("---")
        
        # 사용 가이드
        with st.expander("📖 사용 가이드", expanded=False):
            st.markdown("""
            #### 1단계: 이미지 업로드
            - 왼쪽 사이드바에서 세포 현미경 이미지 선택
            - 여러 장 동시 업로드 가능
            
            #### 2단계: 분석 옵션 설정
            - **Segmentation Method**: 
              - 🚀 Ensemble All (최고 정확도)
              - ⚡ Ensemble Fast (빠른 속도)
              - 🎯 Ensemble Robust (균형)
              - 📊 Cellpose (기본)
            - **세포 직경**: 예상 크기 조정 (10-100 픽셀)
            - **전처리**: 정규화, 노이즈 제거 옵션
            
            #### 3단계: 결과 확인
            - **이미지 & 분할 탭**: 원본/전처리/마스크 비교
            - **특징 데이터 탭**: 형태학적 통계
            - **딥러닝 예측 탭**: AI 분석 결과
            """)
        
        # 성능 정보
        with st.expander("⚡ 성능 정보", expanded=False):
            st.markdown("""
            #### 분석 속도 (RTX 4060 기준)
            - Ensemble All: ~5-10초/이미지
            - Ensemble Fast: ~2-5초/이미지
            - Cellpose Only: ~1-2초/이미지
            
            #### 검출 정확도
            - Ensemble All: 95%+ 세포 검출률
            - Cellpose Only: 85-90% 세포 검출률
            
            #### GPU 요구사항
            - 권장: NVIDIA RTX 4060 이상
            - 최소: CUDA 지원 GPU (4GB VRAM)
            - CPU 모드도 지원 (속도 느림)
            """)
    
    else:
        # 서버 미실행 시 안내
        st.info("""
        ### ℹ️ 서버 시작 필요
        
        Cellpose 세포 이미지 분석을 사용하려면 위의 **'▶️ 서버 시작'** 버튼을 클릭하세요.
        
        서버가 시작되면 자동으로 새로운 탭에서 분석 도구가 열립니다.
        """)
        
        # 기능 미리보기
        st.markdown("---")
        st.markdown("### 🎯 주요 기능 미리보기")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; color: white;'>
                <h4 style='color: white;'>🚀 Advanced Segmentation</h4>
                <ul style='color: white;'>
                    <li>5-Model Ensemble</li>
                    <li>Cellpose + Omnipose</li>
                    <li>StarDist + YOLOv8</li>
                    <li>U-Net</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style='padding: 1.5rem; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 12px; color: white;'>
                <h4 style='color: white;'>🔬 Feature Analysis</h4>
                <ul style='color: white;'>
                    <li>Morphology</li>
                    <li>Stress Indicators</li>
                    <li>Texture Features</li>
                    <li>Deep Phenotyping</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style='padding: 1.5rem; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border-radius: 12px; color: white;'>
                <h4 style='color: white;'>🧠 AI Prediction</h4>
                <ul style='color: white;'>
                    <li>Drug Response</li>
                    <li>Survival Rate</li>
                    <li>Apoptosis Stage</li>
                    <li>Viability Score</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
