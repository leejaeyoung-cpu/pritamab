"""
데이터 처리 및 관리 모듈
엑셀 파일 처리, 약물 데이터 관리
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """데이터 처리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.drug_data = None
        self.cell_data = None
        self.analysis_results = {}
    
    def load_drug_data(self, excel_path: str) -> pd.DataFrame:
        """
        약물 데이터 로드
        
        Args:
            excel_path: 엑셀 파일 경로
            
        Returns:
            DataFrame
        """
        logger.info(f"Loading drug data from: {excel_path}")
        
        try:
            df = pd.read_excel(excel_path)
            self.drug_data = df
            logger.info(f"  Loaded {len(df)} rows")
            logger.info(f"  Columns: {list(df.columns)}")
            return df
        except Exception as e:
            logger.error(f"Failed to load drug data: {e}")
            raise
    
    def load_cell_line_data(self, excel_path: str) -> pd.DataFrame:
        """
        세포주 데이터 로드
        
        Args:
            excel_path: 엑셀 파일 경로
            
        Returns:
            DataFrame
        """
        logger.info(f"Loading cell line data from: {excel_path}")
        
        try:
            df = pd.read_excel(excel_path)
            self.cell_data = df
            logger.info(f"  Loaded {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Failed to load cell line data: {e}")
            raise
    
    def combine_image_and_drug_data(
        self,
        cellpose_results: List[Dict],
        drug_info: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Cellpose 분석 결과와 약물 정보 결합
        
        Args:
            cellpose_results: Cellpose 분석 결과 리스트
            drug_info: 약물 정보 DataFrame
            
        Returns:
            결합된 DataFrame
        """
        logger.info("Combining image analysis and drug data...")
        
        # Cellpose 결과를 DataFrame으로 변환
        data_list = []
        for result in cellpose_results:
            image_name = Path(result['image_path']).stem
            
            data_list.append({
                'image_name': image_name,
                'image_path': result['image_path'],
                'num_cells': result['num_cells'],
                'avg_cell_area': np.mean([c['area'] for c in result['cell_properties']]) if result['cell_properties'] else 0
            })
        
        df_cells = pd.DataFrame(data_list)
        
        # 약물 정보와 결합 (이미지 이름 기준)
        # 실제 프로젝트에서는 매칭 로직을 커스터마이즈해야 함
        combined_df = df_cells
        
        logger.info(f"  Combined data shape: {combined_df.shape}")
        return combined_df
    
    def calculate_efficacy_metrics(
        self,
        control_data: pd.DataFrame,
        treatment_data: pd.DataFrame
    ) -> Dict:
        """
        약효 지표 계산
        
        Args:
            control_data: 대조군 데이터
            treatment_data: 처리군 데이터
            
        Returns:
            지표 딕셔너리
        """
        logger.info("Calculating efficacy metrics...")
        
        control_cells = control_data['num_cells'].mean()
        treatment_cells = treatment_data['num_cells'].mean()
        
        # 세포 성장 억제율 계산
        inhibition_rate = ((control_cells - treatment_cells) / control_cells * 100) if control_cells > 0 else 0
        
        metrics = {
            'control_avg_cells': control_cells,
            'treatment_avg_cells': treatment_cells,
            'inhibition_rate': inhibition_rate,
            'cell_count_ratio': treatment_cells / control_cells if control_cells > 0 else 0
        }
        
        logger.info(f"  Inhibition rate: {inhibition_rate:.2f}%")
        return metrics
    
    def export_results(
        self,
        data: pd.DataFrame,
        output_path: str
    ):
        """
        결과를 엑셀로 export
        
        Args:
            data: DataFrame
            output_path: 출력 파일 경로
        """
        logger.info(f"Exporting results to: {output_path}")
        
        try:
            data.to_excel(output_path, index=False)
            logger.info("  Export successful")
        except Exception as e:
            logger.error(f"Failed to export: {e}")
            raise


class DrugCombinationAnalyzer:
    """약물 조합 분석 클래스"""
    
    def __init__(self):
        """초기화"""
        self.combinations = []
    
    def generate_combinations(
        self,
        drugs: List[str],
        combination_size: int = 2
    ) -> List[Tuple]:
        """
        약물 조합 생성
        
        Args:
            drugs: 약물 리스트
            combination_size: 조합 크기 (2: 2제, 3: 3제)
            
        Returns:
            조합 리스트
        """
        from itertools import combinations
        
        combs = list(combinations(drugs, combination_size))
        self.combinations = combs
        
        logger.info(f"Generated {len(combs)} combinations of size {combination_size}")
        return combs
    
    def score_combination(
        self,
        combination: Tuple[str],
        efficacy_data: Dict
    ) -> float:
        """
        조합 점수 계산
        
        Args:
            combination: 약물 조합
            efficacy_data: 효능 데이터
            
        Returns:
            점수
        """
        # 간단한 점수 계산 로직
        # 실제로는 더 복잡한 모델 사용 가능
        score = 0.0
        
        for drug in combination:
            if drug in efficacy_data:
                score += efficacy_data[drug].get('inhibition_rate', 0)
        
        # 시너지 효과 가정 (간단한 예시)
        if len(combination) > 1:
            score *= 1.2  # 20% 시너지 보너스
        
        return score
    
    def rank_combinations(
        self,
        combinations: List[Tuple],
        efficacy_data: Dict
    ) -> pd.DataFrame:
        """
        조합 순위 매기기
        
        Args:
            combinations: 약물 조합 리스트
            efficacy_data: 효능 데이터
            
        Returns:
            순위 DataFrame
        """
        results = []
        
        for comb in combinations:
            score = self.score_combination(comb, efficacy_data)
            results.append({
                'combination': ' + '.join(comb),
                'drugs': comb,
                'score': score
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('score', ascending=False).reset_index(drop=True)
        df['rank'] = range(1, len(df) + 1)
        
        return df


def test_data_processor():
    """테스트 함수"""
    print("="*80)
    print("Data Processor Test")
    print("="*80)
    
    processor = DataProcessor()
    print("\n[OK] Data Processor initialization successful")
    
    analyzer = DrugCombinationAnalyzer()
    drugs = ['Drug A', 'Drug B', 'Drug C', 'Drug D']
    combs = analyzer.generate_combinations(drugs, combination_size=2)
    print(f"\nGenerated 2-drug combinations: {len(combs)}")
    for c in combs[:5]:
        print(f"  - {' + '.join(c)}")
    
    print("="*80)


if __name__ == "__main__":
    test_data_processor()
