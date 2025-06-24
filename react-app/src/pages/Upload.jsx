import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload as UploadIcon, FileText, Image, Music, File, CheckCircle, Clock, AlertCircle, Trash2, Eye, Copy, RefreshCw, ChevronDown, ChevronUp } from 'lucide-react';
import UploadBox from '../components/UploadBox';
import AIResponseDisplay from '../components/AIResponseDisplay';
import { animations } from '../styles/design-system';
import toast from 'react-hot-toast';

const Upload = ({ onNavigate }) => {
  // Sample/default data
  const defaultHistory = [
    {
      id: 1,
      filename: 'project-presentation.pdf',
      size: 2.4 * 1024 * 1024,
      type: 'application/pdf',
      uploadTime: new Date(Date.now() - 2 * 60 * 60 * 1000),
      status: 'completed',
      analysis: 'Document contains 15 slides about AI project roadmap with timeline and budget analysis.',
      isSample: true
    },
    {
      id: 2,
      filename: 'meeting-audio.mp3',
      size: 8.7 * 1024 * 1024,
      type: 'audio/mp3',
      uploadTime: new Date(Date.now() - 5 * 60 * 60 * 1000),
      status: 'completed',
      analysis: 'Transcribed 45-minute meeting discussing Q4 objectives and team assignments.',
      isSample: true
    },
    {
      id: 3,
      filename: 'data-chart.png',
      size: 1.2 * 1024 * 1024,
      type: 'image/png',
      uploadTime: new Date(Date.now() - 24 * 60 * 60 * 1000),
      status: 'processing',
      analysis: null,
      isSample: true
    }
  ];

  // Load upload history from localStorage or use default
  const loadUploadHistory = () => {
    try {
      const saved = localStorage.getItem('uploadHistory');
      if (saved) {
        const parsed = JSON.parse(saved);
        // Convert uploadTime strings back to Date objects
        return parsed.map(item => ({
          ...item,
          uploadTime: new Date(item.uploadTime)
        }));
      }
      return defaultHistory;
    } catch (error) {
      console.error('Error loading upload history:', error);
      return defaultHistory;
    }
  };

  // Save upload history to localStorage
  const saveUploadHistory = (history) => {
    try {
      localStorage.setItem('uploadHistory', JSON.stringify(history));
    } catch (error) {
      console.error('Error saving upload history:', error);
    }
  };

  const [uploadHistory, setUploadHistory] = useState(loadUploadHistory);
  const [expandedFiles, setExpandedFiles] = useState(new Set());

  // Save to localStorage whenever uploadHistory changes
  useEffect(() => {
    saveUploadHistory(uploadHistory);
  }, [uploadHistory]);

  const handleUploadComplete = (uploadMessage, file) => {
    const newUpload = {
      id: Date.now(),
      filename: file.name,
      size: file.size,
      type: file.type,
      uploadTime: new Date(),
      status: 'completed',
      analysis: uploadMessage.message,
      suggestions: uploadMessage.suggestions || [],
      tasks: uploadMessage.tasks || [],
      metadata: uploadMessage.metadata || {},
      isSample: false // Mark as real upload
    };
    
    setUploadHistory(prev => [newUpload, ...prev]);
  };

  const clearHistory = () => {
    if (window.confirm('Are you sure you want to clear all upload history?')) {
      setUploadHistory(defaultHistory); // Reset to default samples
      localStorage.removeItem('uploadHistory');
    }
  };

  const clearAllIncludingSamples = () => {
    if (window.confirm('Are you sure you want to clear ALL history including samples?')) {
      setUploadHistory([]);
      localStorage.removeItem('uploadHistory');
    }
  };

  const toggleExpanded = (fileId) => {
    setExpandedFiles(prev => {
      const newSet = new Set(prev);
      if (newSet.has(fileId)) {
        newSet.delete(fileId);
      } else {
        newSet.add(fileId);
      }
      return newSet;
    });
  };

  const copyFilename = (filename) => {
    navigator.clipboard.writeText(filename);
    toast.success(`Copied "${filename}" to clipboard`);
  };

  const reAnalyzeFile = async (upload) => {
    toast.success(`Re-analyzing "${upload.filename}"...`);
    // Here you could implement re-upload/re-analysis functionality
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTimeAgo = (date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    return `${diffInDays}d ago`;
  };

  const getFileIcon = (type) => {
    if (type.startsWith('image/')) return Image;
    if (type.startsWith('audio/')) return Music;
    if (type.includes('pdf') || type.includes('document')) return File;
    return FileText;
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return CheckCircle;
      case 'processing':
        return Clock;
      case 'error':
        return AlertCircle;
      default:
        return Clock;
    }
  };

  const tips = [
    {
      icon: Image,
      title: 'Image Analysis',
      description: 'Upload charts, diagrams, screenshots, or photos for detailed AI analysis and text extraction. Best results with clear, high-resolution images.',
      examples: ['Meeting whiteboards', 'Data charts', 'Document photos', 'Planning diagrams']
    },
    {
      icon: Music,
      title: 'Audio Transcription',
      description: 'Convert speech to text from meetings, interviews, or voice recordings. AI will extract action items and key insights.',
      examples: ['Meeting recordings', 'Voice memos', 'Interviews', 'Lecture notes']
    },
    {
      icon: File,
      title: 'Document Processing',
      description: 'Extract insights from PDFs, Word documents, and text files. AI analyzes content for tasks and recommendations.',
      examples: ['Project reports', 'Meeting minutes', 'Research papers', 'Planning docs']
    },
    {
      icon: FileText,
      title: 'Smart Analysis',
      description: 'AI automatically detects content type and provides contextual suggestions for task management and productivity.',
      examples: ['Task extraction', 'Priority detection', 'Deadline identification', 'Action planning']
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div 
        className="text-center space-y-4"
        variants={animations.fadeIn}
        initial="initial"
        animate="animate"
      >
        <div className="flex justify-center">
          <motion.div 
            className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl"
            whileHover={{ scale: 1.1, rotate: 5 }}
            transition={{ duration: 0.3 }}
          >
            <UploadIcon className="w-8 h-8 text-white" />
          </motion.div>
        </div>
        <div>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">File Upload & Analysis</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Upload your files for intelligent AI analysis. Support for images, audio, documents, and text files.
          </p>
        </div>
      </motion.div>

      {/* Upload Component */}
      <motion.div
        variants={animations.slideUp}
        initial="initial"
        animate="animate"
      >
        <UploadBox onUploadComplete={handleUploadComplete} />
      </motion.div>

      {/* Tips Section */}
      <motion.div 
        className="space-y-6"
        variants={animations.staggerChildren}
        initial="initial"
        animate="animate"
      >
        <motion.div 
          className="text-center"
          variants={animations.fadeIn}
        >
          <h2 className="text-2xl font-bold text-gray-900 mb-2">What Can You Upload?</h2>
          <p className="text-gray-600">Discover the different types of files our AI can analyze for you.</p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6">
          {tips.map((tip, index) => (
            <motion.div
              key={index}
              className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-lg border border-gray-200/60 hover:shadow-xl transition-all duration-300"
              variants={animations.fadeIn}
              whileHover={{ scale: 1.02, y: -2 }}
            >
              <div className="space-y-4">
                <div className="w-12 h-12 bg-blue-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <tip.icon className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{tip.title}</h3>
                  <p className="text-gray-600 text-sm leading-relaxed mb-3">{tip.description}</p>
                  {tip.examples && (
                    <div className="space-y-2">
                      <p className="text-xs font-medium text-gray-700 uppercase tracking-wide">Examples:</p>
                      <div className="flex flex-wrap gap-1">
                        {tip.examples.map((example, exampleIndex) => (
                          <span
                            key={exampleIndex}
                            className="inline-block px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded-md border border-blue-200/50"
                          >
                            {example}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Upload History */}
      <motion.div 
        className="space-y-6"
        variants={animations.staggerChildren}
        initial="initial"
        animate="animate"
      >
        <motion.div 
          className="flex justify-between items-center"
          variants={animations.fadeIn}
        >
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Upload History</h2>
            <p className="text-gray-600">Your recent file uploads and analysis results.</p>
          </div>
          {uploadHistory.length > 0 && (
            <div className="flex items-center gap-2">
              {uploadHistory.some(item => !item.isSample) && (
                <motion.button
                  onClick={clearHistory}
                  className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-orange-600 hover:text-orange-700 hover:bg-orange-50/80 rounded-xl transition-all duration-200 border border-orange-200/60 backdrop-blur-sm"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  title="Clear your uploads but keep samples"
                >
                  <RefreshCw className="w-4 h-4" />
                  Reset
                </motion.button>
              )}
              <motion.button
                onClick={clearAllIncludingSamples}
                className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50/80 rounded-xl transition-all duration-200 border border-red-200/60 backdrop-blur-sm"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                title="Clear all history including samples"
              >
                <Trash2 className="w-4 h-4" />
                Clear All
              </motion.button>
            </div>
          )}
        </motion.div>

        <AnimatePresence>
          {uploadHistory.length === 0 ? (
            <motion.div 
              className="text-center py-12 bg-white/80 backdrop-blur-md rounded-2xl shadow-lg border border-gray-200/60"
              variants={animations.fadeIn}
              initial="initial"
              animate="animate"
            >
              <div className="w-16 h-16 bg-gray-100/80 backdrop-blur-sm rounded-2xl flex items-center justify-center mx-auto mb-4">
                <UploadIcon className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No uploads yet</h3>
              <p className="text-gray-600">Your upload history will appear here after you upload files.</p>
            </motion.div>
          ) : (
            <motion.div 
              className="space-y-4"
              variants={animations.staggerChildren}
            >
              {uploadHistory.map((upload, index) => {
                const FileIcon = getFileIcon(upload.type);
                const StatusIcon = getStatusIcon(upload.status);
                const isExpanded = expandedFiles.has(upload.id);
                
                return (
                  <motion.div
                    key={upload.id}
                    className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-lg border border-gray-200/60 hover:shadow-xl transition-all duration-300"
                    variants={animations.fadeIn}
                    whileHover={{ scale: 1.01, y: -2 }}
                  >
                    <div className="flex items-start space-x-4">
                      <div className="w-12 h-12 bg-blue-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center flex-shrink-0">
                        <FileIcon className="w-6 h-6 text-blue-600" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <h3 
                                className="text-lg font-semibold text-gray-900 truncate cursor-pointer hover:text-blue-600 transition-colors"
                                onClick={() => copyFilename(upload.filename)}
                                title="Click to copy filename"
                              >
                                {upload.filename}
                              </h3>
                              {upload.isSample && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100/80 text-gray-600 border border-gray-200/60">
                                  Sample
                                </span>
                              )}
                              <motion.button
                                onClick={() => copyFilename(upload.filename)}
                                className="p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50/80 rounded transition-all"
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                title="Copy filename"
                              >
                                <Copy className="w-3 h-3" />
                              </motion.button>
                            </div>
                            <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                              <span>{formatFileSize(upload.size)}</span>
                              <span>{formatTimeAgo(upload.uploadTime)}</span>
                            </div>
                          </div>
                          
                          <div className="flex items-center gap-2">
                            <div className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium backdrop-blur-sm ${
                              upload.status === 'completed' 
                                ? 'bg-green-100/80 text-green-800'
                                : upload.status === 'processing'
                                ? 'bg-yellow-100/80 text-yellow-800'
                                : 'bg-red-100/80 text-red-800'
                            }`}>
                              <StatusIcon className="w-3 h-3" />
                              {upload.status}
                            </div>
                            
                            {upload.analysis && (
                              <motion.button
                                onClick={() => toggleExpanded(upload.id)}
                                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50/80 rounded-lg transition-all"
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                title={isExpanded ? "Collapse details" : "Expand details"}
                              >
                                {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                              </motion.button>
                            )}
                          </div>
                        </div>
                        
                        {/* Action buttons */}
                        <div className="flex items-center gap-2 mb-3">
                          <motion.button
                            onClick={() => reAnalyzeFile(upload)}
                            className="flex items-center gap-1 px-3 py-1 text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50/80 rounded-lg transition-all border border-blue-200/60"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <RefreshCw className="w-3 h-3" />
                            Re-analyze
                          </motion.button>
                        </div>
                        
                        <AnimatePresence>
                          {upload.analysis && isExpanded && (
                            <motion.div 
                              className="bg-gray-50/80 backdrop-blur-sm rounded-xl p-4 mt-3"
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: "auto" }}
                              exit={{ opacity: 0, height: 0 }}
                              transition={{ duration: 0.3 }}
                            >
                              <div className="flex items-start gap-2">
                                <Eye className="w-4 h-4 text-gray-600 mt-0.5 flex-shrink-0" />
                                <div className="flex-1">
                                  <p className="text-sm font-medium text-gray-900 mb-2">AI Analysis</p>
                                  <AIResponseDisplay 
                                    content={upload.analysis}
                                    suggestions={upload.suggestions || []}
                                    tasks={upload.tasks || []}
                                    metadata={upload.metadata || {}}
                                    onNavigate={onNavigate}
                                  />
                                </div>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* File Format Guidelines */}
      <motion.div 
        className="bg-gradient-to-r from-blue-50/80 to-purple-50/80 backdrop-blur-sm rounded-3xl p-8 border border-gray-200/60"
        variants={animations.fadeIn}
        initial="initial"
        animate="animate"
      >
        <div className="text-center space-y-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">File Format Guidelines</h2>
            <p className="text-gray-600">Best practices for optimal AI analysis results.</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                <Image className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Images</h3>
              <p className="text-sm text-gray-600">Clear, high-resolution images work best. Supported: JPG, PNG, GIF, WebP</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                <Music className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Audio</h3>
              <p className="text-sm text-gray-600">Clear speech recordings. Supported: MP3, WAV, OGG, M4A</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                <File className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Documents</h3>
              <p className="text-sm text-gray-600">Text-based documents. Supported: PDF, DOC, DOCX</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-orange-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-3">
                <FileText className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Text Files</h3>
              <p className="text-sm text-gray-600">Plain text data. Supported: TXT, CSV, JSON, XML</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Upload; 