import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, Trash2, CheckCircle, Clock, AlertCircle, ClipboardList, Tag, AlertTriangle, Circle, Loader, Zap, Edit3, Save, X } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { animations } from '../styles/design-system';

const SavedTasks = ({ className = "" }) => {
  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingTask, setEditingTask] = useState(null);
  const { isAuthenticated, loading: authLoading, initialized } = useAuth();

  const fetchTasks = async () => {
    console.log('fetchTasks called');
    setIsLoading(true);
    setError(null);
    
    try {
      console.log('Making fetch request to:', 'http://localhost:8000/api/v1/tasks');
      
      const response = await fetch('http://localhost:8000/api/v1/tasks', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      console.log('Response received:', response.status, response.statusText);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Data received:', data);
      
      setTasks(data.tasks || []);
      if (!isLoading) { // Only show success toast on manual reload
        toast.success(`Loaded ${data.tasks?.length || 0} tasks`);
      }
    } catch (error) {
      console.error('Fetch error:', error);
      const errorMessage = `Failed to load tasks: ${error.message}`;
      setError(errorMessage);
      setTasks([]);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      // Remove task from local state
      setTasks(prevTasks => prevTasks.filter(task => task.id !== taskId));
      toast.success('Task deleted successfully');
    } catch (error) {
      console.error('Failed to delete task:', error);
      const errorMessage = error.message || 'Failed to delete task';
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
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: newStatus
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
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
      const errorMessage = error.message || 'Failed to update task status';
      toast.error(errorMessage);
    }
  };

  const updateTask = async (taskId, updates) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const updatedTask = await response.json();
      
      // Update task in local state
      setTasks(prevTasks => 
        prevTasks.map(task => 
          task.id === taskId 
            ? { ...task, ...updates }
            : task
        )
      );
      
      setEditingTask(null);
      toast.success('Task updated successfully');
    } catch (error) {
      console.error('Failed to update task:', error);
      const errorMessage = error.message || 'Failed to update task';
      toast.error(errorMessage);
    }
  };

  const clearAllTasks = async () => {
    if (!window.confirm('Are you sure you want to clear all saved tasks? This action cannot be undone.')) {
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/v1/tasks', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      setTasks([]);
      toast.success('All tasks cleared successfully');
    } catch (error) {
      console.error('Failed to clear tasks:', error);
      const errorMessage = error.message || 'Failed to clear tasks';
      toast.error(errorMessage);
    }
  };

  useEffect(() => {
    if (initialized) {
      console.log('Component initialized, fetching tasks...');
      fetchTasks();
    }
  }, [initialized]);

  // Show loading state while auth is initializing
  if (authLoading || !initialized) {
    return (
      <div className={`flex flex-col h-full ${className}`}>
        <div className="flex items-center justify-center flex-1">
          <div className="flex flex-col items-center space-y-4">
            <Loader className="w-8 h-8 text-blue-600 animate-spin" />
            <p className="text-gray-600">Initializing...</p>
          </div>
        </div>
      </div>
    );
  }

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
    const isEditing = editingTask === task.id;
    const [editForm, setEditForm] = useState({
      summary: task.summary || '',
      description: task.description || '',
      priority: task.priority || 'medium',
      category: task.category || 'general'
    });

    const handleEdit = () => {
      setEditingTask(task.id);
      setEditForm({
        summary: task.summary || '',
        description: task.description || '',
        priority: task.priority || 'medium',
        category: task.category || 'general'
      });
    };

    const handleSave = () => {
      if (!editForm.summary.trim()) {
        toast.error('Task summary is required');
        return;
      }
      updateTask(task.id, editForm);
    };

    const handleCancel = () => {
      setEditingTask(null);
      setEditForm({
        summary: task.summary || '',
        description: task.description || '',
        priority: task.priority || 'medium',
        category: task.category || 'general'
      });
    };

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
                {task.created_at ? new Date(task.created_at).toLocaleString() : 'Unknown date'}
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
            
            {!isEditing ? (
              <motion.button
                onClick={handleEdit}
                className="p-2 text-blue-500 hover:text-blue-700 hover:bg-blue-50/80 rounded-lg transition-all duration-200"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                title="Edit task"
              >
                <Edit3 className="w-4 h-4" />
              </motion.button>
            ) : (
              <div className="flex space-x-1">
                <motion.button
                  onClick={handleSave}
                  className="p-2 text-green-500 hover:text-green-700 hover:bg-green-50/80 rounded-lg transition-all duration-200"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="Save changes"
                >
                  <Save className="w-4 h-4" />
                </motion.button>
                <motion.button
                  onClick={handleCancel}
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-50/80 rounded-lg transition-all duration-200"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  title="Cancel editing"
                >
                  <X className="w-4 h-4" />
                </motion.button>
              </div>
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

        <div className="space-y-3">
          {isEditing ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Task Summary
                </label>
                <input
                  type="text"
                  value={editForm.summary}
                  onChange={(e) => setEditForm({...editForm, summary: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Task summary..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={editForm.description}
                  onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows="3"
                  placeholder="Task description..."
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={editForm.priority}
                    onChange={(e) => setEditForm({...editForm, priority: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <input
                    type="text"
                    value={editForm.category}
                    onChange={(e) => setEditForm({...editForm, category: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Category..."
                  />
                </div>
              </div>
            </div>
          ) : (
            <>
              <div>
                <p className="text-gray-800 font-medium leading-relaxed">
                  {task.summary || task.title || 'No description available'}
                </p>
              </div>

              {task.description && (
                <div>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {task.description}
                  </p>
                </div>
              )}

              <div className="flex flex-wrap gap-2 pt-2">
                {task.category && (
                  <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100/80 text-blue-800 text-xs rounded-full backdrop-blur-sm">
                    <Tag className="w-3 h-3" />
                    {task.category}
                  </span>
                )}
                
                {task.priority && (
                  <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs rounded-full backdrop-blur-sm ${
                    task.priority === 'high' 
                      ? 'bg-red-100/80 text-red-800'
                      : task.priority === 'medium'
                      ? 'bg-yellow-100/80 text-yellow-800'
                      : 'bg-green-100/80 text-green-800'
                  }`}>
                    <PriorityIcon className="w-3 h-3" />
                    {task.priority} priority
                  </span>
                )}

                {task.tags && task.tags.length > 0 && (
                  task.tags.map((tag, tagIndex) => (
                    <span key={tagIndex} className="px-2 py-1 bg-gray-100/80 text-gray-700 text-xs rounded-full backdrop-blur-sm">
                      {tag}
                    </span>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      </motion.div>
    );
  };

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header */}
      <motion.div 
        className="bg-white/80 backdrop-blur-md rounded-2xl shadow-sm border border-gray-200/60 p-8 mb-6"
        variants={animations.slideUp}
        initial="initial"
        animate="animate"
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Saved Tasks</h2>
            <p className="text-gray-600">Track and manage your task history</p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center">
              <ClipboardList className="w-6 h-6 text-blue-600" />
            </div>
            <div className="flex space-x-2">
              <motion.button
                onClick={fetchTasks}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 backdrop-blur-sm"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                Reload
              </motion.button>
              
              {tasks.length > 0 && (
                <motion.button
                  onClick={clearAllTasks}
                  className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700 transition-all duration-200 backdrop-blur-sm"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Trash2 className="w-4 h-4" />
                  Clear All
                </motion.button>
              )}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center space-y-4">
              <Loader className="w-8 h-8 text-blue-600 animate-spin" />
              <p className="text-gray-600">Loading tasks...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Failed to load tasks</h3>
              <p className="text-gray-600 mb-4">{error}</p>
              <motion.button
                onClick={fetchTasks}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Try Again
              </motion.button>
            </div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ClipboardList className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No tasks yet</h3>
              <p className="text-gray-600 mb-4">
                Start creating tasks through the chat or upload features to see them here.
              </p>
              <div className="flex items-center justify-center space-x-2">
                <Zap className="w-4 h-4 text-blue-600" />
                <span className="text-sm text-blue-600 font-medium">AI-powered task extraction</span>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-full overflow-y-auto pr-2">
            <motion.div 
              className="grid gap-6 pb-6"
              variants={animations.staggerChildren}
              initial="initial"
              animate="animate"
            >
              <AnimatePresence mode="popLayout">
                {tasks.map((task, index) => (
                  <TaskCard key={task.id || index} task={task} index={index} />
                ))}
              </AnimatePresence>
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SavedTasks; 