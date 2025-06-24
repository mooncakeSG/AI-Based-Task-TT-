import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, Trash2, CheckCircle, Clock, AlertCircle, ClipboardList, Tag, AlertTriangle, Circle, Loader, Zap } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { animations } from '../styles/design-system';

const SavedTasks = ({ className = "" }) => {
  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTasks = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('http://localhost:8000/api/v1/tasks', {
        timeout: 10000,
      });
      
      setTasks(response.data.tasks || []);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to load tasks';
      setError(errorMessage);
      toast.error(errorMessage);
      setTasks([]); // Set empty array on error
    } finally {
      setIsLoading(false);
    }
  };

  const clearTasks = async () => {
    if (!window.confirm('Are you sure you want to clear all saved tasks? This action cannot be undone.')) {
      return;
    }

    try {
      await axios.delete('http://localhost:8000/api/v1/tasks', {
        timeout: 10000,
      });
      
      setTasks([]);
      toast.success('All tasks cleared successfully');
    } catch (error) {
      console.error('Failed to clear tasks:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to clear tasks';
      toast.error(errorMessage);
    }
  };

  const deleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await axios.delete(`http://localhost:8000/api/v1/tasks/${taskId}`, {
        timeout: 10000,
      });
      
      // Remove task from local state
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
      toast.success('Task deleted successfully');
    } catch (error) {
      console.error('Failed to delete task:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to delete task';
      toast.error(errorMessage);
    }
  };

  const toggleTaskStatus = async (taskId, currentStatus) => {
    // Define status cycle: pending -> in_progress -> completed -> pending
    const statusCycle = {
      'pending': 'in_progress',
      'in_progress': 'completed', 
      'completed': 'pending'
    };
    
    const newStatus = statusCycle[currentStatus] || 'pending';
    
    try {
      await axios.put(`http://localhost:8000/api/v1/tasks/${taskId}`, {
        status: newStatus
      }, {
        timeout: 10000,
      });
      
      // Update task in local state
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId 
            ? { ...task, status: newStatus }
            : task
        )
      );
      
      toast.success(`Task status updated to ${newStatus.replace('_', ' ')}`);
    } catch (error) {
      console.error('Failed to update task status:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to update task status';
      toast.error(errorMessage);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Unknown date';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return CheckCircle;
      case 'in_progress':
        return Clock;
      case 'pending':
        return Circle;
      default:
        return Circle;
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high':
        return AlertTriangle;
      case 'medium':
        return AlertCircle;
      case 'low':
        return Circle;
      default:
        return Circle;
    }
  };

  const TaskCard = ({ task, index }) => {
    const StatusIcon = getStatusIcon(task.status);
    const PriorityIcon = getPriorityIcon(task.priority);

    return (
      <motion.div 
        className="bg-white/80 backdrop-blur-md rounded-2xl shadow-sm border border-gray-200/60 p-6 hover:shadow-lg hover:bg-white/90 transition-all duration-200"
        variants={animations.fadeIn}
        initial="initial"
        animate="animate"
        transition={{ delay: index * 0.1 }}
        whileHover={{ scale: 1.01, y: -2 }}
      >
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center">
              <ClipboardList className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 text-lg">
                Task #{index + 1}
              </h3>
              <span className="text-sm text-gray-500">
                {formatDate(task.created_at || task.timestamp)}
              </span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {task.status && (
              <motion.button
                onClick={() => toggleTaskStatus(task.id, task.status)}
                className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium backdrop-blur-sm cursor-pointer hover:shadow-md transition-all duration-200 ${
                  task.status === 'completed' 
                    ? 'bg-green-100/80 text-green-800 hover:bg-green-200/80'
                    : task.status === 'in_progress'
                    ? 'bg-yellow-100/80 text-yellow-800 hover:bg-yellow-200/80'
                    : 'bg-gray-100/80 text-gray-800 hover:bg-gray-200/80'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                title="Click to change status"
              >
                <StatusIcon className="w-3 h-3" />
                {task.status.replace('_', ' ')}
              </motion.button>
            )}
            
            <motion.button
              onClick={() => deleteTask(task.id)}
              className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50/80 rounded-lg transition-all duration-200"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              title="Delete task"
            >
              <Trash2 className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
        
        <div className="space-y-4">
          {task.summary && (
            <div>
              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Summary</span>
              <p className="text-gray-700 mt-2 leading-relaxed">{task.summary}</p>
            </div>
          )}

          {task.category && (
            <div>
              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Category</span>
              <div className="mt-2">
                <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-blue-100/80 backdrop-blur-sm text-blue-800">
                  <Tag className="w-3 h-3" />
                  {task.category}
                </span>
              </div>
            </div>
          )}

          {task.priority && (
            <div>
              <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Priority</span>
              <div className="mt-2">
                <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium backdrop-blur-sm ${
                  task.priority === 'high' 
                    ? 'bg-red-100/80 text-red-800'
                    : task.priority === 'medium'
                    ? 'bg-orange-100/80 text-orange-800'
                    : 'bg-green-100/80 text-green-800'
                }`}>
                  <PriorityIcon className="w-3 h-3" />
                  {task.priority} priority
                </span>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    );
  };

  return (
    <div className={`h-full flex flex-col bg-white/80 backdrop-blur-md rounded-2xl shadow-lg border border-gray-200/60 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="flex-shrink-0 p-6 border-b border-gray-200/60 bg-gradient-to-r from-blue-50/80 to-purple-50/80 backdrop-blur-sm">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Saved Tasks</h2>
            <p className="text-gray-600 mt-1">Track and manage your task history</p>
          </div>
          <div className="flex space-x-3">
            <motion.button
              onClick={fetchTasks}
              disabled={isLoading}
              className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50/80 rounded-xl transition-all duration-200 disabled:opacity-50 border border-blue-200/60 backdrop-blur-sm"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              <span>{isLoading ? 'Loading...' : 'Reload'}</span>
            </motion.button>
            {tasks.length > 0 && (
              <motion.button
                onClick={clearTasks}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50/80 rounded-xl transition-all duration-200 border border-red-200/60 backdrop-blur-sm"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Trash2 className="w-4 h-4" />
                <span>Clear All</span>
              </motion.button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <AnimatePresence>
          {isLoading ? (
            <motion.div 
              className="flex flex-col items-center justify-center h-64 space-y-4"
              variants={animations.fadeIn}
              initial="initial"
              animate="animate"
            >
              <Loader className="w-12 h-12 text-blue-500 animate-spin" />
              <p className="text-gray-600 font-medium">Loading tasks...</p>
            </motion.div>
          ) : error ? (
            <motion.div 
              className="flex flex-col items-center justify-center h-64 space-y-6"
              variants={animations.fadeIn}
              initial="initial"
              animate="animate"
            >
              <div className="w-16 h-16 bg-red-100/80 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                <AlertCircle className="w-8 h-8 text-red-500" />
              </div>
              <div className="text-center">
                <p className="text-gray-600 mb-4 font-medium">Failed to load tasks</p>
                <motion.button
                  onClick={fetchTasks}
                  className="px-6 py-3 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50/80 rounded-xl transition-all duration-200 border border-blue-200/60 backdrop-blur-sm"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Try Again
                </motion.button>
              </div>
            </motion.div>
          ) : tasks.length === 0 ? (
            <motion.div 
              className="flex flex-col items-center justify-center h-64 space-y-6"
              variants={animations.fadeIn}
              initial="initial"
              animate="animate"
            >
              <div className="w-16 h-16 bg-gray-100/80 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                <ClipboardList className="w-8 h-8 text-gray-400" />
              </div>
              <div className="text-center">
                <p className="text-gray-600 mb-2 font-medium">No saved tasks yet</p>
                <p className="text-gray-500 text-sm">Start chatting to create and save tasks!</p>
              </div>
            </motion.div>
          ) : (
            <motion.div 
              className="space-y-6"
              variants={animations.staggerChildren}
              initial="initial"
              animate="animate"
            >
              <motion.div 
                className="flex items-center justify-between mb-6"
                variants={animations.fadeIn}
              >
                <p className="text-gray-600 font-medium">
                  {tasks.length} task{tasks.length !== 1 ? 's' : ''} saved
                </p>
                <div className="flex items-center space-x-2 text-sm text-gray-500">
                  <Zap className="w-4 h-4 text-green-500" />
                  <span>Auto-saved</span>
                </div>
              </motion.div>
              
              <div className="grid gap-6">
                {tasks.map((task, index) => (
                  <TaskCard key={task.id || index} task={task} index={index} />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default SavedTasks; 