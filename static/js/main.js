// Initialize SocketIO connection
const socket = io();

// Voice recognition setup
function initVoiceRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        $('#voice-toggle').hide();
        return null;
    }
    
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    return recognition;
}

// Initialize when document is ready
$(document).ready(function() {
    const recognition = initVoiceRecognition();
    let currentDebateId = null;
    
    // Real-time AI response handling
    socket.on('ai_response', function(data) {
        if (data.debate_id !== currentDebateId) return;
        
        const messageDiv = $('<div>').addClass('flex justify-start mb-2');
        const contentDiv = $('<div>').addClass('bg-gray-100 p-3 rounded-lg max-w-lg');
        const header = $('<div>').addClass('font-bold text-indigo-600').html('<i class="fas fa-robot mr-2"></i>AI');
        contentDiv.append(header);
        
        const textDiv = $('<div>').attr('id', 'typing-text').text('');
        contentDiv.append(textDiv);
        messageDiv.append(contentDiv);
        $('#chat-container').append(messageDiv);
        
        // Typewriter effect for AI response
        let i = 0;
        const speed = 20;
        function typeWriter() {
            if (i < data.text.length) {
                textDiv.text(textDiv.text() + data.text.charAt(i));
                i++;
                setTimeout(typeWriter, speed);
                $('#chat-container').scrollTop($('#chat-container')[0].scrollHeight);
            } else {
                // Play audio when done typing
                const audio = new Audio(data.audio_url);
                audio.play();
            }
        }
        typeWriter();
    });
    
    // Start debate
    $('#start-debate').click(function() {
        const topic = $('#topic').val();
        const firstSpeaker = $('#first-speaker').val();
        const position = $('#position').val();
        
        $.post('/debate/start', {
            topic: topic,
            first_speaker: firstSpeaker,
            user_position: position
        }, function(response) {
            currentDebateId = response.debate_id;
            // Join debate room
            socket.emit('join_debate', {debate_id: currentDebateId});
            
            $('#setup-section').addClass('hidden');
            $('#debate-interface').removeClass('hidden');
            $('#debate-topic').text(topic);
            $('#user-position').text('You: ' + (position === 'for' ? 'In Favor' : 'Against'));
            $('#ai-position').text('AI: ' + (position === 'for' ? 'Against' : 'In Favor'));
            
            // Display initial messages
            response.transcript.forEach(msg => {
                addMessageToChat(msg.speaker, msg.text);
            });
        });
    });
    
    // Voice recognition toggle
    $('#voice-toggle').click(function() {
        if ($(this).hasClass('recording')) {
            recognition.stop();
            $(this).removeClass('recording bg-red-500').addClass('bg-gray-200');
        } else {
            recognition.start();
            $(this).removeClass('bg-gray-200').addClass('recording bg-red-500');
        }
    });
    
    if (recognition) {
        recognition.onresult = function(event) {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    transcript += event.results[i][0].transcript;
                }
            }
            $('#user-input').val(transcript);
        };
    }
    
    // Submit argument
    $('#submit-argument').click(function() {
        const argument = $('#user-input').val().trim();
        if (!argument) return;
        
        addMessageToChat('user', argument);
        $('#user-input').val('');
        
        $.post('/debate/submit', {
            debate_id: currentDebateId,
            argument: argument
        }, function(response) {
            // Response handled through SocketIO
            $('#evaluate-btn').removeClass('hidden');
        });
    });    // End debate
    $('#end-debate').click(function() {
        // Show loading message 
        $('#evaluate-btn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin mr-2"></i> Evaluating...');
        
        // Redirect to evaluation page
        window.location.href = `/debate/evaluate/${currentDebateId}`;
    });
});

function addMessageToChat(speaker, text) {
    const isUser = speaker === 'user';
    const messageClass = isUser ? 'bg-indigo-100 border-indigo-300' : 'bg-gray-100 border-gray-300';
    const name = isUser ? 'You' : 'AI';
    const icon = isUser ? 'fas fa-user' : 'fas fa-robot';
    
    $('#chat-container').append(`
        <div class="flex ${isUser ? 'justify-end' : 'justify-start'} mb-2">
            <div class="max-w-lg p-3 rounded-lg ${messageClass}">
                <div class="font-semibold ${isUser ? 'text-indigo-700' : 'text-gray-700'}">
                    <i class="${icon} mr-2"></i>${name}
                </div>
                <div>${text}</div>
            </div>
        </div>
    `);
    
    // Scroll to bottom
    $('#chat-container').scrollTop($('#chat-container')[0].scrollHeight);
}