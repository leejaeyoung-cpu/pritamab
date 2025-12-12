"""
KRAS 변이 및 분자지표 관리 모듈
환자의 KRAS 변이 상태 및 baseline 분자지표 관리
"""

from typing import Dict, Optional, List
from datetime import datetime
import json
from pathlib import Path


class MolecularMarkerManager:
    """분자지표 관리 클래스"""
    
    # KRAS 변이 타입 목록
    KRAS_MUTATIONS = [
        "Wild-type",
        "G12D", "G12V", "G12C", "G12A", "G12S", "G12R",
        "G13D", "G13C",
        "Q61H", "Q61L", "Q61R",
        "A146T", "A146V",
        "K117N"
    ]
    
    # 발현 수준
    EXPRESSION_LEVELS = ["Negative", "Low", "Medium", "High", "Very High"]
    
    # MSI 상태
    MSI_STATUS = ["MSI-H", "MSI-L", "MSS"]
    
    def __init__(self, data_dir: str = None):
        """초기화"""
        if data_dir is None:
            self.data_dir = Path.cwd() / "data" / "molecular_markers"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def create_kras_profile(
        self,
        status: str = "Unknown",
        mutation_type: Optional[str] = None,
        allele_frequency: Optional[float] = None,
        detection_method: str = "NGS"
    ) -> Dict:
        """
        KRAS 변이 프로파일 생성
        
        Args:
            status: Wild-type, Mutant, Unknown
            mutation_type: 구체적 변이 타입 (예: G12D)
            allele_frequency: 대립유전자 빈도 (%)
            detection_method: 검출 방법 (NGS, PCR, IHC 등)
        
        Returns:
            KRAS 프로파일 딕셔너리
        """
        profile = {
            "status": status,
            "mutation_type": mutation_type,
            "allele_frequency": allele_frequency,
            "detection_method": detection_method,
            "test_date": datetime.now().isoformat(),
            "clinical_significance": self._get_clinical_significance(status, mutation_type)
        }
        
        return profile
    
    def _get_clinical_significance(self, status: str, mutation_type: Optional[str]) -> str:
        """임상적 의의 설명"""
        if status == "Wild-type":
            return "Anti-EGFR 항체 치료 (Cetuximab, Panitumumab) 반응 가능"
        elif status == "Mutant":
            if mutation_type in ["G12D", "G12V"]:
                return "Anti-EGFR 항체 치료 저항성, 대체 치료 필요"
            elif mutation_type == "G12C":
                return "KRAS G12C 억제제 (Sotorasib, Adagrasib) 치료 대상"
            else:
                return "Anti-EGFR 항체 치료 저항성"
        else:
            return "검사 필요"
    
    def create_baseline_markers(
        self,
        prpc: str = "Unknown",
        lrp_lr: str = "Unknown",
        egfr: str = "Unknown",
        c_met: str = "Unknown",
        p_erk: float = 1.0,
        p_akt: float = 1.0,
        p_fak: float = 1.0,
        emt_score: float = 5.0,
        msi_status: str = "MSS",
        tmb: float = 0.0,
        pd_l1: float = 0.0
    ) -> Dict:
        """
        Baseline 분자지표 생성
        
        Returns:
            분자지표 딕셔너리
        """
        markers = {
            "PrPc": {
                "expression_level": prpc,
                "test_date": datetime.now().isoformat()
            },
            "LRP_LR": {
                "expression_level": lrp_lr
            },
            "EGFR": {
                "expression_level": egfr
            },
            "c_MET": {
                "expression_level": c_met
            },
            "signaling_pathways": {
                "p_ERK": {
                    "phosphorylation_ratio": p_erk,
                    "status": "Active" if p_erk > 1.5 else "Normal"
                },
                "p_AKT": {
                    "phosphorylation_ratio": p_akt,
                    "status": "Active" if p_akt > 1.5 else "Normal"
                },
                "p_FAK": {
                    "phosphorylation_ratio": p_fak,
                    "status": "Active" if p_fak > 1.5 else "Normal"
                }
            },
            "EMT": {
                "emt_score": emt_score,  # 0-10 scale
                "status": "High" if emt_score > 6 else ("Medium" if emt_score > 3 else "Low")
            },
            "genomic_markers": {
                "MSI_status": msi_status,
                "TMB": tmb,  # mutations/Mb
                "PD_L1": pd_l1  # % positive
            }
        }
        
        return markers
    
    def save_patient_markers(
        self,
        patient_id: str,
        kras_profile: Dict,
        baseline_markers: Dict
    ) -> str:
        """
        환자 분자지표 저장
        
        Returns:
            저장된 파일 경로
        """
        data = {
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat(),
            "kras_mutation": kras_profile,
            "molecular_markers": baseline_markers
        }
        
        file_path = self.data_dir / f"{patient_id}_markers.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return str(file_path)
    
    def load_patient_markers(self, patient_id: str) -> Optional[Dict]:
        """환자 분자지표 로드"""
        file_path = self.data_dir / f"{patient_id}_markers.json"
        
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_treatment_recommendation(self, kras_status: str, mutation_type: Optional[str]) -> List[str]:
        """KRAS 상태 기반 치료 권장사항"""
        if kras_status == "Wild-type":
            return [
                "Anti-EGFR 항체: Cetuximab 또는 Panitumumab",
                "FOLFOX 또는 FOLFIRI + Anti-EGFR",
                "Bevacizumab 병용 고려"
            ]
        elif kras_status == "Mutant":
            if mutation_type == "G12C":
                return [
                    "KRAS G12C 억제제: Sotorasib 또는 Adagrasib",
                    "표준 화학요법 + Bevacizumab",
                    "면역항암제 병용 고려 (MSI-H인 경우)"
                ]
            else:
                return [
                    "표준 화학요법: FOLFOX, FOLFIRI, FOLFOXIRI",
                    "Bevacizumab 또는 Ramucirumab 병용",
                    "Regorafenib (2차 이상)",
                    "Pritamab 병용요법 임상시험 고려 ⭐"
                ]
        else:
            return ["KRAS 변이 검사 먼저 시행 필요"]


# 사용 예제
if __name__ == "__main__":
    manager = MolecularMarkerManager()
    
    # KRAS 프로파일 생성
    kras = manager.create_kras_profile(
        status="Mutant",
        mutation_type="G12D",
        allele_frequency=45.2,
        detection_method="NGS"
    )
    
    print("KRAS 프로파일:")
    print(json.dumps(kras, indent=2, ensure_ascii=False))
    print()
    
    # Baseline 마커 생성
    markers = manager.create_baseline_markers(
        prpc="High",
        egfr="Medium",
        p_erk=2.3,
        emt_score=7.2,
        msi_status="MSS",
        tmb=5.2
    )
    
    print("Baseline 마커:")
    print(json.dumps(markers, indent=2, ensure_ascii=False))
    print()
    
    # 치료 권장사항
    recommendations = manager.get_treatment_recommendation("Mutant", "G12D")
    print("치료 권장사항:")
    for rec in recommendations:
        print(f"- {rec}")
