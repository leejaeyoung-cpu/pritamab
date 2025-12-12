"""
Pritamab Response Score (PRS) 계산 모듈
KRAS 변이 전이성 대장암 환자의 Pritamab 반응 예측
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from datetime import datetime


class PRSCalculator:
    """
    Pritamab Response Score (PRS) 계산 클래스
    
    입력: 환자 정보, KRAS 변이, 분자지표, Cellpose 분석
    출력: PRS 점수 (0-100), 병용 조합 추천
    """
    
    def __init__(self):
        """초기화"""
        self.model_version = "v4.0_prototype"
        self.weights = self._initialize_weights()
    
    def _initialize_weights(self) -> Dict:
        """Feature 가중치 초기화"""
        return {
            # 분자지표 (35점)
            "kras_mutation": 15.0,
            "molecular_markers": 10.0,
            "genomic_profile": 10.0,
            
            # 세포 phenotype (35점)
            "cellpose_metrics": 15.0,
            "spheroid_characteristics": 10.0,
            "emt_status": 10.0,
            
            # 기능적 분석 (30점)
            "dose_response": 15.0,
            "pdo_viability": 10.0,
            "tgi_prediction": 5.0
        }
    
    def calculate_prs(
        self,
        patient_data: Dict,
        kras_profile: Dict,
        molecular_markers: Dict,
        cellpose_data: Optional[Dict] = None,
        functional_data: Optional[Dict] = None
    ) -> Dict:
        """
        PRS 점수 계산
        
        Args:
            patient_data: 환자 기본 정보
            kras_profile: KRAS 변이 프로파일
            molecular_markers: 분자지표
            cellpose_data: Cellpose 분석 데이터
            functional_data: 기능적 분석 데이터
        
        Returns:
            PRS 결과 딕셔너리
        """
        # 1. 분자지표 점수 (35점)
        molecular_score = self._calculate_molecular_score(
            kras_profile, molecular_markers
        )
        
        # 2. 세포 phenotype 점수 (35점)
        cellular_score = self._calculate_cellular_score(cellpose_data) if cellpose_data else 0
        
        # 3. 기능적 분석 점수 (30점)
        functional_score = self._calculate_functional_score(functional_data) if functional_data else 0
        
        # 총점 계산
        total_score = molecular_score + cellular_score + functional_score
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(
            cellpose_data is not None,
            functional_data is not None,
            len(molecular_markers.get("signaling_pathways", {}))
        )
        
        # 반응 카테고리 결정
        response_category = self._classify_response(total_score)
        
        # 결과 구성
        result = {
            "prs_score": round(total_score, 1),
            "confidence_interval": self._calculate_confidence_interval(total_score, confidence),
            "prediction_confidence":  round(confidence, 2),
            
            "score_breakdown": {
                "molecular_contribution": round(molecular_score, 1),
                "cellular_phenotype": round(cellular_score, 1),
                "functional_assay": round(functional_score, 1)
            },
            
            "interpretation": {
                "response_category": response_category,
                "expected_tgi": self._estimate_tgi(total_score),
                "expected_survival_benefit": self._estimate_survival(total_score, response_category),
                "toxicity_risk": self._assess_toxicity_risk(patient_data, molecular_markers)
            },
            
            "timestamp": datetime.now().isoformat(),
            "model_version": self.model_version
        }
        
        return result
    
    def _calculate_molecular_score(self, kras_profile: Dict, markers: Dict) -> float:
        """분자지표 점수 계산 (35점)"""
        score = 0.0
        
        # KRAS 변이 상태 (15점)
        kras_status = kras_profile.get("status", "Unknown")
        mutation_type = kras_profile.get("mutation_type")
        
        if kras_status == "Mutant":
            # Pritamab은 KRAS mutant에 효과적
            if mutation_type in ["G12D", "G12V"]:
                score += 15.0  # 높은 반응 예상
            elif mutation_type == "G12C":
                score += 10.0  # 중간 반응
            else:
                score += 12.0  # 기타 변이
        elif kras_status == "Wild-type":
            score += 8.0  # Pritamab보다 anti-EGFR 권장
        
        # 분자지표 (10점)
        prpc = markers.get("PrPc", {}).get("expression_level", "Unknown")
        if prpc == "High":
            score += 5.0  # PrPc high는 Pritamab 타겟
        elif prpc == "Medium":
            score += 3.0
        
        lrp_lr = markers.get("LRP_LR", {}).get("expression_level", "Unknown")
        if lrp_lr == "High":
            score += 3.0
        
        # 신호전달 경로 (10점)
        pathways = markers.get("signaling_pathways", {})
        p_erk = pathways.get("p_ERK", {}).get("phosphorylation_ratio", 1.0)
        p_akt = pathways.get("p_AKT", {}).get("phosphorylation_ratio", 1.0)
        
        # 높은 pathway activation은 치료 저항성
        if p_erk > 2.0 or p_akt > 2.0:
            score += 4.0  # 병용요법 필요
        else:
            score += 7.0  # 단독 또는 간단한 병용
        
        return min(score, 35.0)
    
    def _calculate_cellular_score(self, cellpose_data: Dict) -> float:
        """세포 phenotype 점수 (35점)"""
        if not cellpose_data:
            return 0.0
        
        score = 0.0
        
        # Cellpose 기본 분석 (15점)
        viability = cellpose_data.get("viability_rate", 0)
        if viability > 80:
            score += 12.0  # 높은 생존율 = 활발한 종양
        elif viability > 60:
            score += 8.0
        else:
            score += 5.0  # 낮은 생존율 = 약한 종양
        
        # 스페로이드 특성 (10점)
        spheroid = cellpose_data.get("spheroid_metrics", {})
        diameter = spheroid.get("diameter_um", 0)
        compactness = spheroid.get("compactness", 0)
        
        if diameter > 400 and compactness > 0.8:
            score += 10.0  # 큰, 조밀한 스페로이드 = 활동성 높음
        elif diameter > 300:
            score += 7.0
        else:
            score += 4.0
        
        # EMT 상태 (10점)
        emt = cellpose_data.get("emt_reversal", {})
        reversal_degree = emt.get("reversal_degree", 0)
        
        if reversal_degree > 40:
            score += 10.0  # 높은 EMT reversal = 좋은 반응
        elif reversal_degree > 20:
            score += 6.0
        else:
            score += 3.0
        
        return min(score, 35.0)
    
    def _calculate_functional_score(self, functional_data: Dict) -> float:
        """기능적 분석 점수 (30점)"""
        if not functional_data:
            return 0.0
        
        score = 0.0
        
        # 용량-반응 (15점)
        dose_response = functional_data.get("dose_response", {})
        synergy = dose_response.get("synergy_score", 1.0)
        
        if synergy > 1.3:
            score += 15.0  # 높은 시너지
        elif synergy > 1.1:
            score += 10.0
        else:
            score += 5.0
        
        # PDO viability (10점)
        pdo = functional_data.get("organoid_analysis", {})
        pdo_response = pdo.get("drug_response", {})
        ic50 = pdo_response.get("pritamab_ic50", 100)
        
        if ic50 < 30:
            score += 10.0  # 낮은 IC50 = 높은 감수성
        elif ic50 < 50:
            score += 7.0
        else:
            score += 4.0
        
        # TGI 예측 (5점)
        animal = functional_data.get("animal_model", {})
        tgi = animal.get("treatment_response", {}).get("tumor_growth_inhibition", 0)
        
        if tgi > 60:
            score += 5.0
        elif tgi > 40:
            score += 3.0
        else:
            score += 1.0
        
        return min(score, 30.0)
    
    def _calculate_confidence(self, has_cellpose: bool, has_functional: bool, marker_count: int) -> float:
        """예측 신뢰도 계산"""
        confidence = 0.5  # 기본
        
        if has_cellpose:
            confidence += 0.2
        if has_functional:
            confidence += 0.2
        if marker_count >= 5:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _calculate_confidence_interval(self, score: float, confidence: float) -> List[float]:
        """신뢰구간 계산"""
        margin = (1 - confidence) * 10  # 신뢰도에 따라 margin 조정
        lower = max(0, score - margin)
        upper = min(100, score + margin)
        return [round(lower, 1), round(upper, 1)]
    
    def _classify_response(self, score: float) -> str:
        """반응 카테고리 분류"""
        if score >= 75:
            return "Excellent Responder"
        elif score >= 60:
            return "Good Responder"
        elif score >= 40:
            return "Fair Responder"
        else:
            return "Poor Responder"
    
    def _estimate_tgi(self, score: float) -> str:
        """TGI 예상 범위"""
        if score >= 75:
            return "70-85%"
        elif score >= 60:
            return "55-70%"
        elif score >= 40:
            return "35-55%"
        else:
            return "15-35%"
    
    def _estimate_survival(self, score: float, category: str) -> str:
        """생존 이득 예상"""
        if category == "Excellent Responder":
            return "12-18 months"
        elif category == "Good Responder":
            return "8-12 months"
        elif category == "Fair Responder":
            return "4-8 months"
        else:
            return "2-4 months"
    
    def _assess_toxicity_risk(self, patient_data: Dict, markers: Dict) -> str:
        """독성 위험 평가"""
        age = patient_data.get("age", 65)
        ecog = patient_data.get("ecog_score", 1)
        
        # 기본 위험도
        if age > 75 or ecog >= 2:
            risk = "Moderate-High"
        elif age > 65 or ecog == 1:
            risk = "Low-Moderate"
        else:
            risk = "Low"
        
        return risk


# 사용 예제
if __name__ == "__main__":
    calculator = PRSCalculator()
    
    # 테스트 데이터
    patient_data = {
        "age": 65,
        "ecog_score": 1
    }
    
    kras_profile = {
        "status": "Mutant",
        "mutation_type": "G12D"
    }
    
    molecular_markers = {
        "PrPc": {"expression_level": "High"},
        "LRP_LR": {"expression_level": "High"},
        "signaling_pathways": {
            "p_ERK": {"phosphorylation_ratio": 2.3},
            "p_AKT": {"phosphorylation_ratio": 1.8}
        }
    }
    
    cellpose_data = {
        "viability_rate": 88.1,
        "spheroid_metrics": {
            "diameter_um": 450.5,
            "compactness": 0.85
        },
        "emt_reversal": {
            "reversal_degree": 43.1
        }
    }
    
    # PRS 계산
    result = calculator.calculate_prs(
        patient_data=patient_data,
        kras_profile=kras_profile,
        molecular_markers=molecular_markers,
        cellpose_data=cellpose_data
    )
    
    print("Pritamab Response Score (PRS) 결과:")
    print("=" * 60)
    print(f"PRS 점수: {result['prs_score']}/100")
    print(f"신뢰구간: {result['confidence_interval']}")
    print(f"예측 신뢰도: {result['prediction_confidence']}")
    print()
    print("점수 구성:")
    print(f"  - 분자지표: {result['score_breakdown']['molecular_contribution']}/35")
    print(f"  - 세포 특성: {result['score_breakdown']['cellular_phenotype']}/35")
    print(f"  - 기능 분석: {result['score_breakdown']['functional_assay']}/30")
    print()
    print("해석:")
    print(f"  - 반응 카테고리: {result['interpretation']['response_category']}")
    print(f"  - 예상 TGI: {result['interpretation']['expected_tgi']}")
    print(f"  - 예상 생존 이득: {result['interpretation']['expected_survival_benefit']}")
    print(f"  - 독성 위험: {result['interpretation']['toxicity_risk']}")
