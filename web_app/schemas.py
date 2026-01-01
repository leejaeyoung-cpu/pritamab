"""
Pydantic Schemas for Request/Response Validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============ Patient Schemas ============

class PatientBase(BaseModel):
    """기본 환자 정보"""
    patient_id: str = Field(..., description="고유 환자 ID")
    name: str = Field(..., description="환자 이름")
    age: Optional[int] = Field(None, ge=0, le=150, description="나이")
    gender: Optional[str] = Field(None, description="성별")
    cancer_type: str = Field(..., description="암 종류")
    cancer_stage: Optional[str] = Field(None, description="암 병기")
    diagnosis_date: Optional[datetime] = Field(None, description="진단 날짜")
    molecular_markers: Optional[Dict[str, str]] = Field(None, description="분자 마커")
    performance_status: Optional[str] = Field(None, description="ECOG 상태")
    comorbidities: Optional[List[str]] = Field(None, description="동반 질환")


class PatientCreate(PatientBase):
    """환자 생성 요청"""
    pass


class PatientUpdate(BaseModel):
    """환자 정보 업데이트"""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    cancer_type: Optional[str] = None
    cancer_stage: Optional[str] = None
    molecular_markers: Optional[Dict[str, str]] = None
    performance_status: Optional[str] = None
    comorbidities: Optional[List[str]] = None


class PatientResponse(PatientBase):
    """환자 정보 응답"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Treatment Schemas ============

class TreatmentBase(BaseModel):
    """기본 치료 정보"""
    treatment_type: str = Field(..., description="치료 유형 (1제, 2제, 3제)")
    drugs: List[str] = Field(..., description="약물 리스트")
    recommendation_source: Optional[str] = Field(None, description="추천 출처")
    efficacy_score: Optional[float] = Field(None, ge=0, le=1)
    synergy_score: Optional[float] = Field(None, ge=0)
    toxicity_score: Optional[float] = Field(None, ge=0, le=10)
    evidence_level: Optional[str] = Field(None)
    references: Optional[List[str]] = Field(None)
    notes: Optional[str] = Field(None)


class TreatmentCreate(TreatmentBase):
    """치료 기록 생성"""
    patient_id: int


class TreatmentResponse(TreatmentBase):
    """치료 기록 응답"""
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============ Analysis Schemas ============

class AnalysisBase(BaseModel):
    """기본 분석 정보"""
    analysis_type: str = Field(..., description="분석 유형")
    image_path: str = Field(..., description="이미지 경로")
    cell_count: Optional[int] = Field(None)
    average_cell_size: Optional[float] = Field(None)
    cell_density: Optional[float] = Field(None)
    morphology_features: Optional[Dict[str, Any]] = Field(None)
    analysis_params: Optional[Dict[str, Any]] = Field(None)
    result_data: Optional[Dict[str, Any]] = Field(None)


class AnalysisCreate(AnalysisBase):
    """분석 생성"""
    patient_id: int


class AnalysisResponse(AnalysisBase):
    """분석 응답"""
    id: int
    patient_id: int
    analyzed_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ AI Recommendation Schemas ============

class RecommendationRequest(BaseModel):
    """AI 추천 요청"""
    patient_id: int
    therapy_type: str = Field(..., description="1제, 2제, 3제")
    top_n: int = Field(5, ge=1, le=20, description="상위 N개 추천")
    include_paper: bool = Field(True, description="논문 기반 추천 포함")
    include_ai: bool = Field(True, description="AI 기반 추천 포함")


class DrugCombination(BaseModel):
    """약물 조합"""
    drugs: List[str]
    efficacy: float
    synergy: float
    toxicity: float
    evidence: str
    references: List[str]
    notes: str
    score: float  # 종합 점수


class RecommendationResponse(BaseModel):
    """AI 추천 응답"""
    patient_id: int
    cancer_type: str
    therapy_type: str
    paper_recommendations: List[DrugCombination]
    ai_recommendations: List[DrugCombination]
    hybrid_recommendations: List[DrugCombination]
    timestamp: datetime


# ============ Cellpose Analysis Schemas ============

class CellposeRequest(BaseModel):
    """Cellpose 분석 요청"""
    patient_id: Optional[int] = None
    model_type: str = Field("cyto2", description="Cellpose 모델")
    diameter: Optional[float] = Field(None, description="예상 세포 직경")
    channels: List[int] = Field([0, 0], description="채널 설정")


class CellposeResponse(BaseModel):
    """Cellpose 분석 결과"""
    success: bool
    analysis_id: Optional[int] = None
    cell_count: int
    average_size: float
    cell_density: float
    features: Dict[str, Any]
    image_url: str
    labeled_image_url: str
    timestamp: datetime


# ============ User Schemas ============

class UserBase(BaseModel):
    """기본 사용자 정보"""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "user"


class UserCreate(UserBase):
    """사용자 생성"""
    password: str


class UserResponse(UserBase):
    """사용자 응답"""
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """인증 토큰"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """토큰 데이터"""
    username: Optional[str] = None


# ============ Generic Responses ============

class MessageResponse(BaseModel):
    """일반 메시지 응답"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """에러 응답"""
    error: str
    detail: Optional[str] = None
    success: bool = False
