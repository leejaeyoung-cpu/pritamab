"""
Database Models for AI Anticancer Drug System
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Patient(Base):
    """환자 정보 모델"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    
    # 암 정보
    cancer_type = Column(String(100), nullable=False)
    cancer_stage = Column(String(20))
    diagnosis_date = Column(DateTime)
    
    # 분자 마커
    molecular_markers = Column(JSON)  # {"KRAS": "positive", "BRAF": "negative", ...}
    
    # 환자 상태
    performance_status = Column(String(20))  # ECOG score
    comorbidities = Column(JSON)  # 동반 질환 리스트
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    treatments = relationship("Treatment", back_populates="patient", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.patient_id}, name={self.name}, cancer={self.cancer_type})>"


class Treatment(Base):
    """치료 기록 모델"""
    __tablename__ = "treatments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # 치료 정보
    treatment_type = Column(String(50))  # "1제", "2제", "3제"
    drugs = Column(JSON, nullable=False)  # ["Drug1", "Drug2", ...]
    
    # 추천 정보
    recommendation_source = Column(String(50))  # "AI", "Paper", "Hybrid"
    efficacy_score = Column(Float)
    synergy_score = Column(Float)
    toxicity_score = Column(Float)
    
    # 근거
    evidence_level = Column(String(10))  # "1A", "1B", "2A", etc.
    references = Column(JSON)  # ["PMID: 12345678", ...]
    notes = Column(Text)
    
    # 치료 결과
    response = Column(String(50))  # "Complete Response", "Partial Response", etc.
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    patient = relationship("Patient", back_populates="treatments")
    
    def __repr__(self):
        return f"<Treatment(patient_id={self.patient_id}, drugs={self.drugs})>"


class Analysis(Base):
    """이미지 분석 결과 모델"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    
    # 분석 정보
    analysis_type = Column(String(50))  # "cellpose", "pathology", etc.
    image_path = Column(String(500))
    
    # Cellpose 분석 결과
    cell_count = Column(Integer)
    average_cell_size = Column(Float)
    cell_density = Column(Float)
    morphology_features = Column(JSON)  # 세포 형태학적 특징
    
    # 분석 메타데이터
    analysis_params = Column(JSON)  # 분석 파라미터
    result_data = Column(JSON)  # 전체 분석 결과
    
    # 타임스탬프
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    patient = relationship("Patient", back_populates="analyses")
    
    def __repr__(self):
        return f"<Analysis(patient_id={self.patient_id}, type={self.analysis_type})>"


class User(Base):
    """사용자 인증 모델"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # 사용자 정보
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # "admin", "doctor", "researcher", "user"
    is_active = Column(Boolean, default=True)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"


class DrugRecommendation(Base):
    """약물 추천 캐시 (성능 최적화)"""
    __tablename__ = "drug_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 추천 키
    cancer_type = Column(String(100), index=True)
    therapy_type = Column(String(50))  # "1제", "2제", "3제"
    molecular_profile = Column(JSON)  # 분자 마커 프로필
    
    # 추천 결과
    recommended_drugs = Column(JSON)
    efficacy = Column(Float)
    synergy = Column(Float)
    toxicity = Column(Float)
    evidence = Column(String(10))
    references = Column(JSON)
    
    # 캐시 관리
    cache_key = Column(String(255), unique=True, index=True)
    hit_count = Column(Integer, default=0)
    
    # 타임스탬프
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<DrugRecommendation(cancer={self.cancer_type}, therapy={self.therapy_type})>"
