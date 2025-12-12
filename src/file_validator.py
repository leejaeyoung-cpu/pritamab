"""
파일 검증 모듈
업로드된 파일의 유효성을 검사
"""

import numpy as np
from pathlib import Path
from typing import Tuple, List, Optional, Dict
from PIL import Image
import pandas as pd
import io

from utils import Logger

logger = Logger(__name__)


class FileValidator:
    """파일 검증 클래스"""
    
    # 이미지 파일 설정
    SUPPORTED_IMAGE_FORMATS = ['.tif', '.tiff', '.png', '.jpg', '.jpeg', '.bmp']
    MAX_IMAGE_SIZE_MB = 50
    MIN_IMAGE_DIMENSIONS = (256, 256)
    
    # Excel 파일 설정
    SUPPORTED_EXCEL_FORMATS = ['.xlsx', '.xls', '.csv']
    MAX_EXCEL_SIZE_MB = 20
    
    @staticmethod
    def validate_image_file(file, check_content: bool = True) -> Tuple[bool, str]:
        """
        이미지 파일 검증
        
        Args:
            file: Streamlit UploadedFile 객체
            check_content: 파일 내용까지 검증할지 여부
            
        Returns:
            (유효 여부, 메시지) 튜플
        """
        try:
            # 파일명 추출
            filename = file.name
            file_ext = Path(filename).suffix.lower()
            
            # 1. 확장자 검사
            if file_ext not in FileValidator.SUPPORTED_IMAGE_FORMATS:
                return False, f"지원하지 않는 이미지 형식입니다. 지원 형식: {', '.join(FileValidator.SUPPORTED_IMAGE_FORMATS)}"
            
            # 2. 파일 크기 검사
            file_size_mb = file.size / (1024 * 1024)
            if file_size_mb > FileValidator.MAX_IMAGE_SIZE_MB:
                return False, f"파일 크기가 너무 큽니다 ({file_size_mb:.1f}MB). 최대 크기: {FileValidator.MAX_IMAGE_SIZE_MB}MB"
            
            # 3. 파일 내용 검사 (선택적)
            if check_content:
                try:
                    # 파일 포인터를 처음으로 이동
                    file.seek(0)
                    
                    # PIL로 이미지 열기 시도
                    image = Image.open(file)
                    
                    # 4. 이미지 크기 검사
                    width, height = image.size
                    min_w, min_h = FileValidator.MIN_IMAGE_DIMENSIONS
                    
                    if width < min_w or height < min_h:
                        return False, f"이미지 크기가 너무 작습니다 ({width}x{height}). 최소 크기: {min_w}x{min_h}"
                    
                    # 5. 이미지 모드 확인
                    if image.mode not in ['L', 'RGB', 'RGBA']:
                        logger.warning(f"비표준 이미지 모드: {image.mode}. RGB로 변환할 수 있습니다.")
                    
                    # 파일 포인터를 다시 처음으로
                    file.seek(0)
                    
                except Exception as e:
                    return False, f"이미지 파일을 읽을 수 없습니다: {str(e)}"
            
            return True, "유효한 이미지 파일입니다."
        
        except Exception as e:
            logger.error(f"이미지 검증 중 오류: {str(e)}")
            return False, f"파일 검증 중 오류가 발생했습니다: {str(e)}"
    
    @staticmethod
    def validate_excel_file(
        file, 
        required_columns: Optional[List[str]] = None,
        check_content: bool = True
    ) -> Tuple[bool, str]:
        """
        Excel 파일 검증
        
        Args:
            file: Streamlit UploadedFile 객체
            required_columns: 필수 컬럼 리스트
            check_content: 파일 내용까지 검증할지 여부
            
        Returns:
            (유효 여부, 메시지) 튜플
        """
        try:
            # 파일명 추출
            filename = file.name
            file_ext = Path(filename).suffix.lower()
            
            # 1. 확장자 검사
            if file_ext not in FileValidator.SUPPORTED_EXCEL_FORMATS:
                return False, f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(FileValidator.SUPPORTED_EXCEL_FORMATS)}"
            
            # 2. 파일 크기 검사
            file_size_mb = file.size / (1024 * 1024)
            if file_size_mb > FileValidator.MAX_EXCEL_SIZE_MB:
                return False, f"파일 크기가 너무 큽니다 ({file_size_mb:.1f}MB). 최대 크기: {FileValidator.MAX_EXCEL_SIZE_MB}MB"
            
            # 3. 파일 내용 검사 (선택적)
            if check_content:
                try:
                    # 파일 포인터를 처음으로 이동
                    file.seek(0)
                    
                    # pandas로 읽기 시도
                    if file_ext == '.csv':
                        df = pd.read_csv(file, encoding='utf-8', nrows=5)
                    else:
                        df = pd.read_excel(file, nrows=5)
                    
                    # 4. 데이터가 있는지 확인
                    if df.empty:
                        return False, "파일에 데이터가 없습니다."
                    
                    # 5. 필수 컬럼 확인
                    if required_columns:
                        missing_columns = set(required_columns) - set(df.columns)
                        if missing_columns:
                            return False, f"필수 컬럼이 누락되었습니다: {', '.join(missing_columns)}"
                    
                    # 파일 포인터를 다시 처음으로
                    file.seek(0)
                    
                except Exception as e:
                    return False, f"Excel 파일을 읽을 수 없습니다: {str(e)}"
            
            return True, "유효한 Excel 파일입니다."
        
        except Exception as e:
            logger.error(f"Excel 검증 중 오류: {str(e)}")
            return False, f"파일 검증 중 오류가 발생했습니다: {str(e)}"
    
    @staticmethod
    def check_file_size(file, max_size_mb: float) -> bool:
        """
        파일 크기 확인
        
        Args:
            file: Streamlit UploadedFile 객체
            max_size_mb: 최대 크기 (MB)
            
        Returns:
            크기가 제한 이내이면 True
        """
        file_size_mb = file.size / (1024 * 1024)
        return file_size_mb <= max_size_mb
    
    @staticmethod
    def validate_image_dimensions(image: Image.Image) -> Tuple[bool, Tuple[int, int]]:
        """
        이미지 크기 검증
        
        Args:
            image: PIL Image 객체
            
        Returns:
            (유효 여부, (width, height)) 튜플
        """
        width, height = image.size
        min_w, min_h = FileValidator.MIN_IMAGE_DIMENSIONS
        
        is_valid = width >= min_w and height >= min_h
        return is_valid, (width, height)
    
    @staticmethod
    def get_image_info(file) -> Dict[str, any]:
        """
        이미지 파일 정보 추출
        
        Args:
            file: Streamlit UploadedFile 객체
            
        Returns:
            이미지 정보 딕셔너리
        """
        try:
            file.seek(0)
            image = Image.open(file)
            
            info = {
                'filename': file.name,
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.size[0],
                'height': image.size[1],
                'file_size_bytes': file.size,
                'file_size_mb': round(file.size / (1024 * 1024), 2)
            }
            
            file.seek(0)
            return info
        
        except Exception as e:
            logger.error(f"이미지 정보 추출 실패: {str(e)}")
            return {}
    
    @staticmethod
    def get_excel_info(file) -> Dict[str, any]:
        """
        Excel 파일 정보 추출
        
        Args:
            file: Streamlit UploadedFile 객체
            
        Returns:
            Excel 정보 딕셔너리
        """
        try:
            file.seek(0)
            file_ext = Path(file.name).suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file, encoding='utf-8')
            else:
                df = pd.read_excel(file)
            
            info = {
                'filename': file.name,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'file_size_bytes': file.size,
                'file_size_mb': round(file.size / (1024 * 1024), 2)
            }
            
            file.seek(0)
            return info
        
        except Exception as e:
            logger.error(f"Excel 정보 추출 실패: {str(e)}")
            return {}
    
    @staticmethod
    def validate_batch_images(files: List) -> Tuple[List, List]:
        """
        여러 이미지 파일 일괄 검증
        
        Args:
            files: Streamlit UploadedFile 객체 리스트
            
        Returns:
            (유효한 파일 리스트, 오류 메시지 리스트) 튜플
        """
        valid_files = []
        errors = []
        
        for file in files:
            is_valid, message = FileValidator.validate_image_file(file)
            
            if is_valid:
                valid_files.append(file)
            else:
                errors.append(f"{file.name}: {message}")
        
        return valid_files, errors
    
    @staticmethod
    def get_supported_formats_string(file_type: str = 'image') -> str:
        """
        지원하는 파일 형식 문자열 반환
        
        Args:
            file_type: 'image' 또는 'excel'
            
        Returns:
            형식 문자열 (예: ".tif, .png, .jpg")
        """
        if file_type == 'image':
            return ', '.join(FileValidator.SUPPORTED_IMAGE_FORMATS)
        elif file_type == 'excel':
            return ', '.join(FileValidator.SUPPORTED_EXCEL_FORMATS)
        else:
            return ""
