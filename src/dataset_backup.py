"""
AI 추론 데이터셋 일일 백업 스크립트
매일 자동으로 전체 데이터셋을 백업
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
import zipfile


class DatasetBackupManager:
    """데이터셋 백업 관리 클래스"""
    
    def __init__(self, data_dir: str = None, backup_dir: str = None):
        """
        초기화
        
        Args:
            data_dir: 데이터 디렉토리 (기본: ./data)
            backup_dir: 백업 디렉토리 (기본: ./data/backups)
        """
        if data_dir is None:
            self.data_dir = Path.cwd() / "data"
        else:
            self.data_dir = Path(data_dir)
        
        if backup_dir is None:
            self.backup_dir = Path.cwd() / "data" / "backups"
        else:
            self.backup_dir = Path(backup_dir)
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_daily_backup(self) -> str:
        """
        일일 백업 생성
        
        Returns:
            백업 파일 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        date_str = datetime.now().strftime("%Y%m%d")
        
        # 백업 파일명
        backup_filename = f"dataset_backup_{date_str}.zip"
        backup_path = self.backup_dir / backup_filename
        
        # 같은 날짜의 백업이 있으면 삭제 (최신 것만 유지)
        if backup_path.exists():
            backup_path.unlink()
        
        # ZIP 압축
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # inference_results 디렉토리
            inference_dir = self.data_dir / "inference_results"
            if inference_dir.exists():
                for file_path in inference_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.data_dir)
                        zipf.write(file_path, arcname)
            
            # reports 디렉토리
            reports_dir = self.data_dir / "reports"
            if reports_dir.exists():
                for file_path in reports_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(self.data_dir)
                        zipf.write(file_path, arcname)
        
        # 백업 메타데이터 저장
        metadata = {
            "backup_date": datetime.now().isoformat(),
            "backup_file": backup_filename,
            "file_size_mb": backup_path.stat().st_size / (1024 * 1024)
        }
        
        metadata_path = self.backup_dir / f"metadata_{date_str}.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return str(backup_path)
    
    def cleanup_old_backups(self, keep_days: int = 365):
        """
        오래된 백업 정리
        
        Args:
            keep_days: 보관 일수 (기본: 365일, 1년)
        """
        cutoff_date = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for backup_file in self.backup_dir.glob("dataset_backup_*.zip"):
            if backup_file.stat().st_mtime < cutoff_date:
                backup_file.unlink()
                
                # 메타데이터도 삭제
                metadata_file = self.backup_dir / backup_file.name.replace("dataset_backup_", "metadata_").replace(".zip", ".json")
                if metadata_file.exists():
                    metadata_file.unlink()
    
    def get_backup_info(self) -> dict:
        """백업 정보 조회"""
        backups = list(self.backup_dir.glob("dataset_backup_*.zip"))
        
        if not backups:
            return {
                "total_backups": 0,
                "latest_backup": None,
                "total_size_mb": 0
            }
        
        # 최신 백업
        latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
        
        # 총 크기
        total_size = sum(b.stat().st_size for b in backups)
        
        return {
            "total_backups": len(backups),
            "latest_backup": latest_backup.name,
            "latest_backup_date": datetime.fromtimestamp(latest_backup.stat().st_mtime).isoformat(),
            "total_size_mb": total_size / (1024 * 1024)
        }
    
    def restore_backup(self, backup_file: str, restore_dir: str = None):
        """
        백업 복원
        
        Args:
            backup_file: 백업 파일명
            restore_dir: 복원 디렉토리 (기본: 원래 data 디렉토리)
        """
        backup_path = self.backup_dir / backup_file
        
        if not backup_path.exists():
            raise FileNotFoundError(f"백업 파일을 찾을 수 없습니다: {backup_file}")
        
        if restore_dir is None:
            restore_dir = self.data_dir
        else:
            restore_dir = Path(restore_dir)
        
        restore_dir.mkdir(parents=True, exist_ok=True)
        
        # ZIP 압축 해제
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(restore_dir)


def run_daily_backup():
    """일일 백업 실행"""
    print("=" * 80)
    print("AI 추론 데이터셋 일일 백업")
    print("=" * 80)
    print()
    
    manager = DatasetBackupManager()
    
    # 백업 생성
    print("[1/3] 백업 생성 중...")
    backup_path = manager.create_daily_backup()
    print(f"  ✓ 백업 완료: {backup_path}")
    print()
    
    # 오래된 백업 정리
    print("[2/3] 오래된 백업 정리 중...")
    manager.cleanup_old_backups(keep_days=365)
    print("  ✓ 1년(365일) 이상 된 백업 삭제 완료")
    print()
    
    # 백업 정보
    print("[3/3] 백업 정보")
    info = manager.get_backup_info()
    print(f"  총 백업 파일 수: {info['total_backups']}개")
    if info['latest_backup']:
        print(f"  최신 백업: {info['latest_backup']}")
        print(f"  백업 날짜: {info['latest_backup_date']}")
    print(f"  총 백업 크기: {info['total_size_mb']:.2f} MB")
    print()
    
    print("=" * 80)
    print("백업 완료!")
    print("=" * 80)


if __name__ == "__main__":
    run_daily_backup()
