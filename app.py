import html
import os
import time
from datetime import datetime
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

load_dotenv()

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Briefly | AI news summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Instrument+Sans:wght@400;500;600&display=swap');

:root {
    --paper: #EEF2F8;
    --card: #FFFFFF;
    --ink: #13213C;
    --muted: #5B6A86;
    --line: #D7DEEA;
    --cobalt: #2D5BFF;
    --cobalt-deep: #1B3FCC;
    --amber: #FFC857;
}

html, body, [class*="css"], .stApp {
    font-family: 'Instrument Sans', system-ui, sans-serif;
    color: var(--ink);
}
.stApp { background: var(--paper); }

/* hide default chrome */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 2.5rem; padding-bottom: 4rem; max-width: 1180px; }

/* hero */
.hero { margin-bottom: 1.6rem; }
.hero h1 {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 800;
    font-size: clamp(2.2rem, 5vw, 3.6rem);
    line-height: 1.02;
    letter-spacing: -0.03em;
    margin: 0 0 .7rem 0;
    color: var(--ink);
}
.hero p { color: var(--muted); font-size: 1.08rem; max-width: 46ch; margin: 0; }
.brand {
    display: inline-flex; align-items: center; gap: .5rem;
    font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700;
    font-size: 1rem; margin-bottom: 1.2rem; color: var(--ink);
}
.brand-dot { width: 14px; height: 14px; border-radius: 4px; background: var(--cobalt); box-shadow: 5px 5px 0 var(--amber); }

/* search form */
[data-testid="stForm"] {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 1.1rem 1.2rem .6rem 1.2rem;
    box-shadow: 0 10px 30px -18px rgba(19, 33, 60, .35);
}
.stTextInput input {
    font-size: 1.1rem;
    padding: .85rem 1rem;
    border-radius: 12px;
    border: 1.5px solid var(--line);
    background: #F8FAFD;
    color: var(--ink);
}
.stTextInput input:focus { border-color: var(--cobalt); box-shadow: 0 0 0 3px rgba(45, 91, 255, .15); }
.stTextInput label { display: none; }

/* buttons */
.stButton > button, [data-testid="stFormSubmitButton"] > button, .stDownloadButton > button {
    background: var(--cobalt);
    color: #fff;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    padding: .7rem 1.4rem;
    transition: background .15s ease, transform .1s ease;
}
.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover, .stDownloadButton > button:hover {
    background: var(--cobalt-deep); color: #fff; border: none;
}
.stButton > button:active, [data-testid="stFormSubmitButton"] > button:active { transform: scale(.98); }
.stDownloadButton > button { background: transparent; color: var(--cobalt); border: 1.5px solid var(--cobalt); }
.stDownloadButton > button:hover { background: var(--cobalt); color: #fff; }
button:focus-visible { outline: 3px solid var(--amber) !important; outline-offset: 2px; }

/* sidebar */
section[data-testid="stSidebar"] { background: var(--ink); border-right: none; }
section[data-testid="stSidebar"] > div { padding-top: 1rem; }
section[data-testid="stSidebar"] * { color: #E8EEFB; }
section[data-testid="stSidebar"] hr { border-color: #2C4170; margin: 1.2rem 0; }

.side-head { margin-bottom: 1.4rem; }
.side-head .t {
    font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
    font-size: 1.5rem; letter-spacing: -0.02em; color: #FFFFFF !important; margin-bottom: .25rem;
}
.side-head .d { color: #A9B8D8 !important; font-size: .9rem; line-height: 1.4; }
.side-group {
    font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1rem;
    color: var(--amber) !important; margin: 1.1rem 0 .5rem 0;
}

/* widget labels */
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #FFFFFF !important; font-weight: 600; font-size: .88rem;
}

/* radio as selectable rows */
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    width: 100%; padding: .55rem .75rem; margin-bottom: .35rem;
    border: 1px solid #2C4170; border-radius: 10px; background: #1A2D55;
    transition: background .15s ease, border-color .15s ease;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background: #22396A; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: #22396A; border-color: var(--amber);
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label p { color: #FFFFFF !important; font-size: .95rem; }

/* select box */
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #1A2D55; border: 1px solid #34508C; border-radius: 10px;
}
section[data-testid="stSidebar"] [data-baseweb="select"] * { color: #FFFFFF !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] svg { fill: #FFFFFF !important; }

/* dropdown list (renders outside the sidebar) */
div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li { background: #FFFFFF !important; }
div[data-baseweb="popover"] li * { color: var(--ink) !important; }
div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li[aria-selected="true"] { background: #EEF2F8 !important; }

/* slider */
section[data-testid="stSidebar"] [data-testid="stSliderThumbValue"] {
    color: var(--amber) !important; font-weight: 700;
}
section[data-testid="stSidebar"] [data-testid="stTickBarMin"],
section[data-testid="stSidebar"] [data-testid="stTickBarMax"] { color: #A9B8D8 !important; }
section[data-testid="stSidebar"] [role="slider"] {
    background: var(--amber) !important; box-shadow: 0 0 0 4px rgba(255, 200, 87, .25);
}

/* expander */
section[data-testid="stSidebar"] [data-testid="stExpander"] details {
    background: #1A2D55; border: 1px solid #2C4170; border-radius: 12px;
}
section[data-testid="stSidebar"] [data-testid="stExpander"] summary p { color: #FFFFFF !important; font-weight: 600; }

/* status pill */
.pill {
    display: inline-flex; align-items: center; gap: .55rem; padding: .5rem .8rem;
    border-radius: 999px; background: #1A2D55; border: 1px solid #2C4170; font-size: .88rem;
}
.pill i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
.pill.ok i { background: #3DDC97; }
.pill.bad i { background: var(--amber); }

/* summary panel */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card);
    border: 1px solid var(--line) !important;
    border-radius: 18px;
    box-shadow: 0 10px 30px -18px rgba(19, 33, 60, .35);
}
.summary-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 700; font-size: 1.5rem; letter-spacing: -0.02em; margin: .2rem 0 .2rem 0;
}
.summary-meta { color: var(--muted); font-size: .9rem; margin-bottom: .6rem; }
[data-testid="stVerticalBlockBorderWrapper"] li { margin-bottom: .55rem; line-height: 1.55; }
[data-testid="stVerticalBlockBorderWrapper"] p { line-height: 1.6; }

/* source cards */
.col-title {
    font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.15rem; margin-bottom: .7rem;
}
.src {
    display: block; text-decoration: none !important; color: var(--ink) !important;
    background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--cobalt);
    border-radius: 12px; padding: .85rem 1rem; margin-bottom: .75rem;
    transition: border-color .15s ease, box-shadow .15s ease;
}
.src:hover { border-left-color: var(--amber); box-shadow: 0 8px 22px -14px rgba(19, 33, 60, .45); }
.src:focus-visible { outline: 3px solid var(--amber); outline-offset: 2px; }
.src-top { display: flex; align-items: center; gap: .5rem; margin-bottom: .35rem; }
.src-num {
    background: var(--ink); color: #fff; font-weight: 600; font-size: .75rem;
    min-width: 1.4rem; height: 1.4rem; display: inline-flex; align-items: center; justify-content: center;
    border-radius: 6px;
}
.src-domain { color: var(--muted); font-size: .82rem; }
.src-title { font-weight: 600; line-height: 1.3; margin-bottom: .3rem; }
.src-body { color: var(--muted); font-size: .87rem; line-height: 1.45; }

/* empty state */
.empty {
    border: 1.5px dashed #B8C3D8; border-radius: 18px; padding: 2rem 1.6rem; margin-top: 1.4rem;
    color: var(--muted);
}
.empty b { color: var(--ink); font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.15rem; display: block; margin-bottom: .3rem; }

/* example topic chips */
[class*="st-key-ex_"] button {
    background: transparent; color: var(--cobalt); border: 1.5px solid #B9C7E6;
    font-weight: 500; font-size: .9rem; padding: .5rem .8rem;
}
[class*="st-key-ex_"] button:hover { background: #E1E8F8; color: var(--cobalt-deep); border: 1.5px solid var(--cobalt); }

@media (prefers-reduced-motion: reduce) {
    * { transition: none !important; animation: none !important; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
]

STYLES = {
    "Bullet points": "Write 5-8 clear bullet points. Each bullet is one or two sentences.",
    "Quick brief": "Write a single short paragraph (about 80 words) followed by 3 key takeaways as bullets.",
    "Deep dive": "Write a short intro, then group the news under 2-4 bold themes with bullets under each theme.",
}

TIME_RANGES = {
    "Past 24 hours": "day",
    "Past week": "week",
    "Past month": "month",
    "Past year": "year",
}

EXAMPLES = [
    "Latest AI news of 2026",
    "Open-source language models",
    "AI regulation worldwide",
    "AI in healthcare",
]

PROMPT = ChatPromptTemplate.from_template(
    """
You are a sharp, neutral news editor.
Summarize the news below for a busy reader.

{style_instruction}

Rules:
- Use only facts from the sources. Do not invent details.
- Mention the source number in square brackets after each claim, like [1] or [2][3].
- Skip duplicates and ads.
- Use markdown.

Topic: {topic}

Sources:
{news}
"""
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def domain_of(url: str) -> str:
    host = urlparse(url).netloc.replace("www.", "")
    return host or "source"


def fetch_news(topic: str, max_results: int, time_range: str) -> list[dict]:
    tool = TavilySearch(max_results=max_results, topic="news", time_range=time_range)
    raw = tool.invoke({"query": topic})
    if isinstance(raw, dict):
        results = raw.get("results", [])
        if not results and raw.get("error"):
            raise RuntimeError(str(raw["error"]))
        return results
    raise RuntimeError(f"Unexpected search response: {raw}")


def format_sources(results: list[dict]) -> str:
    blocks = []
    for i, r in enumerate(results, 1):
        blocks.append(
            f"[{i}] {r.get('title', 'Untitled')} ({domain_of(r.get('url', ''))})\n{r.get('content', '')}"
        )
    return "\n\n".join(blocks)


def summarize(topic: str, results: list[dict], style: str, model: str, temperature: float) -> str:
    llm = ChatGroq(model=model, temperature=temperature)
    chain = PROMPT | llm | StrOutputParser()
    return chain.invoke(
        {
            "topic": topic,
            "style_instruction": STYLES[style],
            "news": format_sources(results),
        }
    )


def source_card(i: int, r: dict) -> str:
    title = html.escape(r.get("title") or "Untitled")
    url = html.escape(r.get("url") or "#", quote=True)
    body = (r.get("content") or "").strip().replace("\n", " ")
    body = html.escape(body[:200] + ("…" if len(body) > 200 else ""))
    return f"""
    <a class="src" href="{url}" target="_blank" rel="noopener noreferrer">
        <div class="src-top">
            <span class="src-num">{i}</span>
            <span class="src-domain">{html.escape(domain_of(r.get('url', '')))}</span>
        </div>
        <div class="src-title">{title}</div>
        <div class="src-body">{body}</div>
    </a>
    """


def build_markdown_export(topic: str, summary: str, results: list[dict]) -> str:
    lines = [f"# {topic}", f"_Generated {datetime.now():%d %b %Y, %H:%M}_", "", summary, "", "## Sources"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. [{r.get('title', 'Untitled')}]({r.get('url', '')})")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="side-head">
            <div class="t">Settings</div>
            <div class="d">Choose how Briefly searches and writes your summary.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="side-group">Summary</div>', unsafe_allow_html=True)
    style = st.radio("Style", list(STYLES.keys()), index=0)

    st.markdown('<div class="side-group">Search</div>', unsafe_allow_html=True)
    time_label = st.selectbox("News from", list(TIME_RANGES.keys()), index=1)
    max_results = st.slider("Number of sources", 3, 10, 5)

    st.markdown('<div class="side-group">Model</div>', unsafe_allow_html=True)
    with st.expander("Model options"):
        model = st.selectbox("Groq model", MODELS, index=0)
        temperature = st.slider("Creativity", 0.0, 1.0, 0.2, 0.05)

    st.divider()
    keys_ok = bool(os.getenv("GROQ_API_KEY")) and bool(os.getenv("TAVILY_API_KEY"))
    if keys_ok:
        st.markdown('<div class="pill ok"><i></i>API keys found</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="pill bad"><i></i>Add GROQ_API_KEY and TAVILY_API_KEY to .env</div>',
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Hero + search
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <div class="brand"><span class="brand-dot"></span>Briefly</div>
        <h1>The news, minus the noise.</h1>
        <p>Pick a topic. Briefly searches the web and boils the latest stories down to what matters.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "topic_input" not in st.session_state:
    st.session_state.topic_input = "Latest AI news of 2026"
if "result" not in st.session_state:
    st.session_state.result = None

with st.form("search_form", border=True):
    topic = st.text_input(
        "Topic",
        key="topic_input",
        placeholder="What do you want to catch up on?",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Summarize")

# example topics
ex_cols = st.columns(len(EXAMPLES))
clicked_example = None
for col, ex in zip(ex_cols, EXAMPLES):
    if col.button(ex, key=f"ex_{ex}", use_container_width=True):
        clicked_example = ex

if clicked_example:
    topic = clicked_example
    submitted = True

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if submitted:
    if not topic.strip():
        st.error("Type a topic first, for example “AI in healthcare”.")
    elif not keys_ok:
        st.error("API keys are missing. Add GROQ_API_KEY and TAVILY_API_KEY to your .env file and restart the app.")
    else:
        start = time.time()
        try:
            with st.status("Working on it…", expanded=True) as status:
                st.write("Searching the web for fresh stories")
                results = fetch_news(topic.strip(), max_results, TIME_RANGES[time_label])
                if not results:
                    status.update(label="No stories found", state="error")
                    st.session_state.result = None
                    st.error("No stories found. Try a broader topic or a longer time range.")
                    st.stop()
                st.write(f"Found {len(results)} sources. Writing the summary")
                summary = summarize(topic.strip(), results, style, model, temperature)
                status.update(label="Done", state="complete", expanded=False)

            st.session_state.result = {
                "topic": topic.strip(),
                "summary": summary,
                "results": results,
                "seconds": time.time() - start,
                "model": model,
                "time_label": time_label,
            }
        except Exception as e:
            st.session_state.result = None
            st.error(f"Something went wrong: {e}")

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
data = st.session_state.result

if data:
    left, right = st.columns([1.65, 1], gap="large")

    with left:
        with st.container(border=True):
            st.markdown(f'<div class="summary-title">{html.escape(data["topic"])}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="summary-meta">{len(data["results"])} sources from the {data["time_label"].lower()}, '
                f'summarized with {html.escape(data["model"])} in {data["seconds"]:.1f}s</div>',
                unsafe_allow_html=True,
            )
            st.markdown(data["summary"])

        st.write("")
        st.download_button(
            "Download summary",
            data=build_markdown_export(data["topic"], data["summary"], data["results"]),
            file_name="news_summary.md",
            mime="text/markdown",
        )

    with right:
        st.markdown('<div class="col-title">Sources</div>', unsafe_allow_html=True)
        cards = "".join(source_card(i, r) for i, r in enumerate(data["results"], 1))
        st.markdown(cards, unsafe_allow_html=True)
else:
    st.markdown(
        """
        <div class="empty">
            <b>Nothing here yet</b>
            Enter a topic above or tap one of the examples to get your first summary.
        </div>
        """,
        unsafe_allow_html=True,
    )