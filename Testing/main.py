
from js import document, console, window
from pyodide.ffi import create_proxy

# App Texts in English and Korean
texts = {
    "en": {
        "title": "Truthify - Fake News Detection",
        "description": "Check if your news is real or fake in seconds.",
        "placeholder": "Paste or write your news article here...",
        "check": "Check News",
        "reset": "Reset",
        "char_count": "Characters: ",
        "result_real": "✅ Real News",
        "result_fake": "❌ Fake News",
        "explanation_real": "This article appears to be credible.",
        "explanation_fake": "This article shows signs of misinformation.",
        "analyzing": "Analyzing...",
        "select_language": "Select Language",
        "select_category": "Select Category"
    },
    "ko": {
        "title": "트루씨파이 - 가짜 뉴스 탐지",
        "description": "뉴스가 진짜인지 가짜인지 몇 초 만에 확인하세요.",
        "placeholder": "여기에 뉴스 기사를 붙여넣거나 작성하세요...",
        "check": "뉴스 확인",
        "reset": "초기화",
        "char_count": "글자 수: ",
        "result_real": "✅ 진짜 뉴스",
        "result_fake": "❌ 가짜 뉴스",
        "explanation_real": "이 기사는 신뢰할 수 있는 것으로 보입니다.",
        "explanation_fake": "이 기사에는 허위 정보의 징후가 있습니다.",
        "analyzing": "분석 중...",
        "select_language": "언어 선택",
        "select_category": "카테고리 선택"
    }
}

# App state
state = {"lang": "en"}

def update_ui():
    lang = state["lang"]
    t = texts[lang]
    document.getElementById("title").innerText = t["title"]
    document.getElementById("description").innerText = t["description"]
    document.getElementById("news-input").placeholder = t["placeholder"]
    document.getElementById("check-btn").innerText = t["check"]
    document.getElementById("reset-btn").innerText = t["reset"]
    document.getElementById("char-count").innerText = t["char_count"] + "0"
    document.getElementById("lang-label").innerText = t["select_language"]
    document.getElementById("category-label").innerText = t["select_category"]

# Language switcher
def on_lang_change(event):
    state["lang"] = event.target.value
    update_ui()

# Character counter
def on_text_change(event):
    length = len(event.target.value)
    document.getElementById("char-count").innerText = texts[state["lang"]]["char_count"] + str(length)

# Reset form
def reset_form(event):
    document.getElementById("news-input").value = ""
    document.getElementById("result").innerText = ""
    document.getElementById("explanation").innerText = ""
    on_text_change(event)

# Simulated fake news checker
def check_news(event):
    t = texts[state["lang"]]
    result_div = document.getElementById("result")
    explanation_div = document.getElementById("explanation")
    spinner = document.getElementById("spinner")

    result_div.innerText = ""
    explanation_div.innerText = ""
    spinner.style.display = "inline-block"
    result_div.innerText = t["analyzing"]

    def after_check():
        text = document.getElementById("news-input").value
        is_fake = "election" in text.lower() or "scandal" in text.lower()
        result_div.innerText = t["result_fake"] if is_fake else t["result_real"]
        explanation_div.innerText = t["explanation_fake"] if is_fake else t["explanation_real"]
        spinner.style.display = "none"

    window.setTimeout(create_proxy(after_check), 2000)

# Theme toggler
def toggle_theme(event):
    body = document.querySelector("body")
    body.classList.toggle("dark-mode")

# Bind events
def setup():
    update_ui()
    document.getElementById("lang-select").addEventListener("change", create_proxy(on_lang_change))
    document.getElementById("news-input").addEventListener("input", create_proxy(on_text_change))
    document.getElementById("reset-btn").addEventListener("click", create_proxy(reset_form))
    document.getElementById("check-btn").addEventListener("click", create_proxy(check_news))
    document.getElementById("theme-toggle").addEventListener("click", create_proxy(toggle_theme))

setup()
