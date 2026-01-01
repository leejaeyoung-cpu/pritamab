"""
FastAPI Main Application
AI Anticancer Drug Discovery System - Web Version
"""
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
import logging
from typing import List, Optional
from datetime import datetime

# Local imports
from config import settings
from database import get_db, init_db
import db_models
import schemas
from ai_service import get_paper_recommendations, get_ai_recommendations, get_hybrid_recommendations

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered anticancer drug recommendation system with Cellpose integration",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount uploads
uploads_path = settings.UPLOAD_FOLDER
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


# ============ Startup & Shutdown Events ============

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")


# ============ Root Routes ============

@app.get("/")
async def root():
    """Root endpoint - serve index.html or API info"""
    index_file = Path("static/index.html")
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION
    }


# ============ Patient CRUD Routes ============

@app.post("/api/patients", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db)
):
    """환자 생성"""
    try:
        # Check if patient_id already exists
        existing = db.query(db_models.Patient).filter(
            db_models.Patient.patient_id == patient.patient_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Patient with ID {patient.patient_id} already exists"
            )
        
        # Create new patient
        db_patient = db_models.Patient(**patient.model_dump())
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        
        logger.info(f"Created patient: {patient.patient_id}")
        return db_patient
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/patients", response_model=List[schemas.PatientResponse])
async def get_patients(
    skip: int = 0,
    limit: int = 100,
    cancer_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """환자 목록 조회"""
    try:
        query = db.query(db_models.Patient)
        
        if cancer_type:
            query = query.filter(db_models.Patient.cancer_type == cancer_type)
        
        patients = query.offset(skip).limit(limit).all()
        return patients
        
    except Exception as e:
        logger.error(f"Error fetching patients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/patients/{patient_id}", response_model=schemas.PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """특정 환자 조회"""
    patient = db.query(db_models.Patient).filter(db_models.Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    
    return patient


@app.put("/api/patients/{patient_id}", response_model=schemas.PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: schemas.PatientUpdate,
    db: Session = Depends(get_db)
):
    """환자 정보 업데이트"""
    try:
        db_patient = db.query(db_models.Patient).filter(db_models.Patient.id == patient_id).first()
        
        if not db_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )
        
        # Update fields
        update_data = patient_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_patient, key, value)
        
        db.commit()
        db.refresh(db_patient)
        
        logger.info(f"Updated patient: {patient_id}")
        return db_patient
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/api/patients/{patient_id}")
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """환자 삭제"""
    try:
        db_patient = db.query(db_models.Patient).filter(db_models.Patient.id == patient_id).first()
        
        if not db_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {patient_id} not found"
            )
        
        db.delete(db_patient)
        db.commit()
        
        logger.info(f"Deleted patient: {patient_id}")
        return {"message": f"Patient {patient_id} deleted successfully", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting patient: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============ AI Recommendation Routes ============

@app.post("/api/recommendations", response_model=schemas.RecommendationResponse)
async def get_recommendations(
    request: schemas.RecommendationRequest,
    db: Session = Depends(get_db)
):
    """AI 기반 약물 추천 생성"""
    try:
        # Get patient data
        patient = db.query(db_models.Patient).filter(db_models.Patient.id == request.patient_id).first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {request.patient_id} not found"
            )
        
        # Prepare patient data
        patient_data = {
            "age": patient.age,
            "cancer_type": patient.cancer_type,
            "cancer_stage": patient.cancer_stage,
            "molecular_markers": patient.molecular_markers or {},
            "performance_status": patient.performance_status,
            "comorbidities": patient.comorbidities or []
        }
        
        # Generate recommendations
        paper_recs = []
        ai_recs = []
        hybrid_recs = []
        
        if request.include_paper:
            paper_recs = get_paper_recommendations(
                cancer_type=patient.cancer_type,
                therapy_type=request.therapy_type,
                top_n=request.top_n
            )
        
        if request.include_ai:
            ai_recs = get_ai_recommendations(
                patient_data=patient_data,
                therapy_type=request.therapy_type,
                top_n=request.top_n
            )
        
        # Generate hybrid if both are included
        if request.include_paper and request.include_ai:
            hybrid_recs = get_hybrid_recommendations(
                paper_recs=paper_recs,
                ai_recs=ai_recs,
                top_n=request.top_n
            )
        
        response = schemas.RecommendationResponse(
            patient_id=patient.id,
            cancer_type=patient.cancer_type,
            therapy_type=request.therapy_type,
            paper_recommendations=paper_recs,
            ai_recommendations=ai_recs,
            hybrid_recommendations=hybrid_recs,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Generated recommendations for patient {request.patient_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============ Treatment Routes ============

@app.post("/api/treatments", response_model=schemas.TreatmentResponse, status_code=status.HTTP_201_CREATED)
async def create_treatment(
    treatment: schemas.TreatmentCreate,
    db: Session = Depends(get_db)
):
    """치료 기록 생성"""
    try:
        # Verify patient exists
        patient = db.query(db_models.Patient).filter(db_models.Patient.id == treatment.patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient {treatment.patient_id} not found"
            )
        
        db_treatment = db_models.Treatment(**treatment.model_dump())
        db.add(db_treatment)
        db.commit()
        db.refresh(db_treatment)
        
        logger.info(f"Created treatment for patient {treatment.patient_id}")
        return db_treatment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating treatment: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/patients/{patient_id}/treatments", response_model=List[schemas.TreatmentResponse])
async def get_patient_treatments(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """환자의 치료 기록 조회"""
    treatments = db.query(db_models.Treatment).filter(
        db_models.Treatment.patient_id == patient_id
    ).all()
    
    return treatments


# ============ File Upload Route ============

@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    patient_id: Optional[int] = None
):
    """파일 업로드 (이미지, 데이터 등)"""
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Create unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = settings.UPLOAD_FOLDER / safe_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"Uploaded file: {safe_filename}")
        
        return {
            "success": True,
            "filename": safe_filename,
            "path": str(file_path),
            "url": f"/uploads/{safe_filename}",
            "size": len(content)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============ Cellpose Analysis Route ============

@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    patient_id: Optional[int] = None,
    model_type: str = "cyto2",
    db: Session = Depends(get_db)
):
    """Cellpose 이미지 분석"""
    try:
        from cellpose_service import analyze_cell_image, get_analysis_summary
        
        # Upload file first
        upload_result = await upload_file(file, patient_id)
        
        if not upload_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File upload failed"
            )
        
        # Analyze the uploaded image
        file_path = upload_result["path"]
        analysis_results = analyze_cell_image(
            image_path=file_path,
            model_type=model_type
        )
        
        # Save analysis to database if patient_id provided
        if patient_id:
            patient = db.query(db_models.Patient).filter(db_models.Patient.id == patient_id).first()
            if patient:
                db_analysis = db_models.Analysis(
                    patient_id=patient_id,
                    analysis_type="cellpose",
                    image_path=upload_result["url"],
                    cell_count=analysis_results["cell_count"],
                    average_cell_size=analysis_results["average_cell_size"],
                    cell_density=analysis_results["cell_density"],
                    morphology_features=analysis_results["morphology_features"],
                    analysis_params=analysis_results["analysis_params"],
                    result_data=analysis_results
                )
                db.add(db_analysis)
                db.commit()
                db.refresh(db_analysis)
                
                logger.info(f"Saved analysis for patient {patient_id}")
        
        # Generate summary
        summary = get_analysis_summary(analysis_results)
        
        return {
            "success": True,
            "image_url": upload_result["url"],
            "analysis": analysis_results,
            "summary": summary,
            "patient_id": patient_id
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============ Error Handlers ============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
