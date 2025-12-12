"""
통합 데이터셋 빌더
Cellpose 분석 + 이미지 저장 + AI 주석을 하나로 통합
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys

# src 경로 추가
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from inference_dataset_manager import InferenceDatasetManager
from file_storage_manager import FileStorageManager
from ai_analysis_annotator import AIAnalysisAnnotator
from report_generator import ReportGenerator


class IntegratedDatasetBuilder:
    """
    통합 데이터셋 빌더
    
    모든 데이터를 자동으로 저장하고 AI 주석을 생성하는 완전한 시스템
    """
    
    def __init__(self):
        """초기화"""
        self.dataset_manager = InferenceDatasetManager()
        self.file_manager = FileStorageManager()
        self.annotator = AIAnalysisAnnotator()
        self.report_generator = ReportGenerator(self.dataset_manager)
    
    def save_complete_analysis(
        self,
        patient_id: str,
        patient_info: Dict,
        uploaded_files: List = None,
        cellpose_results: List[Dict] = None,
        cellpose_stats: Dict = None,
        paper_recommendations: List[Dict] = None,
        ai_recommendations: List[Dict] = None
    ) -> Dict[str, str]:
        """
        완전한 분석 결과 저장
        
        Args:
            patient_id: 환자 ID
            patient_info: 환자 정보
            uploaded_files: 업로드된 이미지 파일
            cellpose_results: Cellpose 분석 결과
            cellpose_stats: Cellpose 통계
            paper_recommendations: 논문 기반 추천
            ai_recommendations: AI 기반 추천
        
        Returns:
            저장된 파일 경로 딕셔너리
        """
        timestamp = datetime.now()
        saved_paths = {}
        
        # 1. 이미지 파일 저장
        if uploaded_files and cellpose_results:
            print(f"[1/5] 이미지 파일 저장 중...")
            image_paths = self.file_manager.save_cellpose_images(
                patient_id=patient_id,
                uploaded_files=uploaded_files,
                cellpose_results=cellpose_results,
                timestamp=timestamp
            )
            saved_paths.update(image_paths)
            print(f"  ✓ 원본 이미지: {len(image_paths['original_images'])}개")
            print(f"  ✓ 마스크 이미지: {len(image_paths['mask_images'])}개")
        
        # 2. AI 분석 주석 생성 및 저장
        if cellpose_results and cellpose_stats:
            print(f"[2/5] AI 분석 주석 생성 중...")
            annotation_report = self.annotator.generate_annotation_report(
                cellpose_results=cellpose_results,
                cellpose_stats=cellpose_stats,
                patient_info=patient_info
            )
            
            annotation_path = self.file_manager.save_document(
                patient_id=patient_id,
                document_content=annotation_report,
                document_type="ai_annotation",
                filename=f"ai_annotation_{timestamp.strftime('%Y%m%d_%H%M%S')}.md",
                timestamp=timestamp
            )
            saved_paths['ai_annotation'] = annotation_path
            print(f"  ✓ AI 주석 저장: {annotation_path}")
        
        # 3. Cellpose 분석 데이터 구성
        if cellpose_results and cellpose_stats:
            # AI 주석도 포함
            ai_analysis = self.annotator.generate_cellpose_analysis(
                cellpose_results=cellpose_results,
                cellpose_stats=cellpose_stats,
                patient_info=patient_info
            )
            
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
                    "model_type": "cyto3",
                    "gpu_used": True
                },
                "ai_annotation": ai_analysis,  # AI 주석 추가
                "image_paths": saved_paths.get('original_images', []),
                "mask_paths": saved_paths.get('mask_images', [])
            }
        else:
            cellpose_analysis = None
        
        # 4. 추론 결과 데이터셋에 저장
        print(f"[3/5] 추론 결과 데이터셋에 저장 중...")
        inference_path = self.dataset_manager.save_inference_result(
            patient_id=patient_id,
            patient_info=patient_info,
            cellpose_analysis=cellpose_analysis,
            paper_recommendations=paper_recommendations or [],
            ai_recommendations=ai_recommendations or []
        )
        saved_paths['inference_data'] = inference_path
        print(f"  ✓ 추론 데이터: {inference_path}")
        
        # 5. 환자 보고서 생성
        print(f"[4/5] 환자 보고서 생성 중...")
        report_path = self.report_generator.save_patient_report(patient_id)
        saved_paths['patient_report'] = report_path
        print(f"  ✓ 환자 보고서: {report_path}")
        
        # 6. 통계 업데이트
        print(f"[5/5] 통계 업데이트 중...")
        stats = self.dataset_manager.get_summary_statistics()
        print(f"  ✓ 총 환자: {stats['total_patients']}명")
        print(f"  ✓ 총 추론: {stats['total_inferences']}건")
        
        return saved_paths
    
    def get_dataset_summary(self) -> Dict:
        """데이터셋 요약 정보"""
        dataset_stats = self.dataset_manager.get_summary_statistics()
        
        # 파일 통계 추가
        files_dir = Path.cwd() / "data" / "files"
        total_images = len(list(files_dir.glob("images/**/*.png"))) + len(list(files_dir.glob("images/**/*.jpg")))
        total_masks = len(list(files_dir.glob("masks/**/*.png")))
        total_docs = len(list(files_dir.glob("documents/**/*.md")))
        
        return {
            **dataset_stats,
            "file_stats": {
                "total_images": total_images,
                "total_masks": total_masks,
                "total_documents": total_docs
            }
        }


def save_cellpose_complete(
    patient_id: str,
    patient_info: Dict,
    uploaded_files: List,
    cellpose_results: List[Dict],
    cellpose_stats: Dict,
    paper_recommendations: List[Dict] = None,
    ai_recommendations: List[Dict] = None
) -> Dict[str, str]:
    """
    간편한 API: Cellpose 완전 저장
    
    한 번의 호출로 모든 것을 저장
    
    Returns:
        저장된 파일 경로 딕셔너리
    """
    builder = IntegratedDatasetBuilder()
    
    return builder.save_complete_analysis(
        patient_id=patient_id,
        patient_info=patient_info,
        uploaded_files=uploaded_files,
        cellpose_results=cellpose_results,
        cellpose_stats=cellpose_stats,
        paper_recommendations=paper_recommendations,
        ai_recommendations=ai_recommendations
    )


# 사용 예제
if __name__ == "__main__":
    print("=" * 80)
    print("통합 데이터셋 빌더 테스트")
    print("=" * 80)
    print()
    
    builder = IntegratedDatasetBuilder()
    
    # 데이터셋 요약
    summary = builder.get_dataset_summary()
    print("데이터셋 요약:")
    print(f"  총 환자: {summary['total_patients']}명")
    print(f"  총 추론: {summary['total_inferences']}건")
    print(f"  총 이미지: {summary['file_stats']['total_images']}개")
    print(f"  총 마스크: {summary['file_stats']['total_masks']}개")
    print(f"  총 문서: {summary['file_stats']['total_documents']}개")
