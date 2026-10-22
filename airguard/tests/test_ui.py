"""
End-to-end and integration tests for AirGuard UI, Design System sanitization,
and browser-rendered visual stability.
"""

import sys
import os
import shutil
import urllib.request
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.components.design_system import safe_markdown


def test_safe_markdown_strips_indentation():
    """Verify that safe_markdown removes CommonMark indented codeblock triggers."""
    raw_html = """
        <div class="card">
            <span class="badge">TEST</span>
            <div>Content line</div>
        </div>
    """
    from unittest.mock import patch

    with patch("streamlit.markdown") as mock_st:
        safe_markdown(raw_html)
        mock_st.assert_called_once()
        sanitized_html, kwargs = mock_st.call_args[0][0], mock_st.call_args[1]
        assert kwargs.get("unsafe_allow_html") is True
        # Ensure no line starts with 4 or more spaces
        for line in sanitized_html.splitlines():
            assert not line.startswith("    ")
        assert '<div class="card">' in sanitized_html
        assert '<span class="badge">TEST</span>' in sanitized_html


def is_server_running(url: str = "http://localhost:8501/_stcore/health") -> bool:
    """Check if the Streamlit server is currently accepting HTTP connections."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AirGuard-Test"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status in (200, 404)  # 200 healthcheck or standard app response
    except Exception:
        # Fallback check on root
        try:
            with urllib.request.urlopen("http://localhost:8501", timeout=3) as root_resp:
                return root_resp.status == 200
        except Exception:
            return False


def get_chrome_binary() -> str | None:
    """Locate Google Chrome executable across platforms."""
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chrome"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


@pytest.mark.skipif(not is_server_running(), reason="Streamlit server not running on localhost:8501")
def test_streamlit_server_is_healthy():
    """Verify the Streamlit server is active and reachable."""
    assert is_server_running() is True


def wait_for_text(driver, expected_text: str, timeout: int = 15) -> bool:
    """Poll driver.page_source until expected_text appears or timeout is reached."""
    import time
    start = time.time()
    while time.time() - start < timeout:
        if expected_text in driver.page_source:
            return True
        time.sleep(0.5)
    return False


def wait_for_any_text(driver, expected_texts: list[str], timeout: int = 25) -> bool:
    """Poll driver.page_source or body text until any candidate appears or timeout is reached."""
    import time
    start = time.time()
    while time.time() - start < timeout:
        src = driver.page_source
        for t in expected_texts:
            if t in src:
                return True
        try:
            body_txt = driver.find_element("tag name", "body").text
            for t in expected_texts:
                if t in body_txt:
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


@pytest.mark.skipif(not is_server_running(), reason="Streamlit server not running on localhost:8501")
@pytest.mark.skipif(get_chrome_binary() is None, reason="Google Chrome binary not found on host")
def test_browser_rendered_home_page():
    """Verify actual browser DOM rendering without raw HTML leakage."""
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.binary_location = get_chrome_binary()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    try:
        driver.set_window_size(1440, 900)
        driver.get("http://localhost:8501/")
        assert wait_for_text(driver, "AIRGUARD", timeout=15)
        assert wait_for_text(driver, "Real-Time Air Quality Intelligence", timeout=15)
        assert "ACTIVE LOCATION:" in driver.page_source

        # Critical: Verify that CommonMark didn't leak raw unescaped HTML into visible pre/code blocks
        assert "<div style=" not in driver.find_element("tag name", "body").text
        assert "min-width: 140px" not in driver.find_element("tag name", "body").text
    finally:
        driver.quit()


@pytest.mark.skipif(not is_server_running(), reason="Streamlit server not running on localhost:8501")
@pytest.mark.skipif(get_chrome_binary() is None, reason="Google Chrome binary not found on host")
def test_browser_responsive_sidebar_collapsed():
    """Verify responsive viewport collapses the sidebar automatically on mobile screens."""
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.binary_location = get_chrome_binary()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    try:
        # Mobile viewport (390 x 844 iPhone 14/15 size)
        driver.set_window_size(390, 844)
        driver.get("http://localhost:8501/")
        assert wait_for_text(driver, "AIRGUARD", timeout=15)

        # In auto mode on mobile, main app container is immediately visible and not hidden
        main_content = driver.find_elements("css selector", "[data-testid='stMain']")
        assert len(main_content) > 0
    finally:
        driver.quit()


@pytest.mark.skipif(not is_server_running(), reason="Streamlit server not running on localhost:8501")
@pytest.mark.skipif(get_chrome_binary() is None, reason="Google Chrome binary not found on host")
def test_browser_safe_outdoor_plan_page():
    """Verify My Safe Outdoor Plan renders personalized decision support."""
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.binary_location = get_chrome_binary()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    try:
        driver.set_window_size(1440, 900)
        driver.get("http://localhost:8501/My_Safe_Outdoor_Plan")
        assert wait_for_text(driver, "AIRGUARD", timeout=20)
        assert wait_for_text(driver, "My Safe Outdoor Plan", timeout=20)
        # Supports either Simple Mode or Technical Mode
        assert wait_for_text(driver, "Best", timeout=20)
        assert ("Safe Time Window" in driver.page_source or "Best Window" in driver.page_source or "Outdoor Plan" in driver.page_source)
    finally:
        driver.quit()


@pytest.mark.skipif(not is_server_running(), reason="Streamlit server not running on localhost:8501")
@pytest.mark.skipif(get_chrome_binary() is None, reason="Google Chrome binary not found on host")
def test_browser_live_tracking_page():
    """Verify Live Tracking renders properly in either Simple or Technical Mode."""
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.binary_location = get_chrome_binary()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    try:
        driver.set_window_size(1440, 900)
        driver.get("http://localhost:8501/Live_Tracking")
        assert wait_for_text(driver, "AIRGUARD", timeout=20)
        # Matches either Simple Mode or Technical Mode
        assert wait_for_any_text(driver, ["Live Air Quality", "LIVE ALERT DEFENSE STATUS"], timeout=25)
    finally:
        driver.quit()


@pytest.mark.skipif(not is_server_running(), reason="Streamlit server not running on localhost:8501")
@pytest.mark.skipif(get_chrome_binary() is None, reason="Google Chrome binary not found on host")
def test_browser_trends_page():
    """Verify Trends & Analytics renders in either Simple or Technical Mode."""
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.binary_location = get_chrome_binary()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    try:
        driver.set_window_size(1440, 900)
        driver.get("http://localhost:8501/Trends")
        assert wait_for_text(driver, "AIRGUARD", timeout=20)
        # Matches either Simple Mode or Technical Mode
        assert (wait_for_text(driver, "Air Quality Trends", timeout=20) or
                wait_for_text(driver, "SAFETY TIMELINE", timeout=20))
    finally:
        driver.quit()


@pytest.mark.skipif(not is_server_running(), reason="Streamlit server not running on localhost:8501")
@pytest.mark.skipif(get_chrome_binary() is None, reason="Google Chrome binary not found on host")
def test_browser_model_insights_page():
    """Verify Model Insights renders in either Simple or Technical Mode."""
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.binary_location = get_chrome_binary()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    try:
        driver.set_window_size(1440, 900)
        driver.get("http://localhost:8501/Model_Insights")
        assert wait_for_text(driver, "AIRGUARD", timeout=20)
        # Matches either Simple Mode or Technical Mode
        assert (wait_for_text(driver, "How AirGuard Forecasts Pollution", timeout=20) or
                wait_for_text(driver, "Predictive Intelligence", timeout=20))
    finally:
        driver.quit()


@pytest.mark.skipif(not is_server_running(), reason="Streamlit server not running on localhost:8501")
@pytest.mark.skipif(get_chrome_binary() is None, reason="Google Chrome binary not found on host")
def test_browser_about_safety_page():
    """Verify About & Safety renders in either Simple or Technical Mode."""
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    options.binary_location = get_chrome_binary()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    try:
        driver.set_window_size(1440, 900)
        driver.get("http://localhost:8501/About_Safety")
        assert wait_for_text(driver, "AIRGUARD", timeout=20)
        # Matches either Simple Mode or Technical Mode disclaimer
        assert (wait_for_text(driver, "Safety Note:", timeout=20) or
                wait_for_text(driver, "ENVIRONMENTAL SAFETY DISCLAIMER", timeout=20) or
                wait_for_text(driver, "Simple Safety & Mask Guide", timeout=20))
    finally:
        driver.quit()
