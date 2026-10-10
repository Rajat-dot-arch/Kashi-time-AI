import json
import streamlit as st
from rag_chain import answer

st.set_page_config(
    page_title="Kashi-Time AI",
    page_icon="🕉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Custom CSS ---
st.markdown("""
<style>
    /* Import premium font */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Global Font Override */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container width */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* --- Hero Header --- */
    .kashi-header {
        background: linear-gradient(135deg, #1A1F2E 0%, #0B0E14 100%);
        border: 1px solid #FF9933;
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(255, 153, 51, 0.15);
        position: relative;
        overflow: hidden;
    }
    .kashi-header::before {
        content: "";
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,153,51,0.1) 0%, transparent 70%);
        pointer-events: none;
    }
    .kashi-header h1 {
        color: #FFFFFF;
        font-size: 2.8rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .kashi-header p {
        color: #A0AAB5;
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        font-weight: 300;
    }

    /* --- Sidebar --- */
    [data-testid="stSidebar"] {
        background-color: #0B0E14;
        border-right: 1px solid #1F2633;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFFFFF;
    }
    
    /* Sidebar Buttons */
    .stButton > button {
        border-radius: 12px;
        border: 1px solid #1F2633;
        background-color: #151A24;
        color: #F0F2F5;
        transition: all 0.2s ease;
        font-weight: 500;
        padding: 10px 15px;
        width: 100%;
        text-align: left;
    }
    .stButton > button:hover {
        border-color: #FF9933;
        background-color: #1F2633;
        color: #FF9933;
        transform: translateX(4px);
    }

    /* --- Chat Messages --- */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 20px;
        background-color: #151A24;
        border: 1px solid #1F2633;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        animation: fadeIn 0.3s ease-in-out;
    }
    
    /* Assistant message styling */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 4px solid #FF9933;
    }
    
    /* User message styling */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        border-right: 4px solid #4A90E2;
        background-color: #1A202C;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* --- Image Gallery --- */
    .image-card {
        background-color: #151A24;
        border: 1px solid #1F2633;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .image-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(255, 153, 51, 0.15);
        border-color: #FF9933;
    }
    .image-caption {
        color: #A0AAB5;
        font-size: 0.85rem;
        margin-top: 8px;
        line-height: 1.4;
    }

    /* --- Timeline Cards --- */
    .timeline-card {
        background-color: #151A24;
        border-left: 4px solid #FF9933;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        transition: transform 0.2s ease;
    }
    .timeline-card:hover {
        transform: translateX(6px);
        border-left-color: #FFFFFF;
    }
    .timeline-date {
        color: #FF9933;
        font-weight: 700;
        font-size: 1.3rem;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
    }
    .timeline-title {
        color: #FFFFFF;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 8px;
    }
    .timeline-desc {
        color: #A0AAB5;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    /* --- Chat Input --- */
    [data-testid="stChatInput"] {
        border-radius: 16px;
        border: 1px solid #1F2633;
        background-color: #151A24;
        padding: 10px;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #FF9933;
        box-shadow: 0 0 0 2px rgba(255, 153, 51, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# --- Hero Header ---
st.markdown("""
<div class="kashi-header">
    <h1>🕉️ Kashi-Time AI</h1>
    <p>Heritage intelligence for Varanasi — ask, explore, discover.</p>
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🕉️ Kashi-Time AI")
    st.caption("Heritage & History of Varanasi")
    st.markdown("---")

    st.markdown("**Quick Questions**")

    if st.button("🛕 Kashi Vishwanath history", use_container_width=True):
        st.session_state.quick_prompt = "How has Kashi Vishwanath Temple changed over time?"
    if st.button("🔥 Ganga Aarti", use_container_width=True):
        st.session_state.quick_prompt = "What is the Ganga Aarti at Dashashwamedh Ghat?"
    if st.button("🪔 Manikarnika Ghat", use_container_width=True):
        st.session_state.quick_prompt = "Why is Manikarnika Ghat significant?"
    if st.button("☸️ Sarnath", use_container_width=True):
        st.session_state.quick_prompt = "Tell me about Sarnath and its Buddhist heritage."

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

# --- Load timeline data ---
with open("data/timeline.json", "r", encoding="utf-8") as f:
    timeline_events = json.load(f)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["💬 Ask Kashi", "📜 Timeline", "ℹ️ About"])

# --- Tab 1: Chat ---
with tab1:
    st.header("Ask about Kashi's History & Heritage")
    st.caption("🔍 Multimodal RAG · Local LLM · Semantic image search · Runs offline")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []

    # Handle sidebar quick prompt
    if st.session_state.get("quick_prompt"):
        st.session_state.pending_prompt = st.session_state.quick_prompt
        st.session_state.quick_prompt = None

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("e.g., How has Dashashwamedh Ghat changed over time?")
    if not prompt and st.session_state.get("pending_prompt"):
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching heritage records..."):
                result = answer(prompt, st.session_state.history)

                # 1. Text answer
                st.markdown(result["answer"])

                # 2. Related images (CLIP semantic search) - Styled Cards
                if result.get("images"):
                    st.markdown("##### 📸 Related Images")
                    cols = st.columns(min(3, len(result["images"])))
                    for col, img in zip(cols, result["images"]):
                        with col:
                            try:
                                # Using HTML for the card wrapper to get the hover effect
                                st.markdown(f"""
                                <div class="image-card">
                                    <img src="{img['url']}" style="width:100%; border-radius:8px; object-fit:cover;" />
                                    <div class="image-caption">{img.get('caption', '')[:70]}</div>
                                </div>
                                """, unsafe_allow_html=True)
                            except Exception:
                                st.caption("⚠️ Image unavailable")

                # 3. Sources
                if result["sources"]:
                    with st.expander("📖 Sources"):
                        for s in result["sources"]:
                            st.markdown(f"- `{s}`")

        st.session_state.history.append({"role": "user", "content": prompt})
        st.session_state.history.append({"role": "assistant", "content": result["answer"]})
        st.session_state.messages.append({"role": "assistant", "content": result["answer"]})

# --- Tab 2: Timeline ---
with tab2:
    st.header("📜 Timeline of Kashi")
    st.caption("Key historical events in Varanasi's heritage.")

    for event in timeline_events:
        st.markdown(f"""
        <div class="timeline-card">
            <div class="timeline-date">{event['date']}</div>
            <div class="timeline-title">{event['title']}</div>
            <div class="timeline-desc">{event['description']}</div>
        </div>
        """, unsafe_allow_html=True)

# --- Tab 3: About ---
with tab3:
    st.header("About Kashi-Time AI")
    st.markdown("""
    **Kashi-Time AI** is a heritage intelligence system focused on Varanasi/Kashi.
    It uses Retrieval-Augmented Generation (RAG) to answer questions based on a curated knowledge base.

    **MVP Features:**
    - Conversational Q&A over Kashi's history
    - Curated timeline of key events
    - Source citations for transparency
    - Semantic image search via CLIP

    **Future Plans:**
    - Interactive map of historical places
    - Time-based exploration slider
    - Integration with JARVIS Core
    """)