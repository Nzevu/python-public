import streamlit as st
from transformers import pipeline
st.set_page_config(page_title="AI Sentiment Analyzer", page_icon="🎭", layout="wide")
@st.cache_resource
def load_model():
    return pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
analyzer = load_model()
st.title("🎭 Real-Time Sentiment Analysis")
st.markdown("Powered by HuggingFace Transformers - Analyze the emotional tone of any text instantly")
col1, col2 = st.columns([2, 1])
with col1:
    user_input = st.text_area("Enter text to analyze:", height=150, placeholder="Type or paste any text here...")
    analyze_button = st.button("Analyze Sentiment", type="primary")
with col2:
    st.markdown("### About This Model")
    st.info("Using DistilBERT fine-tuned on SST-2 dataset. Fast, accurate sentiment classification.")
if analyze_button and user_input:
    with st.spinner("Analyzing..."):
        result = analyzer(user_input)[0]
        label = result['label']
        score = result['score']
        st.markdown("---")
        if label == "POSITIVE":
            st.success(f"### 😊 Sentiment: {label}")
            st.progress(score)
            st.metric("Confidence", f"{score:.2%}")
        else:
            st.error(f"### 😞 Sentiment: {label}")
            st.progress(score)
            st.metric("Confidence", f"{score:.2%}")
        st.markdown("---")
        st.markdown("**Try these examples:**")
        st.code("This is the best tutorial I've ever read!")
        st.code("I'm frustrated with how complicated this seems.")
elif analyze_button:
    st.warning("Please enter some text to analyze.")
st.markdown("---")
st.caption("Built with HuggingFace Transformers 🤗 | Deployed on Streamlit Cloud ☁️")
