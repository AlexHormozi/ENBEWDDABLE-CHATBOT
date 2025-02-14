(function() {
    let script = document.currentScript;
    let userId = script.getAttribute("data-user-id");  // Get user-specific ID
    let theme = script.getAttribute("data-theme") || "light";
    let color = script.getAttribute("data-color") || "#000";

    // Store user config globally
    window.chatbotConfig = { userId, theme, color };

    let widget = document.createElement("div");
    widget.style = `position: fixed; bottom: 20px; right: 20px; background: ${color}; padding: 10px; border-radius: 10px;`;
    widget.innerHTML = `
        <input type='text' id='chatInput' placeholder='Ask something...' style='width: 200px;'>
        <button id='chatBtn'>Send</button>
        <div id='chatResponse'></div>
    `;

    document.body.appendChild(widget);

    document.getElementById("chatBtn").addEventListener("click", function() {
        let query = document.getElementById("chatInput").value;

        fetch(`https://yourserver.com/api/chat?user_id=${userId}&query=${query}`)
            .then(response => response.json())
            .then(data => document.getElementById("chatResponse").innerText = data.response)
            .catch(err => console.error("API Error:", err));
    });
})();
