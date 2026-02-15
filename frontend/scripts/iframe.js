/**
 * Initializes iframe UI event listeners once the DOM is loaded.
 */
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('close').addEventListener('click', function() {
        console.log('Close button clicked');
        chrome.runtime.sendMessage({ action: "removeIframe" });
    });
});

/**
 * Listens for messages from the background or content scripts
 * to update the iframe UI state.
 */
chrome.runtime.onMessage.addListener(function(request, sender) {
    if (request.action === "updateUI") {
        const loadingText = document.getElementById("loading");
        const suggestionBox = document.getElementById("suggestion");
        const rizzBox = document.getElementById("rizzbox");
        const generateButton = document.getElementById("generate");

        if (request.status === "success") {
            if (loadingText) loadingText.style.display = "none";
            if (suggestionBox) suggestionBox.innerText = request.message;
            if (suggestionBox) suggestionBox.style.display = "block";
            if (rizzBox) rizzBox.style.display = "block";
            if (generateButton) generateButton.style.display = "block";
        } else if (request.status === "error") {
            if (loadingText) loadingText.style.display = "none";
        }
    }
});