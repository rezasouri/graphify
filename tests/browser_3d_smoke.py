"""Chromium smoke test for the generated 2D/3D viewer.

Run by the dedicated GitHub Actions browser workflow. Network access to unpkg
is required for both pinned browser libraries.
"""
import networkx as nx
from pathlib import Path
from playwright.sync_api import sync_playwright
from graphify.export import to_html


def main():
    out = Path("graphify-browser-smoke.html").resolve()
    g = nx.Graph()
    g.add_node("a", label="Alpha", file_type="code", source_file="alpha.py")
    g.add_node("b", label="Beta", file_type="code", source_file="beta.py")
    g.add_edge("a", "b", relation="calls", confidence="EXTRACTED", _src="a", _tgt="b")
    assert to_html(g, {0: ["a", "b"]}, str(out), community_labels={0: "Core"})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader",
            "--disable-web-security",
        ])
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(out.as_uri(), wait_until="load")
        page.wait_for_function("typeof window.vis !== 'undefined'", timeout=30000)
        page.locator("#graphify-view-3d").click()
        page.wait_for_function(
            "document.getElementById('graphify-view-3d').getAttribute('aria-pressed') === 'true'",
            timeout=45000,
        )
        assert page.evaluate("window.graphifyIs3d()")
        assert page.locator("#graph3d canvas").count() > 0
        # Search focuses a real node and updates the shared sidebar.
        page.locator("#search").fill("Alpha")
        page.locator(".search-item").first.click()
        assert "Alpha" in page.locator("#info-content").inner_text()
        page.locator("#graphify-view-2d").click()
        assert not page.evaluate("window.graphifyIs3d()")
        page.locator("#graphify-view-3d").click()
        assert page.evaluate("window.graphifyIs3d()")
        assert not errors, f"Browser JavaScript errors: {errors}"
        browser.close()
    out.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
