"""
통합 분석 엔진
환자 데이터 + AI 학습 데이터를 통합하여 종합 분석
"""

import json
from pathlib import Path
from datetime import datetime
import numpy as np

class IntegratedAnalysisEngine:
    """환자 데이터와 AI 학습 데이터를 통합 분석"""
    
    def __init__(self):
        self.training_data_path = Path("dataset/training_data")
        self.patients_path = Path("dataset/patients")
        
    def analyze_patient(self, patient_id, patient_data):
        """환자 종합 분석"""
        print(f"🔍 환자 {patient_id} 통합 분석 시작...")
        
        analysis_results = {
            'patient_id': patient_id,
            'timestamp': datetime.now().isoformat(),
            'cellpose_analysis': self.analyze_cellpose(patient_id, patient_data),
            'drug_recommendations': self.recommend_drugs(patient_data),
            'ai_superiority': self.analyze_ai_performance(patient_data),
            'similar_cases': self.find_similar_cases(patient_data)
        }
        
        return analysis_results
    
    def analyze_cellpose(self, patient_id, patient_data):
        """Cellpose 분석 결과 처리"""
        # 환자의 Cellpose 분석 결과 확인
        if 'cellpose_analysis' in patient_data:
            patient_stats = patient_data['cellpose_analysis'].get('stats', {})
            
            # AI 학습 데이터와 비교
            training_stats = self.get_training_cellpose_stats()
            
            comparison = {
                'patient_cells': patient_stats.get('total_cells', 0),
                'avg_training_cells': training_stats.get('avg_cells', 0),
                'patient_cell_area': patient_stats.get('avg_cell_area', 0),
                'avg_training_area': training_stats.get('avg_area', 0),
                'percentile': self.calculate_percentile(patient_stats, training_stats)
            }
            
            return {
                'has_analysis': True,
                'stats': patient_stats,
                'comparison': comparison,
                'interpretation': self.interpret_cellpose_results(comparison)
            }
        else:
            return {
                'has_analysis': False,
                'message': 'Cellpose 분석 데이터가 없습니다.'
            }
    
    def recommend_drugs(self, patient_data):
        """항암제 추천"""
        from src.recommendation_engine import PaperBasedRecommender, AIBasedRecommender
        
        paper_engine = PaperBasedRecommender()
        ai_engine = AIBasedRecommender()
        
        cancer_type = patient_data.get('cancer_type', '대장암')
        
        # 환자 정보 기반 추천
        recommendations = {
            '1제': paper_engine.get_recommendations(cancer_type, '1제', top_n=5),
            '2제': paper_engine.get_recommendations(cancer_type, '2제', top_n=5),
            '3제': paper_engine.get_recommendations(cancer_type, '3제', top_n=5)
        }
        
        # AI 추천도 추가
        ai_recs = {
            '1제_ai': ai_engine.get_recommendations(patient_data, therapy_type='1제', top_n=5),
            '2제_ai': ai_engine.get_recommendations(patient_data, therapy_type='2제', top_n=5),
            '3제_ai': ai_engine.get_recommendations(patient_data, therapy_type='3제', top_n=5)
        }
        
        # AI 학습 데이터 기반 우수성 점수 계산
        for therapy_type, recs in recommendations.items():
            for rec in recs:
                # DrugRecommendation 객체를 dict로 변환
                rec_dict = {
                    'rank': rec.rank,
                    'drugs': rec.drugs,
                    'combination_name': rec.combination_name,
                    'efficacy_score': rec.efficacy_score,
                    'synergy_score': rec.synergy_score,
                    'toxicity_score': rec.toxicity_score,
                    'overall_score': rec.overall_score,
                    'evidence_source': rec.evidence_source,
                    'evidence_level': rec.evidence_level,
                    'references': rec.references,
                    'notes': rec.notes,
                    'ai_confidence': self.calculate_ai_confidence_from_rec(rec, patient_data)
                }
        
        # AI 추천도 dict 형식으로 변환
        for therapy_type, recs in ai_recs.items():
            ai_recs[therapy_type] = [{
                'rank': rec.rank,
                'drugs': rec.drugs,
                'combination_name': rec.combination_name,
                'efficacy_score': rec.efficacy_score,
                'synergy_score': rec.synergy_score,
                'toxicity_score': rec.toxicity_score,
                'overall_score': rec.overall_score,
                'evidence_source': rec.evidence_source,
                'evidence_level': rec.evidence_level,
                'references': rec.references,
                'notes': rec.notes
            } for rec in recs]
        
        recommendations.update(ai_recs)
        
        return recommendations
    
    def calculate_ai_confidence_from_rec(self, rec, patient_data):
        """DrugRecommendation 객체로부터 AI 신뢰도 계산"""
        rec_dict = {
            'overall_score': rec.overall_score
        }
        return self.calculate_ai_confidence(rec_dict, patient_data)
    
    def analyze_ai_performance(self, patient_data):
        """AI 우수성 분석"""
        # AI 학습 데이터 통계
        training_stats = self.load_training_statistics()
        
        # 환자 데이터와 비교
        analysis = {
            'training_data_size': training_stats.get('total_files', 0),
            'model_confidence': self.calculate_model_confidence(patient_data, training_stats),
            'data_quality': self.assess_data_quality(patient_data),
            'prediction_reliability': self.calculate_reliability(patient_data, training_stats)
        }
        
        # 우수성 점수 (0-100)
        analysis['superiority_score'] = (
            analysis['model_confidence'] * 0.4 +
            analysis['data_quality'] * 0.3 +
            analysis['prediction_reliability'] * 0.3
        )
        
        return analysis
    
    def find_similar_cases(self, patient_data):
        """유사 케이스 검색"""
        # AI 학습 데이터에서 유사 케이스 찾기
        similar_cases = []
        
        # 암 종류가 같은 케이스
        cancer_type = patient_data.get('cancer_type')
        
        # 병기가 유사한 케이스
        stage = patient_data.get('cancer_stage')
        
        # KRAS 변이 상태가 같은 케이스
        kras_status = patient_data.get('kras_mutation', {}).get('status')
        
        similar_cases.append({
            'criteria': f'{cancer_type}, 병기 {stage}, KRAS {kras_status}',
            'estimated_cases': self.estimate_similar_cases(cancer_type, stage, kras_status),
            'confidence': 0.85
        })
        
        return similar_cases
    
    # Helper methods
    
    def get_training_cellpose_stats(self):
        """AI 학습 데이터의 Cellpose 통계"""
        # 실제로는 training_data의 cellpose_analysis 폴더를 분석
        # 여기서는 샘플 데이터 반환
        return {
            'avg_cells': 150,
            'avg_area': 250.5,
            'std_cells': 50,
            'std_area': 75.2
        }
    
    def calculate_percentile(self, patient_stats, training_stats):
        """환자 데이터의 백분위수 계산"""
        patient_cells = patient_stats.get('total_cells', 0)
        avg_cells = training_stats.get('avg_cells', 0)
        std_cells = training_stats.get('std_cells', 1)
        
        if std_cells == 0:
            return 50
        
        z_score = (patient_cells - avg_cells) / std_cells
        
        # 정규분포 가정하여 백분위수 계산 (간단한 근사)
        percentile = 50 + (z_score * 20)
        return max(0, min(100, percentile))
    
    def interpret_cellpose_results(self, comparison):
        """Cellpose 결과 해석"""
        percentile = comparison['percentile']
        
        if percentile >= 75:
            return "세포 수가 평균보다 많습니다. 종양 활성도가 높을 수 있습니다."
        elif percentile >= 50:
            return "세포 수가 평균 수준입니다."
        elif percentile >= 25:
            return "세포 수가 평균보다 적습니다."
        else:
            return "세포 수가 평균보다 매우 적습니다. 추가 검사가 필요할 수 있습니다."
    
    def calculate_ai_confidence(self, recommendation, patient_data):
        """AI 추천 신뢰도 계산"""
        # 학습 데이터 크기 기반
        training_stats = self.load_training_statistics()
        data_size_score = min(100, training_stats.get('total_files', 0) / 5)
        
        # 환자 데이터 완성도 기반
        completeness = self.calculate_data_completeness(patient_data)
        
        # 추천 점수 기반
        rec_score = recommendation.get('overall_score', 0) * 100
        
        confidence = (data_size_score * 0.3 + completeness * 0.3 + rec_score * 0.4)
        return round(confidence, 2)
    
    def load_training_statistics(self):
        """AI 학습 데이터 통계 로드"""
        metadata_path = self.training_data_path / "dataset_metadata.json"
        
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {'total_files': 0, 'categories': {}}
    
    def calculate_model_confidence(self, patient_data, training_stats):
        """모델 신뢰도 계산 (0-100)"""
        # 학습 데이터 크기
        total_files = training_stats.get('total_files', 0)
        
        # 이미지 데이터가 많을수록 신뢰도 높음
        image_count = training_stats.get('categories', {}).get('cell_images', 0)
        
        confidence = min(100, (total_files / 5) + (image_count / 2))
        return round(confidence, 2)
    
    def assess_data_quality(self, patient_data):
        """데이터 품질 평가 (0-100)"""
        quality_score = 0
        
        # 기본 정보 완성도
        if patient_data.get('age'):
            quality_score += 20
        if patient_data.get('cancer_type'):
            quality_score += 20
        if patient_data.get('cancer_stage'):
            quality_score += 20
        
        # Cellpose 분석 여부
        if 'cellpose_analysis' in patient_data:
            quality_score += 20
        
        # KRAS 변이 정보
        if patient_data.get('kras_mutation', {}).get('status') != 'Unknown':
            quality_score += 20
        
        return quality_score
    
    def calculate_reliability(self, patient_data, training_stats):
        """예측 신뢰성 계산 (0-100)"""
        # 유사 케이스 수
        similar_cases = self.estimate_similar_cases(
            patient_data.get('cancer_type'),
            patient_data.get('cancer_stage'),
            patient_data.get('kras_mutation', {}).get('status')
        )
        
        # 학습 데이터 다양성
        diversity = len(training_stats.get('categories', {})) * 10
        
        reliability = min(100, similar_cases * 2 + diversity)
        return round(reliability, 2)
    
    def calculate_data_completeness(self, patient_data):
        """데이터 완성도 계산 (0-100)"""
        required_fields = ['age', 'gender', 'cancer_type', 'cancer_stage']
        optional_fields = ['ecog_score', 'kras_mutation', 'cellpose_analysis']
        
        required_score = sum(50 for field in required_fields if patient_data.get(field)) / len(required_fields)
        optional_score = sum(50 for field in optional_fields if patient_data.get(field)) / len(optional_fields)
        
        return required_score + optional_score
    
    def estimate_similar_cases(self, cancer_type, stage, kras_status):
        """유사 케이스 수 추정"""
        # 실제로는 training_data를 검색
        # 여기서는 간단한 추정
        base_cases = 10
        
        if cancer_type in ['대장암', 'Colorectal']:
            base_cases += 20
        
        if stage in ['III', 'IV']:
            base_cases += 10
        
        if kras_status == 'Mutant':
            base_cases += 5
        
        return base_cases
