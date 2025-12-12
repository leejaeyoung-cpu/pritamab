"""
Dataset 폴더 분류 및 분석 도구
문서, 이미지, 논문 등을 자동으로 분류하고 분석
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import json
import shutil

class DatasetAnalyzer:
    """Dataset 폴더 분석 및 분류"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.analysis_results = {
            'scan_time': datetime.now().isoformat(),
            'total_files': 0,
            'total_directories': 0,
            'file_categories': {},
            'directory_structure': {},
            'large_files': [],
            'important_documents': [],
            'images': [],
            'research_papers': []
        }
    
    def scan_directory(self) -> Dict:
        """디렉토리 전체 스캔"""
        print(f"📂 스캔 시작: {self.dataset_path}")
        
        for root, dirs, files in os.walk(self.dataset_path):
            self.analysis_results['total_directories'] += len(dirs)
            
            for file in files:
                file_path = Path(root) / file
                self._analyze_file(file_path)
                self.analysis_results['total_files'] += 1
        
        self._generate_statistics()
        return self.analysis_results
    
    def _analyze_file(self, file_path: Path):
        """개별 파일 분석"""
        try:
            file_info = {
                'name': file_path.name,
                'path': str(file_path.relative_to(self.dataset_path)),
                'size_mb': file_path.stat().st_size / (1024 * 1024),
                'extension': file_path.suffix.lower(),
                'category': self._categorize_file(file_path)
            }
            
            # 카테고리별 분류
            category = file_info['category']
            if category not in self.analysis_results['file_categories']:
                self.analysis_results['file_categories'][category] = []
            self.analysis_results['file_categories'][category].append(file_info)
            
            # 큰 파일 (10MB 이상)
            if file_info['size_mb'] > 10:
                self.analysis_results['large_files'].append(file_info)
            
            # 중요 문서
            if self._is_important_document(file_path):
                self.analysis_results['important_documents'].append(file_info)
            
            # 이미지
            if category == 'images':
                self.analysis_results['images'].append(file_info)
            
            # 논문
            if category == 'papers':
                self.analysis_results['research_papers'].append(file_info)
                
        except Exception as e:
            print(f"⚠️ 파일 분석 실패: {file_path.name} - {e}")
    
    def _categorize_file(self, file_path: Path) -> str:
        """파일 카테고리 분류"""
        ext = file_path.suffix.lower()
        name = file_path.name.lower()
        
        # 문서
        if ext in ['.pdf', '.docx', '.doc', '.txt', '.md']:
            if any(keyword in name for keyword in ['논문', 'paper', 'article']):
                return 'papers'
            elif any(keyword in name for keyword in ['보고서', 'report', '분석']):
                return 'reports'
            else:
                return 'documents'
        
        # 이미지
        elif ext in ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp']:
            if any(keyword in name for keyword in ['암', 'cancer', 'cell', 'hct', 'snu']):
                return 'cell_images'
            return 'images'
        
        # 프레젠테이션
        elif ext in ['.pptx', '.ppt']:
            return 'presentations'
        
        # 데이터
        elif ext in ['.csv', '.xlsx', '.xls', '.json']:
            return 'data_files'
        
        else:
            return 'others'
    
    def _is_important_document(self, file_path: Path) -> bool:
        """중요 문서 판별"""
        name = file_path.name.lower()
        keywords = [
            '계획서', '보고서', '특허', 'patent',
            '논문', 'paper', 'article',
            '연구', 'research', '분석', 'analysis',
            'comprehensive', 'report', 'final'
        ]
        return any(keyword in name for keyword in keywords)
    
    def _generate_statistics(self):
        """통계 생성"""
        # 카테고리별 파일 개수
        category_counts = {
            cat: len(files) 
            for cat, files in self.analysis_results['file_categories'].items()
        }
        self.analysis_results['category_statistics'] = category_counts
        
        # 이미지 통계
        total_images = len(self.analysis_results['images'])
        cell_images = len([
            f for f in self.analysis_results['images'] 
            if 'cell' in f['category']
        ])
        self.analysis_results['image_statistics'] = {
            'total': total_images,
            'cell_images': cell_images,
            'other_images': total_images - cell_images
        }
    
    def organize_by_category(self, output_dir: str = None):
        """카테고리별로 파일 정리 (복사)"""
        if output_dir is None:
            output_dir = self.dataset_path.parent / 'dataset_organized'
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        print(f"\n📁 파일 정리 시작: {output_dir}")
        
        organized_count = 0
        for category, files in self.analysis_results['file_categories'].items():
            category_dir = output_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for file_info in files:
                source = self.dataset_path / file_info['path']
                dest = category_dir / file_info['name']
                
                try:
                    # 중복 파일명 처리
                    if dest.exists():
                        base = dest.stem
                        ext = dest.suffix
                        counter = 1
                        while dest.exists():
                            dest = category_dir / f"{base}_{counter}{ext}"
                            counter += 1
                    
                    shutil.copy2(source, dest)
                    organized_count += 1
                except Exception as e:
                    print(f"⚠️ 복사 실패: {file_info['name']} - {e}")
        
        print(f"✅ {organized_count}개 파일 정리 완료!")
        return output_dir
    
    def generate_report(self, output_file: str = None) -> str:
        """분석 보고서 생성"""
        if output_file is None:
            output_file = self.dataset_path.parent / f'dataset_analysis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        report = self._create_markdown_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 보고서 생성: {output_file}")
        return str(output_file)
    
    def _create_markdown_report(self) -> str:
        """마크다운 보고서 생성"""
        results = self.analysis_results
        
        report = f"""# Dataset 폴더 분석 보고서

## 📊 기본 정보

- **스캔 시간**: {results['scan_time']}
- **스캔 경로**: {self.dataset_path}
- **총 파일 수**: {results['total_files']}개
- **총 디렉토리 수**: {results['total_directories']}개

---

## 📁 카테고리별 파일 분류

"""
        
        # 카테고리 통계
        for category, count in sorted(results.get('category_statistics', {}).items(), key=lambda x: x[1], reverse=True):
            category_names = {
                'papers': '📚 논문',
                'reports': '📋 보고서',
                'documents': '📄 문서',
                'cell_images': '🔬 세포 이미지',
                'images': '🖼️ 이미지',
                'presentations': '📊 프레젠테이션',
                'data_files': '📈 데이터 파일',
                'others': '📦 기타'
            }
            name = category_names.get(category, category)
            report += f"- **{name}**: {count}개\n"
        
        report += "\n---\n\n## 🔍 중요 문서\n\n"
        
        for doc in results['important_documents'][:20]:  # 상위 20개
            report += f"- **{doc['name']}**\n"
            report += f"  - 경로: `{doc['path']}`\n"
            report += f"  - 크기: {doc['size_mb']:.2f} MB\n\n"
        
        report += f"\n전체 {len(results['important_documents'])}개\n\n"
        report += "---\n\n## 🔬 세포 이미지\n\n"
        
        cell_images = [f for f in results['images'] if f['category'] == 'cell_images']
        report += f"**총 {len(cell_images)}개의 세포 이미지 발견**\n\n"
        
        # 디렉토리별 그룹화
        image_dirs = {}
        for img in cell_images:
            dir_name = Path(img['path']).parent
            if dir_name not in image_dirs:
                image_dirs[dir_name] = []
            image_dirs[dir_name].append(img)
        
        for dir_name, images in sorted(image_dirs.items()):
            report += f"### {dir_name}\n\n"
            report += f"- 이미지 수: {len(images)}개\n"
            report += f"- 총 크기: {sum(img['size_mb'] for img in images):.2f} MB\n\n"
        
        report += "\n---\n\n## 📚 연구 논문\n\n"
        
        for paper in results['research_papers'][:15]:
            report += f"- **{paper['name']}**\n"
            report += f"  - 경로: `{paper['path']}`\n"
            report += f"  - 크기: {paper['size_mb']:.2f} MB\n\n"
        
        report += "\n---\n\n## 💾 대용량 파일 (10MB 이상)\n\n"
        
        large_files = sorted(results['large_files'], key=lambda x: x['size_mb'], reverse=True)
        for file in large_files[:10]:
            report += f"- **{file['name']}** ({file['size_mb']:.1f} MB)\n"
            report += f"  - 경로: `{file['path']}`\n\n"
        
        report += "\n---\n\n## 📈 분류 제안\n\n"
        report += "### 정리 우선순위\n\n"
        report += "1. **논문 및 보고서** → `논문` 폴더로 통합\n"
        report += "2. **세포 이미지** → `세포이미지` 폴더로 정리\n"
        report += "3. **프레젠테이션** → `발표자료` 폴더로 이동\n"
        report += "4. **데이터 파일** → `data` 폴더로 통합\n\n"
        
        report += "---\n\n"
        report += f"*보고서 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return report
    
    def save_json(self, output_file: str = None):
        """JSON으로 분석 결과 저장"""
        if output_file is None:
            output_file = self.dataset_path.parent / 'dataset_analysis.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 JSON 저장: {output_file}")
        return str(output_file)


def main():
    """메인 실행"""
    import sys
    
    # Dataset 경로
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = Path(__file__).parent.parent / 'dataset'
    
    print("=" * 60)
    print("📂 Dataset 폴더 분류 및 분석 도구")
    print("=" * 60)
    print()
    
    # 분석기 생성
    analyzer = DatasetAnalyzer(dataset_path)
    
    # 스캔 실행
    results = analyzer.scan_directory()
    
    # 결과 출력
    print("\n" + "=" * 60)
    print("📊 분석 완료!")
    print("=" * 60)
    print(f"총 파일: {results['total_files']}개")
    print(f"총 디렉토리: {results['total_directories']}개")
    print()
    print("카테고리별 파일 수:")
    for cat, count in sorted(results.get('category_statistics', {}).items(), key=lambda x: x[1], reverse=True):
        print(f"  - {cat}: {count}개")
    print()
    
    # 보고서 생성
    report_file = analyzer.generate_report()
    
    # JSON 저장
    json_file = analyzer.save_json()
    
    # 정리 옵션
    print("\n파일 정리를 하시겠습니까? (y/n): ", end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        organized_dir = analyzer.organize_by_category()
        print(f"\n✅ 파일 정리 완료: {organized_dir}")
    
    print("\n" + "=" * 60)
    print("✅ 모든 작업 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()
