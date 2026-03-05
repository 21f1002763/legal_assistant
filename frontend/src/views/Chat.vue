<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const route = useRoute()

const messages = ref([
  {
    role: 'assistant',
    content: 'Hello! I\'m your BNS Legal Assistant. You can ask me questions about the Bharatiya Nyaya Sanhita, 2023. I\'ll provide answers with proper section citations.'
  }
])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)

const suggestedQuestions = [
  'What is the difference between murder and culpable homicide?',
  'What are the punishments for different types of theft?',
  'What constitutes criminal intimidation?',
  'Explain the provisions for attempt to commit suicide',
  'What are the provisions regarding mutual consent?'
]

async function sendMessage() {
  if (!inputMessage.value.trim() || isLoading.value) return
  
  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  
  messages.value.push({
    role: 'user',
    content: userMessage
  })
  
  isLoading.value = true
  
  try {
    const response = await axios.post(`${API_URL}/chat`, {
      messages: messages.value.map(m => ({ role: m.role, content: m.content })),
      context_sections: null
    })
    
    messages.value.push({
      role: 'assistant',
      content: response.data.message,
      citations: response.data.citations
    })
  } catch (err) {
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.',
      isError: true
    })
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function askSuggested(q) {
  inputMessage.value = q
  sendMessage()
}

function clearChat() {
  messages.value = [
    {
      role: 'assistant',
      content: 'Hello! I\'m your BNS Legal Assistant. You can ask me questions about the Bharatiya Nyaya Sanhita, 2023. I\'ll provide answers with proper section citations.'
    }
  ]
}

watch(() => route.query.section, (newSection) => {
  if (newSection) {
    inputMessage.value = `Tell me about Section ${newSection} of BNS`
  }
}, { immediate: true })

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="chat-page">
    <div class="chat-container">
      <header class="chat-header">
        <h1>AI Legal Assistant</h1>
        <p>Ask follow-up questions about BNS sections</p>
      </header>

      <div class="messages-area" ref="messagesContainer">
        <div 
          v-for="(msg, index) in messages" 
          :key="index"
          :class="['message', msg.role]"
        >
          <div class="message-avatar">
            <svg v-if="msg.role === 'user'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div class="message-content">
            <div class="message-text" v-html="msg.content.replace(/\n/g, '<br>')"></div>
            <div v-if="msg.citations && msg.citations.length" class="message-citations">
              <span class="citations-label">Sources:</span>
              <span v-for="(cit, i) in msg.citations" :key="i" class="citation">{{ cit }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="isLoading" class="message assistant">
          <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div class="message-content">
            <div class="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <div class="input-container">
          <input
            v-model="inputMessage"
            type="text"
            placeholder="Ask a follow-up question..."
            @keyup.enter="sendMessage"
            :disabled="isLoading"
          />
          <button 
            class="send-btn" 
            @click="sendMessage" 
            :disabled="!inputMessage.trim() || isLoading"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </div>
        
        <div class="suggestions">
          <span class="suggest-label">Suggested:</span>
          <button 
            v-for="q in suggestedQuestions" 
            :key="q"
            class="suggest-btn"
            @click="askSuggested(q)"
          >
            {{ q }}
          </button>
        </div>
      </div>

      <button class="clear-btn" @click="clearChat">
        Clear Chat
      </button>
    </div>
  </div>
</template>

<style scoped>
.chat-page {
  padding: 1.5rem;
  height: calc(100vh - 2rem);
  display: flex;
  flex-direction: column;
}

.chat-container {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.chat-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.chat-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e3a5f;
  margin: 0 0 0.25rem;
}

.chat-header p {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message {
  display: flex;
  gap: 0.75rem;
  max-width: 85%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: #0284c7;
}

.message.assistant .message-avatar {
  background: #1e3a5f;
}

.message-avatar svg {
  width: 20px;
  height: 20px;
  color: #fff;
}

.message-content {
  background: #f8fafc;
  border-radius: 12px;
  padding: 0.875rem 1rem;
}

.message.user .message-content {
  background: #e0f2fe;
}

.message-text {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: #1e293b;
}

.message-citations {
  margin-top: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid #e2e8f0;
}

.citations-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  margin-right: 0.5rem;
}

.citation {
  display: block;
  font-size: 0.75rem;
  color: #0284c7;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #94a3b8;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
}

.input-area {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.input-container {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.input-container input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 0.9375rem;
  color: #1e293b;
  transition: border-color 0.2s;
}

.input-container input:focus {
  outline: none;
  border-color: #0284c7;
}

.input-container input:disabled {
  background: #f8fafc;
}

.send-btn {
  width: 44px;
  height: 44px;
  background: #0284c7;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #0369a1;
}

.send-btn:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.send-btn svg {
  width: 20px;
  height: 20px;
  color: #fff;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.suggest-label {
  font-size: 0.75rem;
  color: #94a3b8;
}

.suggest-btn {
  padding: 0.25rem 0.75rem;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  font-size: 0.75rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}

.suggest-btn:hover {
  background: #e0f2fe;
  border-color: #0284c7;
  color: #0284c7;
}

.clear-btn {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  padding: 0.375rem 0.75rem;
  background: none;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.75rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s;
}

.clear-btn:hover {
  background: #fef2f2;
  border-color: #fecaca;
  color: #dc2626;
}
</style>
