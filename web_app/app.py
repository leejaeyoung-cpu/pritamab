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
from contextlib import asynccontextmanager

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

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down application")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered anticancer drug recommendation system with Cellpose integration",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
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
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Mount uploads  
uploads_path = settings.UPLOAD_FOLDER
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")





# ============ Root Routes ============

@app.get("/")
async def root():
    """Root endpoint - serve index.html or API info"""
    from fastapi.responses import HTMLResponse
    import os
    
    # Try to find index.html
    possible_paths = [
        "static/index.html",
        "./static/index.html",
        os.path.join(os.getcwd(), "static", "index.html")
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return HTMLResponse(content=f.read())
    
    return {
        "message": "GAP AI System Backend v2.0 (Database-enabled) is running",
        "error": "index.html not found"
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
    """?섏옄 ?앹꽦"""
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
    """?섏옄 紐⑸줉 議고쉶"""
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
    """?뱀젙 ?섏옄 議고쉶"""
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
    """?섏옄 ?뺣낫 ?낅뜲?댄듃"""
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
    """?섏옄 ??젣"""
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
    """AI 湲곕컲 ?쎈Ъ 異붿쿇 ?앹꽦"""
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
    """移섎즺 湲곕줉 ?앹꽦"""
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
    """?섏옄??移섎즺 湲곕줉 議고쉶"""
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
    """?뚯씪 ?낅줈??(?대?吏, ?곗씠????"""
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
    """Cellpose ?대?吏 遺꾩꽍 (?명룷 ?곹깭 遺꾩꽍 ?ы븿)"""
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
        
        # Extract cell state from results
        cell_state = analysis_results.get("cell_state", {})
        
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
                    result_data=analysis_results,
                    # === NEW: Save cell state analysis ===
                    cell_state_analysis=cell_state,
                    stress_score=cell_state.get("stress", {}).get("stress_score"),
                    apoptosis_score=cell_state.get("apoptosis", {}).get("apoptosis_score"),
                    health_score=cell_state.get("health", {}).get("health_score"),
                    population_distribution=cell_state.get("population", {})
                )
                db.add(db_analysis)
                db.commit()
                db.refresh(db_analysis)
                
                logger.info(f"Saved analysis for patient {patient_id} with cell state")
        
        # Generate summary
        summary = get_analysis_summary(analysis_results)
        
        # Add cell state summary if available
        if cell_state and cell_state.get("summary"):
            summary += "\n\n" + cell_state["summary"]
        
        return {
            "success": True,
            "image_url": upload_result["url"],
            "analysis": analysis_results,
            "summary": summary,
            "patient_id": patient_id,
            "cell_state": cell_state  # NEW: Include cell state in response
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


# ============== BATCH ANALYSIS API (?섎즺??寃利??ы븿) ==============

@app.post("/api/analyze-images-batch")
async def analyze_images_batch(
    files: List[UploadFile] = File(...),
    patient_id: Optional[int] = None,
    model_type: str = "cyto2",
    diameter: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """?ㅼ쨷 ?대?吏 諛곗튂 遺꾩꽍 (?섎즺 ?곗씠??寃利??ы븿)"""
    try:
        from cellpose_service import batch_analyze_images, calculate_batch_statistics
        import json
        
        logger.info(f"Batch analysis: {len(files)} images")
        
        if len(files) == 0:
            raise HTTPException(400, "No files provided")
        if len(files) > 50:
            raise HTTPException(400, "Maximum 50 files")
        
        # ?섏옄 ?뺤씤
        patient = None
        if patient_id:
            patient = db.query(db_models.Patient).filter(db_models.Patient.id == patient_id).first()
            if not patient:
                raise HTTPException(404, f"Patient {patient_id} not found")
        
        # ?뚯씪 ?낅줈??        upload_dir = Path(settings.UPLOAD_FOLDER)
        upload_dir.mkdir(parents=True, exist_ok=True)
        mask_dir = upload_dir / "masks"
        mask_dir.mkdir(exist_ok=True)
        
        uploaded_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for idx, file in enumerate(files):
            safe_filename = f"{timestamp}_{idx}_{Path(file.filename).name}"
            file_path = upload_dir / safe_filename
            
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            
            uploaded_files.append({
                'original_name': file.filename,
                'path': str(file_path),
                'url': f"/uploads/{safe_filename}"
            })
        
        # 諛곗튂 遺꾩꽍
        image_paths = [f['path'] for f in uploaded_files]
        analysis_results = batch_analyze_images(
            image_paths=image_paths,
            model_type=model_type,
            diameter=diameter if diameter and diameter > 0 else None,
            output_dir=str(mask_dir)
        )
        
        statistics = calculate_batch_statistics(analysis_results)
        
        # DB ???        db_analyses = []
        for idx, (result, file_info) in enumerate(zip(analysis_results, uploaded_files)):
            if 'error' not in result:
                # Extract cell state
                cell_state = result.get('cell_state', {})
                
                db_analysis = db_models.Analysis(
                    patient_id=patient_id,
                    analysis_type="cellpose",
                    image_path=file_info['url'],
                    mask_image_path=f"/uploads/masks/{Path(result.get('mask_image_path', '')).name}" if result.get('mask_image_path') else None,
                    cell_count=result['cell_count'],
                    average_cell_size=result['average_cell_size'],
                    cell_density=result['cell_density'],
                    morphology_features=result['morphology_features'],
                    analysis_params=result['analysis_params'],
                    result_data=json.dumps(result, default=str),
                    # === NEW: Cell state ===
                    cell_state_analysis=cell_state,
                    stress_score=cell_state.get('stress', {}).get('stress_score'),
                    apoptosis_score=cell_state.get('apoptosis', {}).get('apoptosis_score'),
                    health_score=cell_state.get('health', {}).get('health_score'),
                    population_distribution=cell_state.get('population', {})
                )
                db.add(db_analysis)
                db_analyses.append(db_analysis)
        
        db.commit()
        for analysis in db_analyses:
            db.refresh(analysis)
        
        # ?묐떟
        formatted_results = []
        for idx, (result, file_info) in enumerate(zip(analysis_results, uploaded_files)):
            cell_state = result.get('cell_state', {})
            formatted_results.append({
                'index': idx,
                'filename': file_info['original_name'],
                'image_url': file_info['url'],
                'mask_url': f"/uploads/masks/{Path(result.get('mask_image_path', '')).name}" if result.get('mask_image_path') else None,
                'analysis': {
                    'cell_count': result.get('cell_count', 0),
                    'average_cell_size': result.get('average_cell_size', 0),
                    'cell_density': result.get('cell_density', 0),
                    'size_distribution': result.get('size_distribution', {}),
                    'morphology_features': result.get('morphology_features', {})
                },
                # === NEW: Include cell state ===
                'cell_state': {
                    'health_score': cell_state.get('health', {}).get('health_score', 0),
                    'stress_score': cell_state.get('stress', {}).get('stress_score', 0),
                    'apoptosis_score': cell_state.get('apoptosis', {}).get('apoptosis_score', 0),
                    'population': cell_state.get('population', {})
                }
            })
        
        return {
            'success': True,
            'patient_id': patient_id,
            'results': formatted_results,
            'statistics': statistics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        db.rollback()
        raise HTTPException(500, str(e))


@app.post("/api/save-to-ai-dataset")
async def save_to_ai_dataset(
    analysis_ids: List[int],
    db: Session = Depends(get_db)
):
    """遺꾩꽍 寃곌낵瑜?AI ?숈뒿 ?곗씠?곗뀑?쇰줈 ???""
    try:
        import shutil
        import json
        
        if not analysis_ids:
            raise HTTPException(400, "No IDs")
        
        analyses = db.query(db_models.Analysis).filter(
            db_models.Analysis.id.in_(analysis_ids)
        ).all()
        
        if not analyses:
            raise HTTPException(404, "No analyses found")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        batch_dir = Path(f"dataset/training_data/cellpose_analysis/batch_{timestamp}")
        
        (batch_dir / "images").mkdir(parents=True, exist_ok=True)
        (batch_dir / "masks").mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        for analysis in analyses:
            try:
                if analysis.image_path:
                    src = Path(settings.UPLOAD_FOLDER) / Path(analysis.image_path).name
                    if src.exists():
                        shutil.copy2(src, batch_dir / "images" / src.name)
                
                if analysis.mask_image_path:
                    src = Path(settings.UPLOAD_FOLDER) / "masks" / Path(analysis.mask_image_path).name
                    if src.exists():
                        shutil.copy2(src, batch_dir / "masks" / src.name)
                
                saved_count += 1
            except Exception as e:
                logger.error(f"Copy error: {e}")
        
        metadata = {
            'timestamp': timestamp,
            'count': len(analyses),
            'saved': saved_count,
            'cells': sum(a.cell_count or 0 for a in analyses)
        }
        
        with open(batch_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {'success': True, 'batch_dir': str(batch_dir), 'saved': saved_count}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dataset save error: {e}")
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
