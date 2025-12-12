"""
재사용 가능한 Streamlit UI 컴포넌트 모듈
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import json
import io

from utils import Logger

logger = Logger(__name__)


def show_image_gallery(images: List[Dict[str, Any]], columns: int = 3):
    """
    이미지 갤러리 표시
    
    Args:
        images: 이미지 정보 딕셔너리 리스트
                {'name': str, 'path': Path, 'thumbnail': optional}
        columns: 열 개수
    """
    if not images:
        st.info("📷 업로드된 이미지가 없습니다.")
        return
    
    st.markdown(f"### 🖼️ 이미지 갤러리 ({len(images)}개)")
    
    # 그리드 레이아웃
    for i in range(0, len(images), columns):
        cols = st.columns(columns)
        
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(images):
                with col:
                    img_info = images[idx]
                    
                    try:
                        # 이미지 로드
                        img_path = img_info.get('path')
                        if img_path and Path(img_path).exists():
                            image = Image.open(img_path)
                            
                            # 썸네일 표시
                            st.image(image, use_container_width=True)
                            st.caption(f"📄 {img_info.get('name', 'Unknown')}")
                            
                            # 정보 표시
                            if 'width' in img_info and 'height' in img_info:
                                st.caption(f"🔍 {img_info['width']}x{img_info['height']}")
                    
                    except Exception as e:
                        st.error(f"이미지 로드 실패: {str(e)}")


def show_cellpose_results(result: Dict[str, Any], show_metrics: bool = True):
    """
    Cellpose 분석 결과 표시
    
    Args:
        result: Cellpose 분석 결과 딕셔너리
        show_metrics: 메트릭 표시 여부
    """
    st.markdown("### 🔬 분석 결과")
    
    # 1. 이미지 비교 (원본 vs 결과)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 원본 이미지")
        if 'image' in result:
            st.image(result['image'], use_container_width=True)
    
    with col2:
        st.markdown("#### 세그멘테이션 결과")
        if 'masks_image' in result:
            st.image(result['masks_image'], use_container_width=True)
    
    # 2. 메트릭
    if show_metrics and 'features' in result:
        st.markdown("---")
        st.markdown("### 📊 추출된 특징")
        
        features = result['features']
        
        # 핵심 메트릭 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "총 세포 수",
                features.get('total_cells', 0),
                delta=None
            )
        
        with col2:
            st.metric(
                "평균 크기",
                f"{features.get('mean_area', 0):.1f} px²",
                delta=None
            )
        
        with col3:
            st.metric(
                "세포 밀도",
                f"{features.get('cell_density', 0):.3f}",
                delta=None
            )
        
        with col4:
            st.metric(
                "평균 강도",
                f"{features.get('mean_intensity', 0):.1f}",
                delta=None
            )
    
    # 3. 상세 특징 테이블
    if 'features' in result:
        with st.expander("📋 상세 특징 보기"):
            features_df = pd.DataFrame([result['features']])
            st.dataframe(features_df.T, use_container_width=True)


def show_feature_table(
    features_df: pd.DataFrame, 
    title: str = "특징 데이터",
    show_stats: bool = True
):
    """
    특징 데이터 테이블 표시
    
    Args:
        features_df: 특징 데이터프레임
        title: 제목
        show_stats: 통계 표시 여부
    """
    st.markdown(f"### 📊 {title}")
    
    if features_df.empty:
        st.info("데이터가 없습니다.")
        return
    
    # 1. 데이터 테이블
    st.dataframe(features_df, use_container_width=True, height=400)
    
    # 2. 기본 통계
    if show_stats:
        with st.expander("📈 기본 통계"):
            st.dataframe(features_df.describe(), use_container_width=True)
    
    # 3. 다운로드 버튼
    csv = features_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="💾 CSV로 다운로드",
        data=csv,
        file_name=f"{title}.csv",
        mime="text/csv"
    )


def show_analysis_summary(results: List[Dict[str, Any]]):
    """
    여러 분석 결과 요약 표시
    
    Args:
        results: 분석 결과 리스트
    """
    if not results:
        st.info("분석 결과가 없습니다.")
        return
    
    st.markdown("### 📊 분석 요약")
    
    # 1. 전체 통계
    total_cells = sum(r.get('features', {}).get('total_cells', 0) for r in results)
    avg_cells = total_cells / len(results) if results else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("분석된 이미지", len(results))
    
    with col2:
        st.metric("총 검출 세포", total_cells)
    
    with col3:
        st.metric("이미지당 평균 세포", f"{avg_cells:.1f}")
    
    # 2. 결과 목록
    st.markdown("---")
    st.markdown("#### 📋 상세 결과")
    
    summary_data = []
    for r in results:
        features = r.get('features', {})
        summary_data.append({
            '이미지': r.get('image_name', 'Unknown'),
            '세포 수': features.get('total_cells', 0),
            '평균 크기': f"{features.get('mean_area', 0):.1f}",
            '세포 밀도': f"{features.get('cell_density', 0):.3f}",
            '평균 강도': f"{features.get('mean_intensity', 0):.1f}"
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)


def download_results_button(
    data: Any, 
    filename: str, 
    label: str = "💾 결과 다운로드",
    file_format: str = 'json'
):
    """
    결과 다운로드 버튼
    
    Args:
        data: 다운로드할 데이터 (dict, DataFrame 등)
        filename: 파일명 (확장자 제외)
        label: 버튼 레이블
        file_format: 파일 형식 ('json', 'csv', 'excel')
    """
    try:
        if file_format == 'json':
            # JSON 형식
            if isinstance(data, pd.DataFrame):
                json_str = data.to_json(orient='records', force_ascii=False, indent=2)
            else:
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
            
            st.download_button(
                label=label,
                data=json_str,
                file_name=f"{filename}.json",
                mime="application/json"
            )
        
        elif file_format == 'csv':
            # CSV 형식
            if isinstance(data, pd.DataFrame):
                csv = data.to_csv(index=False).encode('utf-8-sig')
            else:
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label=label,
                data=csv,
                file_name=f"{filename}.csv",
                mime="text/csv"
            )
        
        elif file_format == 'excel':
            # Excel 형식
            if isinstance(data, pd.DataFrame):
                df = data
            else:
                df = pd.DataFrame(data)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Results')
            
            st.download_button(
                label=label,
                data=output.getvalue(),
                file_name=f"{filename}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    except Exception as e:
        st.error(f"다운로드 준비 중 오류: {str(e)}")


def show_progress_bar(
    current: int, 
    total: int, 
    message: str = "",
    show_percentage: bool = True
):
    """
    진행률 표시
    
    Args:
        current: 현재 진행
        total: 전체
        message: 표시 메시지
        show_percentage: 퍼센트 표시 여부
    """
    progress = current / total if total > 0 else 0
    
    if show_percentage:
        percentage = int(progress * 100)
        full_message = f"{message} ({percentage}%)" if message else f"{percentage}%"
    else:
        full_message = message
    
    st.progress(progress, text=full_message)


def show_file_info_card(file_info: Dict[str, Any]):
    """
    파일 정보 카드 표시
    
    Args:
        file_info: 파일 정보 딕셔너리
    """
    st.markdown(f"""
    <div style="
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    ">
        <h4>📄 {file_info.get('filename', 'Unknown')}</h4>
        <p><strong>크기:</strong> {file_info.get('file_size_mb', 0):.2f} MB</p>
        {f"<p><strong>해상도:</strong> {file_info.get('width', 0)} x {file_info.get('height', 0)}</p>" if 'width' in file_info else ""}
        {f"<p><strong>행/열:</strong> {file_info.get('rows', 0)} / {file_info.get('columns', 0)}</p>" if 'rows' in file_info else ""}
    </div>
    """, unsafe_allow_html=True)


def show_cellpose_config_panel() -> Dict[str, Any]:
    """
    Cellpose 설정 패널 표시
    
    Returns:
        설정 딕셔너리
    """
    st.markdown("### ⚙️ Cellpose 설정")
    
    col1, col2 = st.columns(2)
    
    with col1:
        diameter = st.slider(
            "예상 세포 직경 (픽셀)",
            min_value=10,
            max_value=100,
            value=30,
            step=5,
            help="세포의 예상 직경을 지정합니다. 자동 설정은 0으로 설정하세요."
        )
        
        flow_threshold = st.slider(
            "Flow Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.4,
            step=0.1,
            help="Flow 예측의 임계값. 낮을수록 더 많은 세포를 검출합니다."
        )
    
    with col2:
        model_type = st.selectbox(
            "모델 타입",
            options=['cyto2', 'cyto', 'nuclei'],
            index=0,
            help="cyto2: 세포질 (권장), nuclei: 핵"
        )
        
        cellprob_threshold = st.slider(
            "Cell Probability Threshold",
            min_value=-6.0,
            max_value=6.0,
            value=0.0,
            step=0.5,
            help="세포 확률의 임계값. 높을수록 엄격하게 검출합니다."
        )
    
    # Grayscale 이미지용 채널 설정
    channels = [0, 0]  # Grayscale
    
    config = {
        'diameter': diameter if diameter > 0 else None,
        'channels': channels,
        'flow_threshold': flow_threshold,
        'cellprob_threshold': cellprob_threshold,
        'model_type': model_type
    }
    
    return config


def show_plot_cell_distribution(results: List[Dict[str, Any]]):
    """
    세포 분포 플롯 표시
    
    Args:
        results: 분석 결과 리스트
    """
    if not results:
        return
    
    st.markdown("### 📈 세포 분포 분석")
    
    # 데이터 준비
    cell_counts = [r.get('features', {}).get('total_cells', 0) for r in results]
    image_names = [r.get('image_name', f'Image {i+1}') for i, r in enumerate(results)]
    
    # 막대 그래프
    fig = go.Figure(data=[
        go.Bar(x=image_names, y=cell_counts, marker_color='lightblue')
    ])
    
    fig.update_layout(
        title="이미지별 세포 수",
        xaxis_title="이미지",
        yaxis_title="세포 수",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
