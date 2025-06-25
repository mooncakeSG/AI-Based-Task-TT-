import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, CheckCircle, X, Plus, FileText, Image, Music, File, Loader } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { animations } from '../styles/design-system';
import { api } from '../lib/api';

const UploadBox = ({ onUploadComplete, className = "" }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const acceptedTypes = {
    'image/*': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
    'audio/*': ['mp3', 'wav', 'ogg', 'm4a'],
    'text/*': ['txt', 'csv', 'json', 'xml'],
    'application/pdf': ['pdf'],
    'application/msword': ['doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['docx']
  };

  const maxFileSize = 5 * 1024 * 1024; // 5MB (recommended for audio)

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateFile = (file) => {
    if (!file) return 'No file selected';
    
    if (file.size > maxFileSize) {
      return `File size must be less than ${formatFileSize(maxFileSize)}`;
    }

    // Check file type
    const fileType = file.type;
    const fileName = file.name.toLowerCase();
    const fileExtension = fileName.split('.').pop();
    
    const isValidType = Object.entries(acceptedTypes).some(([mimeType, extensions]) => {
      return fileType.startsWith(mimeType.replace('/*', '')) || 
             extensions.includes(fileExtension);
    });

    if (!isValidType) {
      return 'File type not supported. Please upload images, audio, text, or document files.';
    }

    return null;
  };

  const handleFileSelect = (selectedFile) => {
    const error = validateFile(selectedFile);
    if (error) {
      toast.error(error);
      return;
    }

    setFile(selectedFile);
    setUploadProgress(0);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const uploadFile = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'}/upload/file`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setUploadProgress(percentCompleted);
        },
        timeout: 120000, // 120 second timeout for AI processing
      });

      console.log('📁 File processing result:', response.data);
      
      // Extract structured data from response
      const processingDetails = response.data.processing_details || {};
      const fileAnalysis = processingDetails.file_analysis || {};
      const suggestions = fileAnalysis.suggestions || [];
      const tasks = fileAnalysis.tasks || [];
      const metadata = fileAnalysis.metadata || {};
      
      const uploadMessage = {
        id: Date.now(),
        message: response.data.response || `File "${file.name}" analyzed successfully!`,
        filename: file.name,
        size: file.size,
        timestamp: new Date(),
        success: true,
        analysis: response.data.response,
        processingDetails: response.data.processing_details,
        suggestions: suggestions,
        tasks: tasks,
        metadata: {
          ...metadata,
          fileType: file.type,
          processingTime: processingDetails.processing_time,
          analysisEnhanced: true
        }
      };

      if (onUploadComplete) {
        onUploadComplete(uploadMessage, file);
      }

      // File-type specific success message
      let successMessage = `File uploaded successfully!`;
      if (file.type.startsWith('image/')) {
        successMessage = `Image analyzed! Check the insights below for visual content and task recommendations.`;
      } else if (file.type.startsWith('audio/')) {
        successMessage = `Audio transcribed! Review the extracted text and action items below.`;
      } else if (file.type.includes('pdf') || file.type.includes('document')) {
        successMessage = `Document processed! See the content analysis and productivity suggestions below.`;
      }

      toast.success(successMessage);
      
      // Reset state
      setFile(null);
      setUploadProgress(0);

    } catch (error) {
      console.error('Upload failed:', error);
      
      let errorMessage = 'Upload failed. Please try again.';
      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Processing timed out. Large images may take longer to analyze.';
      }

      toast.error(errorMessage);
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setUploadProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <motion.div 
      className={`bg-white/80 backdrop-blur-md rounded-2xl shadow-lg border border-gray-200/60 overflow-hidden ${className}`}
      variants={animations.fadeIn}
      initial="initial"
      animate="animate"
    >
      {/* Header */}
      <div className="p-6 border-b border-gray-200/60 bg-gradient-to-r from-blue-50/80 to-purple-50/80 backdrop-blur-sm">
        <div className="flex items-center space-x-3">
          <motion.div 
            className="w-10 h-10 bg-blue-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center"
            whileHover={{ scale: 1.1, rotate: 5 }}
            transition={{ duration: 0.2 }}
          >
            <Upload className="w-5 h-5 text-blue-600" />
          </motion.div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">File Upload</h3>
            <p className="text-sm text-gray-600">Upload files for AI analysis</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Upload Area */}
        <motion.div
          className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-200 backdrop-blur-sm ${
            isDragOver
              ? 'border-blue-500 bg-blue-50/80'
              : file
                ? 'border-green-500 bg-green-50/80'
                : 'border-gray-300/60 bg-gray-50/40 hover:bg-gray-50/60'
          }`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          whileHover={{ scale: 1.01 }}
          transition={{ duration: 0.2 }}
        >
          <input
            ref={fileInputRef}
            type="file"
            onChange={(e) => handleFileSelect(e.target.files[0])}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            accept="image/*,audio/*,text/*,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          />

          <AnimatePresence>
            {!file ? (
              <motion.div
                variants={animations.fadeIn}
                initial="initial"
                animate="animate"
                exit="exit"
              >
                <motion.div 
                  className="w-16 h-16 mx-auto mb-4 bg-blue-100/80 backdrop-blur-sm rounded-2xl flex items-center justify-center"
                  animate={{ y: [0, -4, 0] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                >
                  <Upload className="w-8 h-8 text-blue-600" />
                </motion.div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">
                  {isDragOver ? 'Drop your file here' : 'Choose a file or drag it here'}
                </h4>
                <p className="text-gray-600 mb-4">
                  Support for images, audio, documents and text files
                </p>
                <div className="mb-4 text-xs text-gray-500 space-y-1">
                  <p>✨ <strong>Images:</strong> Get visual analysis, text extraction, and task insights</p>
                  <p>🎵 <strong>Audio:</strong> Transcription with automatic action item detection</p>
                  <p>📄 <strong>Documents:</strong> Content analysis and productivity recommendations</p>
                </div>
                <motion.button
                  type="button"
                  className="inline-flex items-center px-6 py-3 border border-blue-300/60 rounded-xl text-sm font-medium text-blue-700 bg-blue-50/80 hover:bg-blue-100/80 transition-all duration-200 backdrop-blur-sm"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Browse Files
                </motion.button>
              </motion.div>
            ) : (
              <motion.div
                variants={animations.fadeIn}
                initial="initial"
                animate="animate"
                exit="exit"
                className="space-y-4"
              >
                <motion.div 
                  className="w-16 h-16 mx-auto bg-green-100/80 backdrop-blur-sm rounded-2xl flex items-center justify-center"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", duration: 0.5 }}
                >
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </motion.div>
                <div>
                  <h4 className="text-lg font-semibold text-gray-900">{file.name}</h4>
                  <p className="text-gray-600">{formatFileSize(file.size)}</p>
                </div>
                <motion.button
                  onClick={removeFile}
                  className="text-red-600 hover:text-red-700 text-sm font-medium"
                  whileHover={{ scale: 1.05 }}
                >
                  Remove file
                </motion.button>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>

        {/* Upload Progress */}
        <AnimatePresence>
          {isUploading && (
            <motion.div
              variants={animations.slideUp}
              initial="initial"
              animate="animate"
              exit="exit"
              className="space-y-3"
            >
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium text-gray-700">
                  {uploadProgress === 100 ? 'Processing with AI...' : 'Uploading...'}
                </span>
                <span className="text-sm text-gray-500">
                  {uploadProgress === 100 ? 'Please wait' : `${uploadProgress}%`}
                </span>
              </div>
              <div className="w-full bg-gray-200/60 rounded-full h-2 backdrop-blur-sm">
                <motion.div
                  className="bg-blue-600 h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadProgress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Upload Button */}
        <div className="flex space-x-4">
          <motion.button
            onClick={uploadFile}
            disabled={!file || isUploading}
            className="flex-1 flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-2xl font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl backdrop-blur-sm"
            whileHover={{ scale: !file || isUploading ? 1 : 1.02, y: !file || isUploading ? 0 : -1 }}
            whileTap={{ scale: !file || isUploading ? 1 : 0.98 }}
          >
            {isUploading ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                <span>{uploadProgress === 100 ? 'AI Processing...' : 'Uploading...'}</span>
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                <span>Upload & Analyze</span>
              </>
            )}
          </motion.button>
        </div>

        {/* File Format Info */}
        <motion.div 
          className="bg-blue-50/60 backdrop-blur-sm border border-blue-200/60 rounded-xl p-4"
          variants={animations.fadeIn}
          initial="initial"
          animate="animate"
        >
          <h4 className="text-sm font-semibold text-blue-900 mb-2">Supported Formats</h4>
          <div className="grid grid-cols-2 gap-3 text-xs text-blue-800">
            <div className="flex items-center gap-2">
              <Image className="w-3 h-3" />
              <div>
                <span className="font-medium">Images:</span>
                <p>JPG, PNG, GIF, WebP</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Music className="w-3 h-3" />
              <div>
                <span className="font-medium">Audio:</span>
                <p>MP3, WAV, OGG, M4A</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <File className="w-3 h-3" />
              <div>
                <span className="font-medium">Documents:</span>
                <p>PDF, DOC, DOCX</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="w-3 h-3" />
              <div>
                <span className="font-medium">Text:</span>
                <p>TXT, CSV, JSON, XML</p>
              </div>
            </div>
          </div>
          <p className="text-xs text-blue-700 mt-3">
            Maximum file size: {formatFileSize(maxFileSize)}
          </p>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default UploadBox; 