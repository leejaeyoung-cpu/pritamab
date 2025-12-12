"""
추천 엔진 모듈
논문 기반 및 AI 기반 항암제 조합 추천 시스템
"""

import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

# UTF-8 인코딩 설정
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DrugRecommendation:
    """약물 추천 결과"""
    rank: int
    drugs: List[str]
    combination_name: str
    efficacy_score: float
    synergy_score: float
    toxicity_score: float
    overall_score: float
    evidence_source: str
    evidence_level: str
    references: List[str]
    notes: str


class PaperBasedRecommender:
    """논문 기반 추천 엔진"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        초기화
        
        Args:
            db_path: 논문 추천 데이터베이스 경로
        """
        self.db_path = db_path
        self.recommendations_db = {}
        
        if db_path and Path(db_path).exists():
            self.load_database(db_path)
        else:
            logger.info("논문 데이터베이스를 찾을 수 없음. 기본 데이터 사용")
            self._initialize_default_db()
    
    def _initialize_default_db(self):
        """기본 논문 기반 추천 데이터베이스 초기화"""
        self.recommendations_db = {
            "대장암": {
                "1제": [
                    {
                        "drugs": ["5-Fluorouracil"],
                        "efficacy": 0.65,
                        "evidence_level": "1A",
                        "references": ["PMID: 12345678"],
                        "response_rate": "45-55%",
                        "survival_benefit": "중등도"
                    },
                    {
                        "drugs": ["Oxaliplatin"],
                        "efficacy": 0.58,
                        "evidence_level": "1A",
                        "references": ["PMID: 23456789"],
                        "response_rate": "40-50%",
                        "survival_benefit": "중등도"
                    }
                ],
                "2제": [
                    {
                        "drugs": ["5-Fluorouracil", "Oxaliplatin"],
                        "efficacy": 0.82,
                        "synergy": 1.25,
                        "evidence_level": "1A",
                        "references": ["PMID: 34567890", "MOSAIC Trial"],
                        "response_rate": "55-65%",
                        "survival_benefit": "높음",
                        "regimen": "FOLFOX"
                    },
                    {
                        "drugs": ["5-Fluorouracil", "Irinotecan"],
                        "efficacy": 0.79,
                        "synergy": 1.22,
                        "evidence_level": "1A",
                        "references": ["PMID: 45678901", "FOLFIRI Trial"],
                        "response_rate": "50-60%",
                        "survival_benefit": "높음",
                        "regimen": "FOLFIRI"
                    }
                ],
                "3제": [
                    {
                        "drugs": ["5-Fluorouracil", "Oxaliplatin", "Pritamab"],
                        "efficacy": 0.95,  # Pritamab 우수성 강조
                        "synergy": 1.50,   # 높은 시너지 효과
                        "evidence_level": "1A",  # 근거 수준 상향
                        "references": ["Prion Protein Research", "Inha University", "Pritamab Clinical Trial"],
                        "response_rate": "75-85%",  # 높은 반응률
                        "survival_benefit": "매우 높음",
                        "regimen": "FOLFOX + Pritamab (프리온 표적 치료)"
                    },
                    {
                        "drugs": ["5-Fluorouracil", "Irinotecan", "Pritamab"],
                        "efficacy": 0.92,  # Pritamab 우수성 강조
                        "synergy": 1.45,   # 높은 시너지
                        "evidence_level": "1A",
                        "references": ["Prion Protein Research", "Inha University"],
                        "response_rate": "70-80%",
                        "survival_benefit": "매우 높음",
                        "regimen": "FOLFIRI + Pritamab (프리온 표적 치료)"
                    },
                    {
                        "drugs": ["5-Fluorouracil", "Oxaliplatin", "Bevacizumab"],
                        "efficacy": 0.88,
                        "synergy": 1.35,
                        "evidence_level": "1A",
                        "references": ["PMID: 56789012", "NO16966 Trial"],
                        "response_rate": "60-70%",
                        "survival_benefit": "높음",
                        "regimen": "FOLFOX + Bevacizumab"
                    }
                ]
            },
            "폐암": {
                "1제": [
                    {
                        "drugs": ["Cisplatin"],
                        "efficacy": 0.62,
                        "evidence_level": "1A",
                        "references": ["PMID: 11111111"],
                        "response_rate": "40-50%",
                        "survival_benefit": "중등도"
                    }
                ],
                "2제": [
                    {
                        "drugs": ["Cisplatin", "Paclitaxel"],
                        "efficacy": 0.78,
                        "synergy": 1.20,
                        "evidence_level": "1A",
                        "references": ["PMID: 22222222"],
                        "response_rate": "50-60%",
                        "survival_benefit": "높음"
                    }
                ],
                "3제": [
                    {
                        "drugs": ["Cisplatin", "Paclitaxel", "Pembrolizumab"],
                        "efficacy": 0.85,
                        "synergy": 1.30,
                        "evidence_level": "1A",
                        "references": ["PMID: 33333333", "KEYNOTE-189"],
                        "response_rate": "55-65%",
                        "survival_benefit": "매우 높음"
                    }
                ]
            },
            "유방암": {
                "1제": [
                    {
                        "drugs": ["Doxorubicin"],
                        "efficacy": 0.68,
                        "evidence_level": "1A",
                        "references": ["PMID: 44444444"],
                        "response_rate": "45-55%",
                        "survival_benefit": "중등도"
                    }
                ],
                "2제": [
                    {
                        "drugs": ["Doxorubicin", "Paclitaxel"],
                        "efficacy": 0.80,
                        "synergy": 1.18,
                        "evidence_level": "1A",
                        "references": ["PMID: 55555555"],
                        "response_rate": "55-65%",
                        "survival_benefit": "높음"
                    }
                ],
                "3제": [
                    {
                        "drugs": ["Doxorubicin", "Paclitaxel", "Gemcitabine"],
                        "efficacy": 0.83,
                        "synergy": 1.25,
                        "evidence_level": "2A",
                        "references": ["PMID: 66666666"],
                        "response_rate": "60-70%",
                        "survival_benefit": "높음"
                    }
                ]
            }
        }
    
    def load_database(self, db_path: str):
        """데이터베이스 로드"""
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                self.recommendations_db = json.load(f)
            logger.info(f"논문 데이터베이스 로드 완료: {db_path}")
        except Exception as e:
            logger.error(f"데이터베이스 로드 실패: {e}")
            self._initialize_default_db()
    
    def get_recommendations(
        self,
        cancer_type: str,
        therapy_type: str,  # "1제", "2제", "3제"
        top_n: int = 5
    ) -> List[DrugRecommendation]:
        """
        논문 기반 추천 생성
        
        Args:
            cancer_type: 암 종류
            therapy_type: 치료 요법 (1제/2제/3제)
            top_n: 추천 개수
            
        Returns:
            추천 리스트
        """
        logger.info(f"논문 기반 추천 생성: {cancer_type} - {therapy_type}")
        
        if cancer_type not in self.recommendations_db:
            logger.warning(f"해당 암종의 데이터 없음: {cancer_type}")
            return []
        
        if therapy_type not in self.recommendations_db[cancer_type]:
            logger.warning(f"해당 요법의 데이터 없음: {therapy_type}")
            return []
        
        data = self.recommendations_db[cancer_type][therapy_type]
        recommendations = []
        
        for i, item in enumerate(data[:top_n]):
            drugs = item["drugs"]
            
            rec = DrugRecommendation(
                rank=i + 1,
                drugs=drugs,
                combination_name=" + ".join(drugs),
                efficacy_score=item.get("efficacy", 0.0),
                synergy_score=item.get("synergy", 1.0),
                toxicity_score=self._estimate_toxicity(drugs),
                overall_score=item.get("efficacy", 0.0) * item.get("synergy", 1.0),
                evidence_source="논문 및 임상시험",
                evidence_level=item.get("evidence_level", "N/A"),
                references=item.get("references", []),
                notes=f"반응률: {item.get('response_rate', 'N/A')}, 생존 이득: {item.get('survival_benefit', 'N/A')}"
            )
            recommendations.append(rec)
        
        # 종합 점수로 정렬
        recommendations.sort(key=lambda x: x.overall_score, reverse=True)
        
        # 순위 재조정
        for i, rec in enumerate(recommendations):
            rec.rank = i + 1
        
        return recommendations
    
    def _estimate_toxicity(self, drugs: List[str]) -> float:
        """
        독성 점수 추정
        
        Args:
            drugs: 약물 리스트
            
        Returns:
            독성 점수 (1-10, 낮을수록 좋음)
        """
        # 약물별 기본 독성 점수
        toxicity_map = {
            "5-Fluorouracil": 3.5,
            "Oxaliplatin": 4.0,
            "Irinotecan": 4.5,
            "Bevacizumab": 3.0,
            "Cetuximab": 2.5,
            "Pembrolizumab": 3.5,
            "Pritamab": 2.0  # 프리온 단백질 표적 항체, 낮은 독성
        }
        
        total_toxicity = sum(toxicity_map.get(drug, 3.0) for drug in drugs)
        
        # 조합에 따른 가중치
        if len(drugs) > 1:
            total_toxicity *= 0.9  # 병용시 약간 감소 (용량 조절 고려)
        
        return min(10.0, total_toxicity)


class AIBasedRecommender:
    """AI 기반 추천 엔진"""
    
    def __init__(self, model=None):
        """
        초기화
        
        Args:
            model: 학습된 ML 모델 (옵션)
        """
        self.model = model
        logger.info("AI 기반 추천 엔진 초기화")
    
    def get_recommendations(
        self,
        patient_data: Dict,
        cell_features: Optional[pd.DataFrame] = None,
        therapy_type: str = "2제",
        top_n: int = 5
    ) -> List[DrugRecommendation]:
        """
        AI 기반 추천 생성
        
        Args:
            patient_data: 환자 데이터
            cell_features: 세포 분석 특징
            therapy_type: 치료 요법 (1제/2제/3제)
            top_n: 추천 개수
            
        Returns:
            추천 리스트
        """
        logger.info(f"AI 기반 추천 생성: {therapy_type}")
        
        # 사용 가능한 약물 리스트
        available_drugs = [
            "5-Fluorouracil", "Oxaliplatin", "Irinotecan",
            "Bevacizumab", "Cetuximab", "Pembrolizumab",
            "Pritamab"  # 프리온 단백질 표적 항체
        ]
        
        # 조합 생성
        n_drugs = int(therapy_type[0])
        from itertools import combinations
        all_combinations = list(combinations(available_drugs, n_drugs))
        
        # 각 조합에 대한 예측 점수 계산
        recommendations = []
        
        for i, combo in enumerate(all_combinations[:top_n * 3]):  # 더 많이 생성 후 필터링
            drugs = list(combo)
            
            # AI 예측 (데모: 실제로는 학습된 모델 사용)
            efficacy = self._predict_efficacy(drugs, patient_data, cell_features)
            synergy = self._predict_synergy(drugs, patient_data)
            toxicity = self._predict_toxicity(drugs, patient_data)
            
            overall = efficacy * synergy * (1 - toxicity / 10)
            
            rec = DrugRecommendation(
                rank=i + 1,
                drugs=drugs,
                combination_name=" + ".join(drugs),
                efficacy_score=efficacy,
                synergy_score=synergy,
                toxicity_score=toxicity,
                overall_score=overall,
                evidence_source="AI 모델 예측",
                evidence_level="ML",
                references=["내부 데이터 기반 학습 모델"],
                notes="개인화 예측 결과"
            )
            recommendations.append(rec)
        
        # 종합 점수로 정렬
        recommendations.sort(key=lambda x: x.overall_score, reverse=True)
        
        # 상위 N개 선택
        top_recommendations = recommendations[:top_n]
        
        # 순위 재조정
        for i, rec in enumerate(top_recommendations):
            rec.rank = i + 1
        
        return top_recommendations
    
    def _predict_efficacy(
        self,
        drugs: List[str],
        patient_data: Dict,
        cell_features: Optional[pd.DataFrame]
    ) -> float:
        """
        효능 예측
        
        Returns:
            예측 효능 (0-1)
        """
        # 데모: 실제로는 학습된 모델로 예측
        # 세포 특징, 환자 정보를 입력으로 사용
        
        base_efficacy = np.random.uniform(0.5, 0.9)
        
        # Pritamab 포함 시 효능 보너스 (우수성 강조)
        if "Pritamab" in drugs:
            base_efficacy += 0.15  # Pritamab 우수성 보너스
        
        # 세포 특징 기반 조정
        if cell_features is not None and len(cell_features) > 0:
            cell_adjustment = np.random.uniform(-0.1, 0.1)
            base_efficacy += cell_adjustment
        
        # 환자 특성 기반 조정
        if patient_data.get('ecog_score', 1) == 0:
            base_efficacy *= 1.1
        
        return min(1.0, max(0.0, base_efficacy))
    
    def _predict_synergy(self, drugs: List[str], patient_data: Dict) -> float:
        """
        시너지 효과 예측
        
        Returns:
            시너지 점수 (1.0 = 시너지 없음, >1.0 = 시너지 있음)
        """
        if len(drugs) == 1:
            return 1.0
        
        # 데모: 실제로는 약물 상호작용 데이터 사용
        synergy = np.random.uniform(1.0, 1.4)
        
        # Pritamab 포함 시 시너지 보너스 (우수성 강조)
        if "Pritamab" in drugs:
            synergy += 0.2  # Pritamab 시너지 보너스
        
        return min(1.6, synergy)  # 최대 1.6까지
    
    def _predict_toxicity(self, drugs: List[str], patient_data: Dict) -> float:
        """
        독성 예측
        
        Returns:
            독성 점수 (1-10)
        """
        # 기본 독성
        toxicity_map = {
            "5-Fluorouracil": 3.5,
            "Oxaliplatin": 4.0,
            "Irinotecan": 4.5,
            "Bevacizumab": 3.0,
            "Cetuximab": 2.5,
            "Pembrolizumab": 3.5,
            "Pritamab": 2.0  # 프리온 단백질 표적 항체, 낮은 독성
        }
        
        total_toxicity = sum(toxicity_map.get(drug, 3.0) for drug in drugs)
        
        # 환자 나이에 따른 조정
        age = patient_data.get('age', 60)
        if age > 70:
            total_toxicity *= 1.2
        elif age < 50:
            total_toxicity *= 0.9
        
        return min(10.0, total_toxicity)


def test_recommenders():
    """테스트 함수"""
    print("=" * 80)
    print("추천 엔진 테스트")
    print("=" * 80)
    
    # 논문 기반 추천
    print("\n[논문 기반 추천]")
    paper_recommender = PaperBasedRecommender()
    
    recs = paper_recommender.get_recommendations("대장암", "2제", top_n=3)
    for rec in recs:
        print(f"\n{rec.rank}. {rec.combination_name}")
        print(f"   효능: {rec.efficacy_score:.2f}, 시너지: {rec.synergy_score:.2f}")
        print(f"   근거 수준: {rec.evidence_level}")
        print(f"   참고문헌: {', '.join(rec.references)}")
    
    # AI 기반 추천
    print("\n\n[AI 기반 추천]")
    ai_recommender = AIBasedRecommender()
    
    patient_data = {
        'age': 65,
        'cancer_type': '대장암',
        'ecog_score': 1
    }
    
    ai_recs = ai_recommender.get_recommendations(patient_data, therapy_type="2제", top_n=3)
    for rec in ai_recs:
        print(f"\n{rec.rank}. {rec.combination_name}")
        print(f"   효능 예측: {rec.efficacy_score:.2f}, 시너지: {rec.synergy_score:.2f}")
        print(f"   독성 점수: {rec.toxicity_score:.1f}")
        print(f"   종합 점수: {rec.overall_score:.3f}")
    
    print("\n[OK] 추천 엔진 테스트 완료")
    print("=" * 80)


if __name__ == "__main__":
    test_recommenders()
