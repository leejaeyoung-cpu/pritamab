"""
환자 보고서 생성기
통합 분석 결과를 기반으로 환자별 맞춤 보고서 생성
"""

import json
from pathlib import Path
from datetime import datetime
from src.integrated_analysis_engine import IntegratedAnalysisEngine

class PatientReportBuilder:
    """환자별 포괄적 보고서 생성"""
    
    def __init__(self):
        self.analysis_engine = IntegratedAnalysisEngine()
        
    def generate_report(self, patient_id, patient_data):
        """포괄적 분석 보고서 생성"""
        print(f"📄 {patient_id} 보고서 생성 중...")
        
        # 1. 통합 분석 실행
        analysis = self.analysis_engine.analyze_patient(patient_id, patient_data)
        
        # 2. 보고서 섹션 구성
        report = {
            'patient_id': patient_id,
            'generated_at': datetime.now().isoformat(),
            'patient_info': self.create_patient_info_section(patient_data),
            'cellpose_analysis': self.create_cellpose_section(analysis['cellpose_analysis']),
            'drug_recommendations': self.create_recommendations_section(analysis['drug_recommendations']),
            'ai_superiority': self.create_ai_analysis_section(analysis['ai_superiority']),
            'similar_cases': analysis['similar_cases'],
            'summary': self.create_summary(analysis, patient_data)
        }
        
        # 3. JSON 저장
        self.save_json_report(patient_id, report)
        
        # 4. Markdown 보고서 생성
        markdown_path = self.generate_markdown_report(patient_id, report)
        
        print(f"✅ 보고서 생성 완료: {markdown_path}")
        
        return report, markdown_path
    
    def create_patient_info_section(self, patient_data):
        """환자 기본 정보 섹션"""
        return {
            'name': patient_data.get('name', 'Unknown'),
            'age': patient_data.get('age', 0),
            'gender': patient_data.get('gender', 'Unknown'),
            'cancer_type': patient_data.get('cancer_type', 'Unknown'),
            'cancer_stage': patient_data.get('cancer_stage', 'Unknown'),
            'ecog_score': patient_data.get('ecog_score', 'N/A'),
            'kras_mutation': patient_data.get('kras_mutation', {}),
            'diagnosis_date': patient_data.get('diagnosis_date', 'Unknown')
        }
    
    def create_cellpose_section(self, cellpose_analysis):
        """Cellpose 분석 섹션"""
        if not cellpose_analysis.get('has_analysis'):
            return {
                'available': False,
                'message': cellpose_analysis.get('message', 'No analysis available')
            }
        
        stats = cellpose_analysis.get('stats', {})
        comparison = cellpose_analysis.get('comparison', {})
        
        return {
            'available': True,
            'total_cells': stats.get('total_cells', 0),
            'avg_cells_per_image': stats.get('avg_cells_per_image', 0),
            'avg_cell_area': stats.get('avg_cell_area', 0),
            'percentile': comparison.get('percentile', 50),
            'interpretation': cellpose_analysis.get('interpretation', ''),
            'comparison_with_training': {
                'patient_cells': comparison.get('patient_cells', 0),
                'avg_training_cells': comparison.get('avg_training_cells', 0),
                'difference_percent': self.calculate_difference_percent(
                    comparison.get('patient_cells', 0),
                    comparison.get('avg_training_cells', 1)
                )
            }
        }
    
    def create_recommendations_section(self, recommendations):
        """항암제 추천 섹션"""
        formatted_recs = {}
        
        for therapy_type, recs in recommendations.items():
            formatted_recs[therapy_type] = [
                {
                    'rank': rec.get('rank', 0),
                    'drugs': rec.get('drugs', []),
                    'efficacy_score': rec.get('efficacy_score', 0),
                    'synergy_score': rec.get('synergy_score', 0),
                    'toxicity_score': rec.get('toxicity_score', 0),
                    'overall_score': rec.get('overall_score', 0),
                    'ai_confidence': rec.get('ai_confidence', 0)
                }
                for rec in recs[:5]  # Top 5
            ]
        
        return formatted_recs
    
    def create_ai_analysis_section(self, ai_superiority):
        """AI 우수성 분석 섹션"""
        return {
            'superiority_score': ai_superiority.get('superiority_score', 0),
            'model_confidence': ai_superiority.get('model_confidence', 0),
            'data_quality': ai_superiority.get('data_quality', 0),
            'prediction_reliability': ai_superiority.get('prediction_reliability', 0),
            'training_data_size': ai_superiority.get('training_data_size', 0),
            'interpretation': self.interpret_ai_score(ai_superiority.get('superiority_score', 0))
        }
    
    def create_summary(self, analysis, patient_data):
        """종합 요약"""
        cellpose = analysis['cellpose_analysis']
        ai_sup = analysis['ai_superiority']
        
        summary = {
            'overall_assessment': self.generate_overall_assessment(cellpose, ai_sup),
            'key_findings': self.extract_key_findings(analysis, patient_data),
            'recommendations_summary': self.summarize_recommendations(analysis['drug_recommendations']),
            'next_steps': self.suggest_next_steps(analysis, patient_data)
        }
        
        return summary
    
    def save_json_report(self, patient_id, report):
        """JSON 보고서 저장"""
        report_dir = Path(f"dataset/patients/{patient_id}/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"analysis_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report_file
    
    def generate_markdown_report(self, patient_id, report):
        """Markdown 보고서 생성"""
        report_dir = Path(f"dataset/patients/{patient_id}/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"analysis_report_{timestamp}.md"
        
        markdown = self.create_markdown_content(report)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        return report_file
    
    def create_markdown_content(self, report):
        """Markdown 내용 생성"""
        patient_info = report['patient_info']
        cellpose = report['cellpose_analysis']
        recommendations = report['drug_recommendations']
        ai_analysis = report['ai_superiority']
        summary = report['summary']
        
        markdown = f"""# 환자 분석 보고서

**환자 ID**: {report['patient_id']}  
**생성 일시**: {datetime.fromisoformat(report['generated_at']).strftime('%Y-%m-%d %H:%M:%S')}

---

## 📋 환자 기본 정보

| 항목 | 내용 |
|------|------|
| 이름 | {patient_info['name']} |
| 나이 | {patient_info['age']}세 |
| 성별 | {patient_info['gender']} |
| 암 종류 | {patient_info['cancer_type']} |
| 병기 | {patient_info['cancer_stage']} |
| ECOG 점수 | {patient_info['ecog_score']} |
| KRAS 변이 | {patient_info['kras_mutation'].get('status', 'Unknown')} |

---

## 🔬 Cellpose 세포 분석

"""
        
        if cellpose.get('available'):
            markdown += f"""
### 분석 결과

- **총 검출 세포**: {cellpose['total_cells']:,}개
- **평균 세포/이미지**: {cellpose['avg_cells_per_image']:.1f}개
- **평균 세포 크기**: {cellpose['avg_cell_area']:.1f} px²
- **백분위수**: {cellpose['percentile']:.1f}%ile

### AI 학습 데이터와 비교

- 환자 세포 수: {cellpose['comparison_with_training']['patient_cells']:,}개
- 평균 세포 수: {cellpose['comparison_with_training']['avg_training_cells']:.0f}개
- 차이: {cellpose['comparison_with_training']['difference_percent']:+.1f}%

### 해석

{cellpose['interpretation']}

"""
        else:
            markdown += f"\n{cellpose.get('message', 'Cellpose 분석 데이터가 없습니다.')}\n"
        
        markdown += """
---

## 💊 AI 정밀 항암제 추천

"""
        
        for therapy_type, recs in recommendations.items():
            markdown += f"\n### {therapy_type} 추천\n\n"
            
            for rec in recs:
                drugs_str = ' + '.join(rec['drugs'])
                markdown += f"""
#### {rec['rank']}위. {drugs_str}

- **효능 점수**: {rec['efficacy_score']:.2f}
- **시너지 점수**: {rec['synergy_score']:.2f}
- **독성 점수**: {rec['toxicity_score']:.1f}
- **종합 점수**: {rec['overall_score']:.3f}
- **AI 신뢰도**: {rec['ai_confidence']:.1f}%

"""
        
        markdown += f"""
---

## 📈 AI 우수성 분석

### 종합 우수성 점수: {ai_analysis['superiority_score']:.1f}/100

| 지표 | 점수 |
|------|------|
| 모델 신뢰도 | {ai_analysis['model_confidence']:.1f}/100 |
| 데이터 품질 | {ai_analysis['data_quality']:.1f}/100 |
| 예측 신뢰성 | {ai_analysis['prediction_reliability']:.1f}/100 |

**AI 학습 데이터 크기**: {ai_analysis['training_data_size']}개 파일

### 해석

{ai_analysis['interpretation']}

---

## 📝 종합 요약

### 전체 평가

{summary['overall_assessment']}

### 주요 발견사항

{self.format_key_findings(summary['key_findings'])}

### 추천 요약

{summary['recommendations_summary']}

### 다음 단계

{self.format_next_steps(summary['next_steps'])}

---

**보고서 생성 위치**: `dataset/patients/{report['patient_id']}/reports/`
"""
        
        return markdown
    
    # Helper methods
    
    def calculate_difference_percent(self, patient_value, training_avg):
        """차이 백분율 계산"""
        if training_avg == 0:
            return 0
        return ((patient_value - training_avg) / training_avg) * 100
    
    def interpret_ai_score(self, score):
        """AI 우수성 점수 해석"""
        if score >= 80:
            return "매우 높은 신뢰도로 AI 분석이 가능합니다. 추천 결과를 신뢰할 수 있습니다."
        elif score >= 60:
            return "높은 신뢰도로 AI 분석이 가능합니다. 추천 결과가 유용할 것입니다."
        elif score >= 40:
            return "중간 수준의 신뢰도입니다. 추천 결과를 참고하되 추가 검증이 필요합니다."
        else:
            return "신뢰도가 낮습니다. 더 많은 데이터가 필요하거나 전문의 상담이 권장됩니다."
    
    def generate_overall_assessment(self, cellpose, ai_sup):
        """전체 평가 생성"""
        assessment = "이 환자에 대한 AI 분석이 완료되었습니다. "
        
        if cellpose.get('available'):
            percentile = cellpose.get('percentile', 50)
            if percentile >= 75:
                assessment += "세포 분석 결과 종양 활성도가 높은 것으로 나타났습니다. "
            else:
                assessment += "세포 분석 결과가 정상 범위 내에 있습니다. "
        
        superiority = ai_sup.get('superiority_score', 0)
        if superiority >= 70:
            assessment += "AI 모델의 신뢰도가 높아 추천 결과를 신뢰할 수 있습니다."
        else:
            assessment += "추가 데이터 수집이 권장됩니다."
        
        return assessment
    
    def extract_key_findings(self, analysis, patient_data):
        """주요 발견사항 추출"""
        findings = []
        
        # Cellpose 결과
        if analysis['cellpose_analysis'].get('available'):
            percentile = analysis['cellpose_analysis'].get('percentile', 50)
            findings.append(f"세포 분석 백분위수: {percentile:.1f}%ile")
        
        # KRAS 변이
        kras_status = patient_data.get('kras_mutation', {}).get('status')
        if kras_status and kras_status != 'Unknown':
            findings.append(f"KRAS 변이 상태: {kras_status}")
        
        # AI 신뢰도
        ai_score = analysis['ai_superiority'].get('superiority_score', 0)
        findings.append(f"AI 분석 신뢰도: {ai_score:.1f}/100")
        
        return findings
    
    def summarize_recommendations(self, recommendations):
        """추천 요약"""
        summary = "AI 기반 항암제 추천이 생성되었습니다. "
        
        # 최고 추천 찾기
        best_recs = {}
        for therapy_type, recs in recommendations.items():
            if recs:
                best_recs[therapy_type] = recs[0]  # 1위
        
        if '2제' in best_recs:
            drugs = ' + '.join(best_recs['2제']['drugs'])
            score = best_recs['2제']['overall_score']
            summary += f"2제 병용요법 최우수 추천: {drugs} (점수: {score:.3f})"
        
        return summary
    
    def suggest_next_steps(self, analysis, patient_data):
        """다음 단계 제안"""
        steps = []
        
        # Cellpose 분석 여부
        if not analysis['cellpose_analysis'].get('available'):
            steps.append("종양 이미지 Cellpose 분석 수행")
        
        # 데이터 품질
        data_quality = analysis['ai_superiority'].get('data_quality', 0)
        if data_quality < 80:
            steps.append("환자 데이터 보완 (의료 영상, 검사 결과 등)")
        
        # 항암제 추천
        steps.append("추천된 항암제 조합에 대한 전문의 상담")
        steps.append("치료 계획 수립 및 모니터링")
        
        return steps
    
    def format_key_findings(self, findings):
        """주요 발견사항 포맷"""
        return '\n'.join([f"- {finding}" for finding in findings])
    
    def format_next_steps(self, steps):
        """다음 단계 포맷"""
        return '\n'.join([f"{i+1}. {step}" for i, step in enumerate(steps)])
