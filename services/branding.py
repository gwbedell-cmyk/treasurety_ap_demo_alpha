"""
Treasurety platform branding — canonical logo and sidebar identity.
Import this in every page and call sidebar_logo() after load_css().
"""

import base64
import streamlit as st

LOGO_PATH = "assets/logo.png"

_b64_cache: str | None = None


def _logo_b64() -> str:
    global _b64_cache
    if _b64_cache is None:
        with open(LOGO_PATH, "rb") as f:
            _b64_cache = base64.b64encode(f.read()).decode()
    return _b64_cache


def sidebar_logo() -> None:
    """Display Treasurety logo in the sidebar. Call once per page after load_css()."""
    try:
        from PIL import Image
        img  = Image.open(LOGO_PATH)
        h    = img.height
        icon = img.crop((0, 0, h, h))   # square crop = the T-crosshair mark
        st.logo(LOGO_PATH, icon_image=icon)
    except Exception:
        try:
            st.logo(LOGO_PATH)
        except Exception:
            pass   # graceful degradation for older Streamlit builds


def logo_html(width: int = 260, extra_style: str = "") -> str:
    """
    Return an <img> tag with the logo encoded as base64, suitable for
    embedding inside st.markdown(..., unsafe_allow_html=True) blocks.
    Uses mix-blend-mode:screen so the dark logo background dissolves
    into any dark hero/card background.
    """
    b64 = _logo_b64()
    style = f"display:block;mix-blend-mode:screen;{extra_style}"
    return (
        f'<img src="data:image/png;base64,{b64}" '
        f'width="{width}" style="{style}" />'
    )


def page_favicon():
    """Return a PIL Image (square crop of the T mark) for use as page_icon."""
    try:
        from PIL import Image
        img  = Image.open(LOGO_PATH)
        h    = img.height
        return img.crop((0, 0, h, h))
    except Exception:
        return "🛡️"


# -- SECTIONED SIDEBAR NAVIGATION ------------------------------------------

_NAV_SECTIONS = [
    ("Assessment & Certification", False, [
        ("pages/2_Treasurety_Gate.py",       "Treasurety Gate"),
        ("pages/9_Treasurety_Assess.py",      "Trust Assessment"),
    ]),
    ("Runtime Governance", True, [
        ("pages/10_Treasurety_Monitor.py",    "Treasurety Monitor"),
        ("pages/11_Treasurety_Horizon.py",    "Treasurety Horizon"),
        ("pages/12_Treasurety_Shield.py",     "Treasurety Shield"),
    ]),
    ("Trust Infrastructure", False, [
        ("pages/6_Policy_Control_Center.py",  "Policy Control Center"),
    ]),
    ("Operations", False, [
        ("pages/0_Dashboard.py",              "Dashboard"),
        ("pages/3_Autonomous_Queue.py",       "Autonomous Queue"),
        ("pages/4_Decision_Analysis.py",      "Decision Analysis"),
        ("pages/5_Black_Box_Recorder.py",     "Decision Provenance"),
    ]),
    ("Platform", False, [
        ("pages/1_AI_Native_Flow.py",         "AI Native Flow"),
        ("pages/7_Scenario_Control.py",       "Scenario Control"),
        ("pages/8_Architecture.py",           "Architecture"),
        ("pages/13_Platform_Roadmap.py",      "Platform Roadmap"),
    ]),
]


def sidebar_nav() -> None:
    """
    Render logo + sectioned expandable navigation in the sidebar.
    Replaces sidebar_logo() -- call once per page after load_css().
    """
    sidebar_logo()
    with st.sidebar:
        st.page_link("app.py", label="Home", icon=":material/home:")
        st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
        for section_label, expanded, pages in _NAV_SECTIONS:
            with st.expander(section_label, expanded=expanded):
                for page_path, page_label in pages:
                    st.page_link(page_path, label=page_label)
