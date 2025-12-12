"""
유틸리티 함수 모음
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def get_project_root() -> Path:
    """프로젝트 루트 디렉토리 반환"""
    return Path(__file__).parent.parent

def ensure_dir(directory: Path) -> None:
    """디렉토리가 없으면 생성"""
    directory.mkdir(parents=True, exist_ok=True)

def load_json(filepath: Path) -> Dict:
    """JSON 파일 로드"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"파일을 찾을 수 없습니다: {filepath}")
        return {}
    except json.JSONDecodeError:
        logging.error(f"JSON 파싱 오류: {filepath}")
        return {}

def save_json(data: Dict, filepath: Path) -> None:
    """JSON 파일 저장"""
    ensure_dir(filepath.parent)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_excel(filepath: Path, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """Excel 파일 로드"""
    try:
        return pd.read_excel(filepath, sheet_name=sheet_name)
    except Exception as e:
        logging.error(f"Excel 파일 로드 오류: {e}")
        return pd.DataFrame()

def validate_image_file(filepath: Path) -> bool:
    """이미지 파일 유효성 검사"""
    valid_extensions = {'.tif', '.tiff', '.png', '.jpg', '.jpeg'}
    return filepath.suffix.lower() in valid_extensions and filepath.exists()

def normalize_data(data: np.ndarray, method: str = 'minmax') -> np.ndarray:
    """데이터 정규화"""
    if method == 'minmax':
        min_val = np.min(data)
        max_val = np.max(data)
        if max_val - min_val == 0:
            return data
        return (data - min_val) / (max_val - min_val)
    elif method == 'zscore':
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return data
        return (data - mean) / std
    else:
        raise ValueError(f"알 수 없는 정규화 방법: {method}")

def get_file_size_mb(filepath: Path) -> float:
    """파일 크기를 MB 단위로 반환"""
    return filepath.stat().st_size / (1024 * 1024)

def format_number(num: float, decimals: int = 2) -> str:
    """숫자를 포맷팅"""
    return f"{num:.{decimals}f}"

class Logger:
    """커스텀 로거 클래스"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)
    
    def debug(self, message: str) -> None:
        self.logger.debug(message)
