"""
환자 정보 관리 모듈
환자 프로필 생성, 저장, 조회 기능 제공
"""

import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime
import json
import logging

# UTF-8 인코딩 설정 (Windows)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PatientProfile:
    """환자 프로필 데이터 클래스"""
    
    # 기본 정보
    patient_id: str
    name: str
    age: int
    gender: str  # '남성', '여성'
    
    # 진단 정보
    cancer_type: str  # '대장암', '폐암', '유방암', '위암', '간암' 등
    cancer_stage: str  # 'I', 'II', 'III', 'IV'
    diagnosis_date: str
    
    # 의료 정보
    previous_treatments: List[str]  # 이전 치료 이력
    current_medications: List[str]  # 현재 복용 중인 약물
    allergies: List[str]  # 알레르기
    
    # 검사 결과
    ecog_score: Optional[int] = None  # ECOG 수행 상태 점수 (0-5)
    biomarkers: Optional[Dict] = None  # 바이오마커 정보
    
    # 메타 정보
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """초기화 후 처리"""
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        if self.biomarkers is None:
            self.biomarkers = {}
    
    def to_dict(self) -> Dict:
        """딕셔너리로 변환"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PatientProfile':
        """딕셔너리에서 생성"""
        return cls(**data)
    
    def update(self, **kwargs):
        """프로필 업데이트"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()


class PatientManager:
    """환자 관리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.patients: Dict[str, PatientProfile] = {}
        logger.info("환자 관리자 초기화 완료")
    
    def add_patient(self, profile: PatientProfile) -> bool:
        """
        환자 추가
        
        Args:
            profile: 환자 프로필
            
        Returns:
            성공 여부
        """
        if profile.patient_id in self.patients:
            logger.warning(f"이미 존재하는 환자 ID: {profile.patient_id}")
            return False
        
        self.patients[profile.patient_id] = profile
        logger.info(f"환자 추가: {profile.name} (ID: {profile.patient_id})")
        return True
    
    def get_patient(self, patient_id: str) -> Optional[PatientProfile]:
        """
        환자 조회
        
        Args:
            patient_id: 환자 ID
            
        Returns:
            환자 프로필 또는 None
        """
        return self.patients.get(patient_id)
    
    def update_patient(self, patient_id: str, **kwargs) -> bool:
        """
        환자 정보 업데이트
        
        Args:
            patient_id: 환자 ID
            **kwargs: 업데이트할 필드
            
        Returns:
            성공 여부
        """
        patient = self.get_patient(patient_id)
        if patient is None:
            logger.error(f"환자를 찾을 수 없음: {patient_id}")
            return False
        
        patient.update(**kwargs)
        logger.info(f"환자 정보 업데이트: {patient_id}")
        return True
    
    def delete_patient(self, patient_id: str) -> bool:
        """
        환자 삭제
        
        Args:
            patient_id: 환자 ID
            
        Returns:
            성공 여부
        """
        if patient_id not in self.patients:
            logger.error(f"환자를 찾을 수 없음: {patient_id}")
            return False
        
        del self.patients[patient_id]
        logger.info(f"환자 삭제: {patient_id}")
        return True
    
    def get_all_patients(self) -> List[PatientProfile]:
        """
        모든 환자 목록 조회
        
        Returns:
            환자 프로필 리스트
        """
        return list(self.patients.values())
    
    def filter_by_cancer_type(self, cancer_type: str) -> List[PatientProfile]:
        """
        암종별 환자 필터링
        
        Args:
            cancer_type: 암 종류
            
        Returns:
            필터링된 환자 리스트
        """
        return [p for p in self.patients.values() if p.cancer_type == cancer_type]
    
    def filter_by_stage(self, stage: str) -> List[PatientProfile]:
        """
        병기별 환자 필터링
        
        Args:
            stage: 병기 (I, II, III, IV)
            
        Returns:
            필터링된 환자 리스트
        """
        return [p for p in self.patients.values() if p.cancer_stage == stage]
    
    def get_patient_count(self) -> int:
        """총 환자 수 반환"""
        return len(self.patients)
    
    def export_to_json(self, filepath: str):
        """
        환자 데이터를 JSON 파일로 저장
        
        Args:
            filepath: 저장 경로
        """
        data = {
            patient_id: profile.to_dict() 
            for patient_id, profile in self.patients.items()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"환자 데이터 저장 완료: {filepath}")
    
    def import_from_json(self, filepath: str):
        """
        JSON 파일에서 환자 데이터 불러오기
        
        Args:
            filepath: 파일 경로
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for patient_id, patient_data in data.items():
                profile = PatientProfile.from_dict(patient_data)
                self.patients[patient_id] = profile
            
            logger.info(f"환자 데이터 불러오기 완료: {filepath} ({len(data)}명)")
        except Exception as e:
            logger.error(f"환자 데이터 불러오기 실패: {e}")
            raise


def test_patient_manager():
    """테스트 함수"""
    print("=" * 80)
    print("환자 관리 모듈 테스트")
    print("=" * 80)
    
    # 환자 관리자 생성
    manager = PatientManager()
    
    # 테스트 환자 추가
    patient1 = PatientProfile(
        patient_id="P001",
        name="김철수",
        age=65,
        gender="남성",
        cancer_type="대장암",
        cancer_stage="III",
        diagnosis_date="2024-01-15",
        previous_treatments=["수술"],
        current_medications=["진통제"],
        allergies=[],
        ecog_score=1,
        notes="정기 검진 필요"
    )
    
    patient2 = PatientProfile(
        patient_id="P002",
        name="이영희",
        age=58,
        gender="여성",
        cancer_type="유방암",
        cancer_stage="II",
        diagnosis_date="2024-02-20",
        previous_treatments=["방사선치료"],
        current_medications=["타목시펜"],
        allergies=["페니실린"],
        ecog_score=0
    )
    
    # 환자 추가
    manager.add_patient(patient1)
    manager.add_patient(patient2)
    
    print(f"\n총 환자 수: {manager.get_patient_count()}")
    
    # 환자 조회
    print("\n환자 조회:")
    p = manager.get_patient("P001")
    if p:
        print(f"  이름: {p.name}, 나이: {p.age}, 암종: {p.cancer_type}, 병기: {p.cancer_stage}")
    
    # 암종별 필터링
    print("\n대장암 환자:")
    colon_patients = manager.filter_by_cancer_type("대장암")
    for p in colon_patients:
        print(f"  - {p.name} ({p.patient_id})")
    
    print("\n[OK] 환자 관리 모듈 테스트 완료")
    print("=" * 80)


if __name__ == "__main__":
    test_patient_manager()
