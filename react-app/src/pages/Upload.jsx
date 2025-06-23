import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload as UploadIcon, FileText, Image, Music, File, CheckCircle, Clock, AlertCircle, Trash2, Eye } from 'lucide-react';
import UploadBox from '../components/UploadBox';
import { animations } from '../styles/design-system';

const Upload = () => {
  const [uploadHistory, setUploadHistory] = useState([
    {
      id: 1,
      filename: 'project-presentation.pdf',
      size: 2.4 * 1024 * 1024,
      type: 'application/pdf',
      uploadTime: new Date(Date.now() - 2 * 60 * 60 * 1000),
      status: 'completed',
      analysis: 'Document contains 15 slides about AI project roadmap with timeline and budget analysis.'
    },
    {
      id: 2,
      filename: 'meeting-audio.mp3',
      size: 8.7 * 1024 * 1024,
      type: 'audio/mp3',
      uploadTime: new Date(Date.now() - 5 * 60 * 60 * 1000),
      status: 'completed',
      analysis: 'Transcribed 45-minute meeting discussing Q4 objectives and team assignments.'
    },
    {
      id: 3,
      filename: 'data-chart.png',
      size: 1.2 * 1024 * 1024,
      type: 'image/png',
      uploadTime: new Date(Date.now() - 24 * 60 * 60 * 1000),
      status: 'processing',
      analysis: null
    }
  ]);

  const handleUploadComplete = (uploadMessage, file) => {
    const newUpload = {
      id: Date.now(),
      filename: file.name,
      size: file.size,
      type: file.type,
      uploadTime: new Date(),
      status: 'completed',
      analysis: uploadMessage.message
    };
    
    setUploadHistory(prev => [newUpload, ...prev]);
  };

  const clearHistory = () => {
    if (window.confirm('Are you sure you want to clear all upload history?')) {
      setUploadHistory([]);
    }
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
      description: 'Upload charts, diagrams, or photos for detailed AI analysis and text extraction.'
    },
    {
      icon: Music,
      title: 'Audio Transcription',
      description: 'Convert speech to text from meetings, interviews, or voice recordings.'
    },
    {
      icon: File,
      title: 'Document Processing',
      description: 'Extract insights from PDFs, Word documents, and text files.'
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

        <div className="grid md:grid-cols-3 gap-6">
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
                  <p className="text-gray-600 text-sm leading-relaxed">{tip.description}</p>
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
            <motion.button
              onClick={clearHistory}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50/80 rounded-xl transition-all duration-200 border border-red-200/60 backdrop-blur-sm"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Trash2 className="w-4 h-4" />
              Clear History
            </motion.button>
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
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 truncate">{upload.filename}</h3>
                            <div className="flex items-center space-x-4 text-sm text-gray-500">
                              <span>{formatFileSize(upload.size)}</span>
                              <span>{formatTimeAgo(upload.uploadTime)}</span>
                            </div>
                          </div>
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
                        </div>
                        
                        {upload.analysis && (
                          <div className="bg-gray-50/80 backdrop-blur-sm rounded-xl p-4 mt-3">
                            <div className="flex items-start gap-2">
                              <Eye className="w-4 h-4 text-gray-600 mt-0.5 flex-shrink-0" />
                              <div>
                                <p className="text-sm font-medium text-gray-900 mb-1">AI Analysis</p>
                                <p className="text-sm text-gray-700 leading-relaxed">{upload.analysis}</p>
                              </div>
                            </div>
                          </div>
                        )}
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