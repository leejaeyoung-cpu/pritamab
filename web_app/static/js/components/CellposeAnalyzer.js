/**
 * Cellpose 이미지 분석 컴포넌트
 */

import { uploadAPI } from '../utils/api.js';
import { showNotification } from '../utils/helpers.js';

const API_BASE_URL = 'http://localhost:8000/api';

export class CellposeAnalyzer {
    constructor(containerId, app) {
        this.container = document.getElementById(containerId);
        this.app = app;
        this.currentImage = null;
        this.analysisResults = null;

        this.render();
    }

    render() {
        this.container.innerHTML = `
            <div class="header">
                <h1>🔬 Cellpose 이미지 분석</h1>
                <p>세포 이미지 자동 분석 및 정량화</p>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">이미지 업로드</h2>
                </div>
                <div class="card-body">
                    <div class="form-group">
                        <label class="form-label">세포 이미지 선택</label>
                        <input type="file" class="form-input" id="cellpose-file-input" accept=".png,.jpg,.jpeg,.tif,.tiff">
                        <p style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">
                            지원 형식: PNG, JPG, TIF (최대 16MB)
                        </p>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Cellpose 모델</label>
                        <select class="form-select" id="cellpose-model">
                            <option value="cyto2">Cyto2 (일반 세포)</option>
                            <option value="cyto">Cyto (세포질)</option>
                            <option value="nuclei">Nuclei (핵)</option>
                        </select>
                    </div>

                    <button class="btn btn-primary" id="analyze-button" disabled>
                        🔍 분석 시작
                    </button>

                    <div id="upload-progress" style="display: none; margin-top: 1rem;">
                        <div class="loading">
                            <div class="spinner"></div>
                            <p>분석 중... 잠시만 기다려주세요</p>
                        </div>
                    </div>
                </div>
            </div>

            <div id="analysis-results-container"></div>

            <div class="card glass-card">
                <div class="card-header">
                    <h2 class="card-title">📖 Cellpose란?</h2>
                </div>
                <div class="card-body">
                    <p><strong>Cellpose</strong>는 딥러닝 기반 세포 이미지 분할(segmentation) 알고리즘입니다.</p>
                    <ul style="line-height: 2; margin-top: 1rem;">
                        <li><strong>자동화:</strong> 세포를 자동으로 인식하고 경계를 감지</li>
                        <li><strong>정확도:</strong> 다양한 세포 유형과 현미경 이미지에 적용 가능</li>
                        <li><strong>정량화:</strong> 세포 수, 크기, 형태 등 자동 측정</li>
                        <li><strong>연구 활용:</strong> 암 세포 분석, 약물 효과 평가 등</li>
                    </ul>
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    attachEventListeners() {
        const fileInput = this.container.querySelector('#cellpose-file-input');
        const analyzeButton = this.container.querySelector('#analyze-button');
        const modelSelect = this.container.querySelector('#cellpose-model');

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.currentImage = e.target.files[0];
                analyzeButton.disabled = false;
                analyzeButton.textContent = `🔍 "${this.currentImage.name}" 분석`;
            } else {
                this.currentImage = null;
                analyzeButton.disabled = true;
                analyzeButton.textContent = '🔍 분석 시작';
            }
        });

        analyzeButton.addEventListener('click', async () => {
            const modelType = modelSelect.value;
            await this.analyzeImage(modelType);
        });
    }

    async analyzeImage(modelType) {
        if (!this.currentImage) {
            showNotification('이미지를 먼저 선택하세요', 'error');
            return;
        }

        const progressDiv = this.container.querySelector('#upload-progress');
        const analyzeButton = this.container.querySelector('#analyze-button');

        try {
            // Show loading
            progressDiv.style.display = 'block';
            analyzeButton.disabled = true;

            // Create form data
            const formData = new FormData();
            formData.append('file', this.currentImage);
            formData.append('model_type', modelType);

            // Call API
            const response = await fetch(`${API_BASE_URL}/analyze-image`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('분석 실패');
            }

            const result = await response.json();
            this.analysisResults = result;

            // Hide loading
            progressDiv.style.display = 'none';
            analyzeButton.disabled = false;

            // Show results
            this.renderResults(result);
            showNotification('분석 완료!', 'success');

        } catch (error) {
            progressDiv.style.display = 'none';
            analyzeButton.disabled = false;
            showNotification(`분석 오류: ${error.message}`, 'error');
        }
    }

    renderResults(result) {
        const resultsContainer = this.container.querySelector('#analysis-results-container');

        const analysis = result.analysis;
        const summary = result.summary;

        resultsContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">✅ 분석 결과</h2>
                </div>
                <div class="card-body">
                    <!-- Image Display -->
                    <div style="margin-bottom: 2rem;">
                        <h3 style="margin-bottom: 1rem;">업로드된 이미지</h3>
                        <img src="${result.image_url}" alt="Analyzed Image" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                    </div>

                    <!-- Summary -->
                    <div style="background: #E3F2FD; padding: 1.5rem; border-radius: 8px; margin-bottom: 2rem; white-space: pre-line;">
                        <h3 style="color: #1976D2; margin-bottom: 1rem;">📊 분석 요약</h3>
                        ${summary}
                    </div>

                    <!-- Detailed Metrics -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
                        <!-- Cell Count -->
                        <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 2rem; border-radius: 12px; text-align: center;">
                            <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">
                                ${analysis.cell_count}
                            </div>
                            <div style="font-size: 1.1rem; opacity: 0.9;">검출된 세포 수</div>
                        </div>

                        <!-- Average Size -->
                        <div style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); color: white; padding: 2rem; border-radius: 12px; text-align: center;">
                            <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">
                                ${analysis.average_cell_size.toFixed(1)}
                            </div>
                            <div style="font-size: 1.1rem; opacity: 0.9;">평균 크기 (μm²)</div>
                        </div>

                        <!-- Density -->
                        <div style="background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%); color: white; padding: 2rem; border-radius: 12px; text-align: center;">
                            <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">
                                ${(analysis.cell_density * 100).toFixed(2)}%
                            </div>
                            <div style="font-size: 1.1rem; opacity: 0.9;">세포 밀도</div>
                        </div>

                        <!-- Circularity -->
                        <div style="background: linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%); color: white; padding: 2rem; border-radius: 12px; text-align: center;">
                            <div style="font-size: 3rem; font-weight: bold; margin-bottom: 0.5rem;">
                                ${analysis.morphology_features.circularity.toFixed(2)}
                            </div>
                            <div style="font-size: 1.1rem; opacity: 0.9;">원형도</div>
                        </div>
                    </div>

                    <!-- Size Distribution -->
                    <div style="margin-top: 2rem; background: white; padding: 1.5rem; border-radius: 8px; border: 2px solid #E0E0E0;">
                        <h3 style="margin-bottom: 1rem; color: #1976D2;">크기 분포</h3>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; text-align: center;">
                            <div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #4CAF50;">
                                    ${analysis.size_distribution.min.toFixed(1)}
                                </div>
                                <div style="font-size: 0.9rem; color: #666;">최소 (μm²)</div>
                            </div>
                            <div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #2196F3;">
                                    ${analysis.size_distribution.median.toFixed(1)}
                                </div>
                                <div style="font-size: 0.9rem; color: #666;">중앙값 (μm²)</div>
                            </div>
                            <div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #FF9800;">
                                    ${analysis.size_distribution.max.toFixed(1)}
                                </div>
                                <div style="font-size: 0.9rem; color: #666;">최대 (μm²)</div>
                            </div>
                            <div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #9C27B0;">
                                    ${analysis.size_distribution.std.toFixed(1)}
                                </div>
                                <div style="font-size: 0.9rem; color: #666;">표준편차</div>
                            </div>
                        </div>
                    </div>

                    <!-- Morphology Features -->
                    <div style="margin-top: 2rem; background: white; padding: 1.5rem; border-radius: 8px; border: 2px solid #E0E0E0;">
                        <h3 style="margin-bottom: 1rem; color: #1976D2;">형태학적 특징</h3>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                            <div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #4CAF50;">
                                    ${analysis.morphology_features.circularity.toFixed(2)}
                                </div>
                                <div style="font-size: 0.9rem; color: #666;">원형도</div>
                                <div style="font-size: 0.8rem; color: #999;">1에 가까울수록 원형</div>
                            </div>
                            <div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #2196F3;">
                                    ${analysis.morphology_features.aspect_ratio.toFixed(2)}
                                </div>
                                <div style="font-size: 0.9rem; color: #666;">장축/단축 비율</div>
                                <div style="font-size: 0.8rem; color: #999;">1에 가까울수록 대칭</div>
                            </div>
                            <div>
                                <div style="font-size: 1.5rem; font-weight: bold; color: #FF9800;">
                                    ${analysis.morphology_features.solidity.toFixed(2)}
                                </div>
                                <div style="font-size: 0.9rem; color: #666;">Solidity</div>
                                <div style="font-size: 0.8rem; color: #999;">볼록도</div>
                            </div>
                        </div>
                    </div>

                    <!-- Chart Placeholder -->
                    <div id="cellpose-chart-container" style="margin-top: 2rem;"></div>
                </div>
            </div>
        `;

        // Render chart
        this.renderChart(analysis);
    }

    renderChart(analysis) {
        const chartContainer = this.container.querySelector('#cellpose-chart-container');

        if (!chartContainer) return;

        chartContainer.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">📊 분석 데이터 시각화</h3>
                </div>
                <div class="card-body">
                    <div id="cellpose-chart" style="height: 400px;"></div>
                </div>
            </div>
        `;

        // Create Plotly chart
        const data = [
            {
                x: ['세포 수', '평균 크기', '밀도 (×100)', '원형도 (×100)'],
                y: [
                    analysis.cell_count,
                    analysis.average_cell_size,
                    analysis.cell_density * 100,
                    analysis.morphology_features.circularity * 100
                ],
                type: 'bar',
                marker: {
                    color: ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']
                }
            }
        ];

        const layout = {
            title: '세포 분석 주요 지표',
            yaxis: { title: '값' },
            font: { family: 'Noto Sans KR, sans-serif' },
            showlegend: false
        };

        Plotly.newPlot('cellpose-chart', data, layout, { responsive: true });
    }
}
