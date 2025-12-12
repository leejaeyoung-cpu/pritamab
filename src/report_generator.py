"""
AI 추론 결과 보고서 생성 모듈
환자별 보고서, 월간 요약, 분석 리포트 생성
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json


class ReportGenerator:
    """
    AI 추론 결과 보고서 생성 클래스
    
    기능:
    - 환자별 상세 보고서
    - 월간 요약 보고서
    - 암종별 분석 보고서
    - Markdown 형식 출력
    """
    
    def __init__(self, dataset_manager):
        """
        초기화
        
        Args:
            dataset_manager: InferenceDatasetManager 인스턴스
        """
        self.manager = dataset_manager
        self.reports_dir = Path.cwd() / "data" / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_patient_report(self, patient_id: str, timestamp: str = None) -> str:
        """
        환자별 상세 보고서 생성
        
        Args:
            patient_id: 환자 ID
            timestamp: 특정 시점 (None이면 최신)
            
        Returns:
            Markdown 형식 보고서
        """
        result = self.manager.load_inference_result(patient_id, timestamp)
        
        if not result:
            return f"# 오류\n\n환자 {patient_id}의 기록을 찾을 수 없습니다."
        
        # 보고서 작성
        report = []
        
        # 헤더
        report.append("# AI-based Anticancer Drug System")
        report.append("## 환자 추론 결과 보고서\n")
        report.append("---\n")
        
        # 메타데이터
        meta = result["metadata"]
        report.append("## 📋 기본 정보\n")
        report.append(f"- **환자 ID**: {meta['patient_id']}")
        report.append(f"- **생성 일시**: {meta['timestamp']}")
        report.append(f"- **시스템 버전**: {meta['system_version']}")
        report.append(f"- **분석자**: {meta['analyst']}\n")
        
        # 환자 정보
        patient = result["patient_info"]
        report.append("## 👤 환자 정보\n")
        report.append(f"- **나이**: {patient.get('age')}세")
        report.append(f"- **성별**: {patient.get('gender')}")
        report.append(f"- **암 종류**: {patient.get('cancer_type')}")
        report.append(f"- **병기**: {patient.get('cancer_stage')}")
        report.append(f"- **ECOG 수행 상태**: {patient.get('ecog_score')}")
        report.append(f"- **진단일**: {patient.get('diagnosis_date')}")
        
        if patient.get('previous_treatments'):
           report.append(f"- **이전 치료**: {', '.join(patient['previous_treatments'])}\n")
        else:
            report.append("")
        
        # Cellpose 분석
        if result.get("cellpose_analysis") and result["cellpose_analysis"]:
            ca = result["cellpose_analysis"]
            report.append("## 🧬 Cellpose 세포 이미지 분석\n")
            report.append(f"- **분석 이미지 수**: {ca.get('images_analyzed', 'N/A')}장")
            report.append(f"- **검출된 세포 수**: {ca.get('total_cells_detected', 'N/A')}개")
            report.append(f"- **평균 세포/이미지**: {ca.get('avg_cells_per_image', 'N/A'):.1f}개")
            report.append(f"- **평균 세포 크기**: {ca.get('avg_cell_area', 'N/A'):.1f} px²")
            
            if ca.get('analysis_params'):
                params = ca['analysis_params']
                report.append(f"- **사용 모델**: {params.get('model_type', 'N/A')}")
                report.append(f"- **GPU 사용**: {'예' if params.get('gpu_used') else '아니오'}\n")
            else:
                report.append("")
        
        # 논문 기반 추천
        if result.get("paper_recommendations"):
            report.append("## 📚 논문 기반 추천\n")
            
            for rec in result["paper_recommendations"][:5]:
                report.append(f"### {rec['rank']}위. {rec['combination_name']}\n")
                report.append(f"**약물 조합**: {' + '.join(rec['drugs'])}\n")
                report.append("**점수**:")
                report.append(f"- 예상 효능: {rec['efficacy_score']:.2f}")
                report.append(f"- 시너지 점수: {rec['synergy_score']:.2f}")
                report.append(f"- 독성 점수: {rec['toxicity_score']:.1f}")
                report.append(f"- 종합 점수: {rec['overall_score']:.3f}\n")
                report.append(f"**근거 수준**: {rec.get('evidence_level', 'N/A')}\n")
                report.append(f"**참고문헌**: {', '.join(rec.get('references', []))}\n")
                report.append(f"**비고**: {rec.get('notes', '')}\n")
                report.append("---\n")
        
        # AI 기반 추천
        if result.get("ai_recommendations"):
            report.append("## 🤖 AI 기반 추천\n")
            
            for rec in result["ai_recommendations"][:5]:
                report.append(f"### {rec['rank']}위. {rec['combination_name']}\n")
                report.append(f"**약물 조합**: {' + '.join(rec['drugs'])}\n")
                report.append("**AI 예측**:")
                report.append(f"- 예측 효능: {rec['efficacy_score']:.2f}")
                report.append(f"- 예측 시너지: {rec['synergy_score']:.2f}")
                report.append(f"- 예측 독성: {rec['toxicity_score']:.1f}")
                report.append(f"- 종합 점수: {rec['overall_score']:.3f}")
                
                if 'prediction_confidence' in rec:
                    report.append(f"- 예측 신뢰도: {rec['prediction_confidence']:.2f}\n")
                else:
                    report.append("")
                
                report.append("---\n")
        
        # 치료 결과 (있는 경우)
        if result.get("treatment_outcome") and result["treatment_outcome"].get("prescribed_drugs"):
            to = result["treatment_outcome"]
            report.append("## 💊 치료 및 결과\n")
            report.append(f"- **처방 약물**: {' + '.join(to['prescribed_drugs'])}")
            
            if to.get("response"):
                report.append(f"- **치료 반응**: {to['response']}")
            if to.get("side_effects"):
                report.append(f"- **부작용**: {', '.join(to['side_effects'])}")
            if to.get("survival_months"):
                report.append(f"- **생존 개월**: {to['survival_months']}개월")
            
            report.append(f"- **최종 업데이트**: {to.get('last_updated', 'N/A')}\n")
        
        # 푸터
        report.append("---\n")
        report.append("**생성**: AI-based Anticancer Drug System v4.0")
        report.append(f"**일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("**기관**: 인하대학교병원 연구소\n")
        
        return "\n".join(report)
    
    def save_patient_report(self, patient_id: str, timestamp: str = None) -> str:
        """
        환자 보고서를 파일로 저장
        
        Returns:
            저장된 파일 경로
        """
        report = self.generate_patient_report(patient_id, timestamp)
        
        output_dir = self.reports_dir / "patient_reports"
        output_dir.mkdir(exist_ok=True)
        
        filename = f"patient_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(output_path)
    
    def generate_monthly_summary(self, year: int, month: int) -> str:
        """
        월간 요약 보고서 생성
        
        Args:
            year: 연도
            month: 월 (1-12)
            
        Returns:
            Markdown 형식 보고서
        """
        # 날짜 범위 설정
        start_date = f"{year}-{month:02d}-01T00:00:00"
        
        if month == 12:
            end_date = f"{year+1}-01-01T00:00:00"
        else:
            end_date = f"{year}-{month+1:02d}-01T00:00:00"
        
        results = self.manager.search_by_date_range(start_date, end_date)
        
        report = []
        
        # 헤더
        report.append("# 월간 AI 추론 요약 보고서")
        report.append(f"## {year}년 {month}월\n")
        report.append("---\n")
        
        # 전체 통계
        report.append("## 📊 월간 통계\n")
        report.append(f"- **총 환자 수**: {len(set(r['metadata']['patient_id'] for r in results))}명")
        report.append(f"- **총 추론 건수**: {len(results)}건\n")
        
        # 암종별 분포
        cancer_types = {}
        for r in results:
            ct = r['patient_info'].get('cancer_type', 'Unknown')
            cancer_types[ct] = cancer_types.get(ct, 0) + 1
        
        report.append("### 암종별 분포\n")
        for cancer_type, count in sorted(cancer_types.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- {cancer_type}: {count}건")
        report.append("")
        
        # 병기별 분포
        stages = {}
        for r in results:
            stage = r['patient_info'].get('cancer_stage', 'Unknown')
            stages[stage] = stages.get(stage, 0) + 1
        
        report.append("### 병기별 분포\n")
        for stage in ['I', 'II', 'III', 'IV']:
            if stage in stages:
                report.append(f"- 병기 {stage}: {stages[stage]}건")
        report.append("")
        
        # Cellpose 분석 통계
        cellpose_results = [r for r in results if r.get('cellpose_analysis')]
        if cellpose_results:
            total_cells = sum(r['cellpose_analysis'].get('total_cells_detected', 0) for r in cellpose_results)
            avg_cells = total_cells / len(cellpose_results)
            
            report.append("### Cellpose 분석 통계\n")
            report.append(f"- **분석된 케이스**: {len(cellpose_results)}건")
            report.append(f"- **총 검출 세포**: {total_cells}개")
            report.append(f"- **평균 세포/케이스**: {avg_cells:.1f}개\n")
        
        # 주요 추천 약물
        all_paper_drugs = []
        for r in results:
            if r.get('paper_recommendations'):
                top_rec = r['paper_recommendations'][0]
                all_paper_drugs.extend(top_rec['drugs'])
        
        if all_paper_drugs:
            from collections import Counter
            drug_counts = Counter(all_paper_drugs)
            
            report.append("### 주요 추천 약물 (논문 기반)\n")
            for drug, count in drug_counts.most_common(10):
                report.append(f"- {drug}: {count}회")
            report.append("")
        
        # 푸터
        report.append("---\n")
        report.append(f"**생성일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("**기관**: 인하대학교병원 연구소\n")
        
        return "\n".join(report)
    
    def save_monthly_summary(self, year: int, month: int) -> str:
        """월간 요약을 파일로 저장"""
        report = self.generate_monthly_summary(year, month)
        
        output_dir = self.reports_dir / "monthly_summary"
        output_dir.mkdir(exist_ok=True)
        
        filename = f"summary_{year}{month:02d}.md"
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(output_path)


# 사용 예제
if __name__ == "__main__":
    from inference_dataset_manager import InferenceDatasetManager
    
    manager = InferenceDatasetManager()
    generator = ReportGenerator(manager)
    
    # 환자 보고서 생성 및 저장
    report_path = generator.save_patient_report("P001")
    print(f"보고서 저장됨: {report_path}")
