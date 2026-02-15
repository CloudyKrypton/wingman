/**
 * Initializes clipboard copy functionality once the DOM is fully loaded.
 * Requirements:
 * - Must be triggered by a user interaction (click) for clipboard access.
 * - Clipboard API typically requires a secure context (HTTPS).
 * 
 * @listens DOMContentLoaded 
 */
document.addEventListener("DOMContentLoaded", () => {
    const copyButton = document.getElementById("copyButton");
    const suggestionBox = document.getElementById("suggestion");

    if (!copyButton || !suggestionBox) {
        console.log("Missing copy button or suggestion box")
        return;
    }

    copyButton.style.cursor = "pointer";

    copyButton.addEventListener("click", async () => {
        const textToCopy = suggestionBox.textContent || suggestionBox.innerText;
        try {
            await navigator.clipboard.writeText(textToCopy);
            console.log("Text copied:", textToCopy);
        } catch (err) {
            console.error("Clipboard API failed, falling back to execCommand.", err);
            fallbackCopy(textToCopy);
        }
    });

    function fallbackCopy(text) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.opacity = "0";
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand("copy");
        } catch (err) {
            console.error("Fallback execCommand failed:", err);
        }
        document.body.removeChild(textArea);
    }
});
