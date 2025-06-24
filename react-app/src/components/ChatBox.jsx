import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Mic, Send, Loader, Paperclip, X, Check, Plus, Save } from 'lucide-react';
import toast from 'react-hot-toast';
import UploadBox from './UploadBox';
import FileUpload from './FileUpload';
import VoiceRecorder from './VoiceRecorder';
import AIResponseDisplay from './AIResponseDisplay';
import { animations } from '../styles/design-system';
import { supabase } from '../lib/supabase';

// Component for displaying extracted tasks with save options
const TaskSavePrompt = ({ tasks, onSave, onDismiss }) => {
  const [selectedTasks, setSelectedTasks] = useState(new Set(tasks.map((_, index) => index)));

  const toggleTask = (index) => {
    const newSelected = new Set(selectedTasks);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedTasks(newSelected);
  };

  const handleSave = () => {
    const tasksToSave = tasks.filter((_, index) => selectedTasks.has(index));
    onSave(tasksToSave);
  };

  return (
    <motion.div 
      className="bg-blue-50/90 backdrop-blur-sm border border-blue-200/60 rounded-2xl p-4 mt-3"
      variants={animations.slideUp}
      initial="initial"
      animate="animate"
      exit="exit"
    >
      <div className="flex items-center justify-between mb-3">
        <h4 className="text-sm font-medium text-blue-900 flex items-center">
          <Plus className="w-4 h-4 mr-2" />
          Tasks Found ({tasks.length})
        </h4>
        <button
          onClick={onDismiss}
          className="text-blue-600 hover:text-blue-800 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
      
      <div className="space-y-2 mb-4">
        {tasks.map((task, index) => (
          <div 
            key={index}
            className={`flex items-start space-x-3 p-3 rounded-lg transition-all cursor-pointer ${
              selectedTasks.has(index) 
                ? 'bg-blue-100/80 border border-blue-300/60' 
                : 'bg-white/80 border border-gray-200/60 hover:bg-blue-50/50'
            }`}
            onClick={() => toggleTask(index)}
          >
            <div className={`w-4 h-4 rounded border-2 flex items-center justify-center mt-0.5 transition-colors ${
              selectedTasks.has(index) 
                ? 'bg-blue-500 border-blue-500' 
                : 'border-gray-300 hover:border-blue-400'
            }`}>
              {selectedTasks.has(index) && (
                <Check className="w-3 h-3 text-white" />
              )}
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">{task.summary || task.title}</p>
              <div className="flex items-center space-x-2 mt-1">
                <span className={`px-2 py-0.5 text-xs rounded-full ${
                  task.priority === 'high' ? 'bg-red-100 text-red-700' :
                  task.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-green-100 text-green-700'
                }`}>
                  {task.priority || 'medium'}
                </span>
                <span className="px-2 py-0.5 text-xs rounded-full bg-gray-100 text-gray-700">
                  {task.category || 'general'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="flex items-center justify-between">
        <p className="text-xs text-blue-600">
          {selectedTasks.size} of {tasks.length} tasks selected
        </p>
        <div className="flex space-x-2">
          <button
            onClick={onDismiss}
            className="px-3 py-1.5 text-xs text-gray-600 hover:text-gray-800 transition-colors"
          >
            Dismiss
          </button>
          <button
            onClick={handleSave}
            disabled={selectedTasks.size === 0}
            className="px-3 py-1.5 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white text-xs rounded-lg transition-colors flex items-center space-x-1"
          >
            <Save className="w-3 h-3" />
            <span>Save {selectedTasks.size > 0 ? `(${selectedTasks.size})` : ''}</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
};

const ChatBox = ({ className = "" }) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      text: "Welcome! I'm IntelliAssist.AI. I can help you with text, images, and voice messages. How can I assist you with your tasks today?", 
      sender: "ai", 
      timestamp: new Date() 
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [showVoiceRecorder, setShowVoiceRecorder] = useState(false);
  const [showUploadBox, setShowUploadBox] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState([]);
  const [pendingTasks, setPendingTasks] = useState({}); // Store pending tasks by message ID
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Check if we have any input
    if (!message.trim() && attachedFiles.length === 0) {
      toast.error('Please enter a message or attach a file');
      return;
    }

    setIsLoading(true);

    try {
      // Create user message
      const userMessage = {
        id: Date.now(),
        text: message || '',
        sender: "user",
        timestamp: new Date(),
        attachments: [...attachedFiles]
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      // Clear input immediately for better UX
      setMessage('');
      setAttachedFiles([]);
      
      // Prepare request data
      const requestData = {};
      
      if (message.trim()) {
        requestData.message = message;
      }
      
      if (attachedFiles.length > 0) {
        // Find image and audio files
        const imageFile = attachedFiles.find(f => f.type?.startsWith('image/'));
        const audioFile = attachedFiles.find(f => f.type?.startsWith('audio/'));
        
        if (imageFile) requestData.image_file_id = imageFile.id || imageFile.fileId;
        if (audioFile) requestData.audio_file_id = audioFile.id || audioFile.fileId;
      }

      // Choose endpoint based on input type
      const isMultimodal = attachedFiles.length > 0;
      const endpoint = isMultimodal ? 'http://localhost:8000/api/v1/multimodal' : 'http://localhost:8000/api/v1/chat';
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed: ${response.status}`);
      }

      const result = await response.json();
      
      // Create AI response message
      const aiMessageId = Date.now() + 1;
      const aiMessage = {
        id: aiMessageId,
        text: result.response,
        sender: "ai",
        timestamp: new Date(),
        metadata: {
          model: result.model_info?.model || result.model,
          response_time: result.processing_details?.processing_time || result.response_time,
          tokens: result.model_info?.tokens_used || result.tokens_used,
          inputs_processed: result.inputs_processed || ['text'],
          tasks_extracted: result.tasks?.length || 0
        }
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // Handle extracted tasks - show them for manual confirmation instead of auto-saving
      if (result.tasks && result.tasks.length > 0) {
        console.log('🧠 AI extracted tasks:', result.tasks);
        setPendingTasks(prev => ({
          ...prev,
          [aiMessageId]: result.tasks
        }));
      }
      
    } catch (error) {
      console.error('Chat request failed:', error);
      
      // Show error toast
      toast.error(error.message || 'Failed to send message. Please try again.');
      
      // Add error message to chat
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm sorry, I encountered an error processing your request. Please try again.",
        sender: "ai",
        timestamp: new Date(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setShowFileUpload(false);
      setShowVoiceRecorder(false);
      setShowUploadBox(false);
    }
  };

  const handleFileUpload = (fileInfo) => {
    setAttachedFiles(prev => [...prev, fileInfo]);
    setShowFileUpload(false);
  };

  const handleVoiceRecording = async (audioInfo) => {
    console.log('🎤 Voice recording completed:', audioInfo);
    console.log('🔍 Transcription data:', audioInfo.transcription);
    console.log('🔍 AI Response data:', audioInfo.aiResponse);
    
    // Add user message showing the audio was recorded
    const userMessage = {
      id: Date.now(),
      text: `🎤 Voice message recorded (${Math.round(audioInfo.duration || 0)}s)`,
      sender: "user",
      timestamp: new Date(),
      attachments: [audioInfo]
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // If we have transcription results, show them immediately
    if (audioInfo.transcription?.text || audioInfo.aiResponse) {
      const transcriptionText = audioInfo.transcription?.text || '';
      const aiResponse = audioInfo.aiResponse || '';
      
      console.log('📝 Processing transcription:', transcriptionText);
      console.log('🤖 Processing AI response:', aiResponse);
      
      // Show transcription as a separate message if available
      if (transcriptionText.trim()) {
        const transcriptionMessage = {
          id: Date.now() + 1,
          text: `**Transcription:** ${transcriptionText}`,
          sender: "ai",
          timestamp: new Date(),
          metadata: {
            type: 'transcription',
            confidence: audioInfo.transcription?.confidence || 0,
            language: audioInfo.transcription?.language || 'unknown'
          }
        };
        
        setMessages(prev => [...prev, transcriptionMessage]);
      }
      
      // Show AI analysis if available
      if (aiResponse.trim() && aiResponse !== transcriptionText) {
        const aiMessageId = Date.now() + 2;
        const aiMessage = {
          id: aiMessageId,
          text: aiResponse,
          sender: "ai",
          timestamp: new Date(),
          metadata: {
            type: 'voice_analysis',
            model: 'whisper + llama',
            inputs_processed: ['audio']
          }
        };
        
        setMessages(prev => [...prev, aiMessage]);
        
        // Try to extract and save tasks from the AI response
        try {
          const taskExtractionResponse = await fetch('http://localhost:8000/api/v1/chat', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              message: `Extract any tasks from this transcribed voice message: "${transcriptionText}"`
            }),
          });
          
          if (taskExtractionResponse.ok) {
            const result = await taskExtractionResponse.json();
            if (result.tasks && result.tasks.length > 0) {
              console.log('🧠 Tasks extracted from voice message:', result.tasks);
              setPendingTasks(prev => ({
                ...prev,
                [aiMessageId]: result.tasks
              }));
            }
          }
        } catch (error) {
          console.error('Failed to extract tasks from voice message:', error);
        }
      }
    } else {
      console.log('⚠️ No transcription or AI response data found in audioInfo');
      // Show a fallback message
      const fallbackMessage = {
        id: Date.now() + 1,
        text: "Voice message uploaded successfully, but transcription data is not available. Please check the console for details.",
        sender: "ai",
        timestamp: new Date(),
        metadata: {
          type: 'transcription_error'
        }
      };
      
      setMessages(prev => [...prev, fallbackMessage]);
    }
    
    setShowVoiceRecorder(false);
  };

  const handleUploadBoxComplete = (uploadMessage, file) => {
    // Add the upload result as a message
    const uploadResultMessage = {
      id: uploadMessage.id,
      text: uploadMessage.message || `File "${uploadMessage.filename}" processed successfully!`,
      sender: "ai",
      timestamp: uploadMessage.timestamp,
      metadata: {
        type: 'upload_result',
        filename: uploadMessage.filename,
        size: uploadMessage.size
      }
    };
    
    setMessages(prev => [...prev, uploadResultMessage]);
    setShowUploadBox(false);
  };

  const removeAttachment = (fileId) => {
    setAttachedFiles(prev => prev.filter(f => (f.id || f.fileId) !== fileId));
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const saveTasks = async (tasks) => {
    if (!tasks || tasks.length === 0) return;
    
    console.log('🔧 Saving extracted tasks to Supabase:', tasks);
    
    try {
      for (const task of tasks) {
        const taskData = {
          summary: task.summary || task.title,
          category: task.category || 'general',
          priority: task.priority || 'medium',
          status: task.status || 'pending',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        console.log('💾 Inserting task:', taskData);
        
        const { data, error } = await supabase
          .from('tasks')
          .insert([taskData]);
        
        if (error) {
          console.error('❌ Error saving task:', error);
          toast.error(`Failed to save task: ${task.title?.substring(0, 30)}...`);
        } else {
          console.log('✅ Task saved successfully:', data);
        }
      }
      
      if (tasks.length > 0) {
        toast.success(`${tasks.length} task${tasks.length > 1 ? 's' : ''} saved successfully!`);
      }
    } catch (error) {
      console.error('❌ Error in saveTasks:', error);
      toast.error('Failed to save tasks to database');
    }
  };

  return (
    <div className={`flex flex-col h-full bg-white/80 backdrop-blur-md rounded-2xl shadow-lg border border-gray-200/60 overflow-hidden ${className}`}>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <AnimatePresence>
          {messages.map((msg, index) => (
            <motion.div
              key={msg.id}
              className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              variants={animations.fadeIn}
              initial="initial"
              animate="animate"
              exit="exit"
              transition={{ delay: index * 0.1 }}
            >
              <div
                className={`max-w-[85%] sm:max-w-md lg:max-w-lg ${
                  msg.sender === 'user'
                    ? 'bg-blue-50/90 backdrop-blur-sm text-blue-900 rounded-2xl rounded-br-md border-r-4 border-blue-500 shadow-sm'
                    : msg.isError
                    ? 'bg-red-50/90 backdrop-blur-sm text-red-800 border border-red-200/60 rounded-2xl rounded-bl-md border-l-4 border-red-500 shadow-sm'
                    : 'bg-white/90 backdrop-blur-sm text-gray-800 border border-gray-200/60 rounded-2xl rounded-bl-md border-l-4 border-blue-500 shadow-sm'
                } p-4 transition-all duration-200`}
              >
                {msg.sender === 'ai' ? (
                  <AIResponseDisplay content={msg.text} className="text-sm md:text-base" hideChatDirection={true} />
                ) : (
                  <p className="text-sm md:text-base leading-relaxed">{msg.text}</p>
                )}
                
                {/* Show attachments for user messages */}
                {msg.attachments && msg.attachments.length > 0 && (
                  <div className="mt-3 space-y-2">
                    {msg.attachments.map((file, index) => (
                      <div key={index} className="flex items-center bg-blue-100/80 backdrop-blur-sm rounded-lg px-3 py-2 text-xs">
                        <Paperclip className="w-3 h-3 mr-2 text-blue-600" />
                        <span className="font-medium">{file.name}</span>
                        <span className="ml-2 text-blue-600">({formatFileSize(file.size)})</span>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="flex justify-between items-center mt-3">
                  <p className={`text-xs ${
                    msg.sender === 'user' ? 'text-blue-600' : msg.isError ? 'text-red-500' : 'text-gray-500'
                  }`}>
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                  
                  {/* Show metadata for AI messages */}
                  {msg.metadata && (
                    <p className="text-xs text-gray-400">
                      {msg.metadata.response_time && `${msg.metadata.response_time}s`}
                      {msg.metadata.tokens && ` • ${msg.metadata.tokens} tokens`}
                    </p>
                  )}
                </div>
                
                {/* Show task save prompt if this AI message has extracted tasks */}
                {msg.sender === 'ai' && pendingTasks[msg.id] && (
                  <TaskSavePrompt
                    tasks={pendingTasks[msg.id]}
                    onSave={(tasksToSave) => {
                      saveTasks(tasksToSave);
                      setPendingTasks(prev => ({
                        ...prev,
                        [msg.id]: undefined
                      }));
                    }}
                    onDismiss={() => setPendingTasks(prev => ({
                      ...prev,
                      [msg.id]: undefined
                    }))}
                  />
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {/* Thinking indicator */}
        {isLoading && (
          <motion.div 
            className="flex justify-start"
            variants={animations.slideUp}
            initial="initial"
            animate="animate"
          >
            <div className="bg-white/90 backdrop-blur-sm text-gray-800 border border-gray-200/60 rounded-2xl rounded-bl-md border-l-4 border-blue-500 shadow-sm px-4 py-3 max-w-xs">
              <div className="flex items-center space-x-3">
                <div className="flex space-x-1">
                  <motion.div 
                    className="w-2 h-2 bg-blue-500 rounded-full"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                  />
                  <motion.div 
                    className="w-2 h-2 bg-blue-500 rounded-full"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.1 }}
                  />
                  <motion.div 
                    className="w-2 h-2 bg-blue-500 rounded-full"
                    animate={{ y: [0, -8, 0] }}
                    transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                  />
                </div>
                <span className="text-sm text-gray-600 font-medium">Thinking...</span>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Upload Box (when expanded) */}
      <AnimatePresence>
        {showUploadBox && (
          <motion.div 
            className="px-6 pb-4 border-t border-gray-200/60 bg-white/40 backdrop-blur-sm"
            variants={animations.slideUp}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            <div className="pt-4">
              <UploadBox 
                onUploadComplete={handleUploadBoxComplete}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Attached Files Preview */}
      <AnimatePresence>
        {attachedFiles.length > 0 && (
          <motion.div 
            className="px-6 py-3 bg-gray-50/80 backdrop-blur-sm border-t border-gray-200/60"
            variants={animations.slideUp}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            <p className="text-xs text-gray-500 mb-2 font-medium">Attached files:</p>
            <div className="flex flex-wrap gap-2">
              {attachedFiles.map((file, index) => (
                <motion.div 
                  key={file.id || file.fileId || index} 
                  className="flex items-center bg-white/80 backdrop-blur-sm rounded-lg px-3 py-2 text-sm shadow-sm border border-gray-200/60"
                  whileHover={{ scale: 1.02 }}
                >
                  <Paperclip className="w-4 h-4 mr-2 text-gray-600" />
                  <span className="max-w-32 truncate font-medium">{file.name || file.filename}</span>
                  <motion.button
                    onClick={() => removeAttachment(file.id || file.fileId)}
                    className="ml-2 text-red-500 hover:text-red-700 hover:bg-red-50/80 rounded-full w-5 h-5 flex items-center justify-center"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <X className="w-3 h-3" />
                  </motion.button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input Area - Sticky footer */}
      <div className="bg-white/80 backdrop-blur-sm border-t border-gray-200/60 p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Action buttons */}
          <div className="flex items-center justify-center space-x-3">
            <motion.button
              type="button"
              onClick={() => setShowUploadBox(!showUploadBox)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 backdrop-blur-sm ${
                showUploadBox 
                  ? 'bg-blue-100/80 text-blue-700 border border-blue-200/60 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-white/60 border border-gray-200/60'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Upload className="w-4 h-4" />
              <span>Upload Files</span>
            </motion.button>
            
            <motion.button
              type="button"
              onClick={() => setShowVoiceRecorder(!showVoiceRecorder)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium transition-all duration-200 backdrop-blur-sm ${
                showVoiceRecorder 
                  ? 'bg-purple-100/80 text-purple-700 border border-purple-200/60 shadow-sm' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-white/60 border border-gray-200/60'
              }`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Mic className="w-4 h-4" />
              <span>Voice Recording</span>
            </motion.button>
          </div>

          {/* Main input */}
          <div className="flex space-x-3 items-end">
            <textarea
              ref={inputRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Type your message or task..."
              className="flex-1 px-4 py-3 border border-gray-300/60 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm md:text-base resize-none transition-all duration-200 bg-white/80 backdrop-blur-sm"
              rows={1}
              style={{ 
                minHeight: '48px',
                maxHeight: '120px'
              }}
              disabled={isLoading}
            />
            <motion.button
              type="submit"
              disabled={(!message.trim() && attachedFiles.length === 0) || isLoading}
              className="px-6 py-3 bg-blue-600 text-white rounded-2xl font-semibold text-sm md:text-base shadow-lg hover:shadow-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex-shrink-0 backdrop-blur-sm"
              whileHover={{ scale: 1.02, y: -1 }}
              whileTap={{ scale: 0.98 }}
            >
              {isLoading ? (
                <Loader className="w-5 h-5 animate-spin" />
              ) : (
                <div className="flex items-center gap-2">
                  <Send className="w-4 h-4" />
                  <span>Send</span>
                </div>
              )}
            </motion.button>
          </div>
        </form>

        {/* Legacy components (hidden but available) */}
        <AnimatePresence>
          {showFileUpload && (
            <motion.div 
              className="mt-4"
              variants={animations.slideUp}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <FileUpload onFileUpload={handleFileUpload} />
            </motion.div>
          )}
          
          {showVoiceRecorder && (
            <motion.div 
              className="mt-4"
              variants={animations.slideUp}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <VoiceRecorder onRecordingComplete={handleVoiceRecording} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

    </div>
  );
};

export default ChatBox; 