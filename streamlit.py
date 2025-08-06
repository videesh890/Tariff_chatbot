import os
import streamlit as st
import requests
import pandas as pd
import json
import openai
from dotenv import load_dotenv

# --- Load .env and OpenAI Key ---
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
print("OPENAI API KEY loaded?", bool(openai_key), "| Value is:", repr(openai_key)[:15])

# --- Streamlit Page Config and Styling ---
st.set_page_config(
    page_title="Tariff AI Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)



# --- OpenAI Chatbot Function ---
def ask_ai_about_result(feature, data, question, openai_key):
    prompt = f"You are a professional supply chain and tariff advisor. Here are the latest results for {feature}:\n\n{data}\n\nUser question: {question}\n\nAdvice:"
    print("\n---OPENAI PROMPT---\n", prompt)
    try:
        if not openai_key or len(openai_key.strip()) < 10:
            raise ValueError("OpenAI key missing or invalid.")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            api_key=openai_key,
            messages=[
                {"role": "system", "content": "You are a professional assistant for supply chain, tariff, and sourcing analytics."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=320,
            temperature=0.15
        )
        reply = completion.choices[0].message['content'].strip()
        print("---OPENAI REPLY---\n", reply)
        return reply
    except Exception as e:
        print("---OPENAI CHAT ERROR---\n", e)
        return f"**AI chat error:** {e}"


# --- API Response Handling ---
BACKEND_URL = "http://127.0.0.1:8000"

def handle_api_response(resp):
    if resp.status_code == 200:
        try:
            return resp.json()
        except json.JSONDecodeError:
            st.error("Failed to decode JSON from API.")
            st.code(resp.text, language="text")
            return None
    else:
        st.error(f"API Error: Status {resp.status_code}")
        st.code(f"Details: {resp.text}", language="text")
        return None


# --- Utility: No Results Message ---
def show_no_results_message(title="No Results Found", message="Please try adjusting your input.", icon="🤷‍♀️"):
    with st.container():
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">{icon}</div>
            <h3 style="color: #ffe175;">{title}</h3>
            <p style="color: #c7faff;">{message}</p>
        </div>
        """, unsafe_allow_html=True)


# --- Sidebar ---
with st.sidebar:
    st.markdown("<div style='color:#ffe175;font-size:2rem;font-weight:800;margin:15px;'>Tariff AI</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='padding:18px 12px;background:#23304f;border-radius:10px;margin-top:12px;'>
    <b style='color:#ffe175;'>Gold Standard for Tariff Analytics</b>
    <p style='color:#c7faff;'>An executive dashboard for tariff, simulation, and sourcing intelligence.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    with st.expander("How to Use This Dashboard"):
        st.markdown("1. Select a feature tab.\n2. Fill in the inputs.\n3. Get instant insights.")
    st.markdown("---")
    st.warning("**Backend must be running for live results.**", icon="⚠️")


# --- Header ---
st.markdown("""
<div style="background:linear-gradient(90deg, #161716 60%, #E7C873 260%);padding:18px 10px;border-radius:10px;margin-bottom:15px;">
    <span style='font-size:2.2rem;color:#e7c873;font-family:Segoe UI,sans-serif;font-weight:900;letter-spacing:0.02em;'>🤖 Tariff Management AI</span>
</div>
""", unsafe_allow_html=True)


# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🔎 Smart Search", "🧪 Scenario Sim.", "🌱 Material Opt.",
    "💡 Semantic What-if", "🧾 Tariff Lookup", "🧮 Tariff Calc."
])


# --- Tab 1: Smart Search ---
with tab1:
    st.header("Smart Product Search")
    with st.container():
        with st.form("smart_product_form"):
            query = st.text_input("Search phrase", value="High-quality cotton gloves from India")
            top_n = st.selectbox("Number of matches to return", options=list(range(1, 11)), index=2)
            submitted_search = st.form_submit_button("🔍 Find Products", use_container_width=True)

    if submitted_search:
        with st.spinner("AI searching for products..."):
            resp = requests.get(f"{BACKEND_URL}/smart-product-search", params={"query": query, "top_n": top_n})
            data = handle_api_response(resp)
        if data and data.get("results"):
            df = pd.DataFrame(data["results"])
            st.dataframe(df, use_container_width=True)
            with st.form("chat_form_tab1"):
                st.markdown("#### 💬 Chat About These Results")
                user_q = st.text_input("Ask about these products:", key="tab1_chat")
                chat_submitted = st.form_submit_button("Ask AI")
            if chat_submitted and user_q:
                with st.spinner("AI thinking..."):
                    ai_reply = ask_ai_about_result("Smart Product Search", df.head(3).to_string(index=False), user_q, openai_key)
                st.markdown(
                    f"<div style='background:#1c2837;padding:10px 18px;border-radius:10px;margin:18px 0;'>"
                    f"<b>AI:</b> {ai_reply}</div>",
                    unsafe_allow_html=True
                )
        elif submitted_search:
            show_no_results_message("No Products Found", "Try broader keywords or change filters.", "🔍")


# --- Tab 2: Scenario Simulation ---
with tab2:
    st.header("What-If Scenario Simulation")
    with st.form("scenario_form"):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            with st.container():
                product_name = st.text_input("Base Product Name", value="gloves")
                alt_material = st.text_input("Substitute Material", placeholder="e.g., rubber, nitrile")
                alt_country = st.text_input("New Source Country", placeholder="e.g., Vietnam, Malaysia")
        with col2:
            with st.container():
                sort_by = st.selectbox("Sort results by", ["Landed_Cost_USD", "Tariff_Rate_Percent", "Material_Cost_USD"])
                direction = st.radio("Sort order", ["Ascending", "Descending"], horizontal=True)
                direction_val = "asc" if direction == "Ascending" else "desc"
        submitted_scenario = st.form_submit_button("🧪 Run Simulation", use_container_width=True)

    if submitted_scenario:
        with st.spinner("Modeling scenarios..."):
            params = {
                "product_name": product_name,
                "alt_material": alt_material,
                "alt_country": alt_country,
                "sort_by": sort_by,
                "direction": direction_val
            }
            resp = requests.get(f"{BACKEND_URL}/scenario-simulation", params=params)
            data = handle_api_response(resp)
        if data and data.get("scenarios"):
            df = pd.DataFrame(data["scenarios"])
            st.dataframe(df, use_container_width=True)
            with st.form("chat_form_tab2"):
                st.markdown("#### 💬 Chat About These Results")
                user_q = st.text_input("Ask about these scenarios:", key="tab2_chat")
                chat_submitted = st.form_submit_button("Ask AI")
            if chat_submitted and user_q:
                with st.spinner("AI thinking..."):
                    ai_reply = ask_ai_about_result("Scenario Simulation", df.head(3).to_string(index=False), user_q, openai_key)
                st.markdown(
                    f"<div style='background:#1c2837;padding:10px 18px;border-radius:10px;margin:18px 0;'>"
                    f"<b>AI:</b> {ai_reply}</div>",
                    unsafe_allow_html=True
                )
        elif submitted_scenario:
            show_no_results_message("No Scenarios Generated", "Try different inputs or fewer alternatives.", "🧪")


# --- Tab 3: Material Optimization ---
with tab3:
    st.header("Material Cost Optimization")
    with st.container():
        with st.form("material_form"):
            col1, col2 = st.columns(2)
            with col1:
                product_name = st.text_input("Product Name to Optimize", value="gloves")
            with col2:
                hts_code = st.text_input("HTS Code (Optional)")
            submitted_material = st.form_submit_button("🌱 Suggest Materials", use_container_width=True)

    if submitted_material:
        with st.spinner("Analyzing material alternatives..."):
            params = {"product_name": product_name}
            if hts_code:
                params["hts_code"] = hts_code
            resp = requests.get(f"{BACKEND_URL}/material-optimization", params=params)
            data = handle_api_response(resp)
        if data and data.get("suggestions"):
            st.json(data['suggestions'])
            with st.form("chat_form_tab3"):
                st.markdown("#### 💬 Chat About These Suggestions")
                user_q = st.text_input("Ask about these material options:", key="tab3_chat")
                chat_submitted = st.form_submit_button("Ask AI")
            if chat_submitted and user_q:
                with st.spinner("AI thinking..."):
                    ai_reply = ask_ai_about_result("Material Optimization", json.dumps(data['suggestions'], indent=2), user_q, openai_key)
                st.markdown(
                    f"<div style='background:#1c2837;padding:10px 18px;border-radius:10px;margin:18px 0;'>"
                    f"<b>AI:</b> {ai_reply}</div>",
                    unsafe_allow_html=True
                )
        elif submitted_material:
            show_no_results_message("No Suggestions Found", "Try a different product name.", "🌱")


# --- Tab 4: Semantic What-If Scenario ---
with tab4:
    st.header("Semantic What-If Scenario")
    with st.container():
        with st.form("semantic_scenario_form"):
            query = st.text_area("Question", value="What is the lowest landed cost for cotton gloves if sourced from Vietnam?", height=100)
            col1, col2, col3 = st.columns(3)
            with col1:
                top_n = st.selectbox("Candidate products", options=list(range(1, 6)), index=0)
            with col2:
                sort_by = st.selectbox("Sort by", ["Landed_Cost_USD", "Tariff_Rate_Percent"])
            with col3:
                direction = st.radio("Order", ["Ascending", "Descending"])
                direction_val = "asc" if direction == "Ascending" else "desc"
            submitted_whatif = st.form_submit_button("💡 Run AI Scenario", use_container_width=True)

    if submitted_whatif:
        with st.spinner("AI is interpreting and simulating..."):
            params = {"query": query, "top_n": top_n, "sort_by": sort_by, "direction": direction_val}
            resp = requests.get(f"{BACKEND_URL}/semantic-scenario-simulation", params=params)
            data = handle_api_response(resp)
        if data and data.get("scenarios"):
            df = pd.DataFrame(data["scenarios"])
            st.dataframe(df, use_container_width=True)
            with st.form("chat_form_tab4"):
                st.markdown("#### 💬 Chat About These Results")
                user_q = st.text_input("Ask about these scenarios:", key="tab4_chat")
                chat_submitted = st.form_submit_button("Ask AI")
            if chat_submitted and user_q:
                with st.spinner("AI thinking..."):
                    ai_reply = ask_ai_about_result("Semantic What-If Scenario", df.head(3).to_string(index=False), user_q, openai_key)
                st.markdown(
                    f"<div style='background:#1c2837;padding:10px 18px;border-radius:10px;margin:18px 0;'>"
                    f"<b>AI:</b> {ai_reply}</div>",
                    unsafe_allow_html=True
                )
        elif submitted_whatif:
            show_no_results_message("Simulation Failed", "Try rephrasing your question.", "💡")


# --- Tab 5: Tariff Lookup ---
with tab5:
    st.header("Tariff Lookup")
    with st.container():
        with st.form("semantic_lookup_form"):
            query = st.text_input("Enter your tariff question", value="tariff rate for leather shoes from Indonesia")
            top_n = st.selectbox("Number of results", options=list(range(1, 11)), index=2)
            submitted_lookup = st.form_submit_button("🔎 Find Tariff Info", use_container_width=True)

    if submitted_lookup:
        with st.spinner("AI is searching for tariff info..."):
            resp = requests.get(f"{BACKEND_URL}/semantic-tariff-lookup", params={"query": query, "top_n": top_n})
            data = handle_api_response(resp)
        if data and data.get("matches"):
            df = pd.DataFrame(data["matches"])
            st.dataframe(df, use_container_width=True)
            with st.form("chat_form_tab5"):
                st.markdown("#### 💬 Chat About These Results")
                user_q = st.text_input("Ask about these tariffs:", key="tab5_chat")
                chat_submitted = st.form_submit_button("Ask AI")
            if chat_submitted and user_q:
                with st.spinner("AI thinking..."):
                    ai_reply = ask_ai_about_result("Tariff Lookup", df.head(3).to_string(index=False), user_q, openai_key)
                st.markdown(
                    f"<div style='background:#1c2837;padding:10px 18px;border-radius:10px;margin:18px 0;'>"
                    f"<b>AI:</b> {ai_reply}</div>",
                    unsafe_allow_html=True
                )
        elif submitted_lookup:
            show_no_results_message("No Tariff Info Found", "Try simplifying the product description or checking spelling.", "🧾")


# --- Tab 6: Landed Cost Calculator ---
with tab6:
    st.header("Landed Cost Calculator")
    with st.form("tariff_calc_form"):
        col1, col2 = st.columns(2, gap="large")
        with col1:
            with st.container():
                material_cost_usd = st.number_input("Unit Cost (USD)", min_value=0.0, value=10.0, step=0.01)
                quantity = st.number_input("Quantity (units)", min_value=1, value=100)
        with col2:
            with st.container():
                tariff_rate_percent = st.number_input("Tariff Rate (%)", min_value=0.0, value=5.0, step=0.01)
                other_fees_usd = st.number_input("Other Fees (USD)", min_value=0.0, value=25.0, step=0.01)
        submitted_calc = st.form_submit_button("🔢 Calculate Landed Cost", use_container_width=True)

    if submitted_calc:
        with st.spinner("Calculating..."):
            params = {
                "material_cost_usd": material_cost_usd,
                "quantity": quantity,
                "tariff_rate_percent": tariff_rate_percent,
                "other_fees_usd": other_fees_usd
            }
            resp = requests.get(f"{BACKEND_URL}/calculate-tariff", params=params)
            data = handle_api_response(resp)
        if data:
            st.json(data)
            with st.form("chat_form_tab6"):
                st.markdown("#### 💬 Chat About This Calculation")
                user_q = st.text_input("Ask about this calculation:", key="tab6_chat")