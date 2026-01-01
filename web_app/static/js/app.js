import { patientsAPI, recommendationsAPI } from './utils/api.js';
import { showNotification } from './utils/helpers.js';
import { PatientManager } from './components/PatientManager.js';
import { RecommendationEngine } from './components/RecommendationEngine.js';
import { CellposeAnalyzer } from './components/CellposeAnalyzer.js';

class App {
    constructor() {
        this.currentView = 'home';
        this.currentPatient = null;
        this.patients = [];

        this.init();
    }

    async init() {
        this.setupSidebar();
        await this.loadPatients();
        this.renderView('home');
    }

    setupSidebar() {
        const sidebar = document.createElement('div');
        sidebar.className = 'sidebar';
        sidebar.innerHTML = `
            <div class="sidebar-header">
                <div class="sidebar-logo">🧬</div>
                <div class="sidebar-title">AI 항암제<br/>추론 시스템</div>
                <div class="sidebar-subtitle">Inha University Hospital</div>
            </div>
            
            <nav>
                <ul class="nav-menu">
                    <li class="nav-item">
                        <a href="#home" class="nav-link active" data-view="home">
                            <span class="nav-icon">🏠</span>
                            <span>홈</span>
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="#patients" class="nav-link" data-view="patients">
                            <span class="nav-icon">👥</span>
                            <span>환자 관리</span>
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="#recommendations" class="nav-link" data-view="recommendations">
                            <span class="nav-icon">💊</span>
                            <span>AI 추론</span>
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="#analysis" class="nav-link" data-view="analysis">
                            <span class="nav-icon">🔬</span>
                            <span>이미지 분석</span>
                        </a>
                    </li>
                    <li class="nav-item">
                        <a href="#about" class="nav-link" data-view="about">
                            <span class="nav-icon">ℹ️</span>
                            <span>소개</span>
                        </a>
                    </li>
                </ul>
            </nav>
            
            <div style="position: absolute; bottom: 20px; width: calc(100% - 40px); text-align: center; font-size: 0.75rem; opacity: 0.8;">
                <div>AI-based Anticancer</div>
                <div>Drug Discovery System</div>
                <div style="margin-top: 0.5rem;">© 2024 Inha Univ. Hospital</div>
            </div>
        `;

        document.body.insertBefore(sidebar, document.getElementById('app'));

        // Add navigation event listeners
        sidebar.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = e.currentTarget.dataset.view;
                this.renderView(view);

                // Update active state
                sidebar.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                e.currentTarget.classList.add('active');
            });
        });
    }

    async loadPatients() {
        try {
            this.patients = await patientsAPI.getAll();
        } catch (error) {
            console.error('Failed to load patients:', error);
            this.patients = [];
        }
    }

    async renderView(viewName) {
        this.currentView = viewName;
        const app = document.getElementById('app');

        const mainContent = document.createElement('div');
        mainContent.className = 'main-content';

        switch (viewName) {
            case 'home':
                mainContent.innerHTML = this.renderHome();
                break;
            case 'patients':
                mainContent.innerHTML = '<div id="patient-manager"></div>';
                break;
            case 'recommendations':
                mainContent.innerHTML = '<div id="recommendation-engine"></div>';
                break;
            case 'analysis':
                mainContent.innerHTML = '<div id="cellpose-analyzer"></div>';
                break;
            case 'about':
                mainContent.innerHTML = this.renderAbout();
                break;
            default:
                mainContent.innerHTML = this.renderHome();
        }

        app.innerHTML = '';
        app.appendChild(mainContent);

        // Initialize components after rendering
        if (viewName === 'patients') {
            new PatientManager('patient-manager', this);
        } else if (viewName === 'recommendations') {
            new RecommendationEngine('recommendation-engine', this);
        } else if (viewName === 'analysis') {
            new CellposeAnalyzer('cellpose-analyzer', this);
        }
    }

    renderHome() {
        return `
            <div class="header">
                <h1>🧬 AI 항암제 추론 시스템</h1>
                <p>인공지능 기반 개인화 항암제 조합 추천 플랫폼</p>
            </div>

            <div class="card glass-card">
                <div class="card-header">
                    <h2 class="card-title">시스템 개요</h2>
                </div>
                <div class="card-body">
                    <p>본 시스템은 <strong>논문 기반 근거</strong>와 <strong>AI 분석</strong>을 결합하여 
                    환자 맞춤형 항암제 조합을 추천하는 의료 전문가용 플랫폼입니다.</p>
                    
                    <div style="margin-top: 2rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
                        <div class="feature-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                            <h3 style="margin-bottom: 0.5rem;">논문 기반 추천</h3>
                            <p style="opacity: 0.9; font-size: 0.9rem;">최신 임상 연구와 메타분석 기반의 근거중심 약물 조합 제공</p>
                        </div>
                        
                        <div class="feature-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1.5rem; border-radius: 12px;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
                            <h3 style="margin-bottom: 0.5rem;">AI 개인화 추천</h3>
                            <p style="opacity: 0.9; font-size: 0.9rem;">환자의 분자 마커, 나이, 병기 등을 고려한 맞춤형 치료 전략</p>
                        </div>
                        
                        <div class="feature-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 1.5rem; border-radius: 12px;">
                            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔬</div>
                            <h3 style="margin-bottom: 0.5rem;">Cellpose 분석</h3>
                            <p style="opacity: 0.9; font-size: 0.9rem;">세포 이미지 자동 분석 및 형태학적 특징 추출</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">시스템 통계</h2>
                </div>
                <div class="card-body">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem;">
                        <div style="text-align: center; padding: 1rem; background: #E3F2FD; border-radius: 8px;">
                            <div style="font-size: 2.5rem; font-weight: bold; color: #1976D2;">${this.patients.length}</div>
                            <div style="color: #666; margin-top: 0.5rem;">등록 환자</div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: #E8F5E9; border-radius: 8px;">
                            <div style="font-size: 2.5rem; font-weight: bold; color: #4CAF50;">3</div>
                            <div style="color: #666; margin-top: 0.5rem;">암 종류</div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: #FFF3E0; border-radius: 8px;">
                            <div style="font-size: 2.5rem; font-weight: bold; color: #FF9800;">100+</div>
                            <div style="color: #666; margin-top: 0.5rem;">추천 조합</div>
                        </div>
                        <div style="text-align: center; padding: 1rem; background: #F3E5F5; border-radius: 8px;">
                            <div style="font-size: 2.5rem; font-weight: bold; color: #9C27B0;">1A</div>
                            <div style="color: #666; margin-top: 0.5rem;">근거 수준</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderAnalysis() {
        return `
            <div class="header">
                <h1>🔬 이미지 분석</h1>
                <p>Cellpose 기반 세포 이미지 자동 분석</p>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">이미지 업로드</h2>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="form-label">세포 이미지 선택</label>
                        <input type="file" class="form-input" accept=".png,.jpg,.jpeg,.tif,.tiff" id="image-upload">
                    </div>
                    <button class="btn btn-primary" onclick="alert('Cellpose 분석 기능은 개발 중입니다.')">분석 시작</button>
                </div>
            </div>

            <div class="alert alert-info">
                <strong>안내:</strong> Cellpose 이미지 분석 기능은 현재 개발 중입니다. 
                세포 이미지를 업로드하면 자동으로 세포 수, 크기, 형태학적 특징을 분석합니다.
            </div>
        `;
    }

    renderAbout() {
        return `
            <div class="header">
                <h1>ℹ️ 시스템 소개</h1>
                <p>AI 항암제 추론 시스템 정보</p>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">시스템 정보</h2>
                </div>
                <div class="card-body">
                    <table class="table">
                        <tr>
                            <th>시스템 이름</th>
                            <td>AI Anticancer Drug Discovery System</td>
                        </tr>
                        <tr>
                            <th>버전</th>
                            <td>2.0.0 (Web Version)</td>
                        </tr>
                        <tr>
                            <th>개발 기관</th>
                            <td>인하대학교병원</td>
                        </tr>
                        <tr>
                            <th>기술 스택</th>
                            <td>FastAPI, SQLAlchemy, Vanilla JavaScript, Plotly</td>
                        </tr>
                        <tr>
                            <th>AI 모델</th>
                            <td>PyTorch, Cellpose, scikit-learn</td>
                        </tr>
                    </table>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">주요 기능</h2>
                </div>
                <div class="card-body">
                    <ul style="line-height: 2;">
                        <li><strong>환자 관리:</strong> 환자 정보, 분자 마커, 병력 데이터베이스 관리</li>
                        <li><strong>논문 기반 추천:</strong> 최신 임상 연구와 근거 중심 약물 조합 제시</li>
                        <li><strong>AI 개인화 추천:</strong> 환자별 특성을 고려한 맞춤형 치료 전략</li>
                        <li><strong>하이브리드 추천:</strong> 논문 + AI 결합 최적 추천</li>
                        <li><strong>Cellpose 분석:</strong> 세포 이미지 자동 분석</li>
                        <li><strong>데이터 시각화:</strong> 인터랙티브 차트와 그래프</li>
                    </ul>
                </div>
            </div>
        `;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new App();
});
