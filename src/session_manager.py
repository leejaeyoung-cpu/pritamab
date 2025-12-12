"""
세션 상태 관리 모듈
Streamlit 세션 상태를 중앙에서 관리
"""

import streamlit as st
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class SessionManager:
    """Streamlit 세션 상태 관리 클래스"""
    
    # 세션 키 상수
    UPLOADED_IMAGES = "uploaded_images"
    UPLOADED_EXCEL = "uploaded_excel"
    ANALYSIS_RESULTS = "analysis_results"
    CELLPOSE_CONFIG = "cellpose_config"
    PROCESSING_STATUS = "processing_status"
    WORKFLOW_STATE = "workflow_state"
    CACHED_DATA = "cached_data"
    PATIENTS = "patients"  # 환자 정보
    CURRENT_PATIENT = "current_patient"  # 현재 선택된 환자
    RECOMMENDATIONS = "recommendations"  # 추천 결과
    
    @staticmethod
    def init_session_state():
        """세션 상태 초기화"""
        if SessionManager.UPLOADED_IMAGES not in st.session_state:
            st.session_state[SessionManager.UPLOADED_IMAGES] = []
        
        if SessionManager.UPLOADED_EXCEL not in st.session_state:
            st.session_state[SessionManager.UPLOADED_EXCEL] = []
        
        if SessionManager.ANALYSIS_RESULTS not in st.session_state:
            st.session_state[SessionManager.ANALYSIS_RESULTS] = {}
        
        if SessionManager.CELLPOSE_CONFIG not in st.session_state:
            st.session_state[SessionManager.CELLPOSE_CONFIG] = {
                'diameter': 30,
                'channels': [0, 0],
                'flow_threshold': 0.4,
                'cellprob_threshold': 0.0,
                'model_type': 'cyto2'
            }
        
        if SessionManager.PROCESSING_STATUS not in st.session_state:
            st.session_state[SessionManager.PROCESSING_STATUS] = {
                'is_processing': False,
                'current_file': None,
                'progress': 0.0,
                'total_files': 0
            }
        
        if SessionManager.WORKFLOW_STATE not in st.session_state:
            st.session_state[SessionManager.WORKFLOW_STATE] = {
                'data_uploaded': False,
                'images_analyzed': False,
                'predictions_made': False,
                'optimization_done': False
            }
        
        if SessionManager.CACHED_DATA not in st.session_state:
            st.session_state[SessionManager.CACHED_DATA] = {}
        
        if SessionManager.PATIENTS not in st.session_state:
            st.session_state[SessionManager.PATIENTS] = {}
        
        if SessionManager.CURRENT_PATIENT not in st.session_state:
            st.session_state[SessionManager.CURRENT_PATIENT] = None
        
        if SessionManager.RECOMMENDATIONS not in st.session_state:
            st.session_state[SessionManager.RECOMMENDATIONS] = {
                'paper_based': [],
                'ai_based': []
            }
    
    @staticmethod
    def add_uploaded_file(file_type: str, file_info: Dict[str, Any]):
        """
        업로드된 파일 정보 추가
        
        Args:
            file_type: 'image' 또는 'excel'
            file_info: 파일 정보 딕셔너리
                - name: 파일명
                - size: 파일 크기 (bytes)
                - path: 저장 경로
                - upload_time: 업로드 시간
        """
        if file_type == 'image':
            key = SessionManager.UPLOADED_IMAGES
        elif file_type == 'excel':
            key = SessionManager.UPLOADED_EXCEL
        else:
            raise ValueError(f"Unknown file type: {file_type}")
        
        if key not in st.session_state:
            st.session_state[key] = []
        
        # 중복 방지
        existing_names = [f['name'] for f in st.session_state[key]]
        if file_info['name'] not in existing_names:
            file_info['upload_time'] = datetime.now().isoformat()
            st.session_state[key].append(file_info)
    
    @staticmethod
    def get_uploaded_files(file_type: str) -> List[Dict[str, Any]]:
        """
        업로드된 파일 목록 조회
        
        Args:
            file_type: 'image' 또는 'excel'
            
        Returns:
            파일 정보 리스트
        """
        if file_type == 'image':
            key = SessionManager.UPLOADED_IMAGES
        elif file_type == 'excel':
            key = SessionManager.UPLOADED_EXCEL
        else:
            return []
        
        return st.session_state.get(key, [])
    
    @staticmethod
    def remove_uploaded_file(file_type: str, filename: str):
        """
        업로드된 파일 제거
        
        Args:
            file_type: 'image' 또는 'excel'
            filename: 제거할 파일명
        """
        if file_type == 'image':
            key = SessionManager.UPLOADED_IMAGES
        elif file_type == 'excel':
            key = SessionManager.UPLOADED_EXCEL
        else:
            return
        
        if key in st.session_state:
            st.session_state[key] = [
                f for f in st.session_state[key] 
                if f['name'] != filename
            ]
    
    @staticmethod
    def cache_analysis_result(image_id: str, result: Dict[str, Any]):
        """
        분석 결과 캐싱
        
        Args:
            image_id: 이미지 식별자 (파일명)
            result: 분석 결과 딕셔너리
        """
        st.session_state[SessionManager.ANALYSIS_RESULTS][image_id] = result
    
    @staticmethod
    def get_analysis_result(image_id: str) -> Optional[Dict[str, Any]]:
        """
        캐싱된 분석 결과 조회
        
        Args:
            image_id: 이미지 식별자
            
        Returns:
            분석 결과 딕셔너리 또는 None
        """
        return st.session_state[SessionManager.ANALYSIS_RESULTS].get(image_id)
    
    @staticmethod
    def get_all_analysis_results() -> Dict[str, Dict[str, Any]]:
        """모든 분석 결과 조회"""
        return st.session_state[SessionManager.ANALYSIS_RESULTS]
    
    @staticmethod
    def update_cellpose_config(config: Dict[str, Any]):
        """
        Cellpose 설정 업데이트
        
        Args:
            config: 설정 딕셔너리
        """
        st.session_state[SessionManager.CELLPOSE_CONFIG].update(config)
    
    @staticmethod
    def get_cellpose_config() -> Dict[str, Any]:
        """Cellpose 설정 조회"""
        return st.session_state[SessionManager.CELLPOSE_CONFIG]
    
    @staticmethod
    def update_processing_status(
        is_processing: bool = None,
        current_file: str = None,
        progress: float = None,
        total_files: int = None
    ):
        """
        처리 상태 업데이트
        
        Args:
            is_processing: 처리 중 여부
            current_file: 현재 처리 중인 파일
            progress: 진행률 (0.0 ~ 1.0)
            total_files: 전체 파일 수
        """
        status = st.session_state[SessionManager.PROCESSING_STATUS]
        
        if is_processing is not None:
            status['is_processing'] = is_processing
        if current_file is not None:
            status['current_file'] = current_file
        if progress is not None:
            status['progress'] = progress
        if total_files is not None:
            status['total_files'] = total_files
    
    @staticmethod
    def get_processing_status() -> Dict[str, Any]:
        """처리 상태 조회"""
        return st.session_state[SessionManager.PROCESSING_STATUS]
    
    @staticmethod
    def update_workflow_state(step: str, completed: bool):
        """
        워크플로우 단계 업데이트
        
        Args:
            step: 'data_uploaded', 'images_analyzed', 'predictions_made', 'optimization_done'
            completed: 완료 여부
        """
        if step in st.session_state[SessionManager.WORKFLOW_STATE]:
            st.session_state[SessionManager.WORKFLOW_STATE][step] = completed
    
    @staticmethod
    def get_workflow_state() -> Dict[str, bool]:
        """워크플로우 상태 조회"""
        return st.session_state[SessionManager.WORKFLOW_STATE]
    
    @staticmethod
    def cache_data(key: str, data: Any):
        """
        임의 데이터 캐싱
        
        Args:
            key: 캐시 키
            data: 저장할 데이터
        """
        st.session_state[SessionManager.CACHED_DATA][key] = data
    
    @staticmethod
    def get_cached_data(key: str, default: Any = None) -> Any:
        """
        캐싱된 데이터 조회
        
        Args:
            key: 캐시 키
            default: 기본값
            
        Returns:
            캐싱된 데이터 또는 기본값
        """
        return st.session_state[SessionManager.CACHED_DATA].get(key, default)
    
    @staticmethod
    def clear_session():
        """세션 상태 초기화"""
        keys_to_clear = [
            SessionManager.UPLOADED_IMAGES,
            SessionManager.UPLOADED_EXCEL,
            SessionManager.ANALYSIS_RESULTS,
            SessionManager.PROCESSING_STATUS,
            SessionManager.WORKFLOW_STATE,
            SessionManager.CACHED_DATA,
            SessionManager.PATIENTS,
            SessionManager.CURRENT_PATIENT,
            SessionManager.RECOMMENDATIONS
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                if isinstance(st.session_state[key], dict):
                    st.session_state[key] = {}
                elif isinstance(st.session_state[key], list):
                    st.session_state[key] = []
    
    @staticmethod
    def clear_analysis_results():
        """분석 결과만 초기화"""
        st.session_state[SessionManager.ANALYSIS_RESULTS] = {}
    
    @staticmethod
    def export_session_state(filepath: Path):
        """
        세션 상태를 JSON 파일로 내보내기
        
        Args:
            filepath: 저장 경로
        """
        state_data = {
            'uploaded_images': st.session_state.get(SessionManager.UPLOADED_IMAGES, []),
            'uploaded_excel': st.session_state.get(SessionManager.UPLOADED_EXCEL, []),
            'cellpose_config': st.session_state.get(SessionManager.CELLPOSE_CONFIG, {}),
            'workflow_state': st.session_state.get(SessionManager.WORKFLOW_STATE, {}),
            'export_time': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def import_session_state(filepath: Path):
        """
        JSON 파일에서 세션 상태 가져오기
        
        Args:
            filepath: 파일 경로
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        if 'uploaded_images' in state_data:
            st.session_state[SessionManager.UPLOADED_IMAGES] = state_data['uploaded_images']
        if 'uploaded_excel' in state_data:
            st.session_state[SessionManager.UPLOADED_EXCEL] = state_data['uploaded_excel']
        if 'cellpose_config' in state_data:
            st.session_state[SessionManager.CELLPOSE_CONFIG] = state_data['cellpose_config']
        if 'workflow_state' in state_data:
            st.session_state[SessionManager.WORKFLOW_STATE] = state_data['workflow_state']
    
    @staticmethod
    def add_patient(patient_id: str, patient_data: Dict[str, Any]):
        """환자 추가"""
        st.session_state[SessionManager.PATIENTS][patient_id] = patient_data
    
    @staticmethod
    def get_patient(patient_id: str) -> Optional[Dict[str, Any]]:
        """환자 조회"""
        return st.session_state[SessionManager.PATIENTS].get(patient_id)
    
    @staticmethod
    def get_all_patients() -> Dict[str, Dict[str, Any]]:
        """모든 환자 조회"""
        return st.session_state[SessionManager.PATIENTS]
    
    @staticmethod
    def set_current_patient(patient_id: Optional[str]):
        """현재 환자 설정"""
        st.session_state[SessionManager.CURRENT_PATIENT] = patient_id
    
    @staticmethod
    def get_current_patient() -> Optional[str]:
        """현재 환자 ID 조회"""
        return st.session_state[SessionManager.CURRENT_PATIENT]
    
    @staticmethod
    def save_recommendations(rec_type: str, recommendations: List[Any]):
        """추천 결과 저장 (rec_type: 'paper_based' 또는 'ai_based')"""
        st.session_state[SessionManager.RECOMMENDATIONS][rec_type] = recommendations
    
    @staticmethod
    def get_recommendations(rec_type: str) -> List[Any]:
        """추천 결과 조회"""
        return st.session_state[SessionManager.RECOMMENDATIONS].get(rec_type, [])
