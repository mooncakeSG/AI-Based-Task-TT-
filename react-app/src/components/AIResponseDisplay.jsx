import React from 'react';
import { MessageCircle, ArrowRight } from 'lucide-react';

const AIResponseDisplay = ({ content, suggestions = [], tasks = [], onNavigate, className = "", hideChatDirection = false }) => {
  if (!content && !suggestions?.length && !tasks?.length) return null;

  // Filter out chat direction content if hideChatDirection is true
  let filteredContent = content;
  if (hideChatDirection && content) {
    // Remove chat direction sections (everything after --- followed by 💬)
    filteredContent = content.split(/\n\s*---\s*\n\s*💬/)[0].trim();
    
    // Also remove standalone chat direction lines
    filteredContent = filteredContent
      .split('\n')
      .filter(line => !line.includes('💬') || !line.toLowerCase().includes('chat'))
      .join('\n')
      .trim();
  }

  // Check if content contains chat direction (but respect hideChatDirection prop)
  const hasChatDirection = !hideChatDirection && content && content.includes('💬');

  const handleChatNavigation = () => {
    // Use the navigation function if available, otherwise try alternative methods
    if (onNavigate) {
      onNavigate('chat');
    } else {
      // Fallback: try to find the app's navigation function
      const event = new CustomEvent('navigate-to-chat');
      window.dispatchEvent(event);
    }
  };

  // Format the content with proper typography
  const formatContent = (text) => {
    if (!text) return "";
    
    // Split content into paragraphs and format
    return text
      // Replace multiple line breaks with paragraph breaks
      .split(/\n\s*\n/)
      .map(paragraph => paragraph.trim())
      .filter(paragraph => paragraph.length > 0);
  };

  const formatParagraph = (paragraph) => {
    // Handle different text formatting patterns
    return paragraph
      // Convert **bold** to strong tags
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Convert *italic* to em tags
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Convert ### headers
      .replace(/^###\s+(.+)$/gm, '<h3 class="text-lg font-semibold text-blue-900 mt-4 mb-2">$1</h3>')
      // Convert ## headers
      .replace(/^##\s+(.+)$/gm, '<h2 class="text-xl font-bold text-blue-900 mt-5 mb-3">$1</h2>')
      // Convert # headers
      .replace(/^#\s+(.+)$/gm, '<h1 class="text-2xl font-bold text-blue-900 mt-6 mb-4">$1</h1>')
      // Convert - bullet points
      .replace(/^-\s+(.+)$/gm, '<li class="ml-4 text-gray-700">$1</li>')
      // Convert numbered lists
      .replace(/^\d+\.\s+(.+)$/gm, '<li class="ml-4 text-gray-700">$1</li>');
  };

  const formatAsMarkdown = (text) => {
    const paragraphs = formatContent(text);
    
    return paragraphs.map((paragraph, index) => {
      const formattedParagraph = formatParagraph(paragraph);
      
      // Check if this paragraph contains list items
      if (formattedParagraph.includes('<li class="ml-4">')) {
        const listItems = formattedParagraph.split('\n').filter(line => line.includes('<li class="ml-4">'));
        return (
          <ul key={index} className="list-disc list-outside ml-6 mb-4 space-y-2">
            {listItems.map((item, itemIndex) => (
              <div key={itemIndex} dangerouslySetInnerHTML={{ __html: item }} />
            ))}
          </ul>
        );
      }
      
      // Check if this is a header
      if (formattedParagraph.includes('<h1') || formattedParagraph.includes('<h2') || formattedParagraph.includes('<h3')) {
        return (
          <div key={index} dangerouslySetInnerHTML={{ __html: formattedParagraph }} />
        );
      }
      
      // Regular paragraph
      return (
        <p 
          key={index} 
          className="mb-4 leading-relaxed text-gray-700"
          dangerouslySetInnerHTML={{ __html: formattedParagraph }}
        />
      );
    });
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Main Content */}
      <div className="prose prose-sm max-w-none">
        <div className="space-y-2">
          {formatAsMarkdown(filteredContent)}
        </div>
      </div>

      {/* Chat Navigation Button */}
      {hasChatDirection && (
        <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
                <MessageCircle className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h4 className="font-semibold text-gray-900">Continue the Conversation</h4>
                <p className="text-sm text-gray-600">Get personalized help with implementing these insights</p>
              </div>
            </div>
            <button
              onClick={handleChatNavigation}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium"
            >
              <span>Go to Chat</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Enhanced sections for suggestions and tasks would go here if needed */}
      {suggestions?.length > 0 && (
        <div className="mt-4 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
          <h4 className="font-medium text-yellow-800 mb-2">Suggestions Available</h4>
          <p className="text-sm text-yellow-700">{suggestions.length} actionable suggestions extracted from the analysis.</p>
        </div>
      )}

      {tasks?.length > 0 && (
        <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
          <h4 className="font-medium text-green-800 mb-2">Tasks Identified</h4>
          <p className="text-sm text-green-700">{tasks.length} potential tasks found in the content.</p>
        </div>
      )}
    </div>
  );
};

export default AIResponseDisplay; 