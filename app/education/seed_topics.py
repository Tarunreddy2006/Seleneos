import json
from datetime import date
from sqlalchemy.orm import Session
from app.database.models import EducationalTopic
from app.core.logging import logger

FOUNDATIONAL_TOPICS = [
    {
        "id": "how-rbi-monetary-policy-works",
        "title_en": "How RBI Monetary Policy & Repo Rates Work",
        "title_kn": "ರಿಸರ್ವ್ ಬ್ಯಾಂಕ್ (RBI) ಹಣಕಾಸು ನೀತಿ ಮತ್ತು ರೆಪೋ ದರ ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ?",
        "category_id": "indian-economy",
        "simple_definition_en": "Monetary policy is how the Reserve Bank of India controls the supply and cost of money in the economy to keep inflation stable while promoting growth.",
        "simple_definition_kn": "ಹಣದುಬ್ಬರವನ್ನು ನಿಯಂತ್ರಣದಲ್ಲಿಟ್ಟು ಆರ್ಥಿಕ ಬೆಳವಣಿಗೆಯನ್ನು ಉತ್ತೇಜಿಸಲು ರಿಸರ್ವ್ ಬ್ಯಾಂಕ್ ಆಫ್ ಇಂಡಿಯಾ ದೇಶದಲ್ಲಿ ಹಣದ ಪೂರೈಕೆ ಮತ್ತು ಬಡ್ಡಿದರವನ್ನು ನಿಯಂತ್ರಿಸುವ ಪ್ರಕ್ರಿಯೆಯೇ ಹಣಕಾಸು ನೀತಿ.",
        "background_en": "The Monetary Policy Committee (MPC) was established in 2016 under the RBI Act to introduce institutional, consensus-based interest rate decisions with a target inflation band of 4% (+/- 2%).",
        "background_kn": "ಭಾರತದಲ್ಲಿ ಹಣದುಬ್ಬರವನ್ನು 4% (±2%) ಮಿತಿಯಲ್ಲಿಡಲು 2016 ರಲ್ಲಿ ರಿಸರ್ವ್ ಬ್ಯಾಂಕ್ ಕಾಯಿದೆಯಡಿ ಹಣಕಾಸು ನೀತಿ ಸಮಿತಿ (MPC) ಯನ್ನು ಸ್ಥಾಪಿಸಲಾಯಿತು.",
        "how_it_works_en": "When inflation is high, the RBI raises the Repo Rate (the rate at which commercial banks borrow from RBI). This makes home and corporate loans expensive, cooling consumer demand. Conversely, when economic growth slows, RBI cuts repo rates to encourage lending and investment.",
        "how_it_works_kn": "ಹಣದುಬ್ಬರ ಹೆಚ್ಚಾದಾಗ ಆರ್‌ಬಿಐ ರೆಪೋ ದರವನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ. ಇದರಿಂದ ಸಾಲದ ಮೇಲಿನ ಬಡ್ಡಿದರ ಏರಿ, ಖರ್ಚು ಕಡಿಮೆಯಾಗುತ್ತದೆ. ಆರ್ಥಿಕ ಬೆಳವಣಿಗೆ ಕುಂಠಿತಗೊಂಡಾಗ ರೆಪೋ ದರ ಇಳಿಸಿ ಸಾಲ ಸೌಲಭ್ಯ ಹೆಚ್ಚಿಸಲಾಗುತ್ತದೆ.",
        "real_world_example_en": "If you have a floating-rate home loan, a 25 basis point hike in the RBI repo rate directly increases your monthly EMI or loan tenure.",
        "real_world_example_kn": "ನಿಮ್ಮ ಗೃಹ ಸಾಲದ ಬಡ್ಡಿದರ ಫ್ಲೋಟಿಂಗ್ ಆಗಿದ್ದರೆ, ಆರ್‌ಬಿಐ ರೆಪೋ ದರ 25 ಬೇಸಿಸ್ ಪಾಯಿಂಟ್ ಹೆಚ್ಚಿಸಿದಾಗ ನಿಮ್ಮ ಮಾಸಿಕ ಇಎಂಐ (EMI) ಹೆಚ್ಚಾಗುತ್ತದೆ.",
        "current_events_connection_en": "Whenever global crude oil prices fluctuate or food prices spike, the MPC reviews repo rates in its bi-monthly meetings.",
        "current_events_connection_kn": "ಜಾಗತಿಕ ತೈಲ ಬೆಲೆ ಏರಿಳಿತ ಅಥವಾ ಆಹಾರ ಪದಾರ್ಥಗಳ ಬೆಲೆ ಹೆಚ್ಚಾದಾಗ ಆರ್‌ಬಿಐ ರೆಪೋ ದರ ಪರಿಷ್ಕರಣೆ ಸಭೆಗಳನ್ನು ನಡೆಸುತ್ತದೆ.",
        "important_terminology": json.dumps([
            {"term_en": "Repo Rate", "term_kn": "ರೆಪೋ ದರ", "definition_en": "The rate at which the central bank lends money to commercial banks against government securities.", "definition_kn": "ಕೇಂದ್ರ ಬ್ಯಾಂಕ್ ವಾಣಿಜ್ಯ ಬ್ಯಾಂಕುಗಳಿಗೆ ನೀಡುವ ಅಲ್ಪಾವಧಿ ಸಾಲದ ಮೇಲಿನ ಬಡ್ಡಿದರ."},
            {"term_en": "Reverse Repo Rate", "term_kn": "ರಿವರ್ಸ್ ರೆಪೋ ದರ", "definition_en": "The rate at which the RBI borrows money from commercial banks.", "definition_kn": "ವಾಣಿಜ್ಯ ಬ್ಯಾಂಕುಗಳಿಂದ ಆರ್‌ಬಿಐ ಪಡೆಯುವ ಠೇವಣಿಗಳ ಮೇಲಿನ ಬಡ್ಡಿದರ."},
            {"term_en": "Inflation Target", "term_kn": "ಹಣದುಬ್ಬರ ಗುರಿ", "definition_en": "Statutory target of 4% CPI inflation with a +/- 2% tolerance band.", "definition_kn": "4% ಗ್ರಾಹಕ ಬೆಲೆ ಸೂಚ್ಯಂಕ (CPI) ಹಣದುಬ್ಬರ ಗುರಿ."}
        ]),
        "knowledge_check": json.dumps([
            {
                "question": "What typically happens to home loan EMIs when the RBI hikes the repo rate?",
                "options": ["EMIs increase or tenure extends", "EMIs decrease immediately", "No impact on loans", "Bank accounts are frozen"],
                "correct_index": 0,
                "explanation": "Higher repo rates increase the cost of funds for banks, which pass on the higher rates to borrowers."
            }
        ]),
        "is_featured": True,
        "featured_date": date.today()
    },
    {
        "id": "how-ai-large-language-models-work",
        "title_en": "How Artificial Intelligence & Large Language Models Work",
        "title_kn": "ಕೃತಕ ಬುದ್ಧಿಮತ್ತೆ ಮತ್ತು ಲಾರ್ಜ್ ಲ್ಯಾಂಗ್ವೇಜ್ ಮಾಡೆಲ್‌ಗಳು (LLM) ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತವೆ?",
        "category_id": "technology-science",
        "simple_definition_en": "Large Language Models (LLMs) are deep learning neural networks trained on vast amounts of text to predict the most probable next word in a sequence.",
        "simple_definition_kn": "ಲಾರ್ಜ್ ಲ್ಯಾಂಗ್ವೇಜ್ ಮಾಡೆಲ್‌ಗಳು (LLM) ಬೃಹತ್ ಪ್ರಮಾಣದ ಪಠ್ಯದ ಮೇಲೆ ತರಬೇತಿ ಪಡೆದು, ವಾಕ್ಯದಲ್ಲಿ ಮುಂದಿನ ಪದವನ್ನು ಊಹಿಸುವ ಡೀಪ್ ಲರ್ನಿಂಗ್ ನೆಟ್‌ವರ್ಕ್‌ಗಳಾಗಿವೆ.",
        "background_en": "The breakthrough came in 2017 with the 'Attention Is All You Need' paper by Google researchers, introducing the Transformer architecture which enabled self-attention across massive parallel data.",
        "background_kn": "2017 ರಲ್ಲಿ ಗೂಗಲ್ ಸಂಶೋಧಕರು ಪ್ರಕಟಿಸಿದ 'ಟ್ರಾನ್ಸ್‌ಫಾರ್ಮರ್' ಆರ್ಕಿಟೆಕ್ಚರ್ ಎಐ ಕ್ಷೇತ್ರದಲ್ಲಿ ಕ್ರಾಂತಿಕಾರಿ ಬೆಳವಣಿಗೆಗೆ ನಾಂದಿ ಹಾಡಿತು.",
        "how_it_works_en": "Text is broken into numerical tokens. Layers of attention mechanisms evaluate relationships between all words in a prompt simultaneously, outputting contextually accurate responses.",
        "how_it_works_kn": "ಪಠ್ಯವನ್ನು ಟೋಕನ್‌ಗಳಾಗಿ ವಿಭಜಿಸಿ, ಅಟೆನ್ಷನ್ ಮೆಕ್ಯಾನಿಸಂ ಮೂಲಕ ಪದಗಳ ನಡುವಿನ ಸಂಬಂಧವನ್ನು ವಿಶ್ಲೇಷಿಸಿ ಅರ್ಥಪೂರ್ಣ ಉತ್ತರ ನೀಡಲಾಗುತ್ತದೆ.",
        "real_world_example_en": "Real-time auto-completion in Gmail or automated multi-language translation apps.",
        "real_world_example_kn": "ಸ್ಮಾರ್ಟ್‌ಫೋನ್ ಕೀಬೋರ್ಡ್‌ನಲ್ಲಿ ಮುಂದಿನ ಪದದ ಸ್ವಯಂ-ಸಲಹೆ ಅಥವಾ ಭಾಷಾಂತರ ಅಪ್ಲಿಕೇಶನ್‌ಗಳು.",
        "current_events_connection_en": "Central to debates on semiconductor export controls, GPU computing clusters, and automation.",
        "current_events_connection_kn": "ಜಾಗತಿಕ ಸೆಮಿಕಂಡಕ್ಟರ್ ಚಿಪ್ ಮಾರುಕಟ್ಟೆ ಮತ್ತು ಕ್ಲೌಡ್ ಕಂಪ್ಯೂಟಿಂಗ್ ಬೆಳವಣಿಗೆಗೆ ಇದು ಪ್ರಮುಖ ಕಾರಣವಾಗಿದೆ.",
        "important_terminology": json.dumps([
            {"term_en": "Transformer", "term_kn": "ಟ್ರಾನ್ಸ್‌ಫಾರ್ಮರ್", "definition_en": "Neural network architecture relying on self-attention.", "definition_kn": "ಸ್ವಯಂ-ಅಟೆನ್ಷನ್ ಆಧರಿಸಿದ ನರ ಜಾಲ ಮಾದರಿ."},
            {"term_en": "Inference", "term_kn": "ಇನ್‌ಫರೆನ್ಸ್", "definition_en": "Running a trained model to generate predictions.", "definition_kn": "ತರಬೇತಿ ಪಡೆದ ಮಾದರಿಯನ್ನು ಬಳಸಿ ಉತ್ತರ ಪಡೆಯುವ ಹಂತ."}
        ]),
        "knowledge_check": json.dumps([
            {
                "question": "What is the core task performed by an autoregressive language model during text generation?",
                "options": ["Predicting the next most probable token", "Copying exact web pages", "Translating sound waves directly", "Searching a relational database"],
                "correct_index": 0,
                "explanation": "LLMs predict the most statistically likely subsequent token given prior context."
            }
        ]),
        "is_featured": False
    }
]


def seed_educational_topics(db: Session) -> None:
    """Populates the database with foundational educational topics."""
    for t_data in FOUNDATIONAL_TOPICS:
        existing = db.query(EducationalTopic).filter(EducationalTopic.id == t_data["id"]).first()
        if not existing:
            topic = EducationalTopic(
                id=t_data["id"],
                title_en=t_data["title_en"],
                title_kn=t_data["title_kn"],
                category_id=t_data["category_id"],
                simple_definition_en=t_data["simple_definition_en"],
                simple_definition_kn=t_data["simple_definition_kn"],
                background_en=t_data["background_en"],
                background_kn=t_data["background_kn"],
                how_it_works_en=t_data["how_it_works_en"],
                how_it_works_kn=t_data["how_it_works_kn"],
                real_world_example_en=t_data["real_world_example_en"],
                real_world_example_kn=t_data["real_world_example_kn"],
                current_events_connection_en=t_data["current_events_connection_en"],
                current_events_connection_kn=t_data["current_events_connection_kn"],
                important_terminology=t_data["important_terminology"],
                knowledge_check=t_data["knowledge_check"],
                is_featured=t_data.get("is_featured", False),
                featured_date=t_data.get("featured_date")
            )
            db.add(topic)
            logger.info("Seeded educational topic: %s", t_data["title_en"])
    db.commit()
