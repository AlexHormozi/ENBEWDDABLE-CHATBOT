document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.chatbot-container');
    const toggleBtn = document.querySelector('.chatbot-toggle');
    const closeBtn = document.querySelector('.close-btn');
    const sendBtn = document.querySelector('.send-btn');
    const textarea = document.querySelector('textarea');
    const messagesContainer = document.querySelector('.chat-messages');
    let contextData = {};

    // Parse URL parameters to get the user_id
    const urlParams = new URLSearchParams(window.location.search);
    const userId = urlParams.get('user_id');

    if (!userId) {
        console.error('No user_id found in URL, using default context data.');
        // Optionally, fallback to some default context data here
    } else {
        // Fetch dynamic context from your API endpoint
        fetch(`https://enbewddable-chatbot.onrender.com/api/get_context?user_id=${userId}`)
            .then(response => response.json())
            .then(data => {
                if (data.context) {
                    contextData = data.context;
                    console.log('Dynamic context loaded:', contextData);
                } else {
                    console.error('No context found in response:', data);
                }
            })
            .catch(error => console.error('Error loading dynamic context data:', error));
    }

    // Toggle Chatbot
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        container.classList.toggle('active');
    });

    // Close Chatbot
    closeBtn.addEventListener('click', () => {
        container.classList.remove('active');
    });

    // Send Message
    sendBtn.addEventListener('click', sendMessage);
    textarea.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = textarea.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, true);
        textarea.value = '';
        resetTextareaHeight();

        try {
            // Get response from Groq API with dynamic context
            const botResponse = await getGroqResponse(message);
            // Display bot response
            addMessage(botResponse, false);
        } catch (error) {
            console.error('Error fetching response:', error);
            addMessage("Sorry, I couldn't process your request.", false);
        }
    }

    async function getGroqResponse(userInput) {
        const apiKey = "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";
        const apiUrl = "https://api.groq.com/openai/v1/chat/completions";

        // Build system context string from dynamic contextData
        const systemContext = `
            Company: ${contextData.company_name}
            Product: ${contextData.product}
            Description: ${contextData.description}
            Key Features: ${contextData.key_features ? contextData.key_features.join(", ") : ""}
            Target Audience: ${contextData.target_audience}
            Value Proposition: ${contextData.value_proposition}

            **Sales Strategy**:
            - Attention: ${contextData.sales_strategy ? contextData.sales_strategy.attention : ""}
            - Interest: ${contextData.sales_strategy ? contextData.sales_strategy.interest : ""}
            - Desire: ${contextData.sales_strategy ? contextData.sales_strategy.desire : ""}
            - Action: ${contextData.sales_strategy ? contextData.sales_strategy.action : ""}

            **Objection Handling**:
            - Pricing: ${contextData.objection_handling ? contextData.objection_handling.pricing : ""}
            - Complexity: ${contextData.objection_handling ? contextData.objection_handling.complexity : ""}
            - Effectiveness: ${contextData.objection_handling ? contextData.objection_handling.effectiveness : ""}
        `;

        // Sales-Oriented System Prompt with Context Steering
        const systemPrompt = `
            You are a highly skilled sales assistant for ${contextData.company_name || "our company"}, specializing in selling ${contextData.product || "our product"}. 
            Your goal is to tactically engage customers, uncover their needs, and position the product as the ideal solution.
            Always respond with confidence and clarity, ensuring every answer is directly related to the product.
            
            If a question is off-topic, briefly acknowledge it, then transition back to how ${contextData.product || "the product"} is relevant.
            
            Context Data:
            ${systemContext}
        `;

        const requestBody = {
            model: "llama3-8b-8192",
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user", content: userInput }
            ],
            temperature: 0.85,
            max_tokens: 300
        };

        const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Groq API Error: ${errorText}`);
        }

        const responseData = await response.json();
        return responseData.choices?.[0]?.message?.content || "I'm not sure how to respond to that.";
    }

    function addMessage(text, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

        if (!isUser) {
            const img = document.createElement('img');
            img.src = 'https://th.bing.com/th/id/OIP.7tmUOb6RxDxnMrtIwCPitgHaHa?w=192&h=192&c=7&r=0&o=5&pid=1.7';
            img.style.borderRadius = '50%';
            img.alt = 'Bot';
            messageDiv.appendChild(img);
        }

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const messageText = document.createElement('p');
        messageText.textContent = text;

        const timestamp = document.createElement('span');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        contentDiv.appendChild(messageText);
        contentDiv.appendChild(timestamp);
        messageDiv.appendChild(contentDiv);

        messagesContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    function scrollToBottom() {
        messagesContainer.style.scrollBehavior = 'smooth';
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function resetTextareaHeight() {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    // --- User Details Form Functionality ---

    // Function to show the user details form
    function showUserDetailsForm() {
        document.getElementById('user-details-form').style.display = 'block';
    }

    // Function to hide the user details form
    function hideUserDetailsForm() {
        document.getElementById('user-details-form').style.display = 'none';
    }

    // Add event listener for the form submission
    document.getElementById('submit-user-details').addEventListener('click', async () => {
        const name = document.getElementById('user-name').value.trim();
        const email = document.getElementById('user-email').value.trim();
        
        // Parse the user_id from URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const userId = urlParams.get('user_id');

        if (!name || !email || !userId) {
            alert("Please fill in your name and email.");
            return;
        }
        
        try {
            const response = await fetch('https://enbewddable-chatbot.onrender.com/api/update_user_details', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ user_id: userId, name: name, email: email })
            });
            
            const data = await response.json();
            if (response.ok) {
                alert("Your details have been updated!");
                hideUserDetailsForm();
            } else {
                alert("Error: " + data.error);
            }
        } catch (error) {
            console.error("Error updating user details:", error);
            alert("An error occurred. Please try again.");
        }
    });

    // For demonstration purposes, show the form on page load.
    // You may adjust this trigger based on your chatbot flow.
    showUserDetailsForm();
});
