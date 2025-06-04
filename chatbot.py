import streamlit as st
import requests
import google.generativeai as genai

# Configure Google AI Studio API (Gemini Pro)
GEMINI_API_KEY = "AIzaSyDlJeY51OvMvIxfD4l0XLRUHtrR-beuZfs"
genai.configure(api_key=GEMINI_API_KEY)

# SERP API configuration (for retrieving the latest market data)
SERP_API_KEY = "cba0000520d91d2c6efc1d6ae45a0d3a5b52b3b1c20a8a44b755e98e98f3758e"
SERP_BASE_URL = "https://serpapi.com/search"

# Initialize conversation history in session state
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# Function to get the latest financial news from Google News API via SERP API
def get_google_news_data(query):
    """Fetch the latest financial news using Google News API via SERP API."""
    params = {
        "q": query,
        "api_key": SERP_API_KEY,
        "tbm": "nws"
    }
    response = requests.get(SERP_BASE_URL, params=params).json()
    
    if "news_results" in response:
        return [
            {
                "title": article.get("title", "No title available"),
                "link": article.get("link", "No link available"),
                "snippet": article.get("snippet", "No summary available"),
                "date": article.get("date", "Unknown Date")
            }
            for article in response["news_results"][:5]  # Get latest 5 news items
        ]
    return []

# Function to get fundamental financial data from Google Finance API via SERP API
def get_google_finance_data(query):
    """Fetch the latest fundamental financial data using Google Finance API via SERP API."""
    params = {
        "q": f"{query} stock financials",
        "api_key": SERP_API_KEY,
        "tbm": "fin"
    }
    response = requests.get(SERP_BASE_URL, params=params).json()
    
    if "finance_results" in response:
        return [
            {
                "title": article.get("title", "No title available"),
                "snippet": article.get("snippet", "No summary available"),
                "date": article.get("date", "Unknown Date")
            }
            for article in response["finance_results"][:5]  # Get latest 5 financial reports
        ]
    return []

# Function to generate trading insights using Gemini Pro
def generate_summary(query):
    """Generate a detailed summary using Gemini Pro based on Google News and Google Finance data."""
    financial_news = get_google_news_data(query)
    fundamental_data = get_google_finance_data(query)
    
    news_summary = " ".join([f"{article['date']}: {article['title']} - {article['snippet']}" for article in financial_news])
    fundamentals_summary = " ".join([f"{article['date']}: {article['title']} - {article['snippet']}" for article in fundamental_data])
    
    # Construct conversation history to maintain continuity
    conversation_history = "\n".join(
        [f"User: {entry.get('user', '')}\nBot: {entry.get('bot', '')}" for entry in st.session_state.conversation_history]
    )
    
    context = (
        f"You are an expert intraday trader with years of experience. Your role is to provide real-time, actionable insights based on the latest financial data. Ensure your advice is insightful, precise, and tailored for active traders making quick decisions.\n"
        f"Previous conversation context:\n{conversation_history}\n"
        f"Latest financial news about {query}: {news_summary}.\n"
        f"Recent fundamental financial data for {query}: {fundamentals_summary}.\n"
        f"Analyze the data, including timestamps, and provide concise, numbers-driven insights for traders.\n"
        f"Provide a structured, expert-level suggestion, ensuring key financial numbers and timestamps are included for precise, data-driven insights."
    )
    model = genai.GenerativeModel("gemini-2.0-flash", generation_config={"temperature": 0.3})
    response = model.generate_content(context, stream=True)
    return "".join([chunk.text for chunk in response])

# Streamlit UI
st.title("Market Insights & Trading Guidance")

# Chatbot-like Continuous Conversation
user_input = st.chat_input("Ask about any company, stock, or market trend:")
if user_input:
    # Maintain conversation history
    st.session_state.conversation_history.append({"user": user_input, "bot": ""})
    
    summary = generate_summary(user_input)
    st.session_state.conversation_history[-1]["bot"] = summary  # Store bot response properly
    
    # Display conversation history continuously
    for exchange in st.session_state.conversation_history:
        if "user" in exchange:
            st.chat_message("user").write(exchange['user'])
        if "bot" in exchange and exchange['bot']:
            st.chat_message("assistant").write(exchange['bot'])
