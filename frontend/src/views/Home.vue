<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const route = useRoute()
const router = useRouter()

const query = ref('')
const isLoading = ref(false)
const results = ref(null)
const error = ref(null)
const expandedSections = ref({})
const allSections = ref([])

const chapterSections = computed(() => {
  const chap = route.query.chapter
  if (!chap) return []
  return allSections.value.filter(s => s.chapter_number === chap)
})

const activeChapterTitle = computed(() => {
  if (!chapterSections.value.length) return ''
  return chapterSections.value[0].chapter_title
})

const exampleQuestions = [
  "What is the punishment for murder?",
  "What constitutes theft under BNS?",
  "What is the penalty for dowry harassment?",
  "Define criminal conspiracy",
  "What are the provisions for bail?"
]

async function search() {
  if (!query.value.trim()) return
  
  isLoading.value = true
  error.value = null
  results.value = null
  
  try {
    const response = await axios.post(`${API_URL}/search`, {
      query: query.value,
      chapter_filter: route.query.chapter || null,
      limit: 10
    })
    results.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || 'Failed to search'
  } finally {
    isLoading.value = false
  }
}

function toggleSection(sectionNumber) {
  expandedSections.value[sectionNumber] = !expandedSections.value[sectionNumber]
}

function goToSection(sectionNumber) {
  router.push(`/section/${sectionNumber}`)
}

function setQuery(q) {
  query.value = q
  search()
}

async function loadSections() {
  try {
    const response = await axios.get(`${API_URL}/sections`)
    allSections.value = response.data.sections || []
  } catch (err) {
    console.error('Failed to load sections:', err)
  }
}

watch(() => route.query.chapter, () => {
  results.value = null
  query.value = ''
})

onMounted(() => {
  loadSections()
})
</script>

<template>
  <div class="home-page">
    <header class="search-header">
      <div class="header-content">
        <h1>Bharatiya Nyaya Sanhita</h1>
        <p class="subtitle">Search and explore BNS sections with AI assistance</p>
      </div>
      
      <div class="search-container">
        <div class="search-box">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            v-model="query"
            type="text"
            placeholder="Ask a legal question..."
            @keyup.enter="search"
          />
          <button class="search-btn" @click="search" :disabled="isLoading">
            {{ isLoading ? 'Searching...' : 'Search' }}
          </button>
        </div>
      </div>

      <div class="examples">
        <span class="examples-label">Try:</span>
        <button 
          v-for="q in exampleQuestions" 
          :key="q"
          class="example-btn"
          @click="setQuery(q)"
        >
          {{ q }}
        </button>
      </div>
    </header>

    <div class="content-area">
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Searching BNS sections...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p> {{ error }} </p>
      </div>

      <div v-else-if="chapterSections.length && !results" class="chapter-listing">
        <h2 class="chapter-listing-title">
          Chapter {{ route.query.chapter }}: {{ activeChapterTitle }}
        </h2>
        <p class="chapter-listing-subtitle">{{ chapterSections.length }} sections in this chapter</p>
        <div class="sections-list">
          <div 
            v-for="section in chapterSections" 
            :key="section.section_number"
            class="section-card"
            @click="goToSection(section.section_number)"
          >
            <div class="section-header">
              <div class="section-info">
                <span class="section-number">Section {{ section.section_number }}</span>
                <span class="section-title">{{ section.section_title }}</span>
              </div>
              <svg class="expand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 18l6-6-6-6"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="results" class="results">
        <div class="answer-section">
          <h2>Answer</h2>
          <div class="answer-content" v-html="results.answer.replace(/\n/g, '<br>')"></div>
          
          <div v-if="results.citations.length" class="citations">
            <h3>Citations</h3>
            <ul>
              <li v-for="(cit, i) in results.citations" :key="i">{{ cit }}</li>
            </ul>
          </div>
        </div>

        <div class="sections-panel">
          <h2>Relevant Sections</h2>
          <div class="sections-list">
            <div 
              v-for="section in results.sections" 
              :key="section.section_number"
              class="section-card"
            >
              <div class="section-header" @click="toggleSection(section.section_number)">
                <div class="section-info">
                  <span class="section-number">Section {{ section.section_number }}</span>
                  <span class="section-title">{{ section.section_title }}</span>
                  <span class="chapter-badge">Chapter {{ section.chapter_number }}</span>
                </div>
                <svg 
                  class="expand-icon" 
                  :class="{ expanded: expandedSections[section.section_number] }"
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  stroke-width="2"
                >
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </div>
              
              <div v-if="expandedSections[section.section_number]" class="section-content">
                <p>{{ section.preview }}</p>
                <button class="view-full-btn" @click="goToSection(section.section_number)">
                  View Full Section
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
        </div>
        <h3>Search the BNS</h3>
        <p>Ask questions about Indian criminal law under the Bharatiya Nyaya Sanhita, 2023</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.search-header {
  text-align: center;
  margin-bottom: 2rem;
}

.header-content {
  margin-bottom: 2rem;
}

.header-content h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.5rem 0;
}

.subtitle {
  color: #64748b;
  font-size: 1rem;
  margin: 0;
}

.search-container {
  max-width: 720px;
  margin: 0 auto 1.5rem;
}

.search-box {
  display: flex;
  align-items: center;
  background: #fff;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.search-box:focus-within {
  border-color: #0284c7;
  box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.1);
}

.search-icon {
  width: 24px;
  height: 24px;
  color: #94a3b8;
  margin-left: 0.75rem;
}

.search-box input {
  flex: 1;
  border: none;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  color: #1e293b;
  background: transparent;
}

.search-box input:focus {
  outline: none;
}

.search-box input::placeholder {
  color: #94a3b8;
}

.search-btn {
  padding: 0.75rem 1.5rem;
  background: #0284c7;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.search-btn:hover:not(:disabled) {
  background: #0369a1;
}

.search-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.examples {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
  align-items: center;
}

.examples-label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.example-btn {
  padding: 0.375rem 0.75rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  font-size: 0.8125rem;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}

.example-btn:hover {
  background: #e0f2fe;
  border-color: #0284c7;
  color: #0284c7;
}

.content-area {
  min-height: 400px;
}

.chapter-listing {
  padding: 1rem 0;
}

.chapter-listing-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.25rem;
}

.chapter-listing-subtitle {
  font-size: 0.875rem;
  color: #94a3b8;
  margin: 0 0 1.5rem;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
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

.empty-icon {
  width: 80px;
  height: 80px;
  color: #cbd5e1;
  margin-bottom: 1.5rem;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-state h3 {
  font-size: 1.25rem;
  color: #475569;
  margin: 0 0 0.5rem;
}

.empty-state p {
  color: #94a3b8;
  margin: 0;
}

.results {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
}

.answer-section {
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e2e8f0;
}

.answer-section h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 1rem;
}

.answer-content {
  font-size: 0.9375rem;
  line-height: 1.75;
  color: #334155;
}

.citations {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.citations h3 {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #64748b;
  margin: 0 0 0.75rem;
}

.citations ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.citations li {
  font-size: 0.8125rem;
  color: #0284c7;
  padding: 0.375rem 0;
}

.sections-panel h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #1e3a5f;
  margin: 0 0 1rem;
}

.sections-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.section-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 1rem;
  cursor: pointer;
}

.section-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.section-number {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #0284c7;
}

.section-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #1e293b;
}

.chapter-badge {
  display: inline-block;
  font-size: 0.6875rem;
  font-weight: 500;
  color: #64748b;
  background: #f1f5f9;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  width: fit-content;
}

.expand-icon {
  width: 20px;
  height: 20px;
  color: #94a3b8;
  transition: transform 0.2s;
  flex-shrink: 0;
}

.expand-icon.expanded {
  transform: rotate(180deg);
}

.section-content {
  padding: 0 1rem 1rem;
  border-top: 1px solid #f1f5f9;
}

.section-content p {
  font-size: 0.8125rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 1rem;
}

.view-full-btn {
  padding: 0.5rem 1rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s;
}

.view-full-btn:hover {
  background: #e0f2fe;
  border-color: #0284c7;
  color: #0284c7;
}

@media (max-width: 900px) {
  .results {
    grid-template-columns: 1fr;
  }
}
</style>
