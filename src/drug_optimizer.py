"""
약물 조합 최적화 모듈
최적의 항암제 조합 및 용량 추천
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from itertools import combinations
import json

from utils import Logger
from ml_models import SynergyCalculator

class DrugCombinationOptimizer:
    """
    약물 조합 최적화 및 추천 시스템
    """
    
    def __init__(self, drug_database: Dict, combinations_database: Optional[Dict] = None):
        """
        Args:
            drug_database: 약물 데이터베이스
            combinations_database: 알려진 조합 데이터베이스 (선택적)
        """
        self.logger = Logger(__name__)
        self.drug_db = drug_database
        self.combinations_db = combinations_database or {'combinations': []}
        self.synergy_calc = SynergyCalculator()
        
        # 약물 리스트 생성
        self.drugs = drug_database.get('drugs', [])
        self.drug_dict = {drug['id']: drug for drug in self.drugs}
        
        self.logger.info(f"{len(self.drugs)}개 약물 로드 완료")
    
    def get_drugs_by_cancer(self, cancer_type: str) -> List[Dict]:
        """
        특정 암종에 효과적인 약물 필터링
        
        Args:
            cancer_type: 암종 (예: '대장암', '폐암')
            
        Returns:
            해당 암종에 효과적인 약물 리스트
        """
        filtered_drugs = [
            drug for drug in self.drugs
            if cancer_type in drug.get('target_cancers', [])
        ]
        
        self.logger.info(f"{cancer_type}에 효과적인 약물: {len(filtered_drugs)}개")
        return filtered_drugs
    
    def generate_combinations(
        self,
        cancer_type: str,
        n_drugs: int = 2,
        max_combinations: int = 20
    ) -> List[Tuple[Dict, ...]]:
        """
        약물 조합 생성
        
        Args:
            cancer_type: 암종
            n_drugs: 조합할 약물 개수 (1, 2, 3)
            max_combinations: 최대 조합 개수
            
        Returns:
            약물 조합 리스트
        """
        # 해당 암종에 효과적인 약물 추출
        candidate_drugs = self.get_drugs_by_cancer(cancer_type)
        
        if len(candidate_drugs) < n_drugs:
            self.logger.warning(
                f"약물이 부족합니다. {len(candidate_drugs)}개만 사용 가능"
            )
            n_drugs = len(candidate_drugs)
        
        # 조합 생성
        all_combinations = list(combinations(candidate_drugs, n_drugs))
        
        # 최대 개수 제한
        if len(all_combinations) > max_combinations:
            # 독성 스코어가 낮은 조합 우선
            all_combinations = sorted(
                all_combinations,
                key=lambda combo: sum(drug['toxicity_score'] for drug in combo)
            )[:max_combinations]
        
        self.logger.info(f"{len(all_combinations)}개 조합 생성")
        return all_combinations
    
    def score_combination(
        self,
        combination: Tuple[Dict, ...],
        cell_features: Optional[Dict] = None
    ) -> Dict:
        """
        약물 조합 점수 계산
        
        Args:
            combination: 약물 조합 튜플
            cell_features: 세포 특징 (선택적, 개인화된 예측에 사용)
            
        Returns:
            점수 딕셔너리
        """
        drug_ids = [drug['id'] for drug in combination]
        drug_names = [drug['name'] for drug in combination]
        
        # 1. 알려진 조합인지 확인
        known_combo = self._find_known_combination(drug_ids)
        
        if known_combo:
            # 알려진 조합의 시너지 스코어 사용
            synergy_score = known_combo.get('synergy_score', 1.0)
            clinical_efficacy = known_combo.get('clinical_efficacy', 0.5)
        else:
            # 예측된 시너지 스코어 계산
            synergy_score = self._predict_synergy(combination)
            clinical_efficacy = self._estimate_efficacy(combination, cell_features)
        
        # 2. 독성 스코어 계산 (조합의 평균)
        toxicity_scores = [drug['toxicity_score'] for drug in combination]
        avg_toxicity = np.mean(toxicity_scores)
        
        # 3. 종합 점수 계산
        # 효능은 높이고, 독성은 낮추고, 시너지는 높이는 방향
        overall_score = (
            clinical_efficacy * 0.5 +
            synergy_score * 0.3 -
            (avg_toxicity / 10.0) * 0.2
        )
        
        result = {
            'drugs': drug_names,
            'drug_ids': drug_ids,
            'synergy_score': float(synergy_score),
            'clinical_efficacy': float(clinical_efficacy),
            'toxicity_score': float(avg_toxicity),
            'overall_score': float(overall_score),
            'is_known_combo': known_combo is not None,
            'combination_name': known_combo.get('name', '') if known_combo else None
        }
        
        return result
    
    def _find_known_combination(self, drug_ids: List[str]) -> Optional[Dict]:
        """알려진 조합 찾기"""
        drug_ids_set = set(drug_ids)
        
        for combo in self.combinations_db.get('combinations', []):
            if set(combo['drugs']) == drug_ids_set:
                return combo
        
        return None
    
    def _predict_synergy(self, combination: Tuple[Dict, ...]) -> float:
        """
        시너지 예측 (간단한 휴리스틱)
        실제로는 ML 모델 사용 가능
        """
        # 다른 카테고리의 약물 조합은 시너지 가능성 높음
        categories = [drug['category'] for drug in combination]
        unique_categories = len(set(categories))
        
        # 기본 시너지 점수
        if len(combination) == 1:
            return 1.0
        elif unique_categories == len(combination):
            # 모두 다른 카테고리 - 높은 시너지 가능성
            return 1.2 + np.random.uniform(-0.1, 0.2)
        else:
            # 일부 같은 카테고리
            return 1.0 + np.random.uniform(-0.1, 0.1)
    
    def _estimate_efficacy(
        self,
        combination: Tuple[Dict, ...],
        cell_features: Optional[Dict] = None
    ) -> float:
        """
        효능 추정
        실제로는 ML 모델로 예측
        """
        # IC50 범위의 중간값 사용 (낮을수록 효과적)
        ic50_values = []
        for drug in combination:
            ic50_range = drug.get('typical_ic50_range', [1.0, 10.0])
            avg_ic50 = np.mean(ic50_range)
            ic50_values.append(avg_ic50)
        
        # IC50을 효능으로 변환 (IC50이 낮을수록 효능 높음)
        # 효능 = 1 / (1 + IC50)
        efficacies = [1.0 / (1.0 + ic50) for ic50 in ic50_values]
        
        # 조합 효능 (Bliss independence 근사)
        combined_efficacy = 1.0
        for eff in efficacies:
            combined_efficacy *= (1 - eff)
        combined_efficacy = 1 - combined_efficacy
        
        return combined_efficacy
    
    def recommend_combinations(
        self,
        cancer_type: str,
        n_drugs: int = 2,
        top_n: int = 5,
        cell_features: Optional[Dict] = None
    ) -> List[Dict]:
        """
        최적 약물 조합 추천
        
        Args:
            cancer_type: 암종
            n_drugs: 조합할 약물 개수
            top_n: 상위 N개 추천
            cell_features: 세포 특징 (개인화된 추천)
            
        Returns:
            추천 조합 리스트 (점수 순)
        """
        self.logger.info(f"{cancer_type}에 대한 {n_drugs}제 조합 추천 시작")
        
        # 조합 생성
        combinations_list = self.generate_combinations(cancer_type, n_drugs)
        
        if not combinations_list:
            self.logger.warning("생성된 조합이 없습니다.")
            return []
        
        # 각 조합 점수 계산
        scored_combinations = []
        for combo in combinations_list:
            score = self.score_combination(combo, cell_features)
            scored_combinations.append(score)
        
        # 점수 순 정렬
        scored_combinations.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # 상위 N개 반환
        recommendations = scored_combinations[:top_n]
        
        self.logger.info(f"상위 {len(recommendations)}개 조합 추천 완료")
        return recommendations
    
    def recommend_dosage(
        self,
        drug_id: str,
        cancer_type: str,
        cell_features: Optional[Dict] = None
    ) -> Dict:
        """
        약물 용량 추천
        
        Args:
            drug_id: 약물 ID
            cancer_type: 암종
            cell_features: 세포 특징
            
        Returns:
            용량 추천 딕셔너리
        """
        drug = self.drug_dict.get(drug_id)
        
        if not drug:
            raise ValueError(f"약물을 찾을 수 없습니다: {drug_id}")
        
        # IC50 범위에서 추천 용량 계산
        ic50_range = drug.get('typical_ic50_range', [1.0, 10.0])
        
        # 일반적으로 IC50의 2-5배 용량 사용
        recommended_dose = np.mean(ic50_range) * 3.0
        min_dose = ic50_range[0] * 2.0
        max_dose = ic50_range[1] * 5.0
        
        result = {
            'drug_id': drug_id,
            'drug_name': drug['name'],
            'recommended_dose': float(recommended_dose),
            'min_dose': float(min_dose),
            'max_dose': float(max_dose),
            'unit': 'μM',
            'notes': f"{drug['mechanism']} 기반 용량"
        }
        
        return result
    
    def get_combination_details(self, drug_ids: List[str]) -> Dict:
        """
        조합 상세 정보 제공
        
        Args:
            drug_ids: 약물 ID 리스트
            
        Returns:
            상세 정보 딕셔너리
        """
        drugs = [self.drug_dict[drug_id] for drug_id in drug_ids if drug_id in self.drug_dict]
        
        # 알려진 조합 확인
        known_combo = self._find_known_combination(drug_ids)
        
        # 메커니즘 분석
        mechanisms = [drug['mechanism'] for drug in drugs]
        categories = [drug['category'] for drug in drugs]
        
        # 부작용 통합
        all_side_effects = []
        for drug in drugs:
            all_side_effects.extend(drug.get('side_effects', []))
        
        # 중복 제거 및 빈도 계산
        side_effect_counts = {}
        for effect in all_side_effects:
            side_effect_counts[effect] = side_effect_counts.get(effect, 0) + 1
        
        # 공통 부작용 (2개 이상 약물에서 나타나는)
        common_side_effects = [
            effect for effect, count in side_effect_counts.items()
            if count >= 2
        ]
        
        result = {
            'drugs': [
                {
                    'id': drug['id'],
                    'name': drug['name'],
                    'korean_name': drug['korean_name'],
                    'category': drug['category'],
                    'mechanism': drug['mechanism']
                }
                for drug in drugs
            ],
            'mechanisms': mechanisms,
            'categories': categories,
            'unique_mechanisms': len(set(mechanisms)),
            'unique_categories': len(set(categories)),
            'all_side_effects': list(side_effect_counts.keys()),
            'common_side_effects': common_side_effects,
            'known_combination': known_combo,
            'total_drugs': len(drugs)
        }
        
        return result
    
    def analyze_synergy(
        self,
        drug_ids: List[str],
        efficacy_data: Optional[Dict] = None
    ) -> Dict:
        """
        시너지 분석
        
        Args:
            drug_ids: 약물 ID 리스트
            efficacy_data: 실험 데이터 (선택적)
            
        Returns:
            시너지 분석 결과
        """
        if len(drug_ids) == 1:
            return {
                'synergy_type': 'single_agent',
                'synergy_score': 1.0,
                'interpretation': '단일 약물'
            }
        
        # 알려진 조합 확인
        known_combo = self._find_known_combination(drug_ids)
        
        if known_combo:
            synergy_score = known_combo.get('synergy_score', 1.0)
        else:
            # 예측
            drugs = [self.drug_dict[drug_id] for drug_id in drug_ids if drug_id in self.drug_dict]
            synergy_score = self._predict_synergy(tuple(drugs))
        
        # 시너지 해석
        if synergy_score > 1.2:
            synergy_type = 'synergistic'
            interpretation = '강한 시너지 효과'
        elif synergy_score > 1.0:
            synergy_type = 'additive'
            interpretation = '상승 효과'
        elif synergy_score > 0.8:
            synergy_type = 'additive'
            interpretation = '부가 효과'
        else:
            synergy_type = 'antagonistic'
            interpretation = '길항 작용 가능'
        
        result = {
            'synergy_type': synergy_type,
            'synergy_score': float(synergy_score),
            'interpretation': interpretation,
            'is_known': known_combo is not None,
            'confidence': 'high' if known_combo else 'medium'
        }
        
        return result
