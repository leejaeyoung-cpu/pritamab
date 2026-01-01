/**
 * AI 추론 엔진 컴포넌트
 */

import { patientsAPI, recommendationsAPI } from '../utils/api.js';
import { formatScore, formatDrugList, getScoreColor, getEvidenceBadge, showNotification } from '../utils/helpers.js';

export class RecommendationEngine {
    constructor(containerId, app) {
        this.container = document.getElementById(containerId);
        this.app = app;
        this.currentPatient = app.currentPatient;
        this.recommendations = null;

        this.init();
    }

    async init() {
        if (!this.currentPatient) {
            await this.loadDefaultPatient();
        }
        this.render();
    }

    async loadDefaultPatient() {
        try {
            const patients = await patientsAPI.getAll();
            if (patients.length > 0) {
                this.currentPatient = patients[0];
                this.app.currentPatient = patients[0];
            }
        } catch (error) {
            console.error('Failed to load patients:', error);
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="header">
                <h1>💊 AI 추론 엔진</h1>
                <p>논문 + AI 기반 항암제 조합 추천</p>
            </div>

            ${this.currentPatient ? `
                <div class="card glass-card">
                    <div class="card-header">
                        <h3 class="card-title">현재 선택된 환자</h3>
                    </div>
                    <div class="card-body">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                            <div><strong>이름:</strong> ${this.currentPatient.name}</div>
                            <div><strong>환자 ID:</strong> ${this.currentPatient.patient_id}</div>
                            <div><strong>나이:</strong> ${this.currentPatient.age || '-'}</div>
                            <div><strong>암 종류:</strong> ${this.currentPatient.cancer_type}</div>
                            <div><strong>병기:</strong> ${this.currentPatient.cancer_stage || '-'}</div>
                        </div>
                    </div>
                </div>
            ` : `
                <div class="alert alert-info">
                    먼저 환자를 선택해주세요. <a href="#patients" onclick="app.renderView('patients')">환자 관리 페이지로 이동</a>
                </div>
            `}

            ${this.currentPatient ? `
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">추론 설정</h3>
                    </div>
                    <div class="card-body">
                        <form id="recommendation-form">
                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
                                <div class="form-group">
                                    <label class="form-label">치료 유형</label>
                                    <select class="form-select" name="therapy_type" required>
                                        <option value="1제">1제 (단일 치료)</option>
                                        <option value="2제" selected>2제 (병용 치료)</option>
                                        <option value="3제">3제 (삼중 치료)</option>
                                    </select>
                                </div>
                                
                                <div class="form-group">
                                    <label class="form-label">추천 개수</label>
                                    <input type="number" class="form-input" name="top_n" value="5" min="1" max="10">
                                </div>

                                <div class="form-group">
                                    <label class="form-label">추천 방식</label>
                                    <select class="form-select" name="rec_mode">
                                        <option value="hybrid">하이브리드 (논문 + AI)</option>
                                        <option value="paper">논문 기반만</option>
                                        <option value="ai">AI 기반만</option>
                                    </select>
                                </div>
                            </div>

                            <button type="submit" class="btn btn-primary" style="margin-top: 1rem;">
                                🔍 추론 시작
                            </button>
                        </form>
                    </div>
                </div>

                <div id="recommendations-results"></div>
            ` : ''}
        `;

        if (this.currentPatient) {
            this.attachEventListeners();
        }
    }

    attachEventListeners() {
        const form = this.container.querySelector('#recommendation-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.getRecommendations(e.target);
        });
    }

    async getRecommendations(form) {
        const formData = new FormData(form);
        const therapy_type = formData.get('therapy_type');
        const top_n = parseInt(formData.get('top_n'));
        const rec_mode = formData.get('rec_mode');

        const requestData = {
            patient_id: this.currentPatient.id,
            therapy_type,
            top_n,
            include_paper: rec_mode === 'paper' || rec_mode === 'hybrid',
            include_ai: rec_mode === 'ai' || rec_mode === 'hybrid'
        };

        try {
            showNotification('AI 추론 중...', 'info');
            this.recommendations = await recommendationsAPI.get(requestData);
            this.renderRecommendations(rec_mode);
            showNotification('추론 완료!', 'success');
        } catch (error) {
            showNotification(`추론 실패: ${error.message}`, 'error');
        }
    }

    renderRecommendations(mode) {
        const resultsContainer = this.container.querySelector('#recommendations-results');

        let html = '';

        // Hybrid recommendations
        if (mode === 'hybrid' && this.recommendations.hybrid_recommendations.length > 0) {
            html += this.renderRecommendationSection('🏆 하이브리드 추천 (논문 + AI 결합)', this.recommendations.hybrid_recommendations);
        }

        // Paper recommendations
        if (mode === 'paper' || mode === 'hybrid') {
            if (this.recommendations.paper_recommendations.length > 0) {
                html += this.renderRecommendationSection('📚 논문 기반 추천', this.recommendations.paper_recommendations);
            }
        }

        // AI recommendations
        if (mode === 'ai' || mode === 'hybrid') {
            if (this.recommendations.ai_recommendations.length > 0) {
                html += this.renderRecommendationSection('🤖 AI 개인화 추천', this.recommendations.ai_recommendations);
            }
        }

        if (!html) {
            html = '<div class="alert alert-info">추천 결과가 없습니다.</div>';
        }

        resultsContainer.innerHTML = html;

        // Render charts
        this.renderCharts();
    }

    renderRecommendationSection(title, recommendations) {
        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">${title}</h3>
                </div>
                <div class="card-body">
                    ${recommendations.map((rec, idx) => `
                        <div style="border: 2px solid ${idx === 0 ? '#4CAF50' : '#E0E0E0'}; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; ${idx === 0 ? 'background: linear-gradient(135deg, #E8F5E9 0%, #F1F8F4 100%);' : ''}">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                                <div>
                                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                                        <h4 style="margin: 0; font-size: 1.2rem; color: #1976D2;">
                                            ${idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `${idx + 1}.`}
                                            ${formatDrugList(rec.drugs)}
                                        </h4>
                                        <span style="background: ${getEvidenceBadge(rec.evidence).color}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">
                                            ${getEvidenceBadge(rec.evidence).text}
                                        </span>
                                    </div>
                                    <p style="margin: 0.5rem 0; color: #666;">${rec.notes}</p>
                                </div>
                                <div style="text-align: right; min-width: 100px;">
                                    <div style="font-size: 1.5rem; font-weight: bold; color: #4CAF50;">
                                        ${formatScore(rec.score)}
                                    </div>
                                    <div style="font-size: 0.85rem; color: #999;">종합 점수</div>
                                </div>
                            </div>

                            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
                                <div style="text-align: center; padding: 0.75rem; background: white; border-radius: 8px;">
                                    <div style="font-size: 1.3rem; font-weight: bold; color: ${getScoreColor(rec.efficacy)};">
                                        ${formatScore(rec.efficacy * 100, 0)}%
                                    </div>
                                    <div style="font-size: 0.85rem; color: #666; margin-top: 0.25rem;">효능</div>
                                </div>
                                <div style="text-align: center; padding: 0.75rem; background: white; border-radius: 8px;">
                                    <div style="font-size: 1.3rem; font-weight: bold; color: ${getScoreColor(rec.synergy)};">
                                        ${formatScore(rec.synergy, 2)}
                                    </div>
                                    <div style="font-size: 0.85rem; color: #666; margin-top: 0.25rem;">시너지</div>
                                </div>
                                <div style="text-align: center; padding: 0.75rem; background: white; border-radius: 8px;">
                                    <div style="font-size: 1.3rem; font-weight: bold; color: ${getScoreColor(rec.toxicity, true)};">
                                        ${formatScore(rec.toxicity, 1)}
                                    </div>
                                    <div style="font-size: 0.85rem; color: #666; margin-top: 0.25rem;">독성</div>
                                </div>
                            </div>

                            ${rec.references && rec.references.length > 0 ? `
                                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #E0E0E0;">
                                    <strong style="font-size: 0.9rem; color: #666;">참고문헌:</strong>
                                    <div style="font-size: 0.85rem; color: #999; margin-top: 0.25rem;">
                                        ${rec.references.join(', ')}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    renderCharts() {
        // Placeholder for Plotly charts
        const chartsContainer = this.container.querySelector('#recommendations-results');

        // Add chart container
        const chartDiv = document.createElement('div');
        chartDiv.className = 'card';
        chartDiv.innerHTML = `
            <div class="card-header">
                <h3 class="card-title">📊 추천 비교 차트</h3>
            </div>
            <div class="card-body">
                <div id="recommendation-chart" style="height: 400px;"></div>
            </div>
        `;
        chartsContainer.appendChild(chartDiv);

        // Get all recommendations
        const allRecs = this.recommendations.hybrid_recommendations.length > 0
            ? this.recommendations.hybrid_recommendations
            : this.recommendations.paper_recommendations;

        if (allRecs.length === 0) return;

        // Prepare data for Plotly
        const drugLabels = allRecs.map(rec => formatDrugList(rec.drugs));
        const efficacy = allRecs.map(rec => rec.efficacy * 100);
        const synergy = allRecs.map(rec => rec.synergy * 10); // Scale for visibility
        const toxicity = allRecs.map(rec => rec.toxicity);

        const data = [
            {
                x: drugLabels,
                y: efficacy,
                name: '효능 (%)',
                type: 'bar',
                marker: { color: '#4CAF50' }
            },
            {
                x: drugLabels,
                y: synergy,
                name: '시너지 (x10)',
                type: 'bar',
                marker: { color: '#2196F3' }
            },
            {
                x: drugLabels,
                y: toxicity,
                name: '독성',
                type: 'bar',
                marker: { color: '#F44336' }
            }
        ];

        const layout = {
            title: '약물 조합 비교',
            barmode: 'group',
            xaxis: { title: '약물 조합' },
            yaxis: { title: '점수' },
            font: { family: 'Noto Sans KR, sans-serif' },
            margin: { t: 50, b: 100 }
        };

        Plotly.newPlot('recommendation-chart', data, layout, { responsive: true });
    }
}
