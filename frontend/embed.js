(function() {
    let script = document.currentScript;
    let userId = script.getAttribute("data-user-id");
    let theme = script.getAttribute("data-theme") || "light";
    let color = script.getAttribute("data-color") || "#000";
    let position = script.getAttribute("data-position") || "bottom-right";

    window.chatbotConfig = { userId, theme, color, position };

    let widget = document.createElement("div");
    widget.style = `
        position: fixed;
        ${position.includes("bottom") ? "bottom: 20px;" : "top: 20px;"}
        ${position.includes("right") ? "right: 20px;" : "left: 20px;"}
        background: ${color};
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        font-family: Arial, sans-serif;
        z-index: 9999;
    `;
    widget.innerHTML = `
        <input type='text' id='chatInput' placeholder='Ask something...' style='width: 200px; padding: 5px; border-radius: 5px; border: 1px solid #ccc;'>
        <button id='chatBtn' style='padding: 5px 10px; background: #007bff; color: white; border: none; cursor: pointer;'>Send</button>
        <div id='chatResponse' style='margin-top: 10px; padding: 5px; background: white; color: black; border-radius: 5px;'></div>
    `;

    document.body.appendChild(widget);

    document.getElementById("chatBtn").addEventListener("click", function() {
        let query = document.getElementById("chatInput").value;
        fetch(`https://enbewddable-chatbot.onrender.com/api/chat?user_id=${userId}&query=${query}`)
            .then(response => response.json())
            .then(data => document.getElementById("chatResponse").innerText = data.response)
            .catch(err => console.error("API Error:", err));
    });
})();
