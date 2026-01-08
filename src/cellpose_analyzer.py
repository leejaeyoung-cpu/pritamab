"""
Cellpose 기반 세포 이미지 분석 모듈
RTX 4060 GPU 가속 지원
"""

import os
import sys
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import torch

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        # Streamlit 또는 일부 환경에서는 reconfigure를 지원하지 않음
        pass

# Cellpose imports
from cellpose import models, core
from cellpose.io import imread

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CellposeAnalyzer:
    """Cellpose를 사용한 세포 이미지 분석 클래스"""
    
    def __init__(self, model_type='cyto3', use_gpu=True, diameter=None):
        """
        초기화
        
        Args:
            model_type (str): 모델 타입 ('cyto', 'cyto2', 'cyto3', 'nuclei')
            use_gpu (bool): GPU 사용 여부
            diameter (float/None): 세포 직경 (None이면 자동 추정)
        """
        self.model_type = model_type
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.diameter = diameter
        
        logger.info(f"Initializing Cellpose Analyzer...")
        logger.info(f"  Model type: {model_type}")
        logger.info(f"  GPU enabled: {self.use_gpu}")
        
        if self.use_gpu:
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"  Using GPU: {gpu_name}")
        
        # 모델 로드
        self.model = models.CellposeModel(gpu=self.use_gpu, model_type=model_type)
        logger.info("  Model loaded successfully")
    
    def analyze_image(
        self,
        image_path: str,
        diameter: Optional[float] = None,
        flow_threshold: float = 0.4,
        cellprob_threshold: float = 0.0,
        upscale_factor: float = 1.0,
        enhance_contrast: bool = False
    ) -> Dict:
        """
        단일 이미지 분석
        
        Args:
            image_path: 이미지 파일 경로
            diameter: 세포 직경 (None이면 클래스 기본값 사용)
            flow_threshold: Flow threshold
            cellprob_threshold: Cell probability threshold
            
        Returns:
            분석 결과 딕셔너리
        """
        logger.info(f"Analyzing image: {image_path}")
        
        # 이미지 로드
        img = imread(image_path)
        
        # Preprocessing: CLAHE (Contrast Limited Adaptive Histogram Equalization)
        if enhance_contrast:
            logger.info("  Applying CLAHE preprocessing...")
            if img.ndim == 2: # Grayscale
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                img = clahe.apply(img)
            elif img.ndim == 3: # RGB
                # Convert to LAB, apply to L channel
                lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                cl = clahe.apply(l)
                limg = cv2.merge((cl,a,b))
                img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)

        # Upscaling
        original_shape = img.shape[:2]
        if upscale_factor > 1.0:
            logger.info(f"  Upscaling image by {upscale_factor}x...")
            new_width = int(img.shape[1] * upscale_factor)
            new_height = int(img.shape[0] * upscale_factor)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        
        # 직경 설정
        diam = diameter if diameter is not None else self.diameter
        
        # 세포 분할 실행
        # 세포 분할 실행
        masks, flows, styles = self.model.eval(
            img,
            diameter=diam,
            flow_threshold=flow_threshold,
            cellprob_threshold=cellprob_threshold
        )
        
        # Downscale masks if upscaled
        if upscale_factor > 1.0:
            logger.info("  Downscaling masks to original size...")
            masks = cv2.resize(masks, (original_shape[1], original_shape[0]), interpolation=cv2.INTER_NEAREST)
            # Resize flows and styles if needed (omitted for now as they are complex structures)
        
        # 결과 분석
        cell_ids = np.unique(masks)[1:]  # 0은 배경
        num_cells = len(cell_ids)
        
        # 각 세포의 속성 계산
        cell_properties = []
        for cell_id in cell_ids:
            cell_mask = masks == cell_id
            area = np.sum(cell_mask)
            
            # 세포 위치 (중심)
            coords = np.where(cell_mask)
            center_y = int(np.mean(coords[0]))
            center_x = int(np.mean(coords[1]))
            
            cell_properties.append({
                'cell_id': int(cell_id),
                'area': int(area),
                'center_x': center_x,
                'center_y': center_y
            })
        
        result = {
            'image_path': image_path,
            'image_shape': img.shape,
            'num_cells': num_cells,
            'masks': masks,
            'flows': flows,
            'styles': styles,
            'cell_properties': cell_properties,
            'diameter_used': diam
        }
        
        logger.info(f"  Detected {num_cells} cells")
        
        return result
    
    def analyze_batch(
        self,
        image_paths: List[str],
        diameter: Optional[float] = None,
        flow_threshold: float = 0.4,
        cellprob_threshold: float = 0.0
    ) -> List[Dict]:
        """
        여러 이미지 일괄 분석
        
        Args:
            image_paths: 이미지 파일 경로 리스트
            diameter: 세포 직경
            flow_threshold: Flow threshold
            cellprob_threshold: Cell probability threshold
            
        Returns:
            분석 결과 리스트
        """
        logger.info(f"Analyzing {len(image_paths)} images...")
        
        results = []
        for i, path in enumerate(image_paths, 1):
            logger.info(f"Progress: {i}/{len(image_paths)}")
            result = self.analyze_image(
                path,
                diameter=diameter,
                flow_threshold=flow_threshold,
                cellprob_threshold=cellprob_threshold
            )
            results.append(result)
        
        logger.info("Batch analysis complete")
        return results
    
    def calculate_statistics(self, results: List[Dict]) -> Dict:
        """
        분석 결과 통계 계산
        
        Args:
            results: analyze_batch의 결과
            
        Returns:
            통계 딕셔너리
        """
        total_cells = sum(r['num_cells'] for r in results)
        all_areas = []
        
        for result in results:
            for cell in result['cell_properties']:
                all_areas.append(cell['area'])
        
        stats = {
            'total_images': len(results),
            'total_cells': total_cells,
            'avg_cells_per_image': total_cells / len(results) if results else 0,
            'avg_cell_area': np.mean(all_areas) if all_areas else 0,
            'median_cell_area': np.median(all_areas) if all_areas else 0,
            'std_cell_area': np.std(all_areas) if all_areas else 0,
            'min_cell_area': np.min(all_areas) if all_areas else 0,
            'max_cell_area': np.max(all_areas) if all_areas else 0
        }
        
        return stats


def test_analyzer():
    """테스트 함수"""
    print("="*80)
    print("Cellpose Analyzer Test")
    print("="*80)
    
    # GPU 사용 가능 여부 확인
    gpu_available = core.use_gpu()
    print(f"\nGPU Available: {gpu_available}")
    
    if gpu_available:
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
    
    # Analyzer 초기화
    analyzer = CellposeAnalyzer(model_type='cyto3', use_gpu=True)
    
    print("\n[OK] Cellpose Analyzer initialization successful")
    print("="*80)


if __name__ == "__main__":
    test_analyzer()
