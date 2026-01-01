"""
AI Recommendation Service
Migrated from AI_Anticancer_Drug_System.py
"""
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from schemas import DrugCombination

logger = logging.getLogger(__name__)


# 논문 기반 추천 데이터베이스
PAPER_RECOMMENDATIONS = {
  "대장암": {
        "1제": [
            {"drugs": ["5-Fluorouracil"], "efficacy": 0.65, "synergy": 1.0, "toxicity": 3.5,
             "evidence": "1A", "refs": ["PMID: 12345678"], "notes": "표준 1차 치료, 반응률 45-55%"},
            {"drugs": ["Capecitabine"], "efficacy": 0.63, "synergy": 1.0, "toxicity": 3.2,
             "evidence": "1A", "refs": ["PMID: 23456789"], "notes": "경구용 5-FU 전구체"}
        ],
        "2제": [
            {"drugs": ["5-Fluorouracil", "Oxaliplatin"], "efficacy": 0.82, "synergy": 1.26, "toxicity": 4.5,
             "evidence": "1A", "refs": ["PMID: 34567890"], "notes": "FOLFOX, 표준 병용 요법"},
            {"drugs": ["Oxaliplatin", "Bevacizumab"], "efficacy": 0.76, "synergy": 1.18, "toxicity": 3.8,
             "evidence": "1A", "refs": ["PMID: 56789012"], "notes": "혈관신생 억제 병용, 진행성 대장암"}
        ],
        "3제": [
            {"drugs": ["5-Fluorouracil", "Oxaliplatin", "Bevacizumab"], "efficacy": 0.88, "synergy": 1.35, "toxicity": 5.0,
             "evidence": "1A", "refs": ["PMID: 67890123", "NO16966 Trial"], "notes": "FOLFOX + Bevacizumab, 반응률 60-70%, 전이성 대장암 1차 치료"}
        ]
    },
    "폐암": {
        "1제": [
            {"drugs": ["Cisplatin"], "efficacy": 0.62, "synergy": 1.0, "toxicity": 5.0,
             "evidence": "1A", "refs": ["PMID: 11111111"], "notes": "백금 기반 표준 치료"}
        ],
        "2제": [
            {"drugs": ["Cisplatin", "Pemetrexed"], "efficacy": 0.75, "synergy": 1.21, "toxicity": 5.5,
             "evidence": "1A", "refs": ["PMID: 22222222"], "notes": "비소세포폐암 표준 병용"},
            {"drugs": ["Carboplatin", "Paclitaxel"], "efficacy": 0.73, "synergy": 1.18, "toxicity": 4.8,
             "evidence": "1A", "refs": ["PMID: 33333333"], "notes": "백금-탁산 병용"}
        ],
        "3제": [
            {"drugs": ["Carboplatin", "Pemetrexed", "Pembrolizumab"], "efficacy": 0.86, "synergy": 1.39, "toxicity": 6.0,
             "evidence": "1A", "refs": ["PMID: 44444444", "KEYNOTE-189"], "notes": "면역치료 병용, 반응률 55-65%, 큰 생존 이득"}
        ]
    },
    "유방암": {
        "1제": [
            {"drugs": ["Doxorubicin"], "efficacy": 0.68, "synergy": 1.0, "toxicity": 5.5,
             "evidence": "1A", "refs": ["PMID: 55555555"], "notes": "안트라사이클린 기반 표준"}
        ],
        "2제": [
            {"drugs": ["Doxorubicin", "Cyclophosphamide"], "efficacy": 0.79, "synergy": 1.16, "toxicity": 5.8,
             "evidence": "1A", "refs": ["PMID: 66666666"], "notes": "AC 요법, 표준 보조 치료"},
            {"drugs": ["Paclitaxel", "Trastuzumab"], "efficacy": 0.81, "synergy": 1.19, "toxicity": 4.2,
             "evidence": "1A", "refs": ["PMID: 77777777"], "notes": "HER2 양성 유방암"}
        ],
        "3제": [
            {"drugs": ["Doxorubicin", "Paclitaxel", "Gemcitabine"], "efficacy": 0.83, "synergy": 1.25, "toxicity": 6.5,
             "evidence": "2A", "refs": ["PMID: 88888888"], "notes": "삼중 병용, 진행성 유방암"}
        ]
    }
}


def get_paper_recommendations(
    cancer_type: str,
    therapy_type: str,
    top_n: int = 5
) -> List[DrugCombination]:
    """
    논문 기반 추천 생성
    
    Args:
        cancer_type: 암 종류
        therapy_type: 치료 유형 (1제, 2제, 3제)
        top_n: 상위 N개 추천
        
    Returns:
        추천 약물 조합 리스트
    """
    try:
        recommendations = PAPER_RECOMMENDATIONS.get(cancer_type, {}).get(therapy_type, [])
        
        # 효능 점수 기준으로 정렬
        sorted_recs = sorted(recommendations, key=lambda x: x['efficacy'], reverse=True)
        
        # 상위 N개 선택
        top_recs = sorted_recs[:top_n]
        
        # DrugCombination 스키마로 변환
        result = []
        for rec in top_recs:
            # 종합 점수 계산 (효능 60%, 시너지 30%, 독성 -10%)
            score = (rec['efficacy'] * 0.6 + 
                    rec['synergy'] * 0.3 - 
                    (rec['toxicity'] / 10) * 0.1)
            
            result.append(DrugCombination(
                drugs=rec['drugs'],
                efficacy=rec['efficacy'],
                synergy=rec['synergy'],
                toxicity=rec['toxicity'],
                evidence=rec['evidence'],
                references=rec['refs'],
                notes=rec['notes'],
                score=round(score, 3)
            ))
        
        logger.info(f"Generated {len(result)} paper-based recommendations for {cancer_type} ({therapy_type})")
        return result
        
    except Exception as e:
        logger.error(f"Error in get_paper_recommendations: {e}")
        return []


def get_ai_recommendations(
    patient_data: Dict[str, Any],
    therapy_type: str,
    top_n: int = 5
) -> List[DrugCombination]:
    """
    AI 기반 개인화 추천 생성
    
    Args:
        patient_data: 환자 데이터 (age, cancer_type, molecular_markers, etc.)
        therapy_type: 치료 유형
        top_n: 상위 N개 추천
        
    Returns:
        AI 기반 추천 리스트
    """
    try:
        cancer_type = patient_data.get('cancer_type', '')
        age = patient_data.get('age', 60)
        markers = patient_data.get('molecular_markers', {})
        
        # 논문 기반 추천을 기반으로 AI 조정
        base_recommendations = PAPER_RECOMMENDATIONS.get(cancer_type, {}).get(therapy_type, [])
        
        if not base_recommendations:
            logger.warning(f"No base recommendations found for {cancer_type} ({therapy_type})")
            return []
        
        ai_recommendations = []
        
        for rec in base_recommendations:
            # AI 조정 계수
            age_factor = 1.0
            marker_factor = 1.0
            
            # 나이에 따른 조정 (고령 환자는 독성 가중치 증가)
            if age > 70:
                age_factor = 0.95  # 효능 약간 감소
                toxicity_adjustment = 0.3  # 독성 가중치 증가
            elif age < 50:
                age_factor = 1.05  # 효능 약간 증가
                toxicity_adjustment = 0.1
            else:
                toxicity_adjustment = 0.2
            
            # 분자 마커에 따른 조정
            if cancer_type == "대장암":
                if markers.get("KRAS") == "돌연변이":
                    if "Oxaliplatin" in rec['drugs']:
                        marker_factor = 1.1  # KRAS 돌연변이에 Oxaliplatin 효과 증가
                elif markers.get("BRAF") == "돌연변이":
                    marker_factor = 0.9  # BRAF 돌연변이는 일반적으로 예후 나쁨
            
            elif cancer_type == "유방암":
                if markers.get("HER2") == "양성":
                    if "Trastuzumab" in rec['drugs']:
                        marker_factor = 1.3  # HER2 양성에 Trastuzumab 매우 효과적
            
            # AI 조정된 점수 계산
            adjusted_efficacy = rec['efficacy'] * age_factor * marker_factor
            adjusted_efficacy = min(1.0, adjusted_efficacy)  # 최대 1.0으로 제한
            
            # 종합 점수 (효능 50%, 시너지 30%, 독성 20%)
            score = (adjusted_efficacy * 0.5 + 
                    rec['synergy'] * 0.3 - 
                    (rec['toxicity'] / 10) * toxicity_adjustment)
            
            ai_recommendations.append({
                **rec,
                'efficacy': round(adjusted_efficacy, 3),
                'score': round(score, 3)
            })
        
        # 점수 기준 정렬
        sorted_recs = sorted(ai_recommendations, key=lambda x: x['score'], reverse=True)
        top_recs = sorted_recs[:top_n]
        
        # DrugCombination 스키마로 변환
        result = []
        for rec in top_recs:
            result.append(DrugCombination(
                drugs=rec['drugs'],
                efficacy=rec['efficacy'],
                synergy=rec['synergy'],
                toxicity=rec['toxicity'],
                evidence=rec['evidence'],
                references=rec['refs'],
                notes=rec['notes'] + f" (AI 조정: age={age}, markers={markers})",
                score=rec['score']
            ))
        
        logger.info(f"Generated {len(result)} AI-based recommendations")
        return result
        
    except Exception as e:
        logger.error(f"Error in get_ai_recommendations: {e}")
        return []


def get_hybrid_recommendations(
    paper_recs: List[DrugCombination],
    ai_recs: List[DrugCombination],
    top_n: int = 5
) -> List[DrugCombination]:
    """
    논문 + AI 하이브리드 추천 생성
    
    Args:
        paper_recs: 논문 기반 추천
        ai_recs: AI 기반 추천
        top_n: 상위 N개
        
    Returns:
        하이브리드 추천
    """
    try:
        # 모든 추천 합치기
        all_recs = {}
        
        # 논문 추천 (가중치 0.4)
        for rec in paper_recs:
            key = tuple(sorted(rec.drugs))
            all_recs[key] = {
                **rec.model_dump(),
                'hybrid_score': rec.score * 0.4
            }
        
        # AI 추천 (가중치 0.6)
        for rec in ai_recs:
            key = tuple(sorted(rec.drugs))
            if key in all_recs:
                # 이미 존재하면 점수 합산
                all_recs[key]['hybrid_score'] += rec.score * 0.6
            else:
                all_recs[key] = {
                    **rec.model_dump(),
                    'hybrid_score': rec.score * 0.6
                }
        
        # 하이브리드 점수 기준 정렬
        sorted_recs = sorted(all_recs.values(), key=lambda x: x['hybrid_score'], reverse=True)
        top_recs = sorted_recs[:top_n]
        
        # DrugCombination 스키마로 변환
        result = []
        for rec in top_recs:
            result.append(DrugCombination(
                drugs=rec['drugs'],
                efficacy=rec['efficacy'],
                synergy=rec['synergy'],
                toxicity=rec['toxicity'],
                evidence=rec['evidence'],
                references=rec['references'],
                notes=rec['notes'] + " [하이브리드 추천]",
                score=round(rec['hybrid_score'], 3)
            ))
        
        logger.info(f"Generated {len(result)} hybrid recommendations")
        return result
        
    except Exception as e:
        logger.error(f"Error in get_hybrid_recommendations: {e}")
        return []
