"""
AI 추론 결과 데이터셋 관리 모듈
병원의 핵심 자산인 AI 추론 데이터를 체계적으로 저장하고 관리
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd


class InferenceDatasetManager:
    """
    AI 추론 결과 데이터셋 관리 클래스
    
    기능:
    - AI 추론 결과 저장 (JSON 형식)
    - 결과 검색 및 조회
    - 치료 결과 업데이트
    - 통계 및 요약 생성
    - CSV/Excel 내보내기
    """
    
    def __init__(self, base_dir: str = None):
        """
        초기화
        
        Args:
            base_dir: 데이터 저장 기본 디렉토리 (기본값: ./data/inference_results)
        """
        if base_dir is None:
            base_dir = Path.cwd() / "data" / "inference_results"
        else:
            base_dir = Path(base_dir)
        
        self.base_dir = base_dir
        self.index_file = self.base_dir / "index.json"
        self.stats_file = self.base_dir / "summary_stats.json"
        
        # 디렉토리 생성
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # 인덱스 파일 초기화
        if not self.index_file.exists():
            self._save_index({})
    
    def _get_result_path(self, patient_id: str, timestamp: datetime) -> Path:
        """결과 파일 경로 생성"""
        year = timestamp.strftime("%Y")
        month = timestamp.strftime("%m")
        
        dir_path = self.base_dir / year / month
        dir_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"patient_{patient_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        return dir_path / filename
    
    def _load_index(self) -> Dict:
        """인덱스 파일 로드"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_index(self, index: Dict):
        """인덱스 파일 저장"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def save_inference_result(
        self,
        patient_id: str,
        patient_info: Dict,
        cellpose_analysis: Optional[Dict] = None,
        paper_recommendations: Optional[List[Dict]] = None,
        ai_recommendations: Optional[List[Dict]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        AI 추론 결과 저장
        
        Args:
            patient_id: 환자 ID
            patient_info: 환자 정보
            cellpose_analysis: Cellpose 분석 결과
            paper_recommendations: 논문 기반 추천
            ai_recommendations: AI 기반 추천
            metadata: 메타데이터
            
        Returns:
            저장된 파일 경로
        """
        timestamp = datetime.now()
        
        # 결과 데이터 구성
        result_data = {
            "metadata": {
                "patient_id": patient_id,
                "timestamp": timestamp.isoformat(),
                "system_version": metadata.get("system_version", "4.0") if metadata else "4.0",
                "analyst": metadata.get("analyst", "system") if metadata else "system"
            },
            "patient_info": patient_info,
            "cellpose_analysis": cellpose_analysis or {},
            "paper_recommendations": paper_recommendations or [],
            "ai_recommendations": ai_recommendations or [],
            "treatment_outcome": {
                "prescribed_drugs": None,
                "response": None,
                "side_effects": None,
                "survival_months": None,
                "last_updated": None
            }
        }
        
        # 파일 저장
        file_path = self._get_result_path(patient_id, timestamp)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        # 인덱스 업데이트
        index = self._load_index()
        if patient_id not in index:
            index[patient_id] = []
        
        index[patient_id].append({
            "timestamp": timestamp.isoformat(),
            "file_path": str(file_path.relative_to(self.base_dir)),
            "cancer_type": patient_info.get("cancer_type"),
            "cancer_stage": patient_info.get("cancer_stage")
        })
        
        self._save_index(index)
        
        # 통계 업데이트
        self._update_statistics()
        
        return str(file_path)
    
    def load_inference_result(self, patient_id: str, timestamp: str = None) -> Optional[Dict]:
        """
        AI 추론 결과 로드
        
        Args:
            patient_id: 환자 ID
            timestamp: 특정 시점 (None이면 최신)
            
        Returns:
            추론 결과 데이터
        """
        index = self._load_index()
        
        if patient_id not in index:
            return None
        
        records = index[patient_id]
        
        if timestamp:
            # 특정 시점 찾기
            for record in records:
                if record["timestamp"] == timestamp:
                    file_path = self.base_dir / record["file_path"]
                    break
            else:
                return None
        else:
            # 최신 결과
            record = records[-1]
            file_path = self.base_dir / record["file_path"]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_patient_history(self, patient_id: str) -> List[Dict]:
        """환자의 모든 추론 결과 이력"""
        index = self._load_index()
        
        if patient_id not in index:
            return []
        
        history = []
        for record in index[patient_id]:
            file_path = self.base_dir / record["file_path"]
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history.append(data)
        
        return history
    
    def search_by_cancer_type(self, cancer_type: str) -> List[Dict]:
        """암 종류별 검색"""
        index = self._load_index()
        results = []
        
        for patient_id, records in index.items():
            for record in records:
                if record.get("cancer_type") == cancer_type:
                    file_path = self.base_dir / record["file_path"]
                    with open(file_path, 'r', encoding='utf-8') as f:
                        results.append(json.load(f))
        
        return results
    
    def search_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """날짜 범위별 검색"""
        index = self._load_index()
        results = []
        
        for patient_id, records in index.items():
            for record in records:
                ts = record["timestamp"]
                if start_date <= ts <= end_date:
                    file_path = self.base_dir / record["file_path"]
                    with open(file_path, 'r', encoding='utf-8') as f:
                        results.append(json.load(f))
        
        return results
    
    def update_treatment_outcome(
        self,
        patient_id: str,
        prescribed_drugs: List[str],
        response: str = None,
        side_effects: List[str] = None,
        survival_months: float = None
    ) -> bool:
        """
        치료 결과 업데이트
        
        Args:
            patient_id: 환자 ID
            prescribed_drugs: 처방 약물
            response: 치료 반응 (완전관해, 부분관해, 안정, 진행)
            side_effects: 부작용
            survival_months: 생존 개월 수
        """
        # 최신 결과 로드
        result = self.load_inference_result(patient_id)
        
        if not result:
            return False
        
        # 치료 결과 업데이트
        result["treatment_outcome"] = {
            "prescribed_drugs": prescribed_drugs,
            "response": response,
            "side_effects": side_effects or [],
            "survival_months": survival_months,
            "last_updated": datetime.now().isoformat()
        }
        
        # 파일 저장
        index = self._load_index()
        latest_record = index[patient_id][-1]
        file_path = self.base_dir / latest_record["file_path"]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return True
    
    def _update_statistics(self):
        """요약 통계 업데이트"""
        index = self._load_index()
        
        stats = {
            "total_patients": len(index),
            "total_inferences": sum(len(records) for records in index.values()),
            "last_updated": datetime.now().isoformat(),
            "cancer_types": {},
            "cancer_stages": {}
        }
        
        # 암 종류 및 병기별 통계
        for patient_id, records in index.items():
            for record in records:
                cancer_type = record.get("cancer_type", "Unknown")
                cancer_stage = record.get("cancer_stage", "Unknown")
                
                stats["cancer_types"][cancer_type] = stats["cancer_types"].get(cancer_type, 0) + 1
                stats["cancer_stages"][cancer_stage] = stats["cancer_stages"].get(cancer_stage, 0) + 1
        
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    
    def get_summary_statistics(self) -> Dict:
        """요약 통계 조회"""
        if not self.stats_file.exists():
            self._update_statistics()
        
        with open(self.stats_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def export_to_dataframe(self, cancer_type: str = None) -> pd.DataFrame:
        """
        DataFrame으로 내보내기
        
        Args:
            cancer_type: 특정 암 종류만 (None이면 전체)
            
        Returns:
            pandas DataFrame
        """
        if cancer_type:
            results = self.search_by_cancer_type(cancer_type)
        else:
            index = self._load_index()
            results = []
            for patient_id, records in index.items():
                for record in records:
                    file_path = self.base_dir / record["file_path"]
                    with open(file_path, 'r', encoding='utf-8') as f:
                        results.append(json.load(f))
        
        # DataFrame 구성
        rows = []
        for result in results:
            row = {
                "patient_id": result["metadata"]["patient_id"],
                "timestamp": result["metadata"]["timestamp"],
                "age": result["patient_info"].get("age"),
                "gender": result["patient_info"].get("gender"),
                "cancer_type": result["patient_info"].get("cancer_type"),
                "cancer_stage": result["patient_info"].get("cancer_stage"),
                "ecog_score": result["patient_info"].get("ecog_score"),
            }
            
            # Cellpose 분석
            if result.get("cellpose_analysis"):
                ca = result["cellpose_analysis"]
                row["total_cells"] = ca.get("total_cells_detected")
                row["avg_cell_area"] = ca.get("avg_cell_area")
            
            # 추천 결과
            if result.get("paper_recommendations"):
                top_paper = result["paper_recommendations"][0]
                row["paper_top_drugs"] = " + ".join(top_paper["drugs"])
                row["paper_top_score"] = top_paper["overall_score"]
            
            if result.get("ai_recommendations"):
                top_ai = result["ai_recommendations"][0]
                row["ai_top_drugs"] = " + ".join(top_ai["drugs"])
                row["ai_top_score"] = top_ai["overall_score"]
            
            # 치료 결과
            if result.get("treatment_outcome"):
                to = result["treatment_outcome"]
                row["prescribed_drugs"] = " + ".join(to["prescribed_drugs"]) if to.get("prescribed_drugs") else None
                row["response"] = to.get("response")
                row["survival_months"] = to.get("survival_months")
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def export_to_csv(self, output_path: str, cancer_type: str = None):
        """CSV 파일로 내보내기"""
        df = self.export_to_dataframe(cancer_type)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    def export_to_excel(self, output_path: str, cancer_type: str = None):
        """Excel 파일로 내보내기"""
        df = self.export_to_dataframe(cancer_type)
        df.to_excel(output_path, index=False, engine='openpyxl')


# 사용 예제
if __name__ == "__main__":
    # 데이터셋 관리자 초기화
    manager = InferenceDatasetManager()
    
    # 테스트 데이터 저장
    patient_info = {
        "age": 65,
        "gender": "남성",
        "cancer_type": "대장암",
        "cancer_stage": "III",
        "ecog_score": 1,
        "diagnosis_date": "2024-10-15"
    }
    
    cellpose_analysis = {
        "total_cells_detected": 1523,
        "avg_cell_area": 245.3
    }
    
    file_path = manager.save_inference_result(
        patient_id="P001",
        patient_info=patient_info,
        cellpose_analysis=cellpose_analysis
    )
    
    print(f"저장 완료: {file_path}")
    
    # 통계 조회
    stats = manager.get_summary_statistics()
    print(f"통계: {stats}")
