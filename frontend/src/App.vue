<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const route = useRoute()
const router = useRouter()

const sections = ref([])
const chapters = ref([])
const loading = ref(false)
const selectedChapter = ref('')
const selectedSection = ref('')

const navItems = [
  { path: '/', label: 'Search', icon: 'search' },
  { path: '/chat', label: 'AI Assistant', icon: 'chat' }
]

const filteredSections = computed(() => {
  if (!selectedChapter.value) return sections.value
  return sections.value.filter(s => s.chapter_number === selectedChapter.value)
})

async function loadFilters() {
  try {
    const response = await axios.get(`${API_URL}/sections`)
    sections.value = response.data.sections || []
    chapters.value = response.data.chapters || []
  } catch (err) {
    console.error('Failed to load filters:', err)
  }
}

function navigateTo(path) {
  router.push(path)
}

function filterByChapter() {
  selectedSection.value = ''
  if (selectedChapter.value) {
    router.push({ path: '/', query: { chapter: selectedChapter.value } })
  } else {
    router.push({ path: '/' })
  }
}

function filterBySection() {
  if (selectedSection.value) {
    router.push({ path: `/section/${selectedSection.value}` })
  }
}

onMounted(() => {
  loadFilters()
})
</script>

<template>
  <div class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="#1e3a5f"/>
            <path d="M8 8h4v16H8V8zm6 0h4v12h-4V8zm6 0h4v16h-4V8z" fill="#fff"/>
          </svg>
          <span class="logo-text">BNS Legal</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="item in navItems"
          :key="item.path"
          :class="['nav-item', { active: route.path === item.path }]"
          @click="navigateTo(item.path)"
        >
          <svg v-if="item.icon === 'search'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          <svg v-if="item.icon === 'chat'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          {{ item.label }}
        </button>
      </nav>

      <div class="sidebar-filters">
        <h3 class="filter-title">Filters</h3>
        
        <div class="filter-group">
          <label>Chapter</label>
          <select v-model="selectedChapter" @change="filterByChapter">
            <option value="">All Chapters</option>
            <option v-for="chap in chapters" :key="chap.chapter_number" :value="chap.chapter_number">
              Chapter {{ chap.chapter_number }}: {{ chap.chapter_title }}
            </option>
          </select>
        </div>
      </div>

      <div class="sidebar-footer">
        <p class="disclaimer">This tool provides legal information, not legal advice.</p>
      </div>
    </aside>

    <main class="main-content">
      <router-view :key="$route.fullPath" />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: #f8fafc;
}

.sidebar {
  width: 280px;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
}

.sidebar-nav {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border: none;
  background: none;
  border-radius: 8px;
  font-size: 0.9375rem;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
  text-align: left;
  width: 100%;
}

.nav-item:hover {
  background: #f1f5f9;
  color: #1e3a5f;
}

.nav-item.active {
  background: #e0f2fe;
  color: #0284c7;
}

.nav-icon {
  width: 20px;
  height: 20px;
}

.sidebar-filters {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  flex: 1;
  overflow-y: auto;
}

.filter-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 1rem 0;
}

.filter-group {
  margin-bottom: 1rem;
}

.filter-group label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #475569;
  margin-bottom: 0.375rem;
}

.filter-group select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.8125rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #fff;
  color: #334155;
  cursor: pointer;
}

.filter-group select:focus {
  outline: none;
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.1);
}

.sidebar-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.sidebar-footer .disclaimer {
  font-size: 0.6875rem;
  color: #94a3b8;
  text-align: center;
  margin: 0;
  line-height: 1.5;
}

.main-content {
  flex: 1;
  margin-left: 280px;
  min-height: 100vh;
}
</style>
