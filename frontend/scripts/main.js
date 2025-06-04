// main.js - Animations, dynamic loading, and interactivity for FixIt Tech Solutions

document.addEventListener('DOMContentLoaded', () => {
    // Animate service cards on scroll and load them with delay
    const services = [
        { name: 'Screen Replacement', desc: 'Cracked or broken screen? We fix it fast.', price: '$99+', duration: '1-2 hrs' },
        { name: 'Battery Replacement', desc: 'Get your device running like new.', price: '$49+', duration: '30-60 min' },
        { name: 'Water Damage Repair', desc: 'Rescue your device from liquid mishaps.', price: 'From $79', duration: '2-4 hrs' },
        { name: 'Data Recovery', desc: 'Lost files? We can help recover your data.', price: 'From $59', duration: '1-3 hrs' },
    ];
    const grid = document.querySelector('.service-grid');
    if (grid) {
        services.forEach((s, i) => {
            setTimeout(() => {
                const card = document.createElement('div');
                card.className = 'service-card';
                card.style.animationDelay = `${0.2 + i * 0.15}s`;
                card.innerHTML = `
                    <h3>${s.name}</h3>
                    <p>${s.desc}</p>
                    <div class="service-meta">
                        <span class="price">${s.price}</span>
                        <span class="duration">${s.duration}</span>
                    </div>
                    <a href="#booking" class="btn btn-primary">Book Now</a>
                `;
                grid.appendChild(card);
            }, 200 + i * 180);
        });
    }

    // Booking form (placeholder)
    const bookingSection = document.querySelector('.booking-section');
    if (bookingSection) {
        bookingSection.innerHTML = `
            <h2>Book a Repair</h2>
            <form class="booking-form fade-in-up">
                <input type="text" name="name" placeholder="Name" required />
                <input type="email" name="email" placeholder="Email" required />
                <input type="tel" name="phone" placeholder="Phone" required />
                <input type="text" name="device_type" placeholder="Device Type" required />
                <textarea name="issue" placeholder="Describe the issue" required></textarea>
                <input type="datetime-local" name="datetime" required />
                <button class="btn btn-primary" type="submit">Submit Booking</button>
            </form>
        `;
        const form = bookingSection.querySelector('.booking-form');
        form.addEventListener('submit', async e => {
            e.preventDefault();
            // Collect form data with correct field names and ISO date
            const data = {
                name: form.name.value,
                email: form.email.value,
                phone: form.phone.value,
                device: form.device_type.value, // backend expects 'device'
                issue: form.issue.value,
                date: new Date(form.datetime.value).toISOString() // backend expects 'date' in ISO format
            };
            try {
                const resp = await fetch('http://localhost:8080/booking/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                if (resp.ok) {
                    alert('Thank you! We received your booking.');
                    form.reset();
                } else {
                    alert('Sorry, there was a problem. Please try again.');
                }
            } catch (err) {
                alert('Sorry, there was a problem. Please try again.');
            }
        });
    }

    // Chatbot shared functionality
    let chatbotConversationId = null;
    const handleChatbotSubmit = async (form, messagesContainer) => {
        const input = form.querySelector('input');
        if (!input.value.trim()) return;

        // Show user message
        const userMsg = document.createElement('div');
        userMsg.className = 'user-msg';
        userMsg.textContent = input.value;
        messagesContainer.appendChild(userMsg);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        const userInput = input.value;
        input.value = '';

        // Show typing indicator
        const botTyping = document.createElement('div');
        botTyping.className = 'bot-msg typing';
        botTyping.textContent = '...';
        messagesContainer.appendChild(botTyping);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const payload = { message: userInput };
            if (chatbotConversationId) payload.conversation_id = chatbotConversationId;
            const resp = await fetch('http://localhost:8080/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await resp.json();
            botTyping.remove();
            if (data.conversation_id) chatbotConversationId = data.conversation_id;
            const botMsg = document.createElement('div');
            botMsg.className = 'bot-msg';
            // Use backend's .response field, fallback to .message, fallback to LLM content, fallback to error
            botMsg.textContent = data.response || data.message || data.choices?.[0]?.message?.content || 'Sorry, I couldn\'t understand that.';
            messagesContainer.appendChild(botMsg);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        } catch (err) {
            botTyping.textContent = 'Sorry, something went wrong. Please try again.';
        }
    };

    // Optionally, add a function to reset the conversation (e.g., on modal close)
    function resetChatbotConversation() {
        chatbotConversationId = null;
    }

    // Inline chatbot widget
    const chatbotSection = document.querySelector('.chatbot-section');
    if (chatbotSection) {
        chatbotSection.innerHTML = `
            <h2>AI Chatbot Assistant</h2>
            <div class="chatbot-widget fade-in-up">
                <div class="chatbot-messages">
                    <div class="bot-msg">Hi, how can I help you today?</div>
                </div>
                <form class="chatbot-form">
                    <input type="text" placeholder="Type your message..." required />
                    <button class="btn btn-secondary" type="submit">Send</button>
                </form>
            </div>
        `;
        const form = chatbotSection.querySelector('.chatbot-form');
        const messages = chatbotSection.querySelector('.chatbot-messages');
        form.addEventListener('submit', async e => {
            e.preventDefault();
            await handleChatbotSubmit(form, messages);
        });
    }

    // Modal chatbot (declare only once)
    let chatbotFormModal = document.querySelector('.chatbot-form-modal');
    let chatbotMessagesModal = document.querySelector('.chatbot-messages-modal');
    if (chatbotFormModal && chatbotMessagesModal) {
        chatbotFormModal.addEventListener('submit', async e => {
            e.preventDefault();
            await handleChatbotSubmit(chatbotFormModal, chatbotMessagesModal);
        });
    }

    // Floating chatbot button and modal logic
    const chatbotFab = document.getElementById('chatbot-fab');
    const chatbotModal = document.getElementById('chatbot-modal');
    const chatbotModalClose = document.querySelector('.chatbot-modal-close');
    if (chatbotFab && chatbotModal && chatbotModalClose) {
        chatbotFab.addEventListener('click', () => {
            chatbotModal.style.display = 'flex';
            setTimeout(() => chatbotModal.classList.add('open'), 10);
        });
        chatbotModalClose.addEventListener('click', () => {
            chatbotModal.classList.remove('open');
            setTimeout(() => chatbotModal.style.display = 'none', 300);
            resetChatbotConversation(); // Reset conversation on close
        });
        chatbotModal.addEventListener('click', e => {
            if (e.target === chatbotModal) {
                chatbotModal.classList.remove('open');
                setTimeout(() => chatbotModal.style.display = 'none', 300);
                resetChatbotConversation(); // Reset conversation on close
            }
        });
    }

    // Chatbot modal message logic (demo)
    if (chatbotFormModal && chatbotMessagesModal) {
        chatbotFormModal.addEventListener('submit', e => {
            e.preventDefault();
            const input = chatbotFormModal.querySelector('input');
            if (!input.value.trim()) return;
            const userMsg = document.createElement('div');
            userMsg.className = 'user-msg';
            userMsg.textContent = input.value;
            chatbotMessagesModal.appendChild(userMsg);
            setTimeout(() => {
                const botMsg = document.createElement('div');
                botMsg.className = 'bot-msg';
                setTimeout(async () => {
    try {
        const resp = await fetch('http://localhost:8080/chat/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: input.value })
        });
        const data = await resp.json();
        const botMsg = document.createElement('div');
        botMsg.className = 'bot-msg';
        botMsg.textContent = data.response || data.message || data.choices?.[0]?.message?.content || 'Sorry, I couldn\'t understand that.';
        messages.appendChild(botMsg);
        messages.scrollTop = messages.scrollHeight;
    } catch (err) {
        const botMsg = document.createElement('div');
        botMsg.className = 'bot-msg';
        botMsg.textContent = 'Something went wrong. Please try again.';
        messages.appendChild(botMsg);
    }
}, 800);
                chatbotMessagesModal.appendChild(botMsg);
                chatbotMessagesModal.scrollTop = chatbotMessagesModal.scrollHeight;
            }, 800);
            input.value = '';
        });
    }

    // Smooth scroll for nav links (only for same-page anchors)
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            // If href is exactly 'about.html' or 'contact.html', navigate directly
            if (href === 'about.html' || href === 'contact.html') {
                // Let browser navigate normally
                return;
            }
            // Only intercept if href starts with '#'
            if (href && href.startsWith('#')) {
                // Only smooth scroll if the anchor is on the current page
                if (window.location.pathname.endsWith('index.html') || window.location.pathname === '/' || window.location.pathname.endsWith('/index.html')) {
                    const target = document.querySelector(href);
                    if (target) {
                        e.preventDefault();
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                } else {
                    // If not on index.html, navigate to correct relative path
                    e.preventDefault();
                    window.location.href = 'index.html' + href;
                }
            } // For all other links, allow default navigation
        });
    });

    // Make 'Ask the AI Assistant' CTA open the chatbot modal
    const aiAssistantBtn = document.querySelector('.cta-buttons .btn-secondary');
    if (aiAssistantBtn && chatbotFab) {
        aiAssistantBtn.addEventListener('click', function(e) {
            e.preventDefault();
            chatbotFab.click();
        });
    }

    // Contact form logic
    const contactSection = document.querySelector('.contact-section');
    if (contactSection) {
        const contactForm = contactSection.querySelector('.contact-form');
        if (contactForm) {
            contactForm.addEventListener('submit', async e => {
                e.preventDefault();
                const data = {
                    name: contactForm.name.value,
                    email: contactForm.email.value,
                    message: contactForm.message.value
                };
                try {
                    const resp = await fetch('http://localhost:8080/contact/', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    if (resp.ok) {
                        alert('Thank you! Your message has been sent.');
                        contactForm.reset();
                    } else {
                        alert('Sorry, there was a problem. Please try again.');
                    }
                } catch (err) {
                    alert('Sorry, there was a problem. Please try again.');
                }
            });
        }
    }
});
