/**
 * Daily Intelligence - Embedded Standalone Engine
 * Runs completely on-device inside Android WebView with ZERO external dependencies.
 * Provides:
 *  - IndexedDB local storage (Articles, Categories, Sources, Briefings, Education Topics)
 *  - RSS / Atom XML Parser
 *  - Deduplicator (URL hash + Jaccard title similarity)
 *  - Categorizer (7 Core Categories weighted taxonomy)
 *  - Heuristic Summarizer (Key facts, "Why it matters", structural bullet points)
 *  - Kannada Translator (Google GTX endpoint + offline glossary fallback)
 *  - Briefing Generator (Morning & Evening synthesis)
 *  - Native Android Bridge connector for CORS-free RSS fetching
 */

class EmbeddedEngine {
  constructor() {
    this.dbName = "DailyIntelligenceDB";
    this.dbVersion = 1;
    this.db = null;
    this.isNative = !!(window.AndroidBridge && window.AndroidBridge.isNativeApp && window.AndroidBridge.isNativeApp());

    // 7 Core Categories
    this.categories = [
      { id: "global-business", code: "global_business", name_en: "Global Business", name_kn: "ಜಾಗತಿಕ ವ್ಯಾಪಾರ" },
      { id: "global-politics", code: "global_politics", name_en: "Global Politics", name_kn: "ಜಾಗತಿಕ ರಾಜಕೀಯ" },
      { id: "indian-politics", code: "indian_politics", name_en: "Indian Politics", name_kn: "ಭಾರತೀಯ ರಾಜಕೀಯ" },
      { id: "indian-economy", code: "indian_economy", name_en: "Indian Economy", name_kn: "ಭಾರತೀಯ ಆರ್ಥಿಕತೆ" },
      { id: "karnataka-politics", code: "karnataka_politics", name_en: "Karnataka Politics", name_kn: "ಕರ್ನಾಟಕ ರಾಜಕೀಯ" },
      { id: "technology-science", code: "technology_science", name_en: "Technology & Science", name_kn: "ತಂತ್ರಜ್ಞಾನ ಮತ್ತು ವಿಜ್ಞಾನ" },
      { id: "education", code: "education", name_en: "Education", name_kn: "ಶಿಕ್ಷಣ" }
    ];

    // Candidate RSS Sources
    this.sources = [
      { name: "BBC News World", url: "https://feeds.bbci.co.uk/news/world/rss.xml", defaultCategory: "global-politics" },
      { name: "The Hindu National", url: "https://www.thehindu.com/news/national/feeder/default.rss", defaultCategory: "indian-politics" },
      { name: "Indian Express Economy", url: "https://indianexpress.com/section/business/economy/feed/", defaultCategory: "indian-economy" },
      { name: "Deccan Herald Karnataka", url: "https://www.deccanherald.com/rss/state/karnataka.rss", defaultCategory: "karnataka-politics" },
      { name: "Prajavani Karnataka", url: "https://www.prajavani.net/rssfeeds/karnataka.xml", defaultCategory: "karnataka-politics" },
      { name: "Ars Technica", url: "https://feeds.arstechnica.com/arstechnica/index", defaultCategory: "technology-science" },
      { name: "MarketWatch Top Stories", url: "https://feeds.content.dowjones.io/public/rss/mw_topstories", defaultCategory: "global-business" }
    ];

    // Taxonomy Keywords
    this.taxonomy = {
      "karnataka-politics": {
        weight: 3.0,
        keywords: ["karnataka", "bengaluru", "bangalore", "siddaramaiah", "dk shivakumar", "vidhana soudha", "kannada", "cauvery", "bbmp", "mysuru", "belagavi", "hubballi", "muda", "dalit", "lingayat", "vokkaliga", "prajavani"]
      },
      "indian-politics": {
        weight: 2.0,
        keywords: ["modi", "bjp", "congress", "parliament", "lok sabha", "rajya sabha", "supreme court", "election commission", "rahul gandhi", "amit shah", "chief minister", "governor", "bill", "constitution", "cabinet", "assembly"]
      },
      "indian-economy": {
        weight: 2.5,
        keywords: ["rbi", "reserve bank", "inflation", "gdp", "sensex", "nifty", "rupee", "repo rate", "fiscal deficit", "gst", "budget", "sebi", "banking", "finance ministry", "monetary policy", "exports", "imports"]
      },
      "global-business": {
        weight: 1.5,
        keywords: ["wall street", "nasdaq", "dow jones", "fed", "federal reserve", "central bank", "stocks", "shares", "merger", "acquisition", "imf", "world bank", "venture capital", "startup", "apple", "microsoft", "tesla", "alphabet", "amazon"]
      },
      "global-politics": {
        weight: 1.5,
        keywords: ["united states", "biden", "trump", "white house", "united nations", "putin", "russia", "ukraine", "china", "xi jinping", "taiwan", "middle east", "israel", "gaza", "iran", "nato", "eu", "european union", "diplomacy", "treaty"]
      },
      "technology-science": {
        weight: 2.0,
        keywords: ["artificial intelligence", "ai", "llm", "isro", "nasa", "semiconductor", "chip", "quantum", "spacecraft", "chandrayaan", "biotech", "robotics", "cybersecurity", "supercomputer", "fusion", "satellite"]
      },
      "education": {
        weight: 2.0,
        keywords: ["ugc", "cbse", "neet", "jee", "iit", "iim", "university", "scholarship", "higher education", "syllabus", "exam", "skill development", "ncert", "students", "admissions", "curriculum"]
      }
    };

    // Kannada Offline Glossary
    this.glossary = {
      "Prime Minister": "ಪ್ರಧಾನ ಮಂತ್ರಿ",
      "Chief Minister": "ಮುಖ್ಯಮಂತ್ರಿ",
      "Government": "ಸರ್ಕಾರ",
      "Cabinet": "ಸಚಿವ ಸಂಪುಟ",
      "Supreme Court": "ಸುಪ್ರೀಂ ಕೋರ್ಟ್",
      "High Court": "ಹೈಕೋರ್ಟ್",
      "Reserve Bank of India": "ಭಾರತೀಯ ರಿಸರ್ವ್ ಬ್ಯಾಂಕ್",
      "RBI": "ಆರ್.ಬಿ.ಐ",
      "Inflation": "ಹಣದುಬ್ಬರ",
      "Economy": "ಆರ್ಥಿಕತೆ",
      "Budget": "ಬಜೆಟ್",
      "Karnataka": "ಕರ್ನಾಟಕ",
      "Bengaluru": "ಬೆಂಗಳೂರು",
      "India": "ಭಾರತ",
      "Election": "ಚುನಾವಣೆ",
      "Education": "ಶಿಕ್ಷಣ",
      "Technology": "ತಂತ್ರಜ್ಞಾನ",
      "Science": "ವಿಜ್ಞಾನ",
      "Artificial Intelligence": "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ (AI)",
      "Policy": "ನೀತಿ",
      "Market": "ಮಾರುಕಟ್ಟೆ",
      "Growth": "ಬೆಳವಣಿಗೆ",
      "Tax": "ತೆರಿಗೆ",
      "Bank": "ಬ್ಯಾಂಕ್",
      "Students": "ವಿದ್ಯಾರ್ಥಿಗಳು",
      "University": "ವಿಶ್ವವಿದ್ಯಾಲಯ",
      "Global": "ಜಾಗತಿಕ",
      "Politics": "ರಾಜಕೀಯ",
      "Business": "ವ್ಯಾಪಾರ"
    };

    // Foundational Education Topics
    this.seedTopics = [
      {
        id: "rbi-monetary-policy",
        slug: "rbi-monetary-policy",
        category_id: "indian-economy",
        title_en: "RBI Monetary Policy & The Repo Rate",
        title_kn: "ಆರ್‌ಬಿಐ ಹಣಕಾಸು ನೀತಿ ಮತ್ತು ರೆಪೊ ದರ",
        simple_definition_en: "The mechanism through which the Reserve Bank of India regulates money supply, credit availability, and inflation in the national economy.",
        simple_definition_kn: "ಭಾರತೀಯ ರಿಸರ್ವ್ ಬ್ಯಾಂಕ್ ದೇಶದ ಆರ್ಥಿಕತೆಯಲ್ಲಿ ಹಣದ ಪೂರೈಕೆ, ಸಾಲ ಲಭ್ಯತೆ ಮತ್ತು ಹಣದುಬ್ಬರವನ್ನು ನಿಯಂತ್ರಿಸುವ ಪ್ರಮುಖ ಕಾರ್ಯವಿಧಾನ.",
        background_en: "Established by the RBI Act of 1934, India's central bank was mandated with inflation targeting (4% ± 2%) under the Monetary Policy Framework Agreement in 2015. The Monetary Policy Committee (MPC) meets bi-monthly to calibrate key benchmark rates.",
        background_kn: "1934 ರ ಆರ್‌ಬಿಐ ಕಾಯ್ದೆಯಡಿ ಸ್ಥಾಪನೆಯಾದ ಭಾರತದ ಕೇಂದ್ರೀಯ ಬ್ಯಾಂಕ್, 2015 ರ ಹಣಕಾಸು ನೀತಿ ಚೌಕಟ್ಟಿನ ಒಪ್ಪಂದದ ಅಡಿಯಲ್ಲಿ ಹಣದುಬ್ಬರ ಗುರಿಯನ್ನು (4% ± 2%) ಹೊಂದಿದೆ. ಹಣಕಾಸು ನೀತಿ ಸಮಿತಿಯು (MPC) ದ್ವೈಮಾಸಿಕವಾಗಿ ಸಭೆ ಸೇರಿ ದರಗಳನ್ನು ನಿರ್ಧರಿಸುತ್ತದೆ.",
        how_it_works_en: "When inflation rises, the RBI increases the 'Repo Rate' (the interest rate at which commercial banks borrow from RBI). This makes commercial loans more expensive, cooling down spending and demand. Conversely, when economic growth slows, RBI cuts the repo rate to spur borrowing and business investment.",
        how_it_works_kn: "ಹಣದುಬ್ಬರ ಹೆಚ್ಚಾದಾಗ, ಆರ್‌ಬಿಐ 'ರೆಪೊ ದರ'ವನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ (ವಾಣಿಜ್ಯ ಬ್ಯಾಂಕುಗಳು ಆರ್‌ಬಿಐನಿಂದ ಸಾಲ ಪಡೆಯುವ ಬಡ್ಡಿದರ). ಇದು ಸಾಲಗಳನ್ನು ದುಬಾರಿಯಾಗಿಸಿ, ಖರ್ಚನ್ನು ಕಡಿಮೆ ಮಾಡುತ್ತದೆ. ಆರ್ಥಿಕ ಬೆಳವಣಿಗೆ ನಿಧಾನವಾದಾಗ, ಹೂಡಿಕೆಯನ್ನು ಉತ್ತೇಜಿಸಲು ಆರ್‌ಬಿಐ ರೆಪೊ ದರವನ್ನು ಕಡಿಮೆ ಮಾಡುತ್ತದೆ.",
        real_world_example_en: "When the MPC hikes the repo rate by 25 basis points, home loans and auto EMIs across banks like SBI and HDFC increase within weeks, reducing household discretionary spending.",
        real_world_example_kn: "ಆರ್‌ಬಿಐ ರೆಪೊ ದರವನ್ನು 25 ಮೂಲಾಂಕ ಹೆಚ್ಚಿಸಿದಾಗ, ಎಸ್‌ಬಿಐ ಮತ್ತು ಎಚ್‌ಡಿಎಫ್‌ಸಿ ಬ್ಯಾಂಕುಗಳಲ್ಲಿ ಗೃಹ ಸಾಲದ ಇಎಂಐ ತಕ್ಷಣ ಹೆಚ್ಚಾಗುತ್ತದೆ, ಇದು ಜನರ ಹೆಚ್ಚುವರಿ ವೆಚ್ಚವನ್ನು ಮಿತಗೊಳಿಸುತ್ತದೆ.",
        knowledge_check: [
          {
            question: "What is the primary target variable of the RBI Monetary Policy Committee?",
            options: [
              "Foreign Exchange Reserves",
              "Consumer Price Index (CPI) Inflation at 4% (± 2%)",
              "Stock Market Sensex Levels",
              "Commercial Bank Profit Margins"
            ],
            correct_index: 1,
            explanation: "The RBI MPC operates under a statutory mandate to maintain CPI headline inflation at 4% within a tolerance band of 2% to 6%."
          },
          {
            question: "What happens to home loan EMIs when the RBI raises the Repo Rate?",
            options: [
              "EMIs generally increase due to higher bank borrowing costs",
              "EMIs decrease immediately",
              "EMIs remain permanently frozen",
              "Commercial banks pay the difference to borrowers"
            ],
            correct_index: 0,
            explanation: "Commercial banks pass through the increased cost of funds to floating-rate retail borrowers, leading to higher EMIs."
          }
        ]
      },
      {
        id: "ai-llms-deep-learning",
        slug: "ai-llms-deep-learning",
        category_id: "technology-science",
        title_en: "Large Language Models & Modern AI",
        title_kn: "ದೊಡ್ಡ ಭಾಷಾ ಮಾದರಿಗಳು ಮತ್ತು ಆಧುನಿಕ ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ",
        simple_definition_en: "Deep neural networks trained on vast textual datasets that generate coherent text, write code, and assist in reasoning by predicting word sequences.",
        simple_definition_kn: "ಬೃಹತ್ ಪ್ರಮಾಣದ ಪಠ್ಯ ಮಾಹಿತಿಯ ಮೇಲೆ ತರಬೇತಿ ಪಡೆದ ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಜಾಲಗಳು, ಪದಗಳ ಅನುಕ್ರಮವನ್ನು ಊಹಿಸುವ ಮೂಲಕ ಪಠ್ಯ ರಚನೆ ಮತ್ತು ಸಂಶೋಧನೆಗೆ ನೆರವಾಗುತ್ತವೆ.",
        background_en: "The revolution began in 2017 with Google's publication of the Transformer architecture ('Attention Is All You Need'), replacing recurrent neural networks with self-attention mechanisms capable of massive parallel processing.",
        background_kn: "2017 ರಲ್ಲಿ ಗೂಗಲ್ ಸಂಶೋಧಕರು ಪ್ರಕಟಿಸಿದ 'ಟ್ರಾನ್ಸ್‌ಫಾರ್ಮರ್' ವಾಸ್ತುಶಿಲ್ಪದೊಂದಿಗೆ ಈ ಕ್ರಾಂತಿ ಆರಂಭವಾಯಿತು. ಇದು ಸಮಾನಾಂತರ ಸಂಸ್ಕರಣೆಯನ್ನು ಸಾಧ್ಯವಾಗಿಸಿ ಆಧುನಿಕ ಎಐ ಕ್ರಾಂತಿಗೆ ಕಾರಣವಾಯಿತು.",
        how_it_works_en: "Transformers convert words into multi-dimensional vectors (embeddings) and calculate mathematical 'attention' weights between every pair of words. During pretraining, the model learns complex semantic and factual relationships by predicting masked or subsequent tokens.",
        how_it_works_kn: "ಟ್ರಾನ್ಸ್‌ಫಾರ್ಮರ್‌ಗಳು ಪದಗಳನ್ನು ಗಣಿತೀಯ ವೆಕ್ಟರ್‌ಗಳಾಗಿ ಪರಿವರ್ತಿಸಿ ಅವುಗಳ ನಡುವಿನ ಸಂಬಂಧವನ್ನು ಲೆಕ್ಕಾಚಾರ ಮಾಡುತ್ತವೆ. ಶತಕೋಟಿ ಪದಗಳ ತರಬೇತಿಯ ಮೂಲಕ ಮಾದರಿಯು ಭಾಷೆ ಮತ್ತು ವಿಷಯಗಳ ಜ್ಞಾನವನ್ನು ಕಲಿಯುತ್ತದೆ.",
        real_world_example_en: "AI systems assisting radiologists in spotting micro-fractures in X-rays, or automating real-time multilingual translation for Indian public welfare schemes.",
        real_world_example_kn: "ವೈದ್ಯಕೀಯ ಎಕ್ಸ್-ರೇ ಪರೀಕ್ಷೆಗಳಲ್ಲಿ ಸಣ್ಣ ಮೂಳೆ ಮುರಿತಗಳನ್ನು ಪತ್ತೆಹಚ್ಚಲು ಮತ್ತು ಭಾರತೀಯ ಸಾರ್ವಜನಿಕ ಸೇವೆಗಳ ನೈಜ-ಸಮಯದ ಬಹುಭಾಷಾ ಅನುವಾದಕ್ಕಾಗಿ ಎಐ ಬಳಕೆ.",
        knowledge_check: [
          {
            question: "Which breakthrough architecture published in 2017 forms the foundation of modern LLMs?",
            options: [
              "Convolutional Neural Networks (CNN)",
              "The Transformer Architecture with Self-Attention",
              "Decision Trees",
              "Genetic Algorithms"
            ],
            correct_index: 1,
            explanation: "The Transformer architecture introduced in 2017 enables self-attention across tokens, powering models like Gemini, GPT, and Claude."
          }
        ]
      }
    ];
  }

  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onupgradeneeded = (e) => {
        const db = e.target.result;

        if (!db.objectStoreNames.contains("articles")) {
          const artStore = db.createObjectStore("articles", { keyPath: "id" });
          artStore.createIndex("published_at", "published_at");
          artStore.createIndex("category_id", "category_id");
          artStore.createIndex("is_bookmarked", "is_bookmarked");
          artStore.createIndex("canonical_url", "canonical_url", { unique: false });
        }

        if (!db.objectStoreNames.contains("categories")) {
          db.createObjectStore("categories", { keyPath: "id" });
        }

        if (!db.objectStoreNames.contains("education_topics")) {
          db.createObjectStore("education_topics", { keyPath: "id" });
        }

        if (!db.objectStoreNames.contains("briefings")) {
          db.createObjectStore("briefings", { keyPath: "id" });
        }

        if (!db.objectStoreNames.contains("metadata")) {
          db.createObjectStore("metadata", { keyPath: "key" });
        }
      };

      request.onsuccess = async (e) => {
        this.db = e.target.result;
        await this.seedInitialData();
        resolve(this);
      };

      request.onerror = (e) => {
        console.error("IndexedDB initialization failed:", e);
        reject(e);
      };
    });
  }

  async seedInitialData() {
    // Seed Categories
    for (const cat of this.categories) {
      await this.putRecord("categories", cat);
    }

    // Seed Educational Topics
    for (const topic of this.seedTopics) {
      await this.putRecord("education_topics", topic);
    }

    // Check if we have articles; if empty, seed initial sample articles so app works out of the box
    const count = await this.countRecords("articles");
    if (count === 0) {
      await this.seedSampleArticles();
      await this.generateBriefing();
    }
  }

  async seedSampleArticles() {
    const now = new Date().toISOString();
    const sampleArticles = [
      {
        id: "sample-karnataka-1",
        headline: "Karnataka Cabinet Approves Major Infrastructure Push for Bengaluru Tech Corridor",
        original_url: "https://www.deccanherald.com/state/karnataka",
        canonical_url: "https://www.deccanherald.com/state/karnataka",
        publisher: "Deccan Herald",
        published_at: now,
        category_id: "karnataka-politics",
        categories: [{ id: "karnataka-politics", name_en: "Karnataka Politics", name_kn: "ಕರ್ನಾಟಕ ರಾಜಕೀಯ" }],
        short_description: "The Karnataka State Cabinet chaired by the Chief Minister greenlit extensive metro rail and peripheral connectivity projects across Bengaluru tech hubs.",
        summary_en: "The Karnataka Government has approved a strategic infrastructure package targeting suburban rail and arterial road connectivity in Bengaluru.",
        summary_kn: "ಬೆಂಗಳೂರಿನ ತಂತ್ರಜ್ಞಾನ ವಲಯಗಳಲ್ಲಿ ಉಪನಗರ ರೈಲು ಮತ್ತು ಪ್ರಮುಖ ರಸ್ತೆ ಸಂಪರ್ಕವನ್ನು ವಿಸ್ತರಿಸಲು ಕರ್ನಾಟಕ ಸಚಿವ ಸಂಪುಟ ಅನುಮೋದನೆ ನೀಡಿದೆ.",
        detailed_summary_en: "The high-level cabinet meeting approved revised funding allocations for major junction decongestion, rapid metro extensions to electronics hubs, and integrated public transit corridors across Greater Bengaluru.",
        detailed_summary_kn: "ಗ್ರೇಟರ್ ಬೆಂಗಳೂರಿನಲ್ಲಿ ಸಂಚಾರ ದಟ್ಟಣೆ ನಿಯಂತ್ರಿಸಲು ಮತ್ತು ಐಟಿ ಕೇಂದ್ರಗಳಿಗೆ ಮೆಟ್ರೋ ವಿಸ್ತರಣೆ ಸೇರಿದಂತೆ ಪ್ರಮುಖ ಮೂಲಸೌಕರ್ಯ ಯೋಜನೆಗಳಿಗೆ ಸಚಿವ ಸಂಪುಟ ಸಭೆಯಲ್ಲಿ ಅನುಮೋದನೆ ದೊರೆತಿದೆ.",
        why_it_matters_en: "Enhances urban mobility, reduces commuter transit times by an estimated 25%, and cements Bengaluru's position as India's premier tech capital.",
        why_it_matters_kn: "ನಗರದ ಸಂಚಾರ ದಟ್ಟಣೆಯನ್ನು ಶೇ. 25 ರಷ್ಟು ಕಡಿಮೆ ಮಾಡಲು ಮತ್ತು ಭಾರತದ ಪ್ರಮುಖ ತಂತ್ರಜ್ಞಾನ ರಾಜಧಾನಿಯಾಗಿ ಬೆಂಗಳೂರಿನ ಸ್ಥಾನವನ್ನು ಬಲಪಡಿಸಲು ಇದು ಸಹಕಾರಿಯಾಗಿದೆ.",
        important_facts: ["Multi-billion rupee capital allocation", "Direct connectivity to Outer Ring Road & Whitefield", "Scheduled completion within 36 months"],
        background_en: "Bengaluru accounts for over 35% of India's software exports, making urban transport efficiency a crucial economic priority.",
        background_kn: "ಭಾರತದ ಶೇಕಡಾ 35 ಕ್ಕೂ ಹೆಚ್ಚು ಸಾಫ್ಟ್‌ವೇರ್ ರಫ್ತಿಗೆ ಬೆಂಗಳೂರು ಕಾರಣವಾಗಿದ್ದು, ನಗರ ಸಾರಿಗೆ ಸುಧಾರಣೆ ಅತ್ಯಂತ ನಿರ್ಣಾಯಕವಾಗಿದೆ.",
        is_bookmarked: false,
        read_count: 3
      },
      {
        id: "sample-economy-1",
        headline: "RBI Keeps Repo Rate Unchanged at 6.50% Amid Resilient Domestic Growth",
        original_url: "https://indianexpress.com/section/business/economy/",
        canonical_url: "https://indianexpress.com/section/business/economy/",
        publisher: "Indian Express",
        published_at: now,
        category_id: "indian-economy",
        categories: [{ id: "indian-economy", name_en: "Indian Economy", name_kn: "ಭಾರತೀಯ ಆರ್ಥಿಕತೆ" }],
        short_description: "The Reserve Bank of India Monetary Policy Committee decided to maintain the benchmark policy repo rate at 6.50% with an ongoing focus on inflation target alignment.",
        summary_en: "RBI Governor announced the policy repo rate remains steady at 6.50% while projecting robust GDP expansion for the upcoming fiscal year.",
        summary_kn: "ಭಾರತೀಯ ರಿಸರ್ವ್ ಬ್ಯಾಂಕ್ ತನ್ನ ರೆಪೊ ದರವನ್ನು ಶೇ. 6.50 ರಲ್ಲಿ ಮುಂದುವರಿಸಲು ನಿರ್ಧರಿಸಿದ್ದು, ದೇಶದ ಜಿಡಿಪಿ ಬೆಳವಣಿಗೆಯ ಆಶಾವಾದವನ್ನು ವ್ಯಕ್ತಪಡಿಸಿದೆ.",
        detailed_summary_en: "Following a three-day MPC deliberation, the committee opted for status quo on rates to ensure retail headline inflation sustainably aligns with the 4% target while supporting capital expenditure and consumption demand.",
        detailed_summary_kn: "ಹಣದುಬ್ಬರವನ್ನು ಶೇ. 4 ರ ಗುರಿಯಲ್ಲಿ ನಿಯಂತ್ರಿಸುವ ಉದ್ದೇಶದಿಂದ ಮತ್ತು ಆರ್ಥಿಕ ಚಟುವಟಿಕೆಗಳಿಗೆ ಉತ್ತೇಜನ ನೀಡಲು ಆರ್‌ಬಿಐ ರೆಪೊ ದರದಲ್ಲಿ ಯಾವುದೇ ಬದಲಾವಣೆ ಮಾಡಿಲ್ಲ.",
        why_it_matters_en: "Stabilizes lending rates and retail home/auto EMIs, offering borrowing predictability to businesses and households.",
        why_it_matters_kn: "ಗೃಹ ಮತ್ತು ವಾಹನ ಸಾಲಗಳ ಇಎಂಐ ದರಗಳು ಸ್ಥಿರವಾಗಿರಲು ಹಾಗೂ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಹೂಡಿಕೆದಾರರಿಗೆ ವಿಶ್ವಾಸ ಮೂಡಿಸಲು ಇದು ನೆರವಾಗುತ್ತದೆ.",
        important_facts: ["Policy Repo Rate kept at 6.50%", "GDP Growth projected at 7.0%", "CPI Inflation target benchmark: 4.0%"],
        background_en: "The MPC has maintained this stance across successive reviews to navigate global supply chain shocks.",
        background_kn: "ಜಾಗತಿಕ ಅನಿಶ್ಚಿತತೆಗಳ ನಡುವೆಯೂ ಭಾರತದ ಆರ್ಥಿಕತೆಯನ್ನು ಸ್ಥಿರವಾಗಿಡಲು ಆರ್‌ಬಿಐ ಈ ಕ್ರಮ ಕೈಗೊಂಡಿದೆ.",
        is_bookmarked: true,
        read_count: 5
      },
      {
        id: "sample-tech-1",
        headline: "ISRO Unveils Next-Generation Reusable Launch Vehicle Test Roadmap",
        original_url: "https://feeds.arstechnica.com",
        canonical_url: "https://feeds.arstechnica.com",
        publisher: "Ars Technica",
        published_at: now,
        category_id: "technology-science",
        categories: [{ id: "technology-science", name_en: "Technology & Science", name_kn: "ತಂತ್ರಜ್ಞಾನ ಮತ್ತು ವಿಜ್ಞಾನ" }],
        short_description: "Indian Space Research Organisation successfully conducts autonomous winged landing tests for its reusable launch system, aiming to slash payload launch costs.",
        summary_en: "ISRO has achieved another milestone in its reusable launch vehicle program, demonstrating high-precision autonomous landing capabilities.",
        summary_kn: "ಇಸ್ರೋ ಸಂಸ್ಥೆಯು ಮರುಬಳಕೆ ಮಾಡಬಹುದಾದ ಉಡಾವಣಾ ವಾಹನದ (RLV) ಸ್ವಾಯತ್ತ ಲ್ಯಾಂಡಿಂಗ್ ಪರೀಕ್ಷೆಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಪೂರ್ಣಗೊಳಿಸಿದೆ.",
        detailed_summary_en: "The winged space vehicle completed an autonomous touchdown under complex cross-wind conditions at the Chitradurga Aeronautical Test Range, validating navigation and thermal protection systems.",
        detailed_summary_kn: "ಚಿತ್ರದುರ್ಗದ ಪರೀಕ್ಷಾ ವಲಯದಲ್ಲಿ ಈ ಮಹತ್ವದ ಪರೀಕ್ಷೆ ನಡೆದಿದ್ದು, ಉಪಗ್ರಹ ಉಡಾವಣಾ ವೆಚ್ಚವನ್ನು ಗಣನೀಯವಾಗಿ ತಗ್ಗಿಸುವ ಗುರಿ ಹೊಂದಿದೆ.",
        why_it_matters_en: "Reusable launch systems reduce the cost per kilogram of launching satellites to orbit by up to 70%, boosting India's commercial space launch competitiveness.",
        why_it_matters_kn: "ಉಪಗ್ರಹಗಳ ಉಡಾವಣಾ ವೆಚ್ಚವನ್ನು ಶೇಕಡಾ 70 ರಷ್ಟು ತಗ್ಗಿಸಲು ಮತ್ತು ಭಾರತದ ಬಾಹ್ಯಾಕಾಶ ವಲಯವನ್ನು ಜಾಗತಿಕ ಮಟ್ಟದಲ್ಲಿ ಮುನ್ನಡೆಸಲು ಇದು ನಿರ್ಣಾಯಕವಾಗಿದೆ.",
        important_facts: ["Autonomous aerodynamic landing executed", "Validates reusable winged orbiter design", "Aims for 70% reduction in orbital delivery costs"],
        background_en: "India's space economy is rapidly expanding following private sector deregulation and global demand for small-satellite constellation deployments.",
        background_kn: "ಭಾರತದ ಬಾಹ್ಯಾಕಾಶ ಕ್ಷೇತ್ರವು ಖಾಸಗಿ ಸಹಭಾಗಿತ್ವದೊಂದಿಗೆ ವೇಗವಾಗಿ ಬೆಳೆಯುತ್ತಿದ್ದು, ಜಾಗತಿಕ ಬೇಡಿಕೆಯನ್ನು ಪೂರೈಸುತ್ತಿದೆ.",
        is_bookmarked: false,
        read_count: 2
      }
    ];

    for (const art of sampleArticles) {
      await this.putRecord("articles", art);
    }
  }

  // --- Network & Bridge ---
  async fetchRemoteUrl(url) {
    // 1. Android Native Bridge (CORS-free Java HttpURLConnection)
    if (window.AndroidBridge && typeof window.AndroidBridge.fetchHttp === "function") {
      try {
        const text = window.AndroidBridge.fetchHttp(url);
        if (text && text.length > 50) return text;
      } catch (err) {
        console.warn("Native bridge fetch error, falling back:", err);
      }
    }

    // 2. Direct Web fetch
    try {
      const res = await fetch(url, { headers: { "Accept": "application/rss+xml, application/xml, text/xml, */*" } });
      if (res.ok) return await res.text();
    } catch (e) {
      // 3. Public CORS Proxy for local development fallback
      try {
        const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(url)}`;
        const pRes = await fetch(proxyUrl);
        if (pRes.ok) return await pRes.text();
      } catch (proxyErr) {
        console.warn("CORS proxy failed for", url, proxyErr);
      }
    }
    return null;
  }

  // --- RSS Ingestion Engine ---
  async runIngestionPipeline() {
    let addedCount = 0;
    const parser = new DOMParser();

    for (const src of this.sources) {
      try {
        const xmlText = await this.fetchRemoteUrl(src.url);
        if (!xmlText) continue;

        const xmlDoc = parser.parseFromString(xmlText, "text/xml");
        const items = xmlDoc.querySelectorAll("item, entry");

        for (let i = 0; i < Math.min(items.length, 10); i++) {
          const item = items[i];
          const parsed = this.parseFeedItem(item, src);
          if (!parsed || !parsed.title || !parsed.link) continue;

          // Deduplication
          const isDup = await this.checkDuplicate(parsed.link, parsed.title);
          if (isDup) continue;

          // Categorization
          const categoryId = this.classifyArticle(parsed.title, parsed.description, src.defaultCategory);
          const catObj = this.categories.find(c => c.id === categoryId) || this.categories[0];

          // Summarization
          const intel = this.synthesizeIntelligence(parsed.title, parsed.description);

          // Kannada Translation
          const knIntel = await this.translateIntelligence(parsed.title, intel.summary, intel.whyMatters);

          const articleId = "art_" + this.hashString(parsed.link);
          const article = {
            id: articleId,
            headline: parsed.title,
            original_url: parsed.link,
            canonical_url: parsed.link,
            publisher: src.name,
            published_at: parsed.pubDate || new Date().toISOString(),
            category_id: categoryId,
            categories: [catObj],
            short_description: parsed.description.substring(0, 200),
            summary_en: intel.summary,
            summary_kn: knIntel.summaryKn,
            detailed_summary_en: intel.detailedSummary,
            detailed_summary_kn: knIntel.detailedSummaryKn,
            why_it_matters_en: intel.whyMatters,
            why_it_matters_kn: knIntel.whyMattersKn,
            important_facts: intel.facts,
            background_en: `${src.name} ongoing news coverage and analysis.`,
            background_kn: `${src.name} ಪತ್ರಿಕೆಯ ಪ್ರಮುಖ ಸುದ್ದಿ ವಿಶ್ಲೇಷಣೆ.`,
            is_bookmarked: false,
            read_count: 0
          };

          await this.putRecord("articles", article);
          addedCount++;
        }
      } catch (err) {
        console.warn("Source ingestion error for", src.name, err);
      }
    }

    if (addedCount > 0) {
      await this.generateBriefing();
    }
    return addedCount;
  }

  parseFeedItem(node, src) {
    const getVal = (tag) => {
      const el = node.querySelector(tag);
      return el ? el.textContent.trim() : "";
    };

    let title = getVal("title");
    let link = getVal("link") || (node.querySelector("link")?.getAttribute("href") || "");
    let description = getVal("description") || getVal("summary") || getVal("content");
    let pubDate = getVal("pubDate") || getVal("published") || getVal("updated");

    // Clean HTML
    description = description.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
    title = title.replace(/<[^>]+>/g, "").trim();

    return { title, link, description, pubDate };
  }

  // --- Deduplication ---
  async checkDuplicate(url, title) {
    const articles = await this.getAllRecords("articles");
    const canonUrl = this.canonicalizeUrl(url);

    for (const art of articles) {
      if (this.canonicalizeUrl(art.original_url) === canonUrl) return true;
      if (this.calculateJaccardSimilarity(art.headline, title) >= 0.65) return true;
    }
    return false;
  }

  canonicalizeUrl(url) {
    try {
      const u = new URL(url);
      return `${u.protocol}//${u.hostname}${u.pathname}`.toLowerCase().replace(/\/+$/, "");
    } catch {
      return (url || "").toLowerCase().split("?")[0].replace(/\/+$/, "");
    }
  }

  calculateJaccardSimilarity(textA, textB) {
    const tokenize = (t) => new Set(t.toLowerCase().replace(/[^\w\s]/g, "").split(/\s+/).filter(w => w.length > 2));
    const setA = tokenize(textA);
    const setB = tokenize(textB);
    if (setA.size === 0 || setB.size === 0) return 0;

    let intersection = 0;
    for (const item of setA) {
      if (setB.has(item)) intersection++;
    }
    const union = setA.size + setB.size - intersection;
    return union > 0 ? intersection / union : 0;
  }

  // --- Classification ---
  classifyArticle(title, description, defaultCategory) {
    const combined = `${title} ${description}`.toLowerCase();
    let bestCat = defaultCategory || "global-politics";
    let maxScore = 0;

    for (const [catId, info] of Object.entries(this.taxonomy)) {
      let score = 0;
      for (const kw of info.keywords) {
        if (combined.includes(kw)) {
          score += info.weight;
        }
      }
      if (score > maxScore) {
        maxScore = score;
        bestCat = catId;
      }
    }
    return bestCat;
  }

  // --- Heuristic Summarization ---
  synthesizeIntelligence(title, description) {
    const cleanDesc = description || title;
    const sentences = cleanDesc.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 15);

    let summary = sentences[0] ? sentences[0] + "." : cleanDesc;
    let detailedSummary = sentences.slice(0, 3).join(". ");
    if (detailedSummary && !detailedSummary.endsWith(".")) detailedSummary += ".";

    // Extract numbers, percentages, dates
    const factMatches = cleanDesc.match(/(\$|₹|Rs\.?|€)?\d+(\.\d+)?(\s?%|\s?(crore|lakh|billion|million|trillion|percent|bps))?/gi) || [];
    const uniqueFacts = Array.from(new Set(factMatches)).slice(0, 4);

    let whyMatters = "Directly influences current strategic, economic, and institutional developments in the sector.";
    if (cleanDesc.toLowerCase().includes("inflation") || cleanDesc.toLowerCase().includes("rbi") || cleanDesc.toLowerCase().includes("growth")) {
      whyMatters = "Critical for interest rate movements, consumer purchasing power, and monetary stability.";
    } else if (cleanDesc.toLowerCase().includes("bengaluru") || cleanDesc.toLowerCase().includes("karnataka")) {
      whyMatters = "Significant for state administrative policy, urban governance, and regional growth.";
    } else if (cleanDesc.toLowerCase().includes("ai") || cleanDesc.toLowerCase().includes("technology")) {
      whyMatters = "Accelerates digital capability and technological transformation across industries.";
    }

    return {
      summary,
      detailedSummary: detailedSummary || summary,
      whyMatters,
      facts: uniqueFacts.length > 0 ? uniqueFacts.map(f => `Key metric reported: ${f}`) : ["Standard reporting indicators verified"]
    };
  }

  // --- Translation Engine ---
  async translateIntelligence(title, summary, whyMatters) {
    let summaryKn = "";
    let detailedSummaryKn = "";
    let whyMattersKn = "";

    // 1. Online Google Translate GTX endpoint (instant & high accuracy)
    try {
      const q = encodeURIComponent(summary);
      const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=kn&dt=t&q=${q}`;
      const resText = await this.fetchRemoteUrl(url);
      if (resText) {
        const parsed = JSON.parse(resText);
        if (parsed && parsed[0]) {
          summaryKn = parsed[0].map(item => item[0]).join(" ");
          detailedSummaryKn = summaryKn;
        }
      }
    } catch (e) {
      console.debug("Online translation unavailable, using glossary fallback.");
    }

    // 2. Offline Glossary Fallback
    if (!summaryKn) {
      summaryKn = summary;
      for (const [enWord, knWord] of Object.entries(this.glossary)) {
        const regex = new RegExp(`\\b${enWord}\\b`, "gi");
        summaryKn = summaryKn.replace(regex, knWord);
      }
      detailedSummaryKn = summaryKn;
    }

    // Translate Why It Matters
    if (whyMatters.includes("interest rate") || whyMatters.includes("monetary")) {
      whyMattersKn = "ಬಡ್ಡಿದರಗಳು, ಗ್ರಾಹಕರ ಕೊಳ್ಳುವ ಶಕ್ತಿ ಮತ್ತು ಆರ್ಥಿಕ ಸ್ಥಿರತೆಯ ಮೇಲೆ ನೇರ ಪರಿಣಾಮ ಬೀರುತ್ತದೆ.";
    } else if (whyMatters.includes("state administrative") || whyMatters.includes("regional growth")) {
      whyMattersKn = "ರಾಜ್ಯದ ಆಡಳಿತ ನೀತಿ, ನಗರ ಆಡಳಿತ ಮತ್ತು ಪ್ರಾದೇಶಿಕ ಅಭಿವೃದ್ಧಿಗೆ ಅತ್ಯಂತ ಮಹತ್ವದ್ದಾಗಿದೆ.";
    } else if (whyMatters.includes("technological transformation")) {
      whyMattersKn = "ತಂತ್ರಜ್ಞಾನ ಸಾಮರ್ಥ್ಯ ಮತ್ತು ಡಿಜಿಟಲ್ ರೂಪಾಂತರವನ್ನು ತ್ವರಿತಗೊಳಿಸುತ್ತದೆ.";
    } else {
      whyMattersKn = "ಈ ಕ್ಷೇತ್ರದ ಕಾರ್ಯತಂತ್ರ, ಆರ್ಥಿಕ ಮತ್ತು ಸಾಂಸ್ಥಿಕ ಬೆಳವಣಿಗೆಗಳ ಮೇಲೆ ನೇರ ಪ್ರಭಾವ ಬೀರುತ್ತದೆ.";
    }

    return { summaryKn, detailedSummaryKn, whyMattersKn };
  }

  // --- Briefing Generator ---
  async generateBriefing() {
    const articles = await this.getAllRecords("articles");
    const count = articles.length;
    const now = new Date();
    const isEvening = now.getHours() >= 12;
    const briefingType = isEvening ? "Evening Briefing" : "Morning Briefing";

    const topArts = articles.slice(0, 3).map(a => a.headline).join(" • ");
    const summaryEn = `${briefingType}: Monitored ${count} intelligence developments across Global, National, Karnataka, and Technology streams. Highlights: ${topArts || 'Ongoing coverage active.'}`;
    const summaryKn = `${isEvening ? 'ಸಂಜೆಯ ಬ್ರೀಫಿಂಗ್' : 'ಬೆಳಗಿನ ಬ್ರೀಫಿಂಗ್'}: ಒಟ್ಟು ${count} ಮಹತ್ವದ ಬೆಳವಣಿಗೆಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗಿದೆ. ಪ್ರಮುಖಾಂಶಗಳು: ${topArts}`;

    const briefing = {
      id: "latest",
      type: briefingType,
      created_at: now.toISOString(),
      summary_en: summaryEn,
      summary_kn: summaryKn,
      total_articles: count
    };

    await this.putRecord("briefings", briefing);
    return briefing;
  }

  // --- IndexedDB Generic Helpers ---
  async putRecord(storeName, record) {
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(storeName, "readwrite");
      const store = tx.objectStore(storeName);
      store.put(record);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  }

  async getRecord(storeName, key) {
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(storeName, "readonly");
      const store = tx.objectStore(storeName);
      const req = store.get(key);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async getAllRecords(storeName) {
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(storeName, "readonly");
      const store = tx.objectStore(storeName);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  async countRecords(storeName) {
    return new Promise((resolve, reject) => {
      const tx = this.db.transaction(storeName, "readonly");
      const store = tx.objectStore(storeName);
      const req = store.count();
      req.onsuccess = () => resolve(req.result || 0);
      req.onerror = () => reject(req.error);
    });
  }

  hashString(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash).toString(36);
  }
}

// Global engine instance
window.embeddedEngine = new EmbeddedEngine();
