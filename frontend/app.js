const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const imageUpload = document.getElementById('image-upload');
const uploadBtn = document.getElementById('upload-btn');
const imagePreviewContainer = document.getElementById('image-preview-container');
const imagePreview = document.getElementById('image-preview');
const removeImageBtn = document.getElementById('remove-image-btn');

let currentImageBase64 = null;

const API_URL = 'http://localhost:8000/chat';

function addMessage(role, content, sources = [], images = []) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(role === 'user' ? 'user-message' : 'bot-message');
    
    // Parse markdown for bot messages, plain text for user
    const formattedContent = role === 'bot' ? marked.parse(content) : content;
    
    let html = `<div>${formattedContent}</div>`;
    
    // Display images if available
    if (images && images.length > 0) {
        html += '<div class="message-images">';
        images.forEach(img => {
            const imgSrc = img.startsWith('http') ? img : `http://localhost:8000/${img}`;
            html += `
                <div class="image-container">
                    <img src="${imgSrc}" alt="Product Image" class="chat-image" onclick="window.open('${imgSrc}', '_blank')">
                </div>`;
        });
        html += '</div>';
    }
    
    if (sources && sources.length > 0) {
        const sourceLinks = sources.map(s => {
            if (s.includes('http')) {
                const parts = s.split(': ');
                const label = parts[0];
                const url = parts.slice(1).join(': ');
                return `<a href="${url}" target="_blank" class="source-link">${label}</a>`;
            }
            return `<span>${s.split('\\').pop().split('/').pop()}</span>`;
        }).join(', ');
        html += `<div class="sources"><strong>Sources:</strong> ${sourceLinks}</div>`;
    }
    
    messageDiv.innerHTML = html;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function handleSendMessage() {
    const query = userInput.value.trim();
    if (!query && !currentImageBase64) return;

    // Add user message to UI
    let userMsgContent = query;
    if (currentImageBase64) {
        userMsgContent += `<br><img src="${currentImageBase64}" style="max-width: 150px; border-radius: 8px; margin-top: 8px;">`;
    }
    
    addMessage('user', userMsgContent);
    userInput.value = '';
    
    const sentImageBase64 = currentImageBase64;
    currentImageBase64 = null;
    imageUpload.value = '';
    imagePreviewContainer.style.display = 'none';
    
    // Disable input while loading
    userInput.disabled = true;
    sendBtn.disabled = true;
    uploadBtn.disabled = true;
    const originalBtnText = sendBtn.innerText;
    sendBtn.innerHTML = '<span class="loading"></span>';

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query || "What is this image?",
                include_sources: true,
                image_base64: sentImageBase64
            })
        });

        if (!response.ok) {
            throw new Error('Failed to get response from server');
        }

        const data = await response.json();
        addMessage('bot', data.answer, data.sources, data.images);
    } catch (error) {
        console.error('Error:', error);
        addMessage('bot', 'I apologize, but I am having trouble connecting to my brain right now. Please ensure the backend server is running.');
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        uploadBtn.disabled = false;
        sendBtn.innerText = originalBtnText;
        userInput.focus();
    }
}

sendBtn.addEventListener('click', handleSendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSendMessage();
    }
});

uploadBtn.addEventListener('click', () => {
    imageUpload.click();
});

imageUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        if (!file.type.startsWith('image/')) {
            alert('Please select an image file.');
            imageUpload.value = '';
            return;
        }
        
        const reader = new FileReader();
        reader.onload = function(event) {
            currentImageBase64 = event.target.result;
            imagePreview.src = currentImageBase64;
            imagePreviewContainer.style.display = 'block';
            userInput.focus();
        };
        reader.readAsDataURL(file);
    }
});

removeImageBtn.addEventListener('click', () => {
    currentImageBase64 = null;
    imageUpload.value = '';
    imagePreviewContainer.style.display = 'none';
});
