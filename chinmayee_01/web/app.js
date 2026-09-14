/**
 * Nova Voice Assistant — Frontend Web Logic
 * Integrates Web Speech API (STT), Web Speech Synthesis (TTS), and Python Backend REST APIs.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Determine API Base URL (if opened directly as file://, route to http://localhost:5000)
    const API_BASE = (window.location.protocol === 'file:') ? 'http://localhost:5000' : '';

    // UI Elements
    const micButton = document.getElementById('micButton');
    const voiceAura = document.getElementById('voiceAura');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusLabel = document.getElementById('statusLabel');
    const statusSubtext = document.getElementById('statusSubtext');
    const orbCaption = document.getElementById('orbCaption');
    const chatContainer = document.getElementById('chatContainer');
    const commandForm = document.getElementById('commandForm');
    const textInput = document.getElementById('textInput');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const quickButtons = document.querySelectorAll('.quick-btn');
    const ttsToggle = document.getElementById('ttsToggle');
    const voiceSelect = document.getElementById('voiceSelect');
    const cpuVal = document.getElementById('cpuVal');
    const ramVal = document.getElementById('ramVal');

    // Notes Modal Elements
    const notesModal = document.getElementById('notesModal');
    const notesModalBtn = document.getElementById('notesModalBtn');
    const closeNotesBtn = document.getElementById('closeNotesBtn');
    const refreshNotesBtn = document.getElementById('refreshNotesBtn');
    const clearNotesBtn = document.getElementById('clearNotesBtn');
    const notesContent = document.getElementById('notesContent');

    let isListening = false;
    let recognition = null;
    let availableVoices = [];

    // Initialize Web Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            setAssistantState('listening');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.trim();
            if (transcript) {
                appendUserMessage(transcript);
                sendCommandToAssistant(transcript);
            }
        };

        recognition.onerror = (event) => {
            console.warn('Speech recognition error:', event.error);
            if (event.error === 'not-allowed') {
                appendAssistantMessage('Microphone permission was denied. Please allow microphone access in your browser or type your command below.');
            }
            setAssistantState('idle');
            isListening = false;
        };

        recognition.onend = () => {
            isListening = false;
            if (!voiceAura.classList.contains('state-processing') && !voiceAura.classList.contains('state-speaking')) {
                setAssistantState('idle');
            }
        };
    } else {
        console.warn('Web Speech Recognition API is not supported in this browser.');
        statusSubtext.textContent = 'Voice input unavailable in this browser. Use text input below.';
    }

    // Populate Available Voices for Text-to-Speech
    function loadVoices() {
        if ('speechSynthesis' in window) {
            availableVoices = window.speechSynthesis.getVoices();
        }
    }
    loadVoices();
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    // Speak Text Aloud via Web Speech Synthesis
    function speakText(text) {
        if (!ttsToggle.checked || !('speechSynthesis' in window)) {
            setAssistantState('idle');
            return;
        }

        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        const preferredGender = voiceSelect.value;
        const matchedVoice = availableVoices.find(v => {
            const name = v.name.toLowerCase();
            if (preferredGender === 'female') {
                return name.includes('female') || name.includes('zira') || name.includes('samantha') || name.includes('google us english') || name.includes('jenny');
            } else {
                return name.includes('male') || name.includes('david') || name.includes('guy') || name.includes('george');
            }
        });

        if (matchedVoice) {
            utterance.voice = matchedVoice;
        }

        utterance.onstart = () => {
            setAssistantState('speaking');
        };

        utterance.onend = () => {
            setAssistantState('idle');
        };

        utterance.onerror = () => {
            setAssistantState('idle');
        };

        window.speechSynthesis.speak(utterance);
    }

    // State Machine Visual Updater
    function setAssistantState(state) {
        voiceAura.className = 'voice-aura';

        if (state === 'listening') {
            voiceAura.classList.add('state-listening');
            statusIndicator.style.backgroundColor = 'var(--accent-blue)';
            statusIndicator.style.boxShadow = '0 0 10px var(--accent-blue)';
            statusLabel.style.color = 'var(--accent-blue)';
            statusLabel.textContent = 'LISTENING...';
            statusSubtext.textContent = 'Speak your command now...';
            orbCaption.textContent = 'Listening to your voice...';
        } else if (state === 'processing') {
            voiceAura.classList.add('state-processing');
            statusIndicator.style.backgroundColor = 'var(--accent-amber)';
            statusIndicator.style.boxShadow = '0 0 10px var(--accent-amber)';
            statusLabel.style.color = 'var(--accent-amber)';
            statusLabel.textContent = 'PROCESSING...';
            statusSubtext.textContent = 'Analyzing command and generating answer...';
            orbCaption.textContent = 'Thinking...';
        } else if (state === 'speaking') {
            voiceAura.classList.add('state-speaking');
            statusIndicator.style.backgroundColor = 'var(--accent-purple)';
            statusIndicator.style.boxShadow = '0 0 10px var(--accent-purple)';
            statusLabel.style.color = 'var(--accent-purple)';
            statusLabel.textContent = 'SPEAKING...';
            statusSubtext.textContent = 'Synthesizing voice response...';
            orbCaption.textContent = 'Speaking response...';
        } else {
            statusIndicator.style.backgroundColor = 'var(--accent-green)';
            statusIndicator.style.boxShadow = '0 0 10px var(--accent-green)';
            statusLabel.style.color = 'var(--accent-green)';
            statusLabel.textContent = 'SYSTEM READY';
            statusSubtext.textContent = 'Click the orb or press Spacebar to speak';
            orbCaption.textContent = 'Click microphone to speak';
        }
    }

    // Toggle Microphone
    function toggleListening() {
        if (!recognition) {
            alert('Speech Recognition is not supported in this browser. Please use Google Chrome, Microsoft Edge, or type your command.');
            return;
        }

        if (isListening) {
            recognition.stop();
            isListening = false;
            setAssistantState('idle');
        } else {
            try {
                window.speechSynthesis.cancel();
                recognition.start();
            } catch (err) {
                console.error('Error starting recognition:', err);
            }
        }
    }

    micButton.addEventListener('click', toggleListening);

    // Keyboard Spacebar Shortcut to Trigger Voice
    window.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && document.activeElement !== textInput && !isListening) {
            e.preventDefault();
            toggleListening();
        }
    });

    // Curated Content for Offline / Client Engine
    const JOKES = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why do Java developers wear glasses? Because they don't C-sharp!",
        "There are 10 types of people in the world: those who understand binary, and those who don't.",
        "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
        "Why was the JavaScript developer sad? Because they didn't Node how to Express themselves!",
        "What is an algorithm? A word used by programmers when they do not want to explain what they did."
    ];

    const QUOTES = [
        "The only way to do great work is to love what you do. — Steve Jobs",
        "It always seems impossible until it's done. — Nelson Mandela",
        "Success is not final, failure is not fatal: it is the courage to continue that counts. — Winston Churchill",
        "Believe you can and you're halfway there. — Theodore Roosevelt",
        "The future belongs to those who believe in the beauty of their dreams. — Eleanor Roosevelt"
    ];

    const FACTS = [
        "Did you know? Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible!",
        "Did you know? Octopuses have three hearts and blue blood.",
        "Did you know? The first computer programmer in history was Ada Lovelace in 1843.",
        "Did you know? A day on Venus is longer than a year on Venus.",
        "Did you know? Sound travels about 4 times faster in water than in air."
    ];

    const RIDDLES = [
        "Riddle: What has keys but can't open locks? Answer: A piano or a keyboard!",
        "Riddle: What has to be broken before you can use it? Answer: An egg!",
        "Riddle: I’m tall when I’m young, and I’m short when I’m old. What am I? Answer: A candle!",
        "Riddle: What goes up but never comes down? Answer: Your age!"
    ];

    const SITES = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "github": "https://www.github.com",
        "wikipedia": "https://www.wikipedia.org",
        "reddit": "https://www.reddit.com",
        "stackoverflow": "https://stackoverflow.com",
        "gmail": "https://mail.google.com",
        "chatgpt": "https://chat.openai.com",
        "netflix": "https://www.netflix.com",
        "spotify": "https://open.spotify.com",
        "amazon": "https://www.amazon.com",
        "twitter": "https://www.twitter.com",
        "x": "https://www.x.com",
        "instagram": "https://www.instagram.com",
        "linkedin": "https://www.linkedin.com",
        "facebook": "https://www.facebook.com",
        "twitch": "https://www.twitch.tv",
        "discord": "https://discord.com",
        "whatsapp": "https://web.whatsapp.com",
        "maps": "https://maps.google.com"
    };

    // Client-side Knowledge & Intent Engine (Fallback)
    async function processClientSideCommand(cmdText) {
        const text = cmdText.toLowerCase().trim();

        // 1. Time
        if (text.includes("time")) {
            const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            return `The current time is ${timeStr}.`;
        }

        // 2. Date
        if (text.includes("date") || text.includes("day is today") || text.includes("today's date")) {
            const dateStr = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            return `Today is ${dateStr}.`;
        }

        // 3. Open Website
        for (const [siteKey, siteUrl] of Object.entries(SITES)) {
            if (text.includes(`open ${siteKey}`) || text === siteKey) {
                window.open(siteUrl, "_blank");
                return `Opening ${siteKey.charAt(0).toUpperCase() + siteKey.slice(1)} in a new tab.`;
            }
        }

        // 4. Play YouTube Music / Video
        if (text.startsWith("play ") || text.includes("play on youtube") || text.includes("listen to ")) {
            let query = text.replace(/play on youtube|play song|play music|listen to|play/gi, "").trim();
            if (query) {
                window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`, "_blank");
                return `Playing ${query} on YouTube.`;
            }
            window.open("https://www.youtube.com", "_blank");
            return "Opening YouTube.";
        }

        // 5. Search Google / Web
        if (text.startsWith("search ") || text.includes("search for") || text.includes("google search") || text.includes("search google")) {
            let query = text.replace(/search google for|search the web for|google search for|search for|google search|search/gi, "").trim();
            if (query) {
                window.open(`https://www.google.com/search?q=${encodeURIComponent(query)}`, "_blank");
                return `Searching Google for ${query}.`;
            }
            return "What would you like me to search for?";
        }

        // 6. Weather
        if (text.includes("weather") || text.includes("temperature") || text.includes("forecast")) {
            let loc = "";
            if (text.includes(" in ")) loc = text.split(" in ")[1].trim();
            else if (text.includes(" for ")) loc = text.split(" for ")[1].trim();
            
            try {
                const res = await fetch(`https://wttr.in/${encodeURIComponent(loc)}?format=%C+%t+%w&m`);
                if (res.ok) {
                    const data = await res.text();
                    const placeStr = loc ? `in ${loc}` : "locally";
                    return `The current weather ${placeStr} is ${data.trim()}.`;
                }
            } catch (e) {
                window.open(`https://www.google.com/search?q=weather+${encodeURIComponent(loc)}`, "_blank");
                return `Checking current weather for ${loc || 'your location'}.`;
            }
        }

        // 7. Math & Percentage Calculations
        if (text.includes("percent of") || text.includes("% of")) {
            const match = text.match(/(\d+(?:\.\d+)?)\s*(?:percent|%)\s+of\s+(\d+(?:\.\d+)?)/);
            if (match) {
                const pct = parseFloat(match[1]);
                const base = parseFloat(match[2]);
                const res = (pct / 100) * base;
                return `${pct} percent of ${base} is ${res}.`;
            }
        }

        if (text.includes("square root of") || text.includes("sqrt of")) {
            const nums = text.match(/[-+]?(?:\d*\.\d+|\d+)/);
            if (nums) {
                const val = parseFloat(nums[0]);
                return `The square root of ${val} is ${Math.sqrt(val)}.`;
            }
        }

        if (text.includes("calculate") || text.includes("plus") || text.includes("minus") || text.includes("times") || text.includes("multiplied") || text.includes("divided") || text.includes("+") || text.includes("*") || text.includes("-") || text.includes("/")) {
            try {
                let expr = text.replace(/calculate|compute|solve|what is|how much is/g, "")
                               .replace(/plus|add/g, "+")
                               .replace(/minus|subtract/g, "-")
                               .replace(/times|multiplied by|x/g, "*")
                               .replace(/divided by|divide|over/g, "/")
                               .replace(/[^0-9+\-*/().\s]/g, "");
                if (expr.trim()) {
                    const res = Function(`'use strict'; return (${expr})`)();
                    return `The calculated result is ${res}.`;
                }
            } catch (e) {
                // Ignore math parse error and proceed to knowledge
            }
        }

        // 8. Conversions
        if (text.includes("celsius to fahrenheit") || (text.includes("c to f") && text.match(/\d+/))) {
            const num = parseFloat(text.match(/\d+(?:\.\d+)?/)?.[0] || 0);
            const f = (num * 9/5) + 32;
            return `${num} degrees Celsius is ${f.toFixed(2)} degrees Fahrenheit.`;
        }
        if (text.includes("km to miles") || text.includes("kilometers to miles")) {
            const num = parseFloat(text.match(/\d+(?:\.\d+)?/)?.[0] || 0);
            const mi = num * 0.621371;
            return `${num} kilometers is approximately ${mi.toFixed(2)} miles.`;
        }

        // 9. Jokes, Quotes, Facts, Riddles
        if (text.includes("joke") || text.includes("make me laugh")) {
            return JOKES[Math.floor(Math.random() * JOKES.length)];
        }
        if (text.includes("quote") || text.includes("inspire") || text.includes("motivate")) {
            return QUOTES[Math.floor(Math.random() * QUOTES.length)];
        }
        if (text.includes("fact") || text.includes("did you know")) {
            return FACTS[Math.floor(Math.random() * FACTS.length)];
        }
        if (text.includes("riddle") || text.includes("puzzle")) {
            return RIDDLES[Math.floor(Math.random() * RIDDLES.length)];
        }
        if (text.includes("coin") || text.includes("flip") || text.includes("toss")) {
            return `I flipped a coin and got: ${Math.random() > 0.5 ? "Heads" : "Tails"}!`;
        }
        if (text.includes("dice") || text.includes("roll die")) {
            return `I rolled a die and got: ${Math.floor(Math.random() * 6) + 1}!`;
        }

        // 10. Greetings & Assistant Info
        if (text.includes("hello") || text.includes("hi ") || text === "hi" || text.includes("hey") || text.includes("good morning") || text.includes("good evening")) {
            return "Hello Boss! I am online and listening. How can I assist you today?";
        }
        if (text.includes("who are you") || text.includes("what is your name")) {
            return "I am Nova, your intelligent voice assistant.";
        }
        if (text.includes("how are you")) {
            return "I am operating at 100% capacity and ready for your commands!";
        }
        if (text.includes("thank you") || text.includes("thanks")) {
            return "You're very welcome! Let me know if you need anything else.";
        }

        // 11. Live Online Wikipedia Knowledge Lookup
        try {
            let cleanQuery = text.replace(/^(who is|who was|what is|what are|where is|tell me about|explain|define|history of|meaning of|what's)\s+/i, '').replace(/[?!.]/g, '').trim();
            if (cleanQuery.length >= 2) {
                const res = await fetch(`https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(cleanQuery)}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data.extract) {
                        const sentences = data.extract.split('.').filter(s => s.trim().length > 0);
                        return sentences.slice(0, 2).join('.') + '.';
                    }
                }
            }
        } catch (err) {
            console.debug('Wikipedia client fetch error:', err);
        }

        // 12. No client-side fake answers. General questions must be answered by the Python AI backend.
        return "I could not reach the AI backend. Please make sure the Python server is running and an AI API key is configured.";
    }

    // Main Unified Command Dispatcher
    async function sendCommandToAssistant(commandText) {
        if (!commandText) return;
        setAssistantState('processing');

        try {
            // Attempt to communicate with Python Backend
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 90000);

            const response = await fetch(`${API_BASE}/api/command`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: commandText }),
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            if (response.ok) {
                const data = await response.json();
                const reply = data.response || "I couldn't process that command.";
                appendAssistantMessage(reply);
                speakText(reply);
                updateTelemetry();
                return;
            }
            throw new Error(`Server returned status ${response.status}`);

        } catch (error) {
            console.error('Voice assistant backend error:', error);
            // Do not pretend that an unknown question was merely searched in Google.
            // A ChatGPT-like answer must come from the Python AI backend.
            const reply = error.name === 'AbortError'
                ? 'The AI is taking longer than expected. Please try the question again.'
                : 'I could not connect to the AI backend. Please make sure the Python server is running and your AI API key is configured.';
            appendAssistantMessage(reply);
            speakText(reply);
        }
    }

    // Chat Message Helpers
    function appendUserMessage(text) {
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message user-msg';
        msgDiv.innerHTML = `
            <div class="msg-avatar">👤</div>
            <div class="msg-bubble">
                <div class="msg-header">
                    <span class="msg-sender">You</span>
                    <span class="msg-time">${time}</span>
                </div>
                <div class="msg-text">${escapeHtml(text)}</div>
            </div>
        `;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function appendAssistantMessage(text) {
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message assistant-msg';
        msgDiv.innerHTML = `
            <div class="msg-avatar">🎙️</div>
            <div class="msg-bubble">
                <div class="msg-header">
                    <span class="msg-sender">Nova</span>
                    <span class="msg-time">${time}</span>
                </div>
                <div class="msg-text">${escapeHtml(text)}</div>
            </div>
        `;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function escapeHtml(str) {
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }

    // Form Submission
    commandForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = textInput.value.trim();
        if (text) {
            textInput.value = '';
            appendUserMessage(text);
            sendCommandToAssistant(text);
        }
    });

    // Quick Action Buttons
    quickButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const cmd = btn.getAttribute('data-cmd');
            if (cmd) {
                appendUserMessage(cmd);
                sendCommandToAssistant(cmd);
            }
        });
    });

    // Clear Chat
    clearChatBtn.addEventListener('click', () => {
        chatContainer.innerHTML = '';
        appendAssistantMessage("Conversation cleared. How can I assist you now?");
    });

    // Live Telemetry Poller
    async function updateTelemetry() {
        try {
            const res = await fetch(`${API_BASE}/api/status`);
            if (res.ok) {
                const data = await res.json();
                if (data.cpu !== undefined) cpuVal.textContent = `${data.cpu}%`;
                if (data.ram !== undefined) ramVal.textContent = `${data.ram}%`;
            }
        } catch (err) {
            // Ignore telemetry fetch errors
        }
    }
    updateTelemetry();
    setInterval(updateTelemetry, 5000);

    // Saved Notes Modal Management
    async function loadNotes() {
        notesContent.innerHTML = '<p class="loading-text">Loading notes...</p>';
        try {
            const res = await fetch(`${API_BASE}/api/notes`);
            const data = await res.json();
            if (data.notes && data.notes.length > 0) {
                notesContent.innerHTML = data.notes.map(n => `<p style="margin-bottom: 8px; border-bottom: 1px solid var(--border-color); padding-bottom: 6px;">${escapeHtml(n)}</p>`).join('');
            } else {
                notesContent.innerHTML = '<p style="color: var(--text-muted);">No notes found in data/notes.txt.</p>';
            }
        } catch (err) {
            notesContent.innerHTML = '<p style="color: var(--accent-red);">Failed to load notes from server.</p>';
        }
    }

    notesModalBtn.addEventListener('click', () => {
        notesModal.style.display = 'flex';
        loadNotes();
    });

    closeNotesBtn.addEventListener('click', () => {
        notesModal.style.display = 'none';
    });

    refreshNotesBtn.addEventListener('click', loadNotes);

    clearNotesBtn.addEventListener('click', async () => {
        if (confirm("Are you sure you want to clear all notes?")) {
            await fetch(`${API_BASE}/api/notes`, { method: 'DELETE' });
            loadNotes();
            appendAssistantMessage("All notes have been cleared.");
        }
    });

    window.addEventListener('click', (e) => {
        if (e.target === notesModal) {
            notesModal.style.display = 'none';
        }
    });
});

