import time
import streamlit as st
from google import genai
from google.genai import errors
from logic import get_financial_metrics, calculate_goal_roadmap, create_ai_prompt

# --- Page Config ---
st.set_page_config(page_title="AI Financial Advisor", page_icon="💰", layout="centered")
st.title("💰 AI Financial Advisor")
st.caption("Powered by Gemini 2.0 Flash")

# --- Sidebar: API Key ---
API_KEY = st.sidebar.text_input("🔑 Gemini API Key", type="password")

# --- User Inputs ---
st.header("📋 Your Financial Profile")

persona = st.selectbox("Select your persona", ["Salaried Employee", "Freelancer", "Student", "Business Owner", "Retiree"])

col1, col2, col3 = st.columns(3)
with col1:
    income = st.number_input("Monthly Income (₹)", min_value=0, value=50000, step=1000)
with col2:
    expenses = st.number_input("Monthly Expenses (₹)", min_value=0, value=20000, step=1000)
with col3:
    debt = st.number_input("Monthly Debt/EMI (₹)", min_value=0, value=5000, step=500)

st.header("🎯 Your Financial Goal")
g_name = st.text_input("Goal Name", value="Emergency Fund")
col4, col5 = st.columns(2)
with col4:
    g_target = st.number_input("Target Amount (₹)", min_value=0, value=500000, step=10000)
with col5:
    g_years = st.number_input("Time Frame (Years)", min_value=1, value=5, step=1)

# --- Scenario 1: Budget Health ---
surplus, s_rate, dti = get_financial_metrics(income, expenses, debt)

st.header("📊 Budget Health (Scenario 1)")
m1, m2, m3 = st.columns(3)
m1.metric("Monthly Surplus", f"₹{surplus:,.0f}")
m2.metric("Savings Rate", f"{s_rate:.1f}%")
m3.metric("DTI Ratio", f"{dti:.1f}%")

# --- Scenario 2: Goal Roadmap ---
required_monthly = calculate_goal_roadmap(g_target, g_years)

st.header("🗺️ Goal Roadmap (Scenario 2)")
st.info(f"To reach **₹{g_target:,}** for *{g_name}* in **{g_years} years**, you need to save **₹{required_monthly:,.2f}/month** (assuming 8% annual return).")

# --- AI Generation ---
# Initialize the GenAI client only when key is available
client = genai.Client(api_key=API_KEY) if API_KEY else None

# Initialize session state for the response if it doesn't exist
if "ai_response" not in st.session_state:
    st.session_state.ai_response = None

MODELS_TO_TRY = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]

if st.button("🚀 Generate AI Wealth Plan"):
    if not API_KEY:
        st.error("Please enter your Gemini API Key.")
    else:
        with st.spinner("Gemini is analyzing your data..."):
            prompt = create_ai_prompt(persona, income, expenses, debt, g_name, g_target, g_years, surplus, s_rate, dti)
            success = False

            for model_name in MODELS_TO_TRY:
                for attempt in range(2):  # 2 tries per model
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        st.session_state.ai_response = response.text
                        success = True
                        break  # success — exit retry loop

                    except (errors.ClientError, errors.APIError) as e:
                        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                            if attempt == 0:
                                st.warning(f"⏳ Rate limit hit on **{model_name}**. Retrying in 30s...")
                                time.sleep(30)
                            else:
                                st.warning(f"⚠️ **{model_name}** quota exhausted. Trying next model...")
                        else:
                            st.error(f"API Error ({model_name}): {e}")
                            break
                    except Exception as e:
                        st.error(f"Unexpected error: {e}")
                        break

                if success:
                    break  # exit model loop

            if not success and st.session_state.ai_response is None:
                st.error(
                    "⚠️ **All models are rate-limited.** Your Gemini API quota is exhausted.\n\n"
                    "**How to fix:**\n"
                    "- Wait 1-2 minutes and try again.\n"
                    "- Check your quota at https://ai.dev/rate-limit\n"
                    "- Upgrade your plan at https://ai.google.dev/gemini-api/docs/rate-limits"
                )

# Display the response (even after page reruns)
if st.session_state.ai_response:
    st.subheader("💡 Strategic Recommendations")
    st.markdown(st.session_state.ai_response)
