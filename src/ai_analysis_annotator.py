"""
AI 분석 주석 생성 모듈
Cellpose 결과를 분석하여 의미 있는 주석 생성
"""

from typing import Dict, List
from datetime import datetime
import json


class AIAnalysisAnnotator:
    """AI 분석 주석 생성 클래스"""
    
    def __init__(self):
        """초기화"""
        pass
    
    def generate_cellpose_analysis(
        self,
        cellpose_results: List[Dict],
        cellpose_stats: Dict,
        patient_info: Dict
    ) -> Dict:
        """
        Cellpose 분석 주석 생성
        
        Args:
            cellpose_results: Cellpose 분석 결과
            cellpose_stats: Cellpose 통계
            patient_info: 환자 정보
        
        Returns:
            AI 분석 주석
        """
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "overall_assessment": self._assess_overall_quality(cellpose_stats),
            "cell_characteristics": self._analyze_cell_characteristics(cellpose_stats),
            "clinical_insights": self._generate_clinical_insights(cellpose_stats, patient_info),
            "image_quality": self._assess_image_quality(cellpose_results),
            "recommendations": self._generate_recommendations(cellpose_stats),
            "confidence_score": self._calculate_confidence(cellpose_stats)
        }
        
        return analysis
    
    def _assess_overall_quality(self, stats: Dict) -> str:
        """전체 품질 평가"""
        total_cells = stats.get('total_cells', 0)
        avg_cells = stats.get('avg_cells_per_image', 0)
        
        if total_cells == 0:
            return "세포가 검출되지 않았습니다. 이미지 품질이나 염색 상태를 확인하세요."
        
        if avg_cells < 100:
            quality = "낮음"
            comment = "세포 밀도가 낮습니다. 더 많은 시야를 확보하거나 농축된 샘플을 사용하세요."
        elif avg_cells < 500:
            quality = "보통"
            comment = "적절한 세포 밀도입니다."
        else:
            quality = "높음"
            comment = "충분한 세포가 검출되었습니다. 통계적으로 신뢰할 수 있는 분석이 가능합니다."
        
        return f"분석 품질: {quality}. {comment}"
    
    def _analyze_cell_characteristics(self, stats: Dict) -> Dict:
        """세포 특성 분석"""
        avg_area = stats.get('avg_cell_area', 0)
        std_area = stats.get('std_cell_area', 0)
        min_area = stats.get('min_cell_area', 0)
        max_area = stats.get('max_cell_area', 0)
        
        characteristics = {
            "cell_size": "정상",
            "size_variation": "균일",
            "morphology_note": ""
        }
        
        # 세포 크기 평가
        if avg_area < 100:
            characteristics["cell_size"] = "작음"
            characteristics["morphology_note"] = "세포가 평균보다 작습니다. 세포 수축 또는 세포사 가능성을 고려하세요."
        elif avg_area > 500:
            characteristics["cell_size"] = "큼"
            characteristics["morphology_note"] = "세포가 평균보다 큽니다. 암세포의 특징일 수 있습니다."
        
        # 크기 변이 평가
        if std_area > 0:
            cv = (std_area / avg_area) * 100  # 변동계수
            if cv > 50:
                characteristics["size_variation"] = "불균일"
                characteristics["morphology_note"] += " 세포 크기가 매우 불균일합니다. 이종성(heterogeneity)이 높은 종양일 수 있습니다."
            elif cv > 30:
                characteristics["size_variation"] = "중간"
        
        # 극단값 분석
        if max_area > avg_area * 3:
            characteristics["morphology_note"] += " 일부 매우 큰 세포가 관찰됩니다. 다핵세포 또는 거대 암세포 가능성이 있습니다."
        
        return characteristics
    
    def _generate_clinical_insights(self, stats: Dict, patient_info: Dict) -> List[str]:
        """임상적 통찰 생성"""
        insights = []
        
        total_cells = stats.get('total_cells', 0)
        avg_area = stats.get('avg_cell_area', 0)
        cancer_type = patient_info.get('cancer_type', '')
        cancer_stage = patient_info.get('cancer_stage', '')
        
        # 세포 수 기반 인사이트
        if total_cells > 1000:
            insights.append(f"총 {total_cells}개의 세포가 검출되어 충분한 샘플 크기를 확보했습니다.")
        
        # 암종별 인사이트
        if cancer_type:
            insights.append(f"{cancer_type} 환자의 세포 이미지 분석 결과입니다.")
            
            if cancer_type == "대장암":
                if avg_area > 300:
                    insights.append("대장암 세포는 일반적으로 크기가 크고 불규칙합니다. 관찰된 세포 크기가 이와 일치합니다.")
            elif cancer_type == "폐암":
                if avg_area < 200:
                    insights.append("폐암 세포는 상대적으로 작을 수 있습니다. 관찰된 세포 크기 패턴을 확인하세요.")
        
        # 병기별 인사이트
        if cancer_stage:
            if cancer_stage in ['III', 'IV']:
                insights.append(f"병기 {cancer_stage} 환자로, 진행된 암의 세포 특성을 보일 수 있습니다.")
        
        # 치료 반응 예측
        std_area = stats.get('std_cell_area', 0)
        if std_area > 0:
            cv = (std_area / avg_area) * 100
            if cv > 50:
                insights.append("높은 세포 이질성은 치료 저항성과 관련될 수 있습니다. 다제병용요법을 고려할 필요가 있습니다.")
        
        return insights
    
    def _assess_image_quality(self, results: List[Dict]) -> str:
        """이미지 품질 평가"""
        if not results:
            return "이미지가 없습니다."
        
        total_images = len(results)
        images_with_cells = sum(1 for r in results if r.get('num_cells', 0) > 0)
        
        if images_with_cells == 0:
            return "모든 이미지에서 세포가 검출되지 않았습니다. 이미지 품질, 초점, 또는 염색 상태를 확인하세요."
        
        success_rate = (images_with_cells / total_images) * 100
        
        if success_rate == 100:
            return f"모든 {total_images}개 이미지에서 세포가 성공적으로 검출되었습니다. 이미지 품질이 우수합니다."
        elif success_rate >= 80:
            return f"{total_images}개 이미지 중 {images_with_cells}개에서 세포가 검출되었습니다 ({success_rate:.1f}%). 이미지 품질이 양호합니다."
        else:
            return f"{total_images}개 이미지 중 {images_with_cells}개에서만 세포가 검출되었습니다 ({success_rate:.1f}%). 이미지 품질 개선이 필요합니다."
    
    def _generate_recommendations(self, stats: Dict) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        total_cells = stats.get('total_cells', 0)
        avg_cells = stats.get('avg_cells_per_image', 0)
        avg_area = stats.get('avg_cell_area', 0)
        std_area = stats.get('std_cell_area', 0)
        
        # 샘플 크기 권장사항
        if total_cells < 500:
            recommendations.append("통계적 신뢰도 향상을 위해 추가 이미지 촬영을 권장합니다 (목표: 500개 이상 세포).")
        
        # 이미지 품질 권장사항
        if avg_cells < 100:
            recommendations.append("세포 밀도가 낮습니다. 샘플 농축 또는 더 많은 시야 촬영을 고려하세요.")
        
        # 분석 파라미터 권장사항
        if std_area > 0:
            cv = (std_area / avg_area) * 100
            if cv > 50:
                recommendations.append("세포 크기 변이가 큽니다. 수동 검증을 통해 Cellpose 검출의 정확도를 확인하세요.")
        
        # 추가 분석 권장사항
        recommendations.append("세포 형태학적 특징을 바탕으로 AI 약물 추천 정확도가 향상될 수 있습니다.")
        recommendations.append("정기적으로 세포 이미지를 분석하여 치료 반응을 모니터링하세요.")
        
        return recommendations
    
    def _calculate_confidence(self, stats: Dict) -> float:
        """분석 신뢰도 계산"""
        total_cells = stats.get('total_cells', 0)
        avg_cells = stats.get('avg_cells_per_image', 0)
        
        # 기본 점수
        confidence = 0.5
        
        # 세포 수에 따른 가점
        if total_cells > 1000:
            confidence += 0.3
        elif total_cells > 500:
            confidence += 0.2
        elif total_cells > 200:
            confidence += 0.1
        
        # 이미지당 세포 수에 따른 가점
        if avg_cells > 300:
            confidence += 0.2
        elif avg_cells > 150:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def generate_annotation_report(
        self,
        cellpose_results: List[Dict],
        cellpose_stats: Dict,
        patient_info: Dict
    ) -> str:
        """
        Markdown 형식의 주석 보고서 생성
        
        Returns:
            Markdown 문자열
        """
        analysis = self.generate_cellpose_analysis(cellpose_results, cellpose_stats, patient_info)
        
        report = []
        report.append("# AI 세포 이미지 분석 주석\n")
        report.append(f"**생성 시각**: {analysis['timestamp']}\n")
        report.append("---\n")
        
        report.append("## 전체 평가\n")
        report.append(f"{analysis['overall_assessment']}\n")
        
        report.append("## 세포 특성 분석\n")
        char = analysis['cell_characteristics']
        report.append(f"- **세포 크기**: {char['cell_size']}")
        report.append(f"- **크기 변이**: {char['size_variation']}")
        if char['morphology_note']:
            report.append(f"- **형태학적 소견**: {char['morphology_note']}\n")
        
        report.append("## 임상적 통찰\n")
        for insight in analysis['clinical_insights']:
            report.append(f"- {insight}")
        report.append("")
        
        report.append("## 이미지 품질\n")
        report.append(f"{analysis['image_quality']}\n")
        
        report.append("## 권장사항\n")
        for rec in analysis['recommendations']:
            report.append(f"- {rec}")
        report.append("")
        
        report.append(f"## 분석 신뢰도: {analysis['confidence_score']:.2f}\n")
        
        return "\n".join(report)


# 사용 예제
if __name__ == "__main__":
    annotator = AIAnalysisAnnotator()
    
    # 테스트 데이터
    stats = {
        "total_cells": 1523,
        "avg_cells_per_image": 507.67,
        "avg_cell_area": 245.3,
        "std_cell_area": 125.4,
        "min_cell_area": 50,
        "max_cell_area": 850
    }
    
    patient_info = {
        "cancer_type": "대장암",
        "cancer_stage": "III"
    }
    
    results = [{"num_cells": 500}, {"num_cells": 523}, {"num_cells": 500}]
    
    # 주석 생성
    report = annotator.generate_annotation_report(results, stats, patient_info)
    print(report)
