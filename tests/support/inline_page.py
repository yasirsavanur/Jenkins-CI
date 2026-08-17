"""Package the local target as a data URL for browsers outside the Jenkins network."""

from pathlib import Path
from urllib.parse import quote


def build_inline_page(root: Path) -> str:
    """Inline the demo's CSS and JavaScript into one self-contained data URL."""

    html = (root / "index.html").read_text(encoding="utf-8")
    css = (root / "styles.css").read_text(encoding="utf-8")
    javascript = (root / "app.js").read_text(encoding="utf-8")
    html = html.replace('<link rel="stylesheet" href="styles.css">', f"<style>{css}</style>")
    html = html.replace('<script src="app.js"></script>', f"<script>{javascript}</script>")
    return "data:text/html;charset=utf-8," + quote(html, safe="")
