const summarizeBtn = document.getElementById("summarize-btn");
const loadingEl = document.getElementById("loading");
const loadingText = document.getElementById("loading-text");
const errorEl = document.getElementById("error");
const noteEl = document.getElementById("note");
const summaryEl = document.getElementById("summary");

const MIN_TEXT_CHARS = 200;

class UserError extends Error {}

function show(el) { el.classList.remove("hidden"); }
function hide(el) { el.classList.add("hidden"); }

function resetUI() {
  [errorEl, noteEl, summaryEl].forEach(hide);
  errorEl.textContent = "";
  noteEl.textContent = "";
  summaryEl.textContent = "";
}

function setLoading(isLoading, message = "Working...") {
  summarizeBtn.disabled = isLoading;
  loadingText.textContent = message;
  isLoading ? show(loadingEl) : hide(loadingEl);
}

function showError(message) {
  errorEl.textContent = message;
  show(errorEl);
}


function formatSummary(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/^\s*[*-]\s+/gm, "• ")
    .trim();
}

async function extractTextFromActiveTab() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id) {
    throw new UserError("Could not find the active tab.");
  }

  try {
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content.js"],
    });
  } catch (err) {
    throw new UserError(
      "This page can't be read (Chrome blocks extensions on pages like chrome:// and the Web Store)."
    );
  }

  let response;
  try {
    response = await chrome.tabs.sendMessage(tab.id, { action: "EXTRACT_TEXT" });
  } catch (err) {
    throw new UserError("Could not read text from this page. Try reloading the page.");
  }

  if (!response || !response.ok) {
    throw new UserError((response && response.error) || "Could not read text from this page.");
  }
  return response.text;
}


async function requestSummary(text) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  let res;
  try {
    res = await fetch(`${API_BASE_URL}/api/v1/summarize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
      signal: controller.signal,
    });
  } catch (err) {
    if (err.name === "AbortError") {
      throw new UserError("The request took too long. Please try again.");
    }
    // Network failure: server down, wrong URL, or blocked by CORS.
    throw new UserError(
      "Can't reach the summarizer service. Check that the backend is running and the URL in config.js is correct."
    );
  } finally {
    clearTimeout(timer);
  }

  let data = null;
  try {
    data = await res.json();
  } catch (_) { /* response wasn't JSON */ }

  if (!res.ok) {
    throw new UserError((data && data.detail) || `Server error (${res.status}).`);
  }
  if (!data || !data.summary) {
    throw new UserError("The server returned an empty summary.");
  }
  return data.summary;
}


async function handleSummarize() {
  resetUI();
  setLoading(true, "Reading the page...");

  try {
    let text = await extractTextFromActiveTab();

    if (!text || !text.trim()) {
      throw new UserError("This page has no readable text.");
    }
    if (text.length < MIN_TEXT_CHARS) {
      throw new UserError("This page has too little text to summarize.");
    }

    if (text.length > MAX_SEND_CHARS) {
      text = text.slice(0, MAX_SEND_CHARS);
      noteEl.textContent = "This page is very long, so only the first part was used.";
      show(noteEl);
    }

    setLoading(true, "Summarizing... this can take a few seconds.");
    const summary = await requestSummary(text);

    summaryEl.textContent = formatSummary(summary);
    show(summaryEl);
  } catch (err) {
    if (err instanceof UserError) {
      showError(err.message);
    } else {
      showError("Something went wrong. Please try again.");
    }
  } finally {
    setLoading(false);
  }
}

summarizeBtn.addEventListener("click", handleSummarize);