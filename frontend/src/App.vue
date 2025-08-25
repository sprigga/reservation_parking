<template>
  <div class="app">
    <header class="header">
      <div class="container">
        <h1 class="title">
          <span class="icon">🅿️</span>
          和峻沐光公共車位預約系統
        </h1>
        <p class="subtitle">現代化智慧停車管理平台</p>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <section class="card reservation-section">
          <div class="card-header">
            <h2 class="card-title">
              <span class="card-icon">📅</span>
              預約表單
            </h2>
            <p class="card-description">快速預約您的專屬車位</p>
          </div>
          <div class="card-content">
            <ReservationForm />
          </div>
        </section>

        <section class="card admin-section">
          <div class="card-header">
            <h2 class="card-title">
              <span class="card-icon">⚙️</span>
              管理者模式
            </h2>
            <p class="card-description">車位與預約管理中心</p>
          </div>
          <div class="card-content">
            <Admin />
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup>
import ReservationForm from './pages/ReservationForm.vue'
import Admin from './pages/Admin.vue'
</script>

<style>
:root {
  /* Color Palette */
  --color-primary: #3b82f6;
  --color-primary-dark: #2563eb;
  --color-primary-light: #dbeafe;
  --color-secondary: #10b981;
  --color-secondary-dark: #059669;
  --color-danger: #ef4444;
  --color-danger-dark: #dc2626;
  --color-warning: #f59e0b;
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
  --color-white: #ffffff;
  
  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  --spacing-2xl: 3rem;
  
  /* Border Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
  --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
  
  /* Typography */
  --font-sans: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  
  /* Transitions */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 300ms ease-in-out;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  font-family: var(--font-sans);
  background: linear-gradient(135deg, var(--color-gray-50) 0%, var(--color-primary-light) 100%);
  min-height: 100vh;
  line-height: 1.6;
  color: var(--color-gray-800);
}

.app {
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

.header {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: var(--color-white);
  padding: var(--spacing-2xl) 0;
  box-shadow: var(--shadow-lg);
}

.title {
  font-size: var(--font-size-4xl);
  font-weight: 700;
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.icon {
  font-size: var(--font-size-3xl);
}

.subtitle {
  font-size: var(--font-size-lg);
  margin: var(--spacing-sm) 0 0 0;
  opacity: 0.9;
  font-weight: 300;
}

.main {
  padding: var(--spacing-2xl) 0;
}

.card {
  background: var(--color-white);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  margin-bottom: var(--spacing-2xl);
  overflow: hidden;
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}

.card-header {
  background: linear-gradient(135deg, var(--color-gray-50) 0%, var(--color-gray-100) 100%);
  padding: var(--spacing-xl);
  border-bottom: 1px solid var(--color-gray-200);
}

.card-title {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  color: var(--color-gray-800);
}

.card-icon {
  font-size: var(--font-size-xl);
}

.card-description {
  font-size: var(--font-size-base);
  color: var(--color-gray-600);
  margin: var(--spacing-sm) 0 0 0;
}

.card-content {
  padding: var(--spacing-xl);
}

/* Form Styles */
label {
  display: block;
  margin-bottom: var(--spacing-md);
  font-weight: 500;
  color: var(--color-gray-700);
  font-size: var(--font-size-sm);
}

input, select, textarea {
  width: 100%;
  padding: var(--spacing-md);
  border: 2px solid var(--color-gray-200);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  margin-top: var(--spacing-xs);
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgb(59 130 246 / 0.1);
}

input[type="checkbox"] {
  width: auto;
  margin-right: var(--spacing-sm);
}

button {
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  color: var(--color-white);
  border: none;
  padding: var(--spacing-md) var(--spacing-xl);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  box-shadow: var(--shadow-sm);
}

button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

button:active {
  transform: translateY(0);
}

button.btn-secondary {
  background: linear-gradient(135deg, var(--color-gray-500) 0%, var(--color-gray-600) 100%);
}

button.btn-success {
  background: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-secondary-dark) 100%);
}

button.btn-danger {
  background: linear-gradient(135deg, var(--color-danger) 0%, var(--color-danger-dark) 100%);
}

/* Table Styles */
.table {
  width: 100%;
  border-collapse: collapse;
  background: var(--color-white);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.table th {
  background: linear-gradient(135deg, var(--color-gray-100) 0%, var(--color-gray-200) 100%);
  padding: var(--spacing-lg);
  text-align: left;
  font-weight: 600;
  color: var(--color-gray-700);
  font-size: var(--font-size-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table td {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-gray-100);
  font-size: var(--font-size-sm);
}

.table tr:hover {
  background-color: var(--color-gray-50);
}

.table tr:last-child td {
  border-bottom: none;
}

/* Responsive Design */
@media (max-width: 768px) {
  .container {
    padding: 0 var(--spacing-md);
  }
  
  .header {
    padding: var(--spacing-xl) 0;
  }
  
  .title {
    font-size: var(--font-size-3xl);
    flex-direction: column;
    text-align: center;
    gap: var(--spacing-sm);
  }
  
  .card-header, .card-content {
    padding: var(--spacing-lg);
  }
  
  .table {
    font-size: var(--font-size-sm);
  }
  
  .table th, .table td {
    padding: var(--spacing-md);
  }
}

/* Animation */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card {
  animation: fadeIn 0.6s ease-out;
}

.reservation-section {
  animation-delay: 0.1s;
}

.admin-section {
  animation-delay: 0.2s;
}
</style>
