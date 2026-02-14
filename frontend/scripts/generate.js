// Handles the "Generate" button and chat scraping

async function prepForRizz() {
  const generateButton = document.getElementById("generate");
  const rizzBox = document.getElementById("rizzbox");
  const loadingText = document.getElementById("loading");
  const relationshipSelect = document.getElementById("relationships");

  if (!generateButton) return;

  generateButton.style.cursor = "pointer";

  generateButton.addEventListener("click", () => {
    console.log("Generate button clicked.");

    // Hide button and suggestion box
    generateButton.style.display = "none";
    if (rizzBox) rizzBox.style.display = "none";

    // Show loading text
    if (loadingText) loadingText.style.display = "block";

    relationship = relationshipSelect ? relationshipSelect.value : "acquaintance";
    console.log("Relationship:", relationship);

    if (relationshipSelect.value == "Other") {
        var inputField = document.getElementById("relationship_other");
        relationship = inputField.value;
    };

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      const tabId = tabs[0]?.id;
      if (!tabId) return;

      chrome.scripting.executeScript({
        target: { tabId },
        func: (relationship) => {
          const messages = { current_input: "", relationship, chat_history: [] };

          const inputField = document.querySelector('span[data-slate-string="true"]');
          messages.current_input = inputField?.innerText || "";
          console.log("Current input:", messages.current_input);

          let lastUsername = "";
          document.querySelectorAll('li.messageListItem__5126c').forEach(container => {
            const usernameEl = container.querySelector('.username_c19a55');
            let username = usernameEl?.textContent || lastUsername || "Unknown";
            if (username !== "Unknown") lastUsername = username;

            const timestamp = container.querySelector('.timestamp_c19a55 time')?.getAttribute('datetime') || "";
            const message = container.querySelector('.markup__75297.messageContent_c19a55')?.textContent || "";
            const imageSrc = container.querySelector('.loadingOverlay_af017a img')?.src || "";

            messages.chat_history.push({ username, timestamp, message, imageSrc });
          });

          console.log("Messages object:", messages);

          fetch("http://127.0.0.1:8000/rizzify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(messages)
          })
            .then(res => res.json())
            .then(data => {
              const success = data.status === "success";
              console[success ? "log" : "error"](data.msg || data);
              chrome.runtime.sendMessage({
                action: "updateUI",
                status: success ? "success" : "error",
                message: data.msg
              });

              if (success) {
                chrome.runtime.sendMessage({ action: "unhideButton", status: "success" });
              }
            })
            .catch(err => {
              console.error("Error:", err);
              chrome.runtime.sendMessage({ action: "updateUI", status: "error" });
            });
        },
        args: [relationship]
      });
    });
  });
}

document.addEventListener("DOMContentLoaded", prepForRizz);
