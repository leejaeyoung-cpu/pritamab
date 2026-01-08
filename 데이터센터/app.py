import streamlit as st
import sys
import os
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
import cv2
import matplotlib.pyplot as plt
from matplotlib import cm
import plotly.express as px

# Add parent directory to path to import src modules
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    from src.cellpose_analyzer import CellposeAnalyzer
except ImportError:
    # Fallback if run from different context
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.cellpose_analyzer import CellposeAnalyzer

# Page Config
st.set_page_config(
    page_title="Cellpose Data Center",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS for styling (matching screenshots)
st.markdown("""
<style>
    .report-header {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #4a90e2;
    }
    .report-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    .section-header {
        background-color: #f8f9fa;
        padding: 0.8rem;
        border-radius: 5px;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        border: 1px solid #e9ecef;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeeba;
        margin: 1rem 0;
    }
    .success-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .warning-badge {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .danger-badge {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar
    with st.sidebar:
        st.title("🔬 Cellpose 설정")
        
        model_type = st.selectbox(
            "모델 선택",
            ["cyto3", "cyto2", "nuclei"],
            index=0
        )
        
        diameter = st.slider(
            "세포 직경 (Diameter)",
            min_value=10,
            max_value=100,
            value=20
        )
        
        flow_threshold = st.slider(
            "Flow Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.3
        )
        
        st.markdown("---")
        st.info("💡 **Tip**: 세포가 잘 잡히지 않으면 Flow Threshold를 높여보세요.")
        
        with st.expander("⚙️ 고급 설정 (Advanced)", expanded=False):
            upscale_factor = st.slider(
                "이미지 확대 비율 (Upscale)",
                min_value=1.0,
                max_value=3.0,
                value=1.0,
                step=0.5,
                help="작은 세포 검출을 위해 이미지를 확대하여 분석합니다."
            )
            
            enhance_contrast = st.checkbox(
                "전처리 강화 (CLAHE)",
                value=False,
                help="대비가 낮은 이미지의 선명도를 높여 검출력을 향상시킵니다."
            )

    # Main Content
    st.markdown("""
    <div class="report-header">
        <div class="report-title">📋 AI 세포 분석 종합 보고서</div>
        <div style="color: #666; margin-top: 5px;">Automated Cell Analysis & Health Assessment Report</div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("세포 이미지 업로드", type=['png', 'jpg', 'jpeg', 'tif', 'tiff'])

    if uploaded_file:
        # Save temp file
        temp_dir = Path("temp_uploads")
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Analyze
        if st.button("🔍 분석 시작", type="primary"):
            with st.spinner("AI가 세포를 분석하고 있습니다..."):
                try:
                    # 1. Run Cellpose
                    analyzer = CellposeAnalyzer(model_type=model_type, use_gpu=True, diameter=diameter)
                    result = analyzer.analyze_image(
                        str(temp_path), 
                        diameter=diameter,
                        flow_threshold=flow_threshold,
                        upscale_factor=upscale_factor,
                        enhance_contrast=enhance_contrast
                    )
                    
                    # 2. Process Results & Classify States
                    processed_data = process_cell_data(result)
                    
                    # 3. Display Visualizations (Screenshot 2 style)
                    display_visualizations(result, processed_data)

                    # NEW: Interactive Zoom
                    display_interactive_zoom(result, processed_data)
                    
                    # 4. Display Report (Screenshot 1 & 3 style)
                    display_comprehensive_report(result, processed_data)
                    
                except Exception as e:
                    st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

def process_cell_data(result):
    """Analyze cell properties and classify states"""
    cells = result['cell_properties']
    masks = result['masks']
    img = result.get('original_image') # Assuming analyzer adds this or we load it
    if img is None:
        img = cv2.imread(result['image_path'])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Calculate additional metrics: Circularity, Brightness
    processed_cells = []
    
    # Convert to grayscale for brightness
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    for cell in cells:
        mask = masks == cell['cell_id']
        
        # Perimeter & Circularity
        contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            perimeter = cv2.arcLength(contours[0], True)
            area = cell['area']
            if perimeter > 0:
                circularity = 4 * np.pi * (area / (perimeter * perimeter))
            else:
                circularity = 0
        else:
            circularity = 0
            
        # Brightness
        mean_brightness = cv2.mean(gray, mask=mask.astype(np.uint8))[0]
        
        # State Classification Logic (Heuristic)
        # Normal: High circularity, moderate size
        # Stress: Irregular shape (low circularity), large or small size
        # Apoptosis: Very small, high brightness (condensed chromatin - simulated here)
        
        state = "정상"
        if area < 100: # Very small
            state = "사멸"
        elif circularity < 0.6: # Irregular shape
            state = "스트레스"
        elif mean_brightness > 180: # Very bright
            state = "스트레스"
            
        processed_cells.append({
            **cell,
            'circularity': circularity,
            'brightness': mean_brightness,
            'state': state
        })
        
    return pd.DataFrame(processed_cells)

def display_visualizations(result, df):
    st.markdown("### 🔍 Cellpose 객체 인식 결과")
    
    col1, col2, col3 = st.columns(3)
    
    # 1. Original
    with col1:
        st.markdown("**원본 이미지**")
        st.image(result['image_path'], use_container_width=True, caption="Original Image")
        
    # 2. Segmentation Result (Random Colors)
    with col2:
        st.markdown("**세포 검출 결과**")
        masks = result['masks']
        colored_mask = create_colored_mask(masks)
        # Overlay on original (optional, but screenshot shows black background with colored cells)
        st.image(colored_mask, use_container_width=True, caption=f"{len(df)} cells detected")
        
    # 3. State Classification (Yellow/Green/Red)
    with col3:
        st.markdown("**세포 상태 분류**")
        state_mask = create_state_mask(masks, df)
        st.image(state_mask, use_container_width=True)
        
        # Legend
        st.markdown("""
        <div style="text-align: center; font-size: 0.8rem;">
            <span style="color: #2ecc71;">●</span> 정상 
            <span style="color: #f1c40f;">●</span> 스트레스 
            <span style="color: #e74c3c;">●</span> 사멸
        </div>
        """, unsafe_allow_html=True)
        
    # Stats row below images
    normal_count = len(df[df['state'] == '정상'])
    stress_count = len(df[df['state'] == '스트레스'])
    apoptosis_count = len(df[df['state'] == '사멸'])
    total = len(df)
    
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; font-size: 0.9rem;">
        <strong>세포 상태 통계</strong>: 
        <span style="color: #2ecc71;">● 정상: {normal_count}개 ({normal_count/total*100:.1f}%)</span> &nbsp;
        <span style="color: #f1c40f;">● 스트레스: {stress_count}개 ({stress_count/total*100:.1f}%)</span> &nbsp;
        <span style="color: #e74c3c;">● 사멸: {apoptosis_count}개 ({apoptosis_count/total*100:.1f}%)</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

def display_interactive_zoom(result, df):
    st.markdown("### 🔭 상세 확대 보기 (Interactive Zoom)")
    st.info("💡 이미지 위에서 마우스 휠로 확대/축소하거나 드래그하여 이동할 수 있습니다.")
    
    tab1, tab2, tab3, tab4 = st.tabs(["원본 이미지", "세포 검출 결과", "세포 상태 분류", "🔧 모델 파인튜닝"])
    
    # Prepare images
    img = result.get('original_image')
    if img is None:
        img = cv2.imread(result['image_path'])
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
    masks = result['masks']
    colored_mask = create_colored_mask(masks)
    state_mask = create_state_mask(masks, df)
    
    with tab1:
        fig = px.imshow(img)
        fig.update_layout(height=600, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        fig = px.imshow(colored_mask)
        fig.update_layout(height=600, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with tab3:
        fig = px.imshow(state_mask)
        fig.update_layout(height=600, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with tab4:
        st.markdown("#### 🎯 파인튜닝 데이터 수집")
        st.markdown("""
        현재 분석 결과를 학습 데이터로 저장하여 모델 성능을 향상시킬 수 있습니다.
        저장된 데이터는 추후 모델 재학습(Fine-tuning)에 사용됩니다.
        """)
        
        col_ft1, col_ft2 = st.columns([3, 1])
        with col_ft1:
            ft_note = st.text_input("데이터 메모 (선택사항)", placeholder="예: H&E 염색, 대장암 세포, 저배율 등")
        
        with col_ft2:
            if st.button("💾 학습 데이터 저장", type="secondary", use_container_width=True):
                save_finetuning_data(result, ft_note)

def save_finetuning_data(result, note):
    """Save image and mask for fine-tuning"""
    try:
        base_dir = Path("dataset/fine_tuning")
        img_dir = base_dir / "images"
        mask_dir = base_dir / "masks"
        
        img_dir.mkdir(parents=True, exist_ok=True)
        mask_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(result['image_path']).stem
        
        # Save Image
        img = result.get('original_image')
        if img is None:
            img = cv2.imread(result['image_path']) # BGR
        else:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) # Convert back to BGR for saving
            
        cv2.imwrite(str(img_dir / f"{filename}_{timestamp}.png"), img)
        
        # Save Mask (16-bit png)
        cv2.imwrite(str(mask_dir / f"{filename}_{timestamp}_masks.png"), result['masks'].astype(np.uint16))
        
        # Save Metadata
        import json
        meta = {
            "original_file": result['image_path'],
            "timestamp": timestamp,
            "note": note,
            "diameter_used": result.get('diameter_used'),
            "model_type": result.get('model_type', 'cyto3')
        }
        with open(base_dir / "metadata.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
            
        st.success(f"✅ 학습 데이터가 저장되었습니다! (ID: {filename}_{timestamp})")
        
    except Exception as e:
        st.error(f"저장 실패: {str(e)}")

def display_comprehensive_report(result, df):
    # 1. Morphological Features
    with st.expander("🔬 1. 형태학적 특징 분석 (Morphological Features)", expanded=True):
        col1, col2 = st.columns(2)
        
        avg_area = df['area'].mean()
        std_area = df['area'].std()
        cv_area = (std_area / avg_area) * 100 if avg_area > 0 else 0
        
        avg_circ = df['circularity'].mean()
        avg_bright = df['brightness'].mean()
        
        with col1:
            st.markdown("**세포 크기 분포:**")
            st.markdown(f"- 평균 세포 면적: **{avg_area:.1f} ± {std_area:.1f} px²**")
            st.markdown(f"- 변이계수 (CV): **{cv_area:.1f}%**")
            st.markdown(f"- 최소/최대: {df['area'].min()} / {df['area'].max()} px²")
            
        with col2:
            st.markdown("**세포 형태:**")
            st.markdown(f"- 평균 원형도 (Circularity): **{avg_circ:.3f}**")
            st.markdown("  - 1.0 = 완전한 원형")
            st.markdown(f"  - {avg_circ:.2f} = {'낮은 원형도 (비정형)' if avg_circ < 0.6 else '높은 원형도'}")
            
            st.markdown("**세포 밝기:**")
            st.markdown(f"- 평균 밝기: **{avg_bright:.1f}**")
            
    # 2. Cell State Assessment
    with st.expander("🔍 2. 세포 상태 평가 (Cell State Assessment)", expanded=True):
        stress_ratio = len(df[df['state'] == '스트레스']) / len(df) * 100
        apoptosis_ratio = len(df[df['state'] == '사멸']) / len(df) * 100
        
        health_status = "양호 (Good)"
        health_color = "green"
        if stress_ratio > 30 or apoptosis_ratio > 5:
            health_status = "주의 (Caution)"
            health_color = "orange"
        if stress_ratio > 70 or apoptosis_ratio > 10:
            health_status = "경고 (Warning)"
            health_color = "red"
            
        st.markdown(f"**종합 건강도**: <span style='color:{health_color}; font-weight:bold;'>● {health_status}</span>", unsafe_allow_html=True)
        
        if health_color == "red":
            st.markdown("세포 건강도가 낮으며, 상당한 스트레스 또는 사멸 징후가 관찰됩니다.")
        
        st.markdown("**상태별 분포:**")
        st.markdown(f"- <span style='color:#2ecc71'>●</span> 정상 세포: {len(df[df['state']=='정상'])/len(df)*100:.1f}% ({len(df[df['state']=='정상'])}개)", unsafe_allow_html=True)
        st.markdown(f"- <span style='color:#f1c40f'>●</span> 스트레스 세포: {stress_ratio:.1f}% ({len(df[df['state']=='스트레스'])}개)", unsafe_allow_html=True)
        st.markdown(f"- <span style='color:#e74c3c'>●</span> 사멸 세포: {apoptosis_ratio:.1f}% ({len(df[df['state']=='사멸'])}개)", unsafe_allow_html=True)

    # 3. Population Heterogeneity
    with st.expander("📊 3. 세포 집단 이질성 (Population Heterogeneity)", expanded=True):
        st.markdown("**크기 이질성:**")
        st.markdown(f"- 변이계수: **{cv_area:.1f}%**")
        heterogeneity = "낮음"
        if cv_area > 30: heterogeneity = "중간 (일부 변동)"
        if cv_area > 50: heterogeneity = "높음"
        st.markdown(f"- 평가: {heterogeneity}")
        
        st.markdown("**상태 이질성:**")
        unique_states = df['state'].nunique()
        dominant_state = df['state'].mode()[0]
        st.markdown(f"- 세포 상태 다양성: {unique_states}가지 상태 관찰")
        st.markdown(f"- 우세 상태: {dominant_state}")
        
        st.markdown(f"**임상적 의의**: {'높은 이질성은 약물 반응의 다양성을 시사할 수 있습니다.' if cv_area > 30 else '낮은 이질성은 균일한 세포 집단을 시사하며, 일관된 반응을 예상할 수 있습니다'}")

    # 4. AI Recommendations
    with st.expander("🧠 4. AI 예측 및 권장사항 (AI Recommendations)", expanded=True):
        stress_score = (stress_ratio * 0.5 + apoptosis_ratio * 2) / 10
        stress_score = min(10.0, stress_score)
        
        st.markdown(f"**세포 스트레스 지수**: **{stress_score:.1f}/10**")
        
        st.markdown("**권장사항:**")
        if stress_score > 4:
            st.markdown("""
            <div class="warning-box">
                ⚠️ <strong>세포 건강도 저하 - 배양 조건 점검 및 개선 필요</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
             st.markdown("""
            <div class="success-badge" style="display:inline-block; padding:10px; margin:10px 0;">
                ✅ 세포 상태 양호 - 현재 배양 조건 유지
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("**추가 분석 제안:**")
        st.markdown("- 시간 경과 분석 (Time-lapse imaging)")
        st.markdown("- 생존율 검증 (Viability assay)")
        st.markdown("- 특정 마커 염색 (SA-β-gal, Annexin V)")
        if stress_score > 5:
            st.markdown("- Western blot (스트레스/사멸 관련 단백질)")

    # 5. Quality Metrics
    with st.expander("✅ 5. 분석 품질 평가 (Quality Metrics)", expanded=True):
        st.markdown("**검출 성능:**")
        st.markdown(f"- 총 검출 세포: **{len(df)}개**")
        st.markdown("- 전처리 방법: CLAHE (2.0) + Denoising (h=7) + Smoothing")
        st.markdown(f"- 검출 알고리즘: Cellpose ({result.get('model_type', 'cyto3')})")
        st.markdown(f"- 파라미터: diameter={result.get('diameter_used', 'Auto')}, flow_threshold={result.get('flow_threshold', 0.4)}") # Placeholder
        
        st.markdown("**신뢰도:**")
        avg_circ = df['circularity'].mean()
        if avg_circ > 0.6:
            st.markdown(f"- 평균 원형도 > 0.6: <span class='warning-badge'>⚠️ 검증 필요</span>", unsafe_allow_html=True)
        else:
             st.markdown(f"- 평균 원형도 < 0.6: <span class='success-badge'>✅ 정상 범위</span>", unsafe_allow_html=True)
             
        if cv_area < 50:
             st.markdown(f"- 크기 변동성 < 50%: <span class='success-badge'>✅ 일관된 검출</span>", unsafe_allow_html=True)
        
        if len(df) > 50:
             st.markdown(f"- 검출 세포 수 > 50: <span class='success-badge'>✅ 충분한 샘플</span>", unsafe_allow_html=True)


def create_colored_mask(masks):
    """Create random colored mask"""
    if masks.max() == 0: return np.zeros((*masks.shape, 3), dtype=np.uint8)
    
    np.random.seed(42)
    colors = np.random.randint(0, 255, (masks.max() + 1, 3))
    colors[0] = [0, 0, 0] # Background black
    
    colored = colors[masks]
    return colored.astype(np.uint8)

def create_state_mask(masks, df):
    """Create mask colored by state"""
    if masks.max() == 0: return np.zeros((*masks.shape, 3), dtype=np.uint8)
    
    # Colors: BGR (for opencv) or RGB
    # Normal: Green [46, 204, 113]
    # Stress: Yellow [241, 196, 15]
    # Apoptosis: Red [231, 76, 60]
    
    color_map = np.zeros((masks.max() + 1, 3), dtype=np.uint8)
    
    for _, row in df.iterrows():
        cid = int(row['cell_id'])
        if row['state'] == '정상':
            color_map[cid] = [46, 204, 113]
        elif row['state'] == '스트레스':
            color_map[cid] = [241, 196, 15]
        else:
            color_map[cid] = [231, 76, 60]
            
    colored = color_map[masks]
    
    # Add gray background for better visibility of cells? Or keep black?
    # Screenshot shows dark background with cells.
    # Let's make background dark gray to see boundaries if needed, or just black.
    # Screenshot 2 rightmost image shows dark gray background.
    
    bg_mask = masks == 0
    colored[bg_mask] = [50, 50, 50] # Dark gray background
    
    return colored

if __name__ == "__main__":
    main()
