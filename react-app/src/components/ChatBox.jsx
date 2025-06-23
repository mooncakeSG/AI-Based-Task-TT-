import { useState } from 'react';

const ChatBox = () => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    { id: 1, text: "Welcome! How can I help you with your tasks today?", sender: "ai", timestamp: new Date() }
  ]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      // Add user message
      const userMessage = {
        id: Date.now(),
        text: message,
        sender: "user",
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      // Simulate AI response (placeholder)
      setTimeout(() => {
        const aiResponse = {
          id: Date.now() + 1,
          text: `I received your message: "${message}". This is a placeholder response. Backend integration coming soon!`,
          sender: "ai",
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiResponse]);
      }, 1000);
      
      setMessage('');
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 rounded-t-lg">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs md:max-w-md lg:max-w-lg px-4 py-2 rounded-lg ${
                msg.sender === 'user'
                  ? 'bg-blue-500 text-white rounded-br-none'
                  : 'bg-white text-gray-800 border border-gray-200 rounded-bl-none'
              }`}
            >
              <p className="text-sm md:text-base">{msg.text}</p>
              <p className={`text-xs mt-1 ${
                msg.sender === 'user' ? 'text-blue-100' : 'text-gray-500'
              }`}>
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-200 rounded-b-lg">
        <div className="flex space-x-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message or task..."
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm md:text-base"
          />
          <button
            type="submit"
            disabled={!message.trim()}
            className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 text-sm md:text-base font-medium"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatBox; 