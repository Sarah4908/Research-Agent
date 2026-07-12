"""
AI Research Agent — Streamlit front-end for IBM watsonx Orchestrate
"""

import os
import re
import time
import requests
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF

load_dotenv()

# ── Environment ───────────────────────────────────────────────────────────────
IBM_API_KEY  = os.getenv("IBM_API_KEY", "")
WXO_HOST_URL = os.getenv("WXO_HOST_URL", "").rstrip("/")
WXO_AGENT_ID = os.getenv("WXO_AGENT_ID", "")

IAM_TOKEN_URL = "https://iam.cloud.ibm.com/identity/token"

# ── Palette (teal / cream) ────────────────────────────────────────────────────
TEAL       = "#1a5f4a"
TEAL_LIGHT = "#e6f2ee"
CREAM      = "#faf8f5"
BORDER     = "#d8d2c4"
TEXT       = "#22302b"
MUTED      = "#6b7a73"
WHITE      = "#ffffff"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Research Agent",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
html, body, [data-testid="stAppViewContainer"] {{
    background: {CREAM} !important;
    font-family: "Segoe UI", -apple-system, system-ui, sans-serif;
    color: {TEXT};
}}
#MainMenu, header, footer, [data-testid="stSidebar"],
[data-testid="collapsedControl"] {{ display: none !important; }}

[data-testid="block-container"] {{
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: 2.2rem 2rem 3rem !important;
}}

.hero {{ text-align: center; padding: 1.2rem 0 1.8rem; }}
.hero h1 {{
    font-size: 2.15rem; font-weight: 700; color: {TEAL};
    margin-bottom: .3rem; letter-spacing: -.5px;
}}
.hero p {{ color: {MUTED}; font-size: 1.02rem; margin: 0; }}

.examples-label, .section-title {{
    font-size: .75rem; font-weight: 700; color: {MUTED};
    text-transform: uppercase; letter-spacing: .07em;
    margin: 1rem 0 .5rem;
}}

.response-card {{
    background: {CREAM}; border: 1px solid {CREAM}; border-radius: 10px;
    padding: 1rem 1.4rem 1.1rem; margin-top: 0.8rem;
}}
.response-card * {{
    background: transparent !important;
    box-shadow: none !important;
    border-color: transparent !important;
}}
.section-title {{
    border-bottom: 1px solid {TEAL_LIGHT}; padding-bottom: .3rem;
    color: {TEAL}; margin-top: 1.2rem;
}}
.section-title:first-child {{ margin-top: 0; }}

.tag-row {{ display: flex; flex-wrap: wrap; gap: .45rem; }}
.tag {{
    background: {TEAL_LIGHT}; color: {TEAL}; border: 1px solid {BORDER};
    border-radius: 20px; padding: .22rem .75rem; font-size: .82rem; font-weight: 500;
}}

.hypo-box {{
    background: {TEAL_LIGHT}; border-left: 4px solid {TEAL};
    border-radius: 0 8px 8px 0; padding: .9rem 1.1rem;
}}
.hypo-box ol {{ margin: 0; padding-left: 1.1rem; }}
.hypo-box li {{ margin-bottom: .5rem; font-size: .93rem; line-height: 1.6; }}

.summary-text, .outline-list, .ref-list {{ font-size: .93rem; line-height: 1.7; color: {TEXT}; }}
.ref-list a {{ color: {TEAL}; text-decoration: none; }}
.ref-list a:hover {{ text-decoration: underline; }}

.loading-msg {{ text-align: center; color: {MUTED}; font-size: .92rem; padding: 1rem 0; font-style: italic; }}

.footer {{
    text-align: center; font-size: .78rem; color: {MUTED};
    border-top: 1px solid {BORDER}; margin-top: 2.5rem; padding-top: .9rem;
}}

div[data-testid="stButton"] > button {{
    background: {TEAL}; color: #fff; border: none; border-radius: 8px;
    padding: .55rem 1.4rem; font-size: .93rem; font-weight: 600;
}}
div[data-testid="stButton"] > button:hover {{ background: #134539; }}
div[data-testid="stDownloadButton"] > button {{
    background: {WHITE}; color: {TEAL}; border: 1px solid {TEAL};
    border-radius: 8px; font-size: .86rem; font-weight: 500;
}}
div[data-testid="stDownloadButton"] > button:hover {{ background: {TEAL_LIGHT}; }}

.stTabs [data-baseweb="tab"] {{ font-weight: 600; color: {MUTED}; }}
.stTabs [aria-selected="true"] {{ color: {TEAL} !important; }}

/* ---- File uploader — match teal/cream theme instead of default dark ---- */
[data-testid="stFileUploaderDropzone"] {{
    background: {WHITE} !important;
    border: 2px dashed {BORDER} !important;
    border-radius: 10px !important;
}}
[data-testid="stFileUploaderDropzone"] * {{
    color: {TEXT} !important;
}}
[data-testid="stFileUploaderDropzone"] button {{
    background: {TEAL} !important;
    color: #fff !important;
    border: none !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] svg {{
    fill: {MUTED} !important;
}}
[data-testid="stFileUploaderFile"] {{
    background: {TEAL_LIGHT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TEXT} !important;
}}

/* ---- Chat thread bubbles ---- */
.chat-user {{
    background: {TEAL_LIGHT};
    border: 1px solid {BORDER};
    border-radius: 12px 12px 3px 12px;
    padding: 10px 16px;
    margin: 14px 0 6px auto;
    max-width: 75%;
    font-size: .93rem;
    color: {TEXT};
}}
.chat-user-wrap {{ display: flex; justify-content: flex-end; }}


/* ---- Chat input (fixed) ---- */
[data-testid="stChatInput"] {{
    max-width:1100px !important;
    margin:0 auto !important;
    background:{WHITE} !important;
    border:2px solid {TEAL} !important;
    border-radius:28px !important;
    padding:6px 12px !important;
    box-shadow:0 2px 10px rgba(26,95,74,.08) !important;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color:{TEAL} !important;
    box-shadow:0 0 0 3px {TEAL_LIGHT} !important;
}}
[data-testid="stChatInput"] *,
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input,
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInput"] [data-baseweb="input"] {{
    border:none !important;
    outline:none !important;
    box-shadow:none !important;
    background:transparent !important;
}}
[data-testid="stChatInput"] textarea {{
    color:{TEXT} !important;
    -webkit-text-fill-color:{TEXT} !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color:{MUTED} !important;
}}
[data-testid="stChatInput"] button {{
    background:{TEAL} !important;
    color:#fff !important;
    border:none !important;
    border-radius:50% !important;
}}
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"] {{
    background:transparent !important;
    border:none !important;
    box-shadow:none !important;
}}
</style>
""", unsafe_allow_html=True)


# ── IBM IAM token ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=3300, show_spinner=False)
def get_iam_token(api_key: str) -> str:
    resp = requests.post(
        IAM_TOKEN_URL,
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


# ── Orchestrate API call ───────────────────────────────────────────────────────
# Confirmed endpoint (IBM ADK docs): POST {host}/v1/orchestrate/{agent_id}/chat/completions
def call_orchestrate(question: str) -> str:
    if not IBM_API_KEY or IBM_API_KEY == "your_api_key_here":
        raise ValueError(
            "IBM_API_KEY is not set. Open your .env file and replace "
            "'your_api_key_here' with your IBM Cloud IAM API key."
        )
    if not WXO_HOST_URL or not WXO_AGENT_ID:
        raise ValueError("WXO_HOST_URL or WXO_AGENT_ID is missing from your .env file.")

    token = get_iam_token(IBM_API_KEY)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    url = f"{WXO_HOST_URL}/v1/orchestrate/{WXO_AGENT_ID}/chat/completions"

    resp = requests.post(
        url,
        json={
            "messages": [{"role": "user", "content": question}],
            "stream": False,
        },
        headers=headers,
        timeout=120,
    )
    resp.raise_for_status()
    data = resp.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        pass
    try:
        return data["choices"][0]["text"]
    except (KeyError, IndexError, TypeError):
        pass

    return str(data)


# ── PDF text extraction ────────────────────────────────────────────────────────
def extract_pdf_text(uploaded_file) -> str:
    import pdfplumber
    text_parts = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages[:20]:  # cap at 20 pages to keep prompt size reasonable
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


# ── Response parser ────────────────────────────────────────────────────────────
# NOTE: The agent's output format varies (tables, bullet lists, etc.), so rather
# than fragile regex-parsing into custom sections, we keep the raw markdown and
# let Streamlit's native markdown renderer (and a simple PDF dump) handle it.
def parse_response(text: str) -> dict:
    return {"raw": text}


# ── PDF builder (for download) ─────────────────────────────────────────────────
def build_pdf(question: str, sections: dict) -> bytes:
    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    def clean(s: str) -> str:
        # Strip markdown symbols and non-ASCII chars so Helvetica can render it
        s = re.sub(r"[#*_`|]", "", s)
        s = re.sub(r"[^\x00-\x7F]+", "-", s)
        return s

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(26, 95, 74)
    pdf.multi_cell(0, 10, "AI Research Agent", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(107, 122, 115)
    pdf.multi_cell(0, 7, "Powered by IBM watsonx Orchestrate + arXiv", align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(26, 95, 74)
    pdf.multi_cell(0, 8, "Research Question")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(34, 48, 43)
    pdf.multi_cell(0, 7, clean(question))
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(26, 95, 74)
    pdf.multi_cell(0, 8, "Research Agent Response")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(34, 48, 43)

    import textwrap
    raw_text = sections.get("raw", "")
    for line in raw_text.split("\n"):
        stripped = line.strip()
        # Skip markdown table separator rows (e.g. "|---|---|---|") — after
        # stripping pipes these become one unbreakable dash string that is
        # too wide for a single line and crashes fpdf2.
        if re.fullmatch(r"[\s\-|:]*", stripped):
            pdf.ln(2)
            continue
        cleaned_line = clean(line).strip()
        if not cleaned_line:
            pdf.ln(2)
            continue
        # Force-wrap at a safe character width (guarantees every line fits,
        # even single "words" like long URLs with no natural break points).
        wrapped = textwrap.wrap(
            cleaned_line, width=85, break_long_words=True, break_on_hyphens=False
        ) or [""]
        for wline in wrapped:
            pdf.multi_cell(0, 6, wline)

    return bytes(pdf.output())


# ── Render response ────────────────────────────────────────────────────────────
def render_response(question: str, sections: dict, key_prefix: str = "resp"):
    st.markdown('<div class="response-card">', unsafe_allow_html=True)
    # Let Streamlit's native markdown renderer handle whatever format the agent
    # returns (tables, bold, numbered lists, links, etc.) instead of fragile
    # custom regex parsing.
    st.markdown(sections.get("raw", ""))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    try:
        pdf_bytes = build_pdf(question, sections)
        st.download_button(
            label="Download as PDF",
            data=pdf_bytes,
            file_name="research_agent_output.pdf",
            mime="application/pdf",
            key=f"{key_prefix}_download",
        )
    except Exception:
        st.download_button(
            label="Download as Text",
            data=f"AI Research Agent\n\nQuestion: {question}\n\n{sections.get('raw', '')}",
            file_name="research_agent_output.txt",
            mime="text/plain",
            key=f"{key_prefix}_download_txt",
        )


# ── Main UI ───────────────────────────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="hero">
        <h1>AI Research Agent</h1>
        <p>Search, summarize, and organize academic literature</p>
    </div>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []  # list of {"question": ..., "answer": ...}
    if "_pending_question" not in st.session_state:
        st.session_state._pending_question = None
    if "_pending_label" not in st.session_state:
        st.session_state._pending_label = None
    if "paper_context" not in st.session_state:
        st.session_state.paper_context = None  # (filename, extracted_text) once a paper is uploaded

    def _run_question(active_question: str, display_label: str | None = None):
        """Send a question (optionally with paper context) and append to chat history."""
        st.markdown(
            f'<div class="chat-user-wrap"><div class="chat-user">{display_label or active_question}</div></div>',
            unsafe_allow_html=True,
        )
        loading_placeholder = st.empty()
        for msg in ["Searching arXiv...", "Retrieving relevant papers...",
                    "Synthesizing findings...", "Structuring your response..."]:
            loading_placeholder.markdown(f'<div class="loading-msg">{msg}</div>', unsafe_allow_html=True)
            time.sleep(0.25)

        # Recent conversation context
        context_parts = []
        for exchange in st.session_state.chat_history[-3:]:
            context_parts.append(f"Previous question: {exchange['question']}")
            context_parts.append(f"Previous answer: {exchange['answer'][:800]}")

        # Uploaded-paper context, if any
        paper_note = ""
        if st.session_state.paper_context:
            fname, ptext = st.session_state.paper_context
            paper_note = (
                f"\n\nThe user has uploaded a paper titled/named '{fname}'. "
                f"Its content (may be truncated):\n{ptext[:10000]}"
            )

        prefix = ""
        if context_parts:
            prefix = "This is a follow-up in an ongoing research conversation. Recent context:\n\n" + \
                     "\n\n".join(context_parts) + "\n\n"
        full_prompt = f"{prefix}{paper_note}\n\nQuestion: {active_question}" if (prefix or paper_note) else active_question

        try:
            raw_response = call_orchestrate(full_prompt)
            loading_placeholder.empty()
            st.session_state.chat_history.append({
                "question": display_label or active_question,
                "answer": raw_response,
            })
            st.rerun()
        except ValueError as e:
            loading_placeholder.empty()
            st.error(f"**Configuration error:** {e}")
        except requests.HTTPError as e:
            loading_placeholder.empty()
            st.error(f"**API error {e.response.status_code}:** {e.response.text[:500]}")
        except Exception as e:
            loading_placeholder.empty()
            st.error(f"**Unexpected error:** {e}")

    # ── Attach a paper (optional, feeds context into the chat below) ──
    if st.session_state.paper_context:
        fname, _ = st.session_state.paper_context
        st.markdown(
            f'<div class="examples-label">📎 {fname} attached — your questions can reference it '
            f'(<a href="#" id="clear_paper">clear</a>)</div>',
            unsafe_allow_html=True
        )

    # ── Chat thread ──
    for i, exchange in enumerate(st.session_state.chat_history):
        st.markdown(
            f'<div class="chat-user-wrap"><div class="chat-user">{exchange["question"]}</div></div>',
            unsafe_allow_html=True,
        )
        render_response(exchange["question"], {"raw": exchange["answer"]}, key_prefix=f"hist_{i}")

    if not st.session_state.chat_history:
        EXAMPLES = [
            "Search for recent papers on machine learning in climate prediction",
            "Suggest research hypotheses on AI-driven drug discovery",
            "Draft a literature review outline on renewable energy storage",
        ]
        st.markdown('<div class="examples-label">Try an example</div>', unsafe_allow_html=True)
        ex_cols = st.columns(3)
        for i, (col, example) in enumerate(zip(ex_cols, EXAMPLES)):
            with col:
                if st.button(example, key=f"ex_{i}", use_container_width=True):
                    st.session_state._pending_question = example

    # chat_input with inline attach button — ChatGPT/Claude-style single bar
    prompt = st.chat_input(
        "Ask a research question, or attach a paper...",
        accept_file=True,
        file_type=["pdf"],
    )

    if prompt:
        typed_text = (prompt.text or "").strip()
        uploaded_file = prompt.files[0] if prompt.files else None

        if uploaded_file is not None:
            extract_placeholder = st.empty()
            extract_placeholder.markdown('<div class="loading-msg">Reading PDF...</div>', unsafe_allow_html=True)
            try:
                paper_text = extract_pdf_text(uploaded_file)
                extract_placeholder.empty()
                if not paper_text.strip():
                    st.error("Couldn't extract text from this PDF. It may be a scanned image without selectable text.")
                else:
                    st.session_state.paper_context = (uploaded_file.name, paper_text)
                    question_text = typed_text or (
                        "Analyze the uploaded research paper. Summarize its key findings, "
                        "methodology, and contributions. Present your response in clear sections: "
                        "Key Concepts, Summary, Suggested Hypotheses, Draft Outline, References."
                    )
                    label = f"{typed_text} 📎 {uploaded_file.name}" if typed_text else f"Analyze paper: {uploaded_file.name}"
                    st.session_state._pending_question = question_text
                    st.session_state._pending_label = label
            except Exception as e:
                extract_placeholder.empty()
                st.error(f"**Error reading PDF:** {e}")
        elif typed_text:
            st.session_state._pending_question = typed_text
            st.session_state._pending_label = None

    if st.session_state._pending_question:
        q = st.session_state._pending_question
        label = st.session_state.get("_pending_label")
        st.session_state._pending_question = None
        st.session_state._pending_label = None
        _run_question(q, display_label=label)

    st.markdown('<div class="footer">Powered by IBM watsonx Orchestrate + arXiv</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()