<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const route = useRoute()
const router = useRouter()

const section = ref(null)
const isLoading = ref(true)
const error = ref(null)

async function loadSection() {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await axios.get(`${API_URL}/sections/${route.params.number}`)
    section.value = response.data
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = 'Section not found'
    } else {
      error.value = err.response?.data?.detail || err.message || 'Failed to load section'
    }
  } finally {
    isLoading.value = false
  }
}

function goBack() {
  router.push('/')
}

onMounted(() => {
  loadSection()
})

watch(() => route.params.number, () => {
  loadSection()
})
</script>

<template>
  <div class="section-page">
    <div class="section-container">
      <button class="back-btn" @click="goBack">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5"/>
          <path d="M12 19l-7-7 7-7"/>
        </svg>
        Back to Search
      </button>

      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading section...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
      </div>

      <div v-else-if="section" class="section-content">
        <header class="section-header">
          <div class="section-meta">
            <span class="act-badge">{{ section.act }}</span>
            <span class="chapter-info">Chapter {{ section.chapter_number }}: {{ section.chapter_title }}</span>
          </div>
          <h1>Section {{ section.section_number }}</h1>
          <h2 class="section-title">{{ section.section_title }}</h2>
        </header>

        <div class="legal-text">
          <h3>Legal Text</h3>
          <div class="text-content">
            {{ section.text }}
          </div>
        </div>

        <div class="section-actions">
          <button class="action-btn" @click="router.push({ path: '/chat', query: { section: section.section_number } })">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            Ask about this section
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.section-page {
  padding: 2rem;
  max-width: 900px;
  margin: 0 auto;
}

.section-container {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 2rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  margin-bottom: 1.5rem;
  transition: all 0.15s;
}

.back-btn:hover {
  background: #f1f5f9;
  color: #1e3a5f;
}

.back-btn svg {
  width: 18px;
  height: 18px;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e2e8f0;
  border-top-color: #0284c7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-state {
  color: #dc2626;
}

.section-header {
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.section-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.act-badge {
  font-size: 0.75rem;
  font-weight: 600;
  color: #0284c7;
  background: #e0f2fe;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
}

.chapter-info {
  font-size: 0.875rem;
  color: #64748b;
}

.section-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.5rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #334155;
  margin: 0;
}

.legal-text {
  margin-bottom: 2rem;
}

.legal-text h3 {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 1rem;
}

.text-content {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 1.5rem;
  font-size: 1rem;
  line-height: 1.8;
  color: #1e293b;
  white-space: pre-wrap;
}

.section-actions {
  display: flex;
  gap: 1rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: #0284c7;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #0369a1;
}

.action-btn svg {
  width: 20px;
  height: 20px;
}
</style>
