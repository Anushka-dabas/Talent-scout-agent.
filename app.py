import streamlit as st
import json
import os
import pandas as pd
from scout import get_match_score, start_outreach, check_interest

st.set_page_config(page_title="TalentScout Pro", layout="wide", page_icon="🎯")

# Professional Light Theme
st.markdown("""
<style>
    .stApp { background-color: #f3f2ef; }
    h1, h2, h3, p, label { color: #000000 !important; font-family: 'Segoe UI', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #004182 !important; }
    section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p { color: white !important; }
    .stButton>button { background-color: #0077b5; color: white !important; border-radius: 25px; border: none; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<h2 style='color:white;'>Hiring Tools</h2>", unsafe_allow_html=True)
    exp_options = ["Fresher", "1", "2", "3", "4", "5", "6-10", "10+"]
    exp_val = st.selectbox("Target Experience (Years)", options=exp_options, index=2)
    st.divider()
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

st.title("🎯 TalentScout Pro")

# --- SOURCING SECTION ---
st.subheader("1. Candidate Sourcing")
col1, col2 = st.columns([2, 1])

with col1:
    jd_input = st.text_area("Job Description & Career Details:", height=200, placeholder="Paste JD with career growth details here...")

with col2:
    source_type = st.radio("Sourcing Method:", ["URL Link", "PDF Resume"])
    if source_type == "PDF Resume":
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    else:
        url_link = st.text_input("Paste Profile URL:")

if st.button("Analyze & Rank Match", use_container_width=True):
    if not jd_input:
        st.error("Please enter JD first.")
    else:
        st.session_state.current_jd = jd_input
        results = []
        
        with st.status("Analyzing Candidate Profile...", expanded=True) as status:
            s_data = url_link if source_type == "URL Link" and url_link else ""
            if source_type == "PDF Resume" and uploaded_file:
                s_data = uploaded_file.name
            
            if s_data:
                out = get_match_score(jd_input, s_data, exp_val)
                
                # Fixed Parsing Logic to avoid 50% default
                try:
                    s_text = out.split("Score:")[1].split("\n")[0].strip()
                    # Remove any extra characters like '%' or '.'
                    score = int(''.join(filter(str.isdigit, s_text)))
                    reason = out.split("Reason:")[1].split("Gaps:")[0].strip()
                    gaps = out.split("Gaps:")[1].strip()
                    
                    results.append({"Candidate": s_data, "Match": score, "Analysis": reason, "Gaps": gaps})
                except Exception as e:
                    # If parsing fails, we show the raw AI output instead of 50%
                    st.warning("Parsing adjustment required. Showing raw analysis.")
                    results.append({"Candidate": s_data, "Match": 0, "Analysis": out, "Gaps": "Check manually"})
            
            if results:
                st.session_state.shortlist = results
                status.update(label="Complete!", state="complete")
            else:
                status.update(label="No source detected.", state="error")

# --- RESULTS DASHBOARD ---
if "shortlist" in st.session_state:
    st.divider()
    st.subheader("2. Ranked Shortlist Dashboard")
    
    df = pd.DataFrame(st.session_state.shortlist)
    st.dataframe(df, column_order=("Candidate", "Match", "Gaps"), column_config={
        "Match": st.column_config.ProgressColumn("Match Strength", format="%d%%", min_value=0, max_value=100)
    }, use_container_width=True, hide_index=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.write("**Candidate Audit Trail**")
        for i, m in enumerate(st.session_state.shortlist):
            with st.expander(f"👤 {m['Candidate']} - {m['Match']}%"):
                st.write(f"**Analysis:** {m['Analysis']}")
                st.error(f"**Gaps:** {m['Gaps']}")
                if st.button(f"Engage {m['Candidate']}", key=f"e_{i}"):
                    st.session_state.target = m['Candidate']
                    # Recruiter starts the chat
                    st.session_state.chat = [("Recruiter", start_outreach(m['Candidate'], st.session_state.current_jd))]
                    st.rerun()

    with c2:
        if "target" in st.session_state:
            st.write(f"**Messaging: {st.session_state.target}**")
            for role, msg in st.session_state.chat:
                with st.chat_message("assistant" if role == "Recruiter" else "user"):
                    st.markdown(f"**{role}:** {msg}")
            
            if reply := st.chat_input("Enter candidate response..."):
                st.session_state.chat.append(("Candidate", reply))
                st.session_state.i_score = check_interest(reply)
                st.rerun()
            
            if "i_score" in st.session_state:
                st.metric("Candidate Interest Score", f"{st.session_state.i_score}/100")