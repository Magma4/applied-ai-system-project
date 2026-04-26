import streamlit as st
import logging
from src.recommender import load_songs
from src.agent import CuratorAgent
from src.guardrails import EnergyAlignmentGuardrail, MoodSafetyGuardrail

# Set page config for a premium feel
st.set_page_config(
    page_title="VibeFinder AI",
    page_icon="🎵",
    layout="wide"
)

# Custom CSS for aesthetics
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }
    .reasoning-box {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff4b4b;
        margin-bottom: 20px;
    }
    .song-card {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def get_catalog():
    return load_songs("data/songs.csv")

def main():
    st.title("🎵 Agentic VibeFinder")
    st.markdown("### *Your Personal AI Music Curator*")
    st.divider()

    catalog = get_catalog()
    agent = CuratorAgent(catalog)
    guardrails = [EnergyAlignmentGuardrail(0.4), MoodSafetyGuardrail()]

    # Sidebar for technical info
    with st.sidebar:
        st.header("⚙️ System Status")
        st.success("Catalog Loaded: 18 Songs")
        st.info("Agent Mode: Deterministic")
        st.info("Guardrails: Active")
        
        st.divider()
        st.markdown("### [System Logs]")
        log_container = st.empty()

    # Main Input
    query = st.text_input("How are you feeling? (e.g., 'I need a high energy rock workout track')", placeholder="Describe your vibe...")

    if st.button("Generate Recommendations") or query:
        if not query:
            st.warning("Please enter a prompt first!")
            return

        with st.spinner("Agent is planning and retrieving..."):
            # Run the Agentic Workflow
            recommendations, profile, strategy = agent.process_request(query, guardrails=guardrails)

        # Show Agent Reasoning
        st.markdown("#### 🤖 Agent Reasoning")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Detected Genre", profile.favorite_genre.title())
        with col2:
            st.metric("Detected Mood", profile.favorite_mood.title())
        with col3:
            st.metric("Target Energy", f"{profile.target_energy:.2f}")

        st.markdown(f"<div class='reasoning-box'><b>Strategy Selected:</b> {strategy.replace('_', ' ').title()}<br>"
                    f"<i>The agent analyzed your prompt and prioritized the {strategy.split('_')[0]} characteristics of the catalog.</i></div>", 
                    unsafe_allow_html=True)

        # Show Results
        st.divider()
        st.markdown("### 🎼 Recommended Tracks")
        
        if not recommendations:
            st.error("No songs passed the safety guardrails for this specific prompt. Try a broader vibe!")
        else:
            for i, (song, score, reasons) in enumerate(recommendations, start=1):
                with st.container():
                    st.markdown(f"""
                        <div class='song-card'>
                            <h3 style='margin:0;'>{i}. {song['title']}</h3>
                            <p style='color:#888; margin-bottom:5px;'>{song['artist']} | {song['genre'].title()} | Energy: {song['energy']}</p>
                            <p style='font-size:0.9em; color:#bbb;'><b>Score: {score:.2f}</b></p>
                            <ul style='font-size:0.85em; color:#aaa;'>
                                {''.join([f'<li>{r}</li>' for r in reasons])}
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
