const MIN_USEFUL_LENGTH = 200;

function cleanText(text) {
  return text
    .replace(/\u00a0/g, " ")        
    .replace(/[ \t]+/g, " ")        
    .replace(/\n\s*\n+/g, "\n\n")   
    .trim();
}

function extractPageText() {
  const candidates = [
    { source: "article", el: document.querySelector("article") },
    { source: "main", el: document.querySelector("main") },
    { source: "body", el: document.body },
  ];

  for (const { source, el } of candidates) {
    if (!el) continue;
    const text = cleanText(el.innerText || "");
    
    if (text.length >= MIN_USEFUL_LENGTH || source === "body") {
      return { text, source };
    }
  }
  return { text: "", source: "none" };
}

if (!window.__summarizerListenerAdded) {
  window.__summarizerListenerAdded = true;

  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message && message.action === "EXTRACT_TEXT") {
      try {
        const { text, source } = extractPageText();
        sendResponse({ ok: true, text, source, title: document.title });
      } catch (err) {
        sendResponse({ ok: false, error: "Could not read this page." });
      }
    }
    
  });
}