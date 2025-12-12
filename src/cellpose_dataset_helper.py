"""
Cellpose 분석 결과 자동 저장 헬퍼 함수
AI_Anticancer_Drug_System.py에서 사용
"""

from datetime import datetime
from pathlib import Path
import sys

# src 경로 추가
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from inference_dataset_manager import InferenceDatasetManager
from report_generator import ReportGenerator


def save_cellpose_inference(
    patient_id: str,
    patient_info: dict,
    cellpose_results: list,
    cellpose_stats: dict,
    paper_recommendations: list = None,
    ai_recommendations: list = None
) -> str:
    """
    Cellpose 분석 결과를 데이터셋에 저장
    
    Args:
        patient_id: 환자 ID
        patient_info: 환자 정보
        cellpose_results: Cellpose 분석 결과 리스트
        cellpose_stats: Cellpose 통계
        paper_recommendations: 논문 기반 추천 (선택)
        ai_recommendations: AI 기반 추천 (선택)
    
    Returns:
        저장된 파일 경로
    """
    manager = InferenceDatasetManager()
    
    # Cellpose 분석 데이터 구성
    cellpose_analysis = {
        "images_analyzed": cellpose_stats.get('total_images', 0),
        "total_cells_detected": cellpose_stats.get('total_cells', 0),
        "avg_cells_per_image": cellpose_stats.get('avg_cells_per_image', 0),
        "avg_cell_area": cellpose_stats.get('avg_cell_area', 0),
        "cell_size_distribution": {
            "min": cellpose_stats.get('min_cell_area', 0),
            "max": cellpose_stats.get('max_cell_area', 0),
            "median": cellpose_stats.get('median_cell_area', 0),
            "std": cellpose_stats.get('std_cell_area', 0)
        },
        "analysis_params": {
            "model_type": "cyto3",  # 기본값, 실제 사용된 값으로 업데이트 가능
            "gpu_used": True  # GPU 사용 여부
        }
    }
    
    # 추론 결과 저장
    file_path = manager.save_inference_result(
        patient_id=patient_id,
        patient_info=patient_info,
        cellpose_analysis=cellpose_analysis,
        paper_recommendations=paper_recommendations or [],
        ai_recommendations=ai_recommendations or []
    )
    
    return file_path


def generate_and_save_report(patient_id: str) -> str:
    """
    환자 보고서 생성 및 저장
    
    Args:
        patient_id: 환자 ID
    
    Returns:
        보고서 파일 경로
    """
    manager = InferenceDatasetManager()
    generator = ReportGenerator(manager)
    
    report_path = generator.save_patient_report(patient_id)
    
    return report_path


def get_dataset_stats() -> dict:
    """
    데이터셋 통계 조회
    
    Returns:
        통계 딕셔너리
    """
    manager = InferenceDatasetManager()
    return manager.get_summary_statistics()


# 사용 예제
if __name__ == "__main__":
    # 테스트
    patient_info = {
        "age": 65,
        "gender": "남성",
        "cancer_type": "대장암",
        "cancer_stage": "III",
        "ecog_score": 1,
        "diagnosis_date": "2024-10-15"
    }
    
    cellpose_stats = {
        "total_images": 3,
        "total_cells": 1523,
        "avg_cells_per_image": 507.67,
        "avg_cell_area": 245.3,
        "min_cell_area": 50,
        "max_cell_area": 850,
        "median_cell_area": 230,
        "std_cell_area": 125.4
    }
    
    # 저장
    file_path = save_cellpose_inference(
        patient_id="P001",
        patient_info=patient_info,
        cellpose_results=[],
        cellpose_stats=cellpose_stats
    )
    
    print(f"저장 완료: {file_path}")
    
    # 보고서 생성
    report_path = generate_and_save_report("P001")
    print(f"보고서 생성: {report_path}")
    
    # 통계 조회
    stats = get_dataset_stats()
    print(f"데이터셋 통계: {stats}")
