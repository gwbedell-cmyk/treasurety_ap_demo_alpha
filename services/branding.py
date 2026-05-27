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
