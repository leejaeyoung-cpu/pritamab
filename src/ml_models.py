"""
머신러닝 모델 모듈
약물 효능 예측 및 특징 추출
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import pickle
import json

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from utils import Logger, ensure_dir

class EfficacyPredictor:
    """
    약물 효능 예측 모델
    이미지 특징을 기반으로 약물 효능(IC50, 억제율 등)을 예측
    """
    
    def __init__(self, model_type: str = 'random_forest'):
        """
        Args:
            model_type: 모델 타입 ('random_forest', 'xgboost', 'gradient_boosting')
        """
        self.logger = Logger(__name__)
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = None
        
        self._initialize_model()
    
    def _initialize_model(self):
        """모델 초기화"""
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            self.logger.info("Random Forest 모델 초기화")
            
        elif self.model_type == 'xgboost':
            if XGBOOST_AVAILABLE:
                self.model = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42,
                    n_jobs=-1
                )
                self.logger.info("XGBoost 모델 초기화")
            else:
                self.logger.warning("XGBoost를 사용할 수 없습니다. Random Forest로 대체")
                self.model_type = 'random_forest'
                self._initialize_model()
                
        elif self.model_type == 'gradient_boosting':
            self.model = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
            self.logger.info("Gradient Boosting 모델 초기화")
        else:
            raise ValueError(f"알 수 없는 모델 타입: {self.model_type}")
    
    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: Optional[List[str]] = None,
        test_size: float = 0.2,
        cv: int = 5
    ) -> Dict:
        """
        모델 학습
        
        Args:
            X: 특징 배열
            y: 타겟 배열
            feature_names: 특징 이름 리스트
            test_size: 테스트 세트 비율
            cv: Cross-validation folds
            
        Returns:
            학습 결과 딕셔너리
        """
        self.logger.info("모델 학습 시작...")
        
        # 특징 이름 저장
        if feature_names:
            self.feature_names = feature_names
        else:
            self.feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        # 데이터 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # 스케일링
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # 모델 학습
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        # 예측
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)
        
        # 평가
        train_metrics = self._calculate_metrics(y_train, y_train_pred)
        test_metrics = self._calculate_metrics(y_test, y_test_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, cv=cv, scoring='r2'
        )
        
        results = {
            'model_type': self.model_type,
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'cv_r2_mean': float(np.mean(cv_scores)),
            'cv_r2_std': float(np.std(cv_scores)),
            'feature_importance': self._get_feature_importance()
        }
        
        self.logger.info(f"학습 완료 - Test R²: {test_metrics['r2']:.4f}")
        return results
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        효능 예측
        
        Args:
            X: 특징 배열
            
        Returns:
            예측값 배열
        """
        if not self.is_trained:
            raise RuntimeError("모델이 학습되지 않았습니다. train()을 먼저 호출하세요.")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """평가 지표 계산"""
        return {
            'mse': float(mean_squared_error(y_true, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred))),
            'mae': float(mean_absolute_error(y_true, y_pred)),
            'r2': float(r2_score(y_true, y_pred))
        }
    
    def _get_feature_importance(self) -> Dict[str, float]:
        """특징 중요도 추출"""
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            
            if self.feature_names:
                return {
                    name: float(imp) 
                    for name, imp in zip(self.feature_names, importances)
                }
        
        return {}
    
    def save(self, filepath: Union[str, Path]) -> None:
        """모델 저장"""
        filepath = Path(filepath)
        ensure_dir(filepath.parent)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'feature_names': self.feature_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        self.logger.info(f"모델 저장 완료: {filepath}")
    
    def load(self, filepath: Union[str, Path]) -> None:
        """모델 로드"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.model_type = model_data['model_type']
        self.is_trained = model_data['is_trained']
        self.feature_names = model_data.get('feature_names', None)
        
        self.logger.info(f"모델 로드 완료: {filepath}")


class SynergyCalculator:
    """
    약물 조합 시너지 계산
    """
    
    @staticmethod
    def bliss_independence(ic50_a: float, ic50_b: float, ic50_combo: float) -> float:
        """
        Bliss Independence 모델로 시너지 계산
        
        Args:
            ic50_a: 약물 A의 IC50
            ic50_b: 약물 B의 IC50
            ic50_combo: 조합의 IC50
            
        Returns:
            시너지 스코어 (>1: 시너지, <1: 길항)
        """
        # 예상 효과 (Bliss model)
        # E_expected = E_a + E_b - E_a * E_b
        # 여기서는 IC50 기반으로 간단히 계산
        
        expected_ic50 = (ic50_a + ic50_b) / 2
        
        if ic50_combo == 0:
            return 1.0
        
        synergy = expected_ic50 / ic50_combo
        return synergy
    
    @staticmethod
    def combination_index(
        dose_a: float,
        dose_b: float,
        ic50_a: float,
        ic50_b: float
    ) -> float:
        """
        Combination Index (CI) 계산 (Chou-Talalay method)
        
        CI < 1: synergism
        CI = 1: additive
        CI > 1: antagonism
        
        Args:
            dose_a: 약물 A 용량
            dose_b: 약물 B 용량
            ic50_a: 약물 A의 IC50
            ic50_b: 약물 B의 IC50
            
        Returns:
            CI 값
        """
        if ic50_a == 0 or ic50_b == 0:
            return 1.0
        
        ci = (dose_a / ic50_a) + (dose_b / ic50_b)
        return ci
    
    @staticmethod
    def calculate_synergy_score(
        efficacy_single: Dict[str, float],
        efficacy_combo: float,
        method: str = 'bliss'
    ) -> float:
        """
        시너지 스코어 계산
        
        Args:
            efficacy_single: 단일 약물 효능 딕셔너리 {'drug_a': 0.5, 'drug_b': 0.6}
            efficacy_combo: 조합 효능
            method: 계산 방법 ('bliss', 'loewe')
            
        Returns:
            시너지 스코어
        """
        if method == 'bliss':
            # Bliss independence
            expected_efficacy = 1.0
            for efficacy in efficacy_single.values():
                expected_efficacy *= (1 - efficacy)
            expected_efficacy = 1 - expected_efficacy
            
            if expected_efficacy == 0:
                return 1.0
            
            synergy = efficacy_combo / expected_efficacy
            return synergy
        
        elif method == 'loewe':
            # Loewe additivity (간단한 버전)
            expected_efficacy = np.mean(list(efficacy_single.values()))
            
            if expected_efficacy == 0:
                return 1.0
            
            synergy = efficacy_combo / expected_efficacy
            return synergy
        
        else:
            raise ValueError(f"알 수 없는 방법: {method}")


class FeatureExtractor:
    """
    이미지에서 고급 특징 추출 (선택적, CNN 기반)
    """
    
    def __init__(self, use_pretrained: bool = True):
        """
        Args:
            use_pretrained: 사전학습 모델 사용 여부
        """
        self.logger = Logger(__name__)
        self.use_pretrained = use_pretrained
        self.model = None
        
        # 향후 PyTorch/TensorFlow 모델 통합 가능
        self.logger.info("FeatureExtractor 초기화 (기본 특징 추출)")
    
    def extract_texture_features(self, image: np.ndarray) -> Dict[str, float]:
        """
        텍스처 특징 추출
        
        Args:
            image: 이미지 배열
            
        Returns:
            텍스처 특징 딕셔너리
        """
        # 간단한 통계적 특징
        features = {
            'mean_intensity': float(np.mean(image)),
            'std_intensity': float(np.std(image)),
            'min_intensity': float(np.min(image)),
            'max_intensity': float(np.max(image)),
            'median_intensity': float(np.median(image))
        }
        
        return features
    
    def extract_morphological_features(self, masks: np.ndarray) -> Dict[str, float]:
        """
        형태학적 특징 추출
        
        Args:
            masks: 세그멘테이션 마스크
            
        Returns:
            형태학적 특징 딕셔너리
        """
        cell_ids = np.unique(masks)[1:]  # 0은 배경
        
        if len(cell_ids) == 0:
            return {}
        
        areas = []
        for cell_id in cell_ids:
            area = np.sum(masks == cell_id)
            areas.append(area)
        
        features = {
            'cell_count': len(cell_ids),
            'mean_cell_area': float(np.mean(areas)),
            'std_cell_area': float(np.std(areas)),
            'total_cell_area': float(np.sum(areas))
        }
        
        return features
