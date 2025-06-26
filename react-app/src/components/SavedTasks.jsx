import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Star, 
  Trash2, 
  Plus, 
  Filter,
  Loader,
  Database,
  RefreshCw,
  CheckSquare,
  Square
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { api } from '../lib/api';
import { animations } from '../styles/design-system';

const SavedTasks = ({ className = "" }) => {
  const [tasks, setTasks] = useState([]);
  const [filteredTasks, setFilteredTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [selectedTasks, setSelectedTasks] = useState(new Set());
  const [isMultiSelect, setIsMultiSelect] = useState(false);
  const [dbInfo, setDbInfo] = useState(null);

  // Load tasks on component mount
  useEffect(() => {
    loadTasks();
  }, []);

  // Filter tasks when filter or tasks change
  useEffect(() => {
    filterTasks();
  }, [tasks, filter, sortBy]);

  const loadTasks = async () => {
    setLoading(true);
    try {
      console.log('🔄 Loading tasks from backend...');
      const response = await api.getTasks();
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      console.log('📋 Tasks loaded:', result);
      
      setTasks(result.tasks || []);
      setDbInfo({
        source: result.source || 'unknown',
        count: result.count || 0,
        status: result.status || 'unknown'
      });
      
      toast.success(`Loaded ${result.count || 0} tasks from ${result.source || 'database'}`);
      
    } catch (error) {
      console.error('❌ Error loading tasks:', error);
      toast.error('Failed to load tasks: ' + error.message);
      setTasks([]);
    } finally {
      setLoading(false);
    }
  };

  const filterTasks = () => {
    let filtered = [...tasks];
    
    // Apply status filter
    if (filter !== 'all') {
      filtered = filtered.filter(task => task.status === filter);
    }
    
    // Sort tasks
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'priority':
          const priorityOrder = { 'urgent': 4, 'high': 3, 'medium': 2, 'low': 1 };
          return (priorityOrder[b.priority] || 2) - (priorityOrder[a.priority] || 2);
        case 'created_at':
          return new Date(b.created_at || 0) - new Date(a.created_at || 0);
        case 'title':
          return (a.title || a.summary || '').localeCompare(b.title || b.summary || '');
        default:
          return 0;
      }
    });
    
    setFilteredTasks(filtered);
  };

  const createTask = async () => {
    const title = prompt('Enter task title:');
    if (!title) return;
    
    const taskData = {
      title: title.trim(),
      description: 'Manually created task',
      category: 'general',
      priority: 'medium',
      status: 'pending'
    };
    
    try {
      console.log('➕ Creating new task:', taskData);
      const response = await api.createTask(taskData);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }
      
      const result = await response.json();
      console.log('✅ Task created:', result);
      
      toast.success('Task created successfully!');
      await loadTasks(); // Reload tasks
      
    } catch (error) {
      console.error('❌ Error creating task:', error);
      toast.error('Failed to create task: ' + error.message);
    }
  };

  const updateTaskStatus = async (taskId, newStatus) => {
    try {
      console.log(`🔄 Updating task ${taskId} status to ${newStatus}`);
      const response = await api.updateTask(taskId, { status: newStatus });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }
      
      const result = await response.json();
      console.log('✅ Task updated:', result);
      
      // Update local state
      setTasks(prev => prev.map(task => 
        task.id === taskId ? { ...task, status: newStatus } : task
      ));
      
      toast.success(`Task ${newStatus === 'completed' ? 'completed' : 'updated'}!`);
      
    } catch (error) {
      console.error('❌ Error updating task:', error);
      toast.error('Failed to update task: ' + error.message);
    }
  };

  const deleteTask = async (taskId) => {
    if (!confirm('Are you sure you want to delete this task?')) return;
    
    try {
      console.log(`🗑️ Deleting task ${taskId}`);
      const response = await api.deleteTask(taskId);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }
      
      console.log('✅ Task deleted');
      
      // Update local state
      setTasks(prev => prev.filter(task => task.id !== taskId));
      setSelectedTasks(prev => {
        const newSet = new Set(prev);
        newSet.delete(taskId);
        return newSet;
      });
      
      toast.success('Task deleted successfully!');
      
    } catch (error) {
      console.error('❌ Error deleting task:', error);
      toast.error('Failed to delete task: ' + error.message);
    }
  };

  const clearAllTasks = async () => {
    if (!confirm('Are you sure you want to delete ALL tasks? This cannot be undone.')) return;
    
    try {
      console.log('🗑️ Clearing all tasks');
      const response = await api.clearAllTasks();
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }
      
      const result = await response.json();
      console.log('✅ All tasks cleared:', result);
      
      setTasks([]);
      setSelectedTasks(new Set());
      
      toast.success(`Cleared ${result.deleted_count || 0} tasks successfully!`);
      
    } catch (error) {
      console.error('❌ Error clearing tasks:', error);
      toast.error('Failed to clear tasks: ' + error.message);
    }
  };

  const toggleTaskSelection = (taskId) => {
    setSelectedTasks(prev => {
      const newSet = new Set(prev);
      if (newSet.has(taskId)) {
        newSet.delete(taskId);
      } else {
        newSet.add(taskId);
      }
      return newSet;
    });
  };

  const bulkUpdateTasks = async (status) => {
    if (selectedTasks.size === 0) return;
    
    try {
      const promises = Array.from(selectedTasks).map(taskId => 
        updateTaskStatus(taskId, status)
      );
      
      await Promise.all(promises);
      setSelectedTasks(new Set());
      setIsMultiSelect(false);
      
      toast.success(`Updated ${selectedTasks.size} tasks!`);
      
    } catch (error) {
      console.error('❌ Error in bulk update:', error);
      toast.error('Failed to update some tasks');
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'in_progress': return <Clock className="w-4 h-4 text-blue-500" />;
      case 'pending': return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      default: return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'No date';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Invalid date';
    }
  };

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-full bg-white/80 backdrop-blur-md rounded-2xl shadow-lg border border-gray-200/60 ${className}`}>
        <div className="text-center space-y-4">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
          <p className="text-gray-600">Loading tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full bg-white/80 backdrop-blur-md rounded-2xl shadow-lg border border-gray-200/60 overflow-hidden ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200/60 bg-gradient-to-r from-blue-50/80 to-purple-50/80">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Saved Tasks</h2>
              {dbInfo && (
                <p className="text-sm text-gray-600 flex items-center space-x-2">
                  <Database className="w-3 h-3" />
                  <span>{dbInfo.count} tasks from {dbInfo.source}</span>
                </p>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={loadTasks}
              className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              title="Refresh tasks"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              onClick={createTask}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden sm:inline">Add Task</span>
            </button>
          </div>
        </div>

        {/* Filters and Controls */}
        <div className="flex flex-wrap items-center justify-between mt-4 gap-3">
          <div className="flex items-center space-x-3">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 bg-white/90 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Tasks</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 bg-white/90 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="created_at">Sort by Date</option>
              <option value="priority">Sort by Priority</option>
              <option value="title">Sort by Title</option>
            </select>
          </div>

          {tasks.length > 0 && (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsMultiSelect(!isMultiSelect)}
                className={`px-3 py-2 text-sm rounded-lg transition-colors ${
                  isMultiSelect 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-white/90 text-gray-700 border border-gray-200'
                }`}
              >
                {isMultiSelect ? 'Cancel' : 'Select'}
              </button>
              
              {isMultiSelect && selectedTasks.size > 0 && (
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => bulkUpdateTasks('completed')}
                    className="px-3 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
                  >
                    Complete ({selectedTasks.size})
                  </button>
                </div>
              )}
              
              <button
                onClick={clearAllTasks}
                className="px-3 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors"
              >
                Clear All
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Tasks List */}
      <div className="flex-1 overflow-y-auto p-6">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-12">
            <CheckCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {filter === 'all' ? 'No tasks yet' : `No ${filter} tasks`}
            </h3>
            <p className="text-gray-600 mb-6">
              {filter === 'all' 
                ? 'Start by chatting with the AI or creating a task manually'
                : `Try switching to "All Tasks" to see other tasks`
              }
            </p>
            {filter === 'all' && (
              <button
                onClick={createTask}
                className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>Create Your First Task</span>
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <AnimatePresence>
              {filteredTasks.map((task) => (
                <motion.div
                  key={task.id}
                  className={`bg-white/90 backdrop-blur-sm rounded-xl p-4 shadow-sm border transition-all duration-200 ${
                    selectedTasks.has(task.id) 
                      ? 'border-blue-300 ring-2 ring-blue-100' 
                      : 'border-gray-200/60 hover:border-gray-300/60'
                  }`}
                  variants={animations.fadeIn}
                  initial="initial"
                  animate="animate"
                  exit="exit"
                  layout
                >
                  <div className="flex items-start space-x-4">
                    {isMultiSelect && (
                      <button
                        onClick={() => toggleTaskSelection(task.id)}
                        className="mt-1 text-blue-600 hover:text-blue-800"
                      >
                        {selectedTasks.has(task.id) ? 
                          <CheckSquare className="w-5 h-5" /> : 
                          <Square className="w-5 h-5" />
                        }
                      </button>
                    )}
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-lg font-medium text-gray-900 mb-1">
                            {task.title || task.summary || 'Untitled Task'}
                          </h3>
                          {task.description && (
                            <p className="text-gray-600 text-sm mb-3">{task.description}</p>
                          )}
                          
                          <div className="flex flex-wrap items-center gap-2 mb-3">
                            <span className={`px-2 py-1 text-xs rounded-full border ${getPriorityColor(task.priority)}`}>
                              {task.priority || 'medium'}
                            </span>
                            <span className="px-2 py-1 text-xs rounded-full bg-gray-100 text-gray-700 border border-gray-200">
                              {task.category || 'general'}
                            </span>
                            <div className="flex items-center space-x-1">
                              {getStatusIcon(task.status)}
                              <span className="text-xs text-gray-600 capitalize">{task.status}</span>
                            </div>
                          </div>
                          
                          <p className="text-xs text-gray-500">
                            Created: {formatDate(task.created_at)}
                          </p>
                        </div>
                        
                        <div className="flex items-center space-x-2 ml-4">
                          {task.status !== 'completed' && (
                            <button
                              onClick={() => updateTaskStatus(task.id, 'completed')}
                              className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-lg transition-colors"
                              title="Mark as completed"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                          )}
                          
                          {task.status === 'completed' && (
                            <button
                              onClick={() => updateTaskStatus(task.id, 'pending')}
                              className="p-2 text-yellow-600 hover:text-yellow-700 hover:bg-yellow-50 rounded-lg transition-colors"
                              title="Mark as pending"
                            >
                              <Clock className="w-4 h-4" />
                            </button>
                          )}
                          
                          <button
                            onClick={() => deleteTask(task.id)}
                            className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete task"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
};

export default SavedTasks; 