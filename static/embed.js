(function() {
    // Retrieve configuration from the script tag's data attributes
    var script = document.currentScript;
    var userId = script.getAttribute("data-user-id");
    var theme = script.getAttribute("data-theme") || "light";
    var color = script.getAttribute("data-color") || "#000";
    var position = script.getAttribute("data-position") || "bottom-right";

    // Build query parameters to pass configuration to index.html
    var params = new URLSearchParams();
    params.set("user_id", userId);
    params.set("theme", theme);
    params.set("color", color);

    // Create an iframe that loads your full chatbot UI (index.html)
    var iframe = document.createElement("iframe");
    iframe.src = "https://enbewddable-chatbot.onrender.com/index.html?" + params.toString();
    
    // Style the iframe to match your widget's desired dimensions and position
    iframe.style.position = "fixed";
    if (position.includes("bottom")) {
        iframe.style.bottom = "20px";
    } else {
        iframe.style.top = "20px";
    }
    if (position.includes("right")) {
        iframe.style.right = "20px";
    } else {
        iframe.style.left = "20px";
    }
    iframe.style.width = "350px";   // Adjust as needed (matches your designed width)
    iframe.style.height = "500px";  // Adjust as needed (matches your designed height)
    iframe.style.border = "none";
    iframe.style.borderRadius = "10px";
    iframe.style.boxShadow = "0 4px 10px rgba(0, 0, 0, 0.2)";
    iframe.style.zIndex = "9999";

    // Append the iframe to the document body
    document.body.appendChild(iframe);
})();
