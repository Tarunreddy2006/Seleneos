/**
 * Daily Intelligence - Client Application
 * Modular, vanilla JavaScript with zero external runtime dependencies.
 */

const appState = {
  language: localStorage.getItem("daily_intel_lang") || "en",
  theme: localStorage.getItem("daily_intel_theme") || "light",
  currentView: "feed",
  currentCategory: "all",
  searchQuery: "",
  articles: [],
  briefing: null,
  featuredConcept: null,
  activeTopic: null
};

// Lifecycle Bootstrap
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initLanguage();
  setupCategoryNav();
  loadHealthTelemetry();
  loadLatestBriefing();
  loadConceptOfTheDay();
  loadArticles();
});

function initTheme() {
  document.documentElement.setAttribute("data-theme", appState.theme);
  const icon = document.getElementById("theme-icon");
  if (icon) icon.textContent = appState.theme === "dark" ? "☀️" : "🌙";
}

function toggleTheme() {
  appState.theme = appState.theme === "dark" ? "light" : "dark";
  localStorage.setItem("daily_intel_theme", appState.theme);
  initTheme();
}

function initLanguage() {
  document.querySelectorAll(".lang-btn").forEach(b => b.classList.remove("active"));
  const btn = document.getElementById(`lang-${appState.language}`);
  if (btn) btn.classList.add("active");
  document.documentElement.lang = appState.language;
}

function setLanguage(lang) {
  appState.language = lang;
  localStorage.setItem("daily_intel_lang", lang);
  initLanguage();
  renderBriefing();
  renderConceptSpotlight();
  renderArticles();
  if (appState.activeTopic) renderTopicDetail(appState.activeTopic);
}

function switchView(viewName) {
  appState.currentView = viewName;
  document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
  document.querySelectorAll(".view-panel").forEach(p => p.classList.remove("active"));

  const tabBtn = document.getElementById(`tab-${viewName}`);
  if (tabBtn) tabBtn.classList.add("active");

  const catNav = document.getElementById("category-nav-bar");

  if (viewName === "feed") {
    document.getElementById("view-feed")?.classList.add("active");
    if (catNav) catNav.style.display = "block";
    loadArticles();
  } else if (viewName === "bookmarks") {
    document.getElementById("view-feed")?.classList.add("active");
    if (catNav) catNav.style.display = "none";
    loadArticles(true);
  } else if (viewName === "education") {
    document.getElementById("view-education")?.classList.add("active");
    if (catNav) catNav.style.display = "none";
    loadEducationalTopics();
  }
}

function setupCategoryNav() {
  const nav = document.getElementById("category-nav");
  if (!nav) return;

  nav.addEventListener("click", (e) => {
    if (e.target.classList.contains("cat-link")) {
      e.preventDefault();
      document.querySelectorAll(".cat-link").forEach(el => el.classList.remove("active"));
      e.target.classList.add("active");
      appState.currentCategory = e.target.getAttribute("data-category") || "all";
      loadArticles();
    }
  });
}

// Health Telemetry
async function loadHealthTelemetry() {
  try {
    const res = await fetch("/api/health");
    if (res.ok) {
      const data = await res.json();
      const tsEl = document.getElementById("briefing-timestamp");
      if (tsEl) {
        tsEl.textContent = `Schedule: 6 AM / 6 PM IST | Active Sources: ${data.stats.sources_active} | Articles: ${data.stats.articles}`;
      }
    }
  } catch (err) {
    console.debug("Telemetry unavailable:", err);
  }
}

// Briefing
async function loadLatestBriefing() {
  try {
    const res = await fetch("/api/briefings/latest");
    if (res.ok) {
      appState.briefing = await res.json();
      renderBriefing();
    }
  } catch (err) {
    console.debug("Briefing fetch error:", err);
  }
}

function renderBriefing() {
  const titleEl = document.getElementById("briefing-title");
  const summaryEl = document.getElementById("briefing-summary");
  if (!titleEl || !summaryEl || !appState.briefing) return;

  const isKn = appState.language === "kn";
  titleEl.textContent = isKn ? "ದೈನಂದಿನ ಇಂಟೆಲಿಜೆನ್ಸ್ ಬ್ರೀಫಿಂಗ್" : "Daily Intelligence Briefing";
  summaryEl.textContent = isKn
    ? (appState.briefing.summary_kn || appState.briefing.summary_en)
    : (appState.briefing.summary_en || "Briefing compilation scheduled for 6:00 AM and 6:00 PM IST.");
}

// Concept of the Day Spotlight
async function loadConceptOfTheDay() {
  try {
    const res = await fetch("/api/education/concept-of-the-day");
    if (res.ok) {
      appState.featuredConcept = await res.json();
      appState.activeTopic = appState.featuredConcept;
      renderConceptSpotlight();
    }
  } catch (err) {
    console.debug("Concept load error:", err);
  }
}

function renderConceptSpotlight() {
  const titleEl = document.getElementById("concept-title");
  const defEl = document.getElementById("concept-def");
  if (!titleEl || !defEl || !appState.featuredConcept) return;

  const isKn = appState.language === "kn";
  titleEl.textContent = isKn ? appState.featuredConcept.title_kn : appState.featuredConcept.title_en;
  defEl.textContent = isKn ? appState.featuredConcept.simple_definition_kn : appState.featuredConcept.simple_definition_en;
}

// Articles Feed
async function loadArticles(bookmarkedOnly = false) {
  const container = document.getElementById("articles-container");
  if (container) {
    container.innerHTML = `<div class="state-box"><div class="spinner"></div><p>Loading intelligence stream...</p></div>`;
  }

  let url = `/api/articles?limit=30`;
  if (appState.currentCategory && appState.currentCategory !== "all") {
    url += `&category=${encodeURIComponent(appState.currentCategory)}`;
  }
  if (bookmarkedOnly) {
    url += `&bookmarked=true`;
  }

  try {
    const res = await fetch(url);
    if (res.ok) {
      const data = await res.json();
      appState.articles = data.articles || [];
      renderArticles();
    }
  } catch (err) {
    if (container) {
      container.innerHTML = `<div class="state-box"><p>Unable to load articles right now.</p></div>`;
    }
  }
}

function renderArticles() {
  const container = document.getElementById("articles-container");
  if (!container) return;

  if (appState.articles.length === 0) {
    container.innerHTML = `
      <div class="state-box">
        <p>No intelligence articles available in this view.</p>
        <p style="font-size: 0.85rem; margin-top: 8px;">Trigger Refresh or wait for scheduled 6:00 AM / 6:00 PM briefing.</p>
      </div>
    `;
    return;
  }

  const isKn = appState.language === "kn";

  container.innerHTML = appState.articles.map(a => {
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
          <h4 class="article-title" onclick="openArticleModal('${a.id}')">
            ${escapeHtml(headline)}
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
            <button class="btn-detail" onclick="openArticleModal('${a.id}')">Read Full →</button>
            <button class="btn-bookmark ${a.is_bookmarked ? 'bookmarked' : ''}" onclick="toggleBookmark('${a.id}')" title="Bookmark">
              ★
            </button>
          </div>
        </div>
      </article>
    `;
  }).join('');
}

// Article Detail Modal
async function openArticleModal(articleId) {
  const modal = document.getElementById("article-modal");
  if (!modal) return;

  try {
    const res = await fetch(`/api/articles/${articleId}`);
    if (res.ok) {
      const art = await res.json();
      const isKn = appState.language === "kn";

      document.getElementById("modal-publisher").textContent = art.publisher;
      document.getElementById("modal-headline").textContent = art.headline;
      document.getElementById("modal-meta").textContent = `Published: ${art.published_at ? new Date(art.published_at).toLocaleString() : 'Recent'} | Read: ${art.read_count} times`;

      document.getElementById("modal-summary").textContent = isKn ? (art.summary_kn || art.summary_en) : art.summary_en;
      document.getElementById("modal-detailed").textContent = isKn ? (art.detailed_summary_kn || art.detailed_summary_en) : (art.detailed_summary_en || art.summary_en);

      document.getElementById("modal-why-heading").textContent = isKn ? "ಇದು ಏಕೆ ಮುಖ್ಯ" : "Why It Matters";
      document.getElementById("modal-why-matters").textContent = isKn ? (art.why_it_matters_kn || art.why_it_matters_en) : art.why_it_matters_en;

      const factsList = document.getElementById("modal-facts");
      factsList.innerHTML = (art.important_facts || []).map(f => `<li>${escapeHtml(f)}</li>`).join('');
      document.getElementById("modal-facts-section").style.display = (art.important_facts && art.important_facts.length > 0) ? "block" : "none";

      const bgText = isKn ? (art.background_kn || art.background_en) : art.background_en;
      document.getElementById("modal-background").textContent = bgText || "";
      document.getElementById("modal-bg-section").style.display = bgText ? "block" : "none";

      const linkEl = document.getElementById("modal-original-link");
      linkEl.href = art.original_url;

      modal.classList.add("open");
    }
  } catch (err) {
    console.error("Modal load failed:", err);
  }
}

function closeArticleModal() {
  document.getElementById("article-modal")?.classList.remove("open");
}

async function toggleBookmark(articleId) {
  try {
    const res = await fetch(`/api/articles/${articleId}/bookmark`, { method: "POST" });
    if (res.ok) {
      const data = await res.json();
      const art = appState.articles.find(a => a.id === articleId);
      if (art) {
        art.is_bookmarked = data.is_bookmarked;
        renderArticles();
      }
    }
  } catch (err) {
    console.error("Bookmark toggle failed:", err);
  }
}

// Search
function handleSearch(event) {
  if (event.key === "Enter") executeSearch();
}

async function executeSearch() {
  const query = document.getElementById("search-input")?.value?.trim();
  if (!query) {
    loadArticles();
    return;
  }

  const container = document.getElementById("articles-container");
  if (container) {
    container.innerHTML = `<div class="state-box"><div class="spinner"></div><p>Searching intelligence records...</p></div>`;
  }

  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    if (res.ok) {
      const data = await res.json();
      appState.articles = data.articles || [];
      renderArticles();
    }
  } catch (err) {
    console.error("Search failed:", err);
  }
}

// Educational Topics
async function loadEducationalTopics() {
  try {
    const res = await fetch("/api/education/topics");
    if (res.ok) {
      const data = await res.json();
      renderTopicsList(data.topics || []);
      if (appState.activeTopic) {
        renderTopicDetail(appState.activeTopic);
      } else if (data.topics.length > 0) {
        loadTopicDetail(data.topics[0].id);
      }
    }
  } catch (err) {
    console.error("Topics load failed:", err);
  }
}

async function loadTopicDetail(topicId) {
  try {
    const res = await fetch(`/api/education/topics/${topicId}`);
    if (res.ok) {
      appState.activeTopic = await res.json();
      renderTopicDetail(appState.activeTopic);
    }
  } catch (err) {
    console.error("Topic detail failed:", err);
  }
}

function renderTopicDetail(topic) {
  const card = document.getElementById("topic-detail-card");
  if (!card || !topic) return;

  const isKn = appState.language === "kn";
  const title = isKn ? topic.title_kn : topic.title_en;
  const def = isKn ? topic.simple_definition_kn : topic.simple_definition_en;
  const bg = isKn ? topic.background_kn : topic.background_en;
  const works = isKn ? topic.how_it_works_kn : topic.how_it_works_en;
  const ex = isKn ? topic.real_world_example_kn : topic.real_world_example_en;

  card.innerHTML = `
    <h2 style="font-family: var(--font-serif); font-size: 1.6rem; margin-bottom: 12px;">${escapeHtml(title)}</h2>
    <div style="background-color: var(--accent-soft); padding: 14px; border-radius: var(--radius-md); margin-bottom: 20px;">
      <strong>${isKn ? 'ಸರಳ ವ್ಯಾಖ್ಯಾನ:' : 'Core Definition:'}</strong>
      <p style="margin-top: 4px; font-size: 1.05rem;">${escapeHtml(def)}</p>
    </div>

    <div style="margin-bottom: 20px;">
      <h4 style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase;">${isKn ? 'ಹಿನ್ನೆಲೆ' : 'Background & Context'}</h4>
      <p style="font-size: 1.02rem; line-height: 1.7; margin-top: 4px;">${escapeHtml(bg)}</p>
    </div>

    <div style="margin-bottom: 20px;">
      <h4 style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase;">${isKn ? 'ಇದು ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ?' : 'How It Works'}</h4>
      <p style="font-size: 1.02rem; line-height: 1.7; margin-top: 4px;">${escapeHtml(works)}</p>
    </div>

    <div style="margin-bottom: 20px;">
      <h4 style="color: var(--text-muted); font-size: 0.9rem; text-transform: uppercase;">${isKn ? 'ನೈಜ ಉದಾಹರಣೆ' : 'Real-World Example'}</h4>
      <p style="font-size: 1.02rem; line-height: 1.7; margin-top: 4px;">${escapeHtml(ex)}</p>
    </div>

    ${topic.knowledge_check && topic.knowledge_check.length > 0 ? `
      <div style="border-top: 1px solid var(--border-color); padding-top: 20px; margin-top: 24px;">
        <h4 style="margin-bottom: 12px;">🧠 ${isKn ? 'ಜ್ಞಾನ ಪರೀಕ್ಷೆ (Knowledge Check)' : 'Knowledge Check'}</h4>
        ${topic.knowledge_check.map((q, qIdx) => `
          <div style="margin-bottom: 16px;">
            <p style="font-weight: 600; margin-bottom: 8px;">${escapeHtml(q.question)}</p>
            <div>
              ${q.options.map((opt, optIdx) => `
                <button class="quiz-option" id="quiz-opt-${qIdx}-${optIdx}" onclick="checkAnswer(${qIdx}, ${optIdx}, ${q.correct_index}, '${escapeHtml(q.explanation)}')">
                  ${escapeHtml(opt)}
                </button>
              `).join('')}
            </div>
            <div id="quiz-feedback-${qIdx}" style="display: none; padding: 10px; border-radius: var(--radius-sm); margin-top: 8px; font-size: 0.9rem;"></div>
          </div>
        `).join('')}
      </div>
    ` : ''}
  `;
}

function checkAnswer(qIdx, selectedIdx, correctIdx, explanation) {
  const feedback = document.getElementById(`quiz-feedback-${qIdx}`);
  const btn = document.getElementById(`quiz-opt-${qIdx}-${selectedIdx}`);
  if (!feedback || !btn) return;

  if (selectedIdx === correctIdx) {
    btn.classList.add("correct");
    feedback.style.display = "block";
    feedback.style.backgroundColor = "#dcfce7";
    feedback.style.color = "#15803d";
    feedback.innerHTML = `<strong>✓ Correct!</strong> ${explanation}`;
  } else {
    btn.classList.add("incorrect");
    feedback.style.display = "block";
    feedback.style.backgroundColor = "#fee2e2";
    feedback.style.color = "#b91c1c";
    feedback.innerHTML = `<strong>✕ Incorrect.</strong> ${explanation}`;
  }
}

function renderTopicsList(topics) {
  const container = document.getElementById("topics-list-container");
  if (!container) return;

  const isKn = appState.language === "kn";
  container.innerHTML = topics.map(t => `
    <div class="topic-summary-card" onclick="loadTopicDetail('${t.id}')">
      <h5 style="font-family: var(--font-serif); font-size: 1.05rem; margin-bottom: 6px;">${isKn ? escapeHtml(t.title_kn) : escapeHtml(t.title_en)}</h5>
      <span style="font-size: 0.78rem; color: var(--accent-color); font-weight: 600;">View Concept Analysis →</span>
    </div>
  `).join('');
}

// Manual Ingestion Trigger
async function triggerManualRefresh() {
  const btn = document.getElementById("refresh-btn");
  const label = document.getElementById("refresh-label");
  if (btn && label) {
    btn.disabled = true;
    label.textContent = "Updating...";

    try {
      const res = await fetch("/api/sources/refresh", { method: "POST" });
      if (res.ok) {
        const data = await res.json();
        label.textContent = `+${data.articles_added} New`;
        loadArticles();
        loadHealthTelemetry();
      }
    } catch (err) {
      label.textContent = "Offline";
    } finally {
      setTimeout(() => {
        btn.disabled = false;
        label.textContent = "Refresh";
      }, 3000);
    }
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
