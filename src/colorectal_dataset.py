"""
대장암 데이터셋 파서 및 프로그램 통합
JSON 데이터를 프로그램에서 사용할 수 있도록 로드
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

class ColorectalCancerDataset:
    """대장암 항암제 및 시그널 패스웨이 데이터셋"""
    
    def __init__(self, dataset_path: Optional[str] = None):
        if dataset_path is None:
            dataset_path = Path(__file__).parent.parent / "data" / "colorectal_cancer_dataset.json"
        
        self.dataset_path = Path(dataset_path)
        self.data = self.load_dataset()
    
    def load_dataset(self) -> Dict:
        """데이터셋 로드"""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"데이터셋 파일을 찾을 수 없습니다: {self.dataset_path}")
            return self._get_empty_dataset()
    
    def _get_empty_dataset(self) -> Dict:
        """빈 데이터셋 구조"""
        return {
            "dataset_info": {},
            "drugs": [],
            "signaling_pathways": [],
            "drug_combinations": [],
            "biomarkers": []
        }
    
    def get_drug(self, drug_name: str) -> Optional[Dict]:
        """약물 정보 조회"""
        for drug in self.data.get('drugs', []):
            if drug['name'].lower() == drug_name.lower() or \
               drug.get('abbreviation', '').lower() == drug_name.lower():
                return drug
        return None
    
    def get_drugs_by_pathway(self, pathway_name: str) -> List[Dict]:
        """특정 경로를 표적하는 약물 조회"""
        pathway = self.get_pathway(pathway_name)
        if not pathway:
            return []
        
        targeted_drugs = pathway.get('targeted_drugs', [])
        return [self.get_drug(name) for name in targeted_drugs if self.get_drug(name)]
    
    def get_pathway(self, pathway_name: str) -> Optional[Dict]:
        """시그널 패스웨이 정보 조회"""
        for pathway in self.data.get('signaling_pathways', []):
            if pathway['name'].lower() == pathway_name.lower():
                return pathway
        return None
    
    def get_combination(self, combo_name: str) -> Optional[Dict]:
        """약물 조합 정보 조회"""
        for combo in self.data.get('drug_combinations', []):
            if combo['name'].lower() == combo_name.lower():
                return combo
        return None
    
    def get_biomarker(self, biomarker_name: str) -> Optional[Dict]:
        """바이오마커 정보 조회"""
        for marker in self.data.get('biomarkers', []):
            if marker['name'].lower() == biomarker_name.lower():
                return marker
        return None
    
    def get_all_drugs(self) -> List[Dict]:
        """모든 약물 정보"""
        return self.data.get('drugs', [])
    
    def get_all_pathways(self) -> List[Dict]:
        """모든 시그널 패스웨이"""
        return self.data.get('signaling_pathways', [])
    
    def get_all_combinations(self) -> List[Dict]:
        """모든 약물 조합"""
        return self.data.get('drug_combinations', [])
    
    def search_by_biomarker(self, biomarker: str, status: str) -> List[Dict]:
        """
        바이오마커 상태에 따른 약물 추천
        
        Args:
            biomarker: 바이오마커 이름 (예: "KRAS")
            status: 상태 (예: "mutant", "wild-type")
        
        Returns:
            추천 약물 리스트
        """
        marker_info = self.get_biomarker(biomarker)
        if not marker_info:
            return []
        
        therapeutics_impact = marker_info.get('therapeutics_impact', {})
        recommended_drugs = []
        
        for drug_name, impact in therapeutics_impact.items():
            if status.lower() in impact.lower():
                drug = self.get_drug(drug_name)
                if drug:
                    recommended_drugs.append(drug)
        
        return recommended_drugs
    
    def to_dataframe(self, data_type: str) -> pd.DataFrame:
        """
        데이터를 DataFrame으로 변환
        
        Args:
            data_type: 'drugs', 'pathways', 'combinations', 'biomarkers'
        """
        if data_type == 'drugs':
            return pd.DataFrame(self.get_all_drugs())
        elif data_type == 'pathways':
            return pd.DataFrame(self.get_all_pathways())
        elif data_type == 'combinations':
            return pd.DataFrame(self.get_all_combinations())
        elif data_type == 'biomarkers':
            return pd.DataFrame(self.data.get('biomarkers', []))
        else:
            raise ValueError(f"Unknown data type: {data_type}")
    
    def get_statistics(self) -> Dict:
        """데이터셋 통계"""
        return {
            'total_drugs': len(self.get_all_drugs()),
            'total_pathways': len(self.get_all_pathways()),
            'total_combinations': len(self.get_all_combinations()),
            'total_biomarkers': len(self.data.get('biomarkers', [])),
            'drug_categories': self._count_drug_categories(),
            'pathway_alterations': self._count_pathway_alterations()
        }
    
    def _count_drug_categories(self) -> Dict[str, int]:
        """약물 카테고리별 개수"""
        categories = {}
        for drug in self.get_all_drugs():
            category = drug.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _count_pathway_alterations(self) -> Dict[str, int]:
        """패스웨이 변이 빈도"""
        alterations = {}
        for pathway in self.get_all_pathways():
            name = pathway['name']
            freq = pathway.get('alterations', {}).get('frequency', 0)
            alterations[name] = freq
        return alterations


def example_usage():
    """사용 예시"""
    # 데이터셋 로드
    dataset = ColorectalCancerDataset()
    
    # 약물 조회
    folfox = dataset.get_combination('FOLFOX')
    print(f"FOLFOX 정보: {folfox['drugs']}")
    print(f"효능: {folfox['efficacy']}")
    
    # 바이오마커 기반 추천
    kras_wt_drugs = dataset.search_by_biomarker('KRAS', 'wild-type')
    print(f"KRAS wild-type 환자에게 적합한 약물: {[d['name'] for d in kras_wt_drugs]}")
    
    # 통계
    stats = dataset.get_statistics()
    print(f"데이터셋 통계: {stats}")
    
    # DataFrame 변환
    drugs_df = dataset.to_dataframe('drugs')
    print(f"약물 데이터프레임:\n{drugs_df[['name', 'category', 'efficacy']]}")


if __name__ == "__main__":
    example_usage()
