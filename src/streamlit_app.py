import json
import time
import html
import streamlit as st
from planner_service import generate_plan

st.set_page_config(page_title="AI Task Planner Agent", page_icon="✅", layout="centered")

def _type_line(placeholder, css_class: str, text: str, delay: float = 0.035) -> None:
    typed = ""
    for ch in text:
        typed += ch
        placeholder.markdown(
            f"<div class='{css_class}'>{html.escape(typed)}</div>",
            unsafe_allow_html=True,
        )
        time.sleep(delay)

    placeholder.markdown(
        f"<div class='{css_class}'>{html.escape(text)}</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <style>
    :root {
        --heading-size: 3.8rem;
        --sub-size: calc(var(--heading-size) * 0.38);
        --caption-size: calc(var(--heading-size) * 0.26);
    }

    .stApp {
        background: radial-gradient(circle at top left, #0f172a, #111827 35%, #020617 100%);
        color: #e5e7eb;
    }

    .flow-title {
        font-size: var(--heading-size);
        font-weight: 850;
        line-height: 1.1;
        letter-spacing: 0.35px;
        margin-bottom: 0.3rem;

        background: linear-gradient(90deg, #22d3ee, #a78bfa, #f472b6, #22d3ee);
        background-size: 250% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: flowText 5s linear infinite;
    }

    .subtext {
        color: #cbd5e1;
        font-size: var(--sub-size);
        margin-bottom: 0.38rem;
        font-weight: 520;
        line-height: 1.35;
    }

    .glass-caption {
        color: #93c5fd;
        font-size: var(--caption-size);
        margin: 0.05rem 0 0.55rem 0;
        line-height: 1.4;
    }

    @keyframes flowText {
        0% { background-position: 0% center; }
        100% { background-position: 250% center; }
    }

    /* Gradient prompt box */
    div[data-testid="stTextArea"] > div {
        padding: 2px;
        border-radius: 14px;
        background: linear-gradient(120deg, #22d3ee, #8b5cf6, #ec4899, #22d3ee);
        background-size: 250% 250%;
        animation: flowBorder 6s ease infinite;
        box-shadow: 0 8px 30px rgba(34, 211, 238, 0.18);
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 12px !important;
        border: 0 !important;
        color: #f8fafc !important;
        background: linear-gradient(160deg, rgba(15,23,42,0.95), rgba(30,41,59,0.92)) !important;
        backdrop-filter: blur(2px);
    }

    div[data-testid="stTextArea"] {
        background: linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.10),
            rgba(255, 255, 255, 0.04)
        );
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 16px;
        padding: 14px 14px 10px 14px;
        backdrop-filter: blur(10px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.28);
    }

    /* Glassmorphism button */
    div.stButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.26);
        color: #eaf2ff;
        font-weight: 700;
        letter-spacing: 0.2px;
        background: linear-gradient(
            120deg,
            rgba(34, 211, 238, 0.28),
            rgba(139, 92, 246, 0.28),
            rgba(236, 72, 153, 0.25)
        );
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 26px rgba(59, 130, 246, 0.25);
        transition: all 0.25s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        border-color: rgba(255, 255, 255, 0.45);
        box-shadow: 0 14px 30px rgba(168, 85, 247, 0.30);
        filter: brightness(1.06);
    }

    .glass-card {
        margin-top: 1rem;
        border-radius: 18px;
        padding: 1rem;
        background: linear-gradient(
            145deg,
            rgba(15, 23, 42, 0.62),   /* app dark bg tone */
            rgba(30, 41, 59, 0.45)
        );
        border: 1px solid rgba(147, 197, 253, 0.30); /* caption blue */
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow:
            0 14px 36px rgba(2, 6, 23, 0.45),
            inset 0 1px 0 rgba(226, 232, 240, 0.10);
    }

    .card-title {
        margin: 0 0 0.65rem 0;
        font-size: 1.06rem;
        font-weight: 760;
        color: #e2e8f0; /* heading/sub text family */
        padding: 0.6rem 0.75rem;
        border-radius: 12px;
        background: linear-gradient(
            120deg,
            rgba(34, 211, 238, 0.14), /* cyan from flow title */
            rgba(167, 139, 250, 0.12), /* violet from flow title */
            rgba(244, 114, 182, 0.10)  /* pink from flow title */
        );
        border: 1px solid rgba(203, 213, 225, 0.28);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    .card-list {
        margin: 0;
        padding: 0.4rem;
        list-style: none;
        border-radius: 12px;
        background: linear-gradient(
            145deg,
            rgba(15, 23, 42, 0.55),
            rgba(30, 41, 59, 0.40)
        );
        border: 1px solid rgba(148, 163, 184, 0.26);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }

    .card-list li {
        color: #dbeafe; /* existing list text color */
        margin: 0.38rem 0;
        line-height: 1.4;
        padding: 0.55rem 0.7rem;
        border-radius: 10px;
        background: linear-gradient(
            135deg,
            rgba(34, 211, 238, 0.10),
            rgba(139, 92, 246, 0.10),
            rgba(244, 114, 182, 0.08)
        );
        border: 1px solid rgba(147, 197, 253, 0.24);
        box-shadow: inset 0 1px 0 rgba(226, 232, 240, 0.12);
    }

    .card-list li::before {
        content: "• ";
        color: #93c5fd;
        font-weight: 700;
        margin-right: 0.2rem;
    }

    @keyframes flowBorder {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

title_text = "AI Task Planner Agent"
sub_text = "Generate structured agenda, checklist, and timeline from your goal."
caption_text = "Describe your goal and generate a polished plan."

title_placeholder = st.empty()
sub_placeholder = st.empty()
caption_placeholder = st.empty()

if "intro_typed" not in st.session_state:
    _type_line(title_placeholder, "flow-title", title_text, delay=0.04)
    _type_line(sub_placeholder, "subtext", sub_text, delay=0.02)
    _type_line(caption_placeholder, "glass-caption", caption_text, delay=0.015)
    st.session_state.intro_typed = True
else:
    title_placeholder.markdown(f"<div class='flow-title'>{title_text}</div>", unsafe_allow_html=True)
    sub_placeholder.markdown(f"<div class='subtext'>{sub_text}</div>", unsafe_allow_html=True)
    caption_placeholder.markdown(f"<div class='glass-caption'>{caption_text}</div>", unsafe_allow_html=True)

user_goal = st.text_area(
    "Enter your goal",
    placeholder="Example: Plan a 4-week launch roadmap for my portfolio website",
    height=120,
)

if st.button("Generate Plan", type="primary"):
    if not user_goal.strip():
        st.warning("Please enter a goal first.")
    else:
        with st.spinner("Generating your plan..."):
            try:
                plan = generate_plan(user_goal.strip())
            except Exception as exc:
                st.error(f"Failed to generate plan: {exc}")
            else:
                st.success("Plan generated")

                def render_card(title: str, items: list[str]) -> None:
                    list_html = "".join(f"<li>{html.escape(item)}</li>" for item in items)
                    st.markdown(
                        (
                            "<div class='glass-card'>"
                            f"<div class='card-title'>{html.escape(title)}</div>"
                            f"<ul class='card-list'>{list_html}</ul>"
                            "</div>"
                        ),
                        unsafe_allow_html=True,
                    )

                render_card("Agenda", plan.get("agenda", []))
                render_card("Checklist", plan.get("checklist", []))
                render_card("Timeline", plan.get("timeline", []))

                st.markdown("<div class='json-shell'>", unsafe_allow_html=True)
                with st.expander("Raw JSON"):
                    st.code(json.dumps(plan, indent=2, ensure_ascii=False), language="json")
                st.markdown("</div>", unsafe_allow_html=True)
