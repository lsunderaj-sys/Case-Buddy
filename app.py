import streamlit as st
import google.generativeai as genai
from cases import CASE_STUDIES

# Setup AI - You will need to add your API Key in Streamlit Secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Case Buddy | H2 Economics", layout="wide")
st.title("🎓 Case Buddy: H2 Economics Feedback Assistant")

# Sidebar for Case Selection
selected_case_title = st.sidebar.selectbox("Select a Case Study", [c["title"] for c in CASE_STUDIES])
case = next(c for c in CASE_STUDIES if c["title"] == selected_case_title)

# Layout: Extracts on the left, Questions on the right
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Case Extracts & Data")
    with st.expander("View Extracts", expanded=True):
        for ext in case["extracts"]:
            st.write(ext)
            st.divider()
    st.info(case["table_data"])

with col2:
    st.header("Your Analysis")
    
    for q in case["questions"]:
        q_id = q["id"]
        # Initialize session state for attempts
        if f"attempts_{q_id}" not in st.session_state:
            st.session_state[f"attempts_{q_id}"] = 0
            st.session_state[f"feedback_{q_id}"] = ""

        st.subheader(q["text"])
        user_answer = st.text_area(f"Type your response for {q_id} here:", key=f"input_{q_id}")
        
        if st.button(f"Get Feedback for {q_id}", key=f"btn_{q_id}"):
            if not user_answer:
                st.warning("Please type something first!")
            else:
                st.session_state[f"attempts_{q_id}"] += 1
                attempts = st.session_state[f"attempts_{q_id}"]
                
                # Socratic Prompting Logic
                prompt = f"""
                You are an expert H2 Economics Tutor for A-Level students. 
                Question: {q['text']}
                Mark Scheme: {case['mark_scheme'][q_id]}
                Student's Answer: {user_answer}
                Attempt Number: {attempts}
                
                Guidelines:
                - If attempts < 3: Use Socratic questioning. Point out gaps in analysis (e.g., missing $PED$ definition or $TR$ formula) without giving the answer.
                - If attempts >= 3: Provide a detailed high-quality model answer and a rough mark estimate out of {q['marks']}.
                - Always be encouraging but maintain high academic rigor.
                """
                
                response = model.generate_content(prompt)
                st.session_state[f"feedback_{q_id}"] = response.text

        # Display Feedback
        if st.session_state[f"feedback_{q_id}"]:
            st.markdown("---")
            st.markdown(f"**Attempt {st.session_state[f'attempts_{q_id}']}/3 Feedback:**")
            st.write(st.session_state[f"feedback_{q_id}"])
