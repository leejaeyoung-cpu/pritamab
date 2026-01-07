# -*- coding: utf-8 -*-
"""
Cellpose Integration Module for ADDS
Safe implementation without file encoding issues
"""

import streamlit as st
import subprocess
import time
from pathlib import Path
import psutil


def check_port_in_use(port):
    """Check if a port is in use"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return True
    return False


def render_cellpose_page():
    """Render the Cellpose analysis page"""
    
    st.markdown("""
    <div class='hospital-header'>
        <div class='hospital-title'>🔬 Advanced Cell Image Analysis</div>
        <div style='text-align: center; margin-top: 0.5rem; font-size: 1.1rem;'>
            Cellpose-based Cell Analysis System
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Session state
    if 'cellpose_port_status' not in st.session_state:
        st.session_state.cellpose_port_status = check_port_in_use(8502)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🚀 Cellpose Analysis System
        
        **Features:**
        - 🎯 **Advanced Segmentation**: Cellpose AI-powered cell detection
        - 🔬 **Morphology Analysis**: Automated feature extraction
        - 🧠 **AI Prediction**: Drug response and viability prediction
        - 📊 **Real-time Visualization**: Cell segmentation and statistics
        
        **Current Status:**
        """)
        
        if st.session_state.cellpose_port_status:
            st.success("✅ Cellpose server is running on port 8502")
        else:
            st.info("ℹ️ Cellpose server is not running")
    
    with col2:
        st.markdown("### 🎮 Server Control")
        
        if st.session_state.cellpose_port_status:
            st.success("🟢 Active")
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
                🔗 Open Cellpose
            </a>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚪ Not Running")
    
    st.markdown("---")
    
    # Instructions
    if st.session_state.cellpose_port_status:
        st.markdown("""
        ### 📡 Access Information
        
        The Cellpose analysis system is running. Click the button above or visit:
        - **Local**: http://localhost:8502
        
        ### 📖 Quick Guide
        1. Upload cell microscopy images (.tif, .png, .jpg)
        2. Select segmentation method
        3. Adjust cell diameter if needed
        4. View results in multiple tabs
        """)
        
        with st.expander("⚡ Performance Info"):
            st.markdown("""
            #### Analysis Speed
            - Single Image: ~1-5 seconds
            - Batch (10 images): ~10-50 seconds
            
            #### Accuracy
            - Cell Detection: 85-95%
            - Segmentation Quality: High
            
            #### Requirements
            - GPU: NVIDIA CUDA-capable (recommended)
            - CPU: Also supported (slower)
            """)
    
    else:
        st.markdown("""
        ### 🚀 How to Start Cellpose Server
        
        The Cellpose analysis system runs on a separate port (8502). 
        To use it, please run the startup script:
        
        ```bash
        # Option 1: Run integrated launcher
        ADDS_전체실행.bat
        
        # Option 2: Run Cellpose separately
        cd web_app
        streamlit run app.py --server.port 8502
        ```
        
        Or start it manually from the command line.
        """)
        
        if st.button("🔄 Refresh Status"):
            st.session_state.cellpose_port_status = check_port_in_use(8502)
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🎯 Key Features Preview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🔬 Cell Segmentation**
            - Cellpose AI model
            - Auto cell detection
            - Precise boundaries
            """)
        
        with col2:
            st.markdown("""
            **📊 Feature Analysis**  
            - Cell count & size
            - Morphology metrics
            - Density calculation
            """)
        
        with col3:
            st.markdown("""
            **🧠 AI Prediction**
            - Drug response
            - Cell viability
            - Apoptosis detection
            """)
