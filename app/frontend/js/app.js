/**
 * Daily Intelligence - Client-Side Orchestrator
 * High performance, zero framework, mobile-first vanilla JS.
 */

const state = {
  language: localStorage.getItem("daily_intel_lang") || "en",
  theme: localStorage.getItem("daily_intel_theme") || "light",
  currentCategory: "all",
  articles: [],
  briefing: null,
  health: null
};

// Initialize Application on DOM Ready
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initLanguage();
  setupNavigation();
  loadHealth();
});

function initTheme() {
  document.documentElement.setAttribute("data-theme", state.theme);
  const themeIcon = document.getElementById("theme-icon");
  if (themeIcon) {
    themeIcon.textContent = state.theme === "dark" ? "☀️" : "🌙";
  }
}

function toggleTheme() {
  state.theme = state.theme === "dark" ? "light" : "dark";
  localStorage.setItem("daily_intel_theme", state.theme);
  initTheme();
}

function initLanguage() {
  document.querySelectorAll(".lang-btn").forEach(btn => btn.classList.remove("active"));
  const activeBtn = document.getElementById(`lang-${state.language}`);
  if (activeBtn) activeBtn.classList.add("active");
  document.documentElement.lang = state.language;
}

function setLanguage(lang) {
  state.language = lang;
  localStorage.setItem("daily_intel_lang", lang);
  initLanguage();
  renderBriefing();
  renderArticles();
}

function setupNavigation() {
  const nav = document.getElementById("category-nav");
  if (!nav) return;

  nav.addEventListener("click", (e) => {
    if (e.target.classList.contains("cat-link")) {
      e.preventDefault();
      document.querySelectorAll(".cat-link").forEach(el => el.classList.remove("active"));
      e.target.classList.add("active");
      const cat = e.target.getAttribute("data-category");
      state.currentCategory = cat;
      renderArticles();
    }
  });
}

async function loadHealth() {
  try {
    const res = await fetch("/api/health");
    if (res.ok) {
      const data = await res.json();
      state.health = data;
      updateStatusHeader(data);
    }
  } catch (err) {
    console.warn("Health probe error:", err);
  }
}

function updateStatusHeader(healthData) {
  const tsEl = document.getElementById("briefing-timestamp");
  if (tsEl && healthData) {
    const d = new Date(healthData.timestamp);
    tsEl.textContent = `System: ${healthData.status.toUpperCase()} | Sources: ${healthData.stats.sources_active} | Articles: ${healthData.stats.articles}`;
  }
}

function renderBriefing() {
  const titleEl = document.getElementById("briefing-title");
  const summaryEl = document.getElementById("briefing-summary");
  if (!titleEl || !summaryEl) return;

  if (state.language === "kn") {
    titleEl.textContent = "ದೈನಂದಿನ ಇಂಟೆಲಿಜೆನ್ಸ್ ಬ್ರೀಫಿಂಗ್";
    summaryEl.textContent = state.briefing?.summary_kn || "ತಾಜಾ ವರದಿಗಳು ಸಂಗ್ರಹವಾಗುತ್ತಿವೆ...";
  } else {
    titleEl.textContent = "Intelligence Briefing";
    summaryEl.textContent = state.briefing?.summary_en || "Daily synthesized analysis of major global, national, and regional events.";
  }
}

function renderArticles() {
  const container = document.getElementById("articles-container");
  if (!container) return;

  if (!state.articles || state.articles.length === 0) {
    container.innerHTML = `
      <div class="state-box">
        <p>No articles found for the selected category.</p>
        <p style="font-size: 0.85rem; margin-top: 8px;">Run ingestion or wait for scheduled 6:00 AM / 6:00 PM briefing.</p>
      </div>
    `;
    return;
  }

  // Filter if needed
  const filtered = state.currentCategory === "all"
    ? state.articles
    : state.articles.filter(a => a.categories && a.categories.some(c => c.id === state.currentCategory));

  if (filtered.length === 0) {
    container.innerHTML = `<div class="state-box"><p>No articles in this category yet.</p></div>`;
    return;
  }

  const isKn = state.language === "kn";

  container.innerHTML = filtered.map(a => {
    const headline = a.headline;
    const summary = isKn ? (a.summary_kn || a.summary_en || a.short_description) : (a.summary_en || a.short_description);
    const whyMatters = isKn ? (a.why_it_matters_kn || a.why_it_matters_en) : a.why_it_matters_en;
    const pubDate = a.published_at ? new Date(a.published_at).toLocaleDateString() : "";

    return `
      <article class="article-card ${isKn ? 'kannada-text' : ''}">
        <div class="article-header">
          <div class="article-meta">
            <span class="publisher-badge">${escapeHtml(a.publisher)}</span>
            <span>•</span>
            <span>${pubDate}</span>
          </div>
          <h4 class="article-title">
            <a href="${escapeHtml(a.original_url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(headline)}</a>
          </h4>
          <p class="article-summary">${escapeHtml(summary || "")}</p>
          ${whyMatters ? `
            <div class="why-matters-box">
              <strong>${isKn ? 'ಇದು ಏಕೆ ಮುಖ್ಯ:' : 'Why It Matters:'}</strong>
              ${escapeHtml(whyMatters)}
            </div>
          ` : ''}
        </div>
        <div class="article-footer">
          <div class="category-tags">
            ${(a.categories || []).map(c => `
              <span class="category-tag">${isKn ? escapeHtml(c.name_kn) : escapeHtml(c.name_en)}</span>
            `).join('')}
          </div>
          <div class="article-actions">
            <button class="btn-bookmark ${a.is_bookmarked ? 'bookmarked' : ''}" onclick="toggleBookmark('${a.id}')" title="Bookmark">
              ★
            </button>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

function manualRefresh() {
  const btn = document.getElementById("refresh-btn");
  const label = document.getElementById("refresh-label");
  if (btn && label) {
    btn.disabled = true;
    label.textContent = "Updating...";
    fetch("/api/health")
      .then(r => r.json())
      .then(d => {
        updateStatusHeader(d);
        setTimeout(() => {
          btn.disabled = false;
          label.textContent = "Refresh";
        }, 1500);
      })
      .catch(() => {
        btn.disabled = false;
        label.textContent = "Refresh";
      });
  }
}

function toggleBookmark(articleId) {
  const article = state.articles.find(a => a.id === articleId);
  if (article) {
    article.is_bookmarked = !article.is_bookmarked;
    renderArticles();
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
