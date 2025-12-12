"""
이미지 및 파일 저장 관리 모듈
Cellpose 이미지, 마스크, 원본 파일을 체계적으로 저장
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import json
import numpy as np
from PIL import Image


class FileStorageManager:
    """파일 저장 관리 클래스"""
    
    def __init__(self, base_dir: str = None):
        """
        초기화
        
        Args:
            base_dir: 기본 저장 디렉토리 (기본: ./data/files)
        """
        if base_dir is None:
            self.base_dir = Path.cwd() / "data" / "files"
        else:
            self.base_dir = Path(base_dir)
        
        # 하위 디렉토리
        self.images_dir = self.base_dir / "images"
        self.masks_dir = self.base_dir / "masks"
        self.documents_dir = self.base_dir / "documents"
        
        # 디렉토리 생성
        for dir_path in [self.images_dir, self.masks_dir, self.documents_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def save_cellpose_images(
        self,
        patient_id: str,
        uploaded_files: List,
        cellpose_results: List[Dict],
        timestamp: datetime = None
    ) -> Dict[str, List[str]]:
        """
        Cellpose 분석 이미지 저장
        
        Args:
            patient_id: 환자 ID
            uploaded_files: 업로드된 파일 리스트
            cellpose_results: Cellpose 분석 결과
            timestamp: 타임스탬프
        
        Returns:
            저장된 파일 경로 딕셔너리
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # 환자별 디렉토리
        patient_images_dir = self.images_dir / patient_id / timestamp_str
        patient_masks_dir = self.masks_dir / patient_id / timestamp_str
        
        patient_images_dir.mkdir(parents=True, exist_ok=True)
        patient_masks_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = {
            "original_images": [],
            "mask_images": [],
            "metadata": []
        }
        
        # 원본 이미지 저장
        for idx, file in enumerate(uploaded_files):
            file.seek(0)
            original_path = patient_images_dir / file.name
            
            with open(original_path, 'wb') as f:
                f.write(file.read())
            
            saved_paths["original_images"].append(str(original_path))
        
        # 마스크 이미지 저장
        for idx, result in enumerate(cellpose_results):
            mask = result.get('masks')
            
            if mask is not None:
                # 마스크를 이미지로 저장
                mask_normalized = (mask > 0).astype(np.uint8) * 255
                mask_img = Image.fromarray(mask_normalized)
                
                mask_filename = f"mask_{idx+1}.png"
                mask_path = patient_masks_dir / mask_filename
                mask_img.save(mask_path)
                
                saved_paths["mask_images"].append(str(mask_path))
                
                # 메타데이터 저장
                metadata = {
                    "image_index": idx,
                    "original_image": result.get('image_path'),
                    "num_cells": result.get('num_cells'),
                    "diameter_used": result.get('diameter_used'),
                    "timestamp": timestamp.isoformat()
                }
                
                metadata_path = patient_masks_dir / f"metadata_{idx+1}.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
                
                saved_paths["metadata"].append(str(metadata_path))
        
        # 전체 요약 저장
        summary = {
            "patient_id": patient_id,
            "timestamp": timestamp.isoformat(),
            "num_images": len(uploaded_files),
            "num_masks": len(cellpose_results),
            "saved_paths": saved_paths
        }
        
        summary_path = patient_images_dir / "summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return saved_paths
    
    def save_document(
        self,
        patient_id: str,
        document_content: str,
        document_type: str,
        filename: str = None,
        timestamp: datetime = None
    ) -> str:
        """
        문서 저장
        
        Args:
            patient_id: 환자 ID
            document_content: 문서 내용
            document_type: 문서 타입 (report, note, etc)
            filename: 파일명 (선택)
            timestamp: 타임스탬프
        
        Returns:
            저장된 파일 경로
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        if filename is None:
            filename = f"{document_type}_{timestamp_str}.md"
        
        # 환자별 디렉토리
        patient_docs_dir = self.documents_dir / patient_id
        patient_docs_dir.mkdir(parents=True, exist_ok=True)
        
        doc_path = patient_docs_dir / filename
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(document_content)
        
        return str(doc_path)
    
    def get_patient_files(self, patient_id: str) -> Dict:
        """
        환자의 모든 파일 조회
        
        Args:
            patient_id: 환자 ID
        
        Returns:
            파일 정보 딕셔너리
        """
        files_info = {
            "images": [],
            "masks": [],
            "documents": []
        }
        
        # 이미지
        patient_images_dir = self.images_dir / patient_id
        if patient_images_dir.exists():
            for img_file in patient_images_dir.rglob("*.png"):
                files_info["images"].append(str(img_file))
            for img_file in patient_images_dir.rglob("*.jpg"):
                files_info["images"].append(str(img_file))
        
        # 마스크
        patient_masks_dir = self.masks_dir / patient_id
        if patient_masks_dir.exists():
            for mask_file in patient_masks_dir.rglob("*.png"):
                files_info["masks"].append(str(mask_file))
        
        # 문서
        patient_docs_dir = self.documents_dir / patient_id
        if patient_docs_dir.exists():
            for doc_file in patient_docs_dir.rglob("*.md"):
                files_info["documents"].append(str(doc_file))
            for doc_file in patient_docs_dir.rglob("*.txt"):
                files_info["documents"].append(str(doc_file))
        
        return files_info


# 사용 예제
if __name__ == "__main__":
    manager = FileStorageManager()
    
    print("파일 저장 관리 시스템 초기화 완료")
    print(f"기본 디렉토리: {manager.base_dir}")
