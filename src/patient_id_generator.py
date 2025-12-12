"""
환자 ID 자동 생성 유틸리티
날짜 + 순서 형식으로 자동 생성 (예: 20241202-001)
"""

from datetime import datetime
from pathlib import Path
import json


class PatientIDGenerator:
    """환자 ID 자동 생성 클래스"""
    
    def __init__(self, data_dir: str = None):
        """
        초기화
        
        Args:
            data_dir: 데이터 디렉토리 (기본: ./data)
        """
        if data_dir is None:
            self.data_dir = Path.cwd() / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.counter_file = self.data_dir / "patient_id_counter.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 카운터 파일 초기화
        if not self.counter_file.exists():
            self._save_counter({})
    
    def _load_counter(self) -> dict:
        """카운터 로드"""
        try:
            with open(self.counter_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_counter(self, counter: dict):
        """카운터 저장"""
        with open(self.counter_file, 'w', encoding='utf-8') as f:
            json.dump(counter, f, ensure_ascii=False, indent=2)
    
    def generate_patient_id(self, date: datetime = None) -> str:
        """
        환자 ID 생성
        
        Args:
            date: 날짜 (기본: 오늘)
        
        Returns:
            환자 ID (예: 20241202-001)
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y%m%d")
        
        # 오늘 날짜의 카운터 로드
        counter = self._load_counter()
        
        # 오늘 날짜의 현재 번호
        current_num = counter.get(date_str, 0)
        
        # 다음 번호
        next_num = current_num + 1
        
        # 업데이트
        counter[date_str] = next_num
        self._save_counter(counter)
        
        # ID 생성 (3자리 숫자)
        patient_id = f"{date_str}-{next_num:03d}"
        
        return patient_id
    
    def get_today_count(self) -> int:
        """오늘 등록된 환자 수"""
        date_str = datetime.now().strftime("%Y%m%d")
        counter = self._load_counter()
        return counter.get(date_str, 0)
    
    def get_total_count(self) -> int:
        """전체 등록된 환자 수"""
        counter = self._load_counter()
        return sum(counter.values())
    
    def reset_counter(self, date_str: str = None):
        """
        특정 날짜의 카운터 리셋
        
        Args:
            date_str: 날짜 문자열 (YYYYMMDD, None이면 오늘)
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y%m%d")
        
        counter = self._load_counter()
        if date_str in counter:
            del counter[date_str]
            self._save_counter(counter)


# 전역 인스턴스
_generator = None

def get_generator():
    """전역 generator 인스턴스 가져오기"""
    global _generator
    if _generator is None:
        _generator = PatientIDGenerator()
    return _generator


def generate_new_patient_id() -> str:
    """
    새 환자 ID 생성 (간편 함수)
    
    Returns:
        환자 ID (예: 20241202-001)
    """
    generator = get_generator()
    return generator.generate_patient_id()


# 사용 예제
if __name__ == "__main__":
    generator = PatientIDGenerator()
    
    print("환자 ID 자동 생성 테스트")
    print("=" * 50)
    
    # 새 ID 생성
    for i in range(5):
        patient_id = generator.generate_patient_id()
        print(f"생성된 ID {i+1}: {patient_id}")
    
    print()
    print(f"오늘 등록 환자 수: {generator.get_today_count()}")
    print(f"전체 등록 환자 수: {generator.get_total_count()}")
