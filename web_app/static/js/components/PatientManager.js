/**
 * 환자 관리 컴포넌트
 */

import { patientsAPI } from '../utils/api.js';
import { formatDate, showNotification } from '../utils/helpers.js';

export class PatientManager {
    constructor(containerId, app) {
        this.container = document.getElementById(containerId);
        this.app = app;
        this.patients = [];
        this.selectedPatient = null;

        this.init();
    }

    async init() {
        await this.loadPatients();
        this.render();
    }

    async loadPatients() {
        try {
            this.patients = await patientsAPI.getAll();
        } catch (error) {
            showNotification('환자 목록 로드 실패', 'error');
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="header">
                <h1>👥 환자 관리</h1>
                <p>환자 등록 및 정보 관리</p>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">신규 환자 등록</h2>
                </div>
                <div class="card-body">
                    <form id="patient-form">
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                            <div class="form-group">
                                <label class="form-label">환자 ID *</label>
                                <input type="text" class="form-input" name="patient_id" required placeholder="P001">
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">이름 *</label>
                                <input type="text" class="form-input" name="name" required placeholder="홍길동">
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">나이</label>
                                <input type="number" class="form-input" name="age" min="0" max="150" placeholder="65">
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">성별</label>
                                <select class="form-select" name="gender">
                                    <option value="">선택</option>
                                    <option value="남성">남성</option>
                                    <option value="여성">여성</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">암 종류 *</label>
                                <select class="form-select" name="cancer_type" required>
                                    <option value="">선택</option>
                                    <option value="대장암">대장암</option>
                                    <option value="폐암">폐암</option>
                                    <option value="유방암">유방암</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label class="form-label">병기</label>
                                <select class="form-select" name="cancer_stage">
                                    <option value="">선택</option>
                                    <option value="I">I기</option>
                                    <option value="II">II기</option>
                                    <option value="III">III기</option>
                                    <option value="IV">IV기</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label">진단 날짜</label>
                            <input type="date" class="form-input" name="diagnosis_date">
                        </div>

                        <div class="form-group">
                            <label class="form-label">분자 마커 (JSON 형식)</label>
                            <textarea class="form-textarea" name="molecular_markers" placeholder='{"KRAS": "돌연변이", "BRAF": "야생형"}'></textarea>
                        </div>

                        <button type="submit" class="btn btn-primary">환자 등록</button>
                    </form>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">등록된 환자 (${this.patients.length}명)</h2>
                </div>
                <div class="card-body">
                    <div id="patients-list"></div>
                </div>
            </div>
        `;

        this.renderPatientsList();
        this.attachEventListeners();
    }

    renderPatientsList() {
        const listContainer = this.container.querySelector('#patients-list');

        if (this.patients.length === 0) {
            listContainer.innerHTML = '<p style="text-align: center; color: #999; padding: 2rem;">등록된 환자가 없습니다.</p>';
            return;
        }

        const tableHTML = `
            <table class="table">
                <thead>
                    <tr>
                        <th>환자 ID</th>
                        <th>이름</th>
                        <th>나이</th>
                        <th>성별</th>
                        <th>암 종류</th>
                        <th>병기</th>
                        <th>등록일</th>
                        <th>작업</th>
                    </tr>
                </thead>
                <tbody>
                    ${this.patients.map(p => `
                        <tr>
                            <td><strong>${p.patient_id}</strong></td>
                            <td>${p.name}</td>
                            <td>${p.age || '-'}</td>
                            <td>${p.gender || '-'}</td>
                            <td><span style="background: #E3F2FD; padding: 0.25rem 0.5rem; border-radius: 4px;">${p.cancer_type}</span></td>
                            <td>${p.cancer_stage || '-'}</td>
                            <td>${formatDate(p.created_at)}</td>
                            <td>
                                <button class="btn btn-secondary" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;" onclick="window.selectPatient(${p.id})">선택</button>
                                <button class="btn btn-danger" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;" onclick="window.deletePatient(${p.id})">삭제</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;

        listContainer.innerHTML = tableHTML;
    }

    attachEventListeners() {
        const form = this.container.querySelector('#patient-form');
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleSubmit(e.target);
        });

        // Global functions for patient actions
        window.selectPatient = async (id) => {
            try {
                const patient = await patientsAPI.getById(id);
                this.app.currentPatient = patient;
                showNotification(`환자 ${patient.name} 선택됨`, 'success');
                this.app.renderView('recommendations');
            } catch (error) {
                showNotification('환자 정보 로드 실패', 'error');
            }
        };

        window.deletePatient = async (id) => {
            if (!confirm('정말 이 환자를 삭제하시겠습니까?')) return;

            try {
                await patientsAPI.delete(id);
                showNotification('환자 삭제 완료', 'success');
                await this.loadPatients();
                this.renderPatientsList();
            } catch (error) {
                showNotification('환자 삭제 실패', 'error');
            }
        };
    }

    async handleSubmit(form) {
        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            if (value) {
                if (key === 'molecular_markers') {
                    try {
                        data[key] = JSON.parse(value);
                    } catch {
                        showNotification('분자 마커는 올바른 JSON 형식이어야 합니다', 'error');
                        return;
                    }
                } else if (key === 'age') {
                    data[key] = parseInt(value);
                } else if (key === 'diagnosis_date') {
                    data[key] = value ? new Date(value).toISOString() : null;
                } else {
                    data[key] = value;
                }
            }
        }

        try {
            await patientsAPI.create(data);
            showNotification('환자 등록 완료', 'success');
            form.reset();
            await this.loadPatients();
            this.renderPatientsList();
        } catch (error) {
            showNotification(`환자 등록 실패: ${error.message}`, 'error');
        }
    }
}
