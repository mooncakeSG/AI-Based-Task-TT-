import React from 'react';
import { motion } from 'framer-motion';
import { MessageCircle, Upload, CheckCircle, Clock, Users, Zap, Brain, Target, Sparkles } from 'lucide-react';
import { animations } from '../styles/design-system';

const Home = ({ onNavigate }) => {
  const features = [
    {
      icon: MessageCircle,
      title: 'Smart Conversations',
      description: 'Chat with our AI assistant powered by advanced language models for intelligent task management.',
      color: 'text-blue-600',
      bgColor: 'bg-blue-100/80'
    },
    {
      icon: Upload,
      title: 'Multimodal Input',
      description: 'Upload images, audio files, and documents for comprehensive AI analysis and processing.',
      color: 'text-purple-600',
      bgColor: 'bg-purple-100/80'
    },
    {
      icon: CheckCircle,
      title: 'Task Management',
      description: 'Organize, track, and manage your tasks with AI-powered insights and recommendations.',
      color: 'text-green-600',
      bgColor: 'bg-green-100/80'
    },
    {
      icon: Brain,
      title: 'AI-Powered Analysis',
      description: 'Get intelligent insights from your data with advanced machine learning capabilities.',
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100/80'
    }
  ];

  const stats = [
    { icon: CheckCircle, label: 'Tasks Completed', value: '10,000+', color: 'text-green-600' },
    { icon: Clock, label: 'Avg Response Time', value: '< 2s', color: 'text-blue-600' },
    { icon: Users, label: 'Active Users', value: '5,000+', color: 'text-purple-600' },
    { icon: Zap, label: 'Uptime', value: '99.9%', color: 'text-yellow-600' }
  ];

  const tips = [
    {
      icon: Target,
      title: 'Be Specific',
      description: 'Provide clear, detailed instructions for better AI responses.'
    },
    {
      icon: Upload,
      title: 'Use Multimodal Input',
      description: 'Combine text, images, and audio for richer interactions.'
    },
    {
      icon: Brain,
      title: 'Leverage AI Insights',
      description: 'Ask for analysis, suggestions, and task breakdowns.'
    }
  ];

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <motion.div 
        className="text-center space-y-8"
        variants={animations.staggerChildren}
        initial="initial"
        animate="animate"
      >
        <motion.div 
          className="space-y-4"
          variants={animations.fadeIn}
        >
          <div className="flex justify-center">
            <motion.div 
              className="w-20 h-20 bg-gradient-to-br from-blue-600 to-purple-600 rounded-3xl flex items-center justify-center shadow-2xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ duration: 0.3 }}
            >
              <Sparkles className="w-10 h-10 text-white" />
            </motion.div>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900">
            Welcome to{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              IntelliAssist.AI
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Your intelligent AI companion for task management, multimodal analysis, and productivity enhancement. 
            Experience the future of AI-powered assistance.
          </p>
        </motion.div>

        <motion.div 
          className="flex flex-col sm:flex-row gap-4 justify-center items-center"
          variants={animations.fadeIn}
        >
          <motion.button
            onClick={() => onNavigate('chat')}
            className="flex items-center gap-3 px-8 py-4 bg-blue-600 text-white rounded-2xl font-semibold text-lg shadow-xl hover:shadow-2xl hover:bg-blue-700 transition-all duration-300"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            <MessageCircle className="w-6 h-6" />
            Start Chatting
          </motion.button>
          
          <motion.button
            onClick={() => onNavigate('upload')}
            className="flex items-center gap-3 px-8 py-4 bg-white/80 backdrop-blur-sm text-gray-700 border-2 border-gray-200/60 rounded-2xl font-semibold text-lg hover:bg-gray-50/80 hover:border-gray-300/60 transition-all duration-300"
            whileHover={{ scale: 1.05, y: -2 }}
            whileTap={{ scale: 0.95 }}
          >
            <Upload className="w-6 h-6" />
            Upload Files
          </motion.button>
        </motion.div>
      </motion.div>

      {/* Features Grid */}
      <motion.div 
        className="space-y-8"
        variants={animations.staggerChildren}
        initial="initial"
        animate="animate"
      >
        <motion.div 
          className="text-center"
          variants={animations.fadeIn}
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Powerful Features</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Discover what makes IntelliAssist.AI the perfect companion for your productivity needs.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="bg-white/80 backdrop-blur-md rounded-2xl p-8 shadow-lg border border-gray-200/60 hover:shadow-xl transition-all duration-300"
              variants={animations.fadeIn}
              whileHover={{ scale: 1.02, y: -4 }}
            >
              <div className="flex items-start space-x-4">
                <div className={`w-12 h-12 ${feature.bgColor} backdrop-blur-sm rounded-xl flex items-center justify-center flex-shrink-0`}>
                  <feature.icon className={`w-6 h-6 ${feature.color}`} />
                </div>
                <div className="space-y-3">
                  <h3 className="text-xl font-semibold text-gray-900">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>



      {/* Productivity Tips */}
      <motion.div 
        className="space-y-8"
        variants={animations.staggerChildren}
        initial="initial"
        animate="animate"
      >
        <motion.div 
          className="text-center"
          variants={animations.fadeIn}
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Productivity Tips</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Maximize your efficiency with these AI-powered strategies.
          </p>
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
                <div className="w-10 h-10 bg-blue-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <tip.icon className="w-5 h-5 text-blue-600" />
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

      {/* Enhanced CTA Section */}
      <motion.div 
        className="relative text-center bg-gradient-to-br from-blue-500 via-purple-600 to-pink-500 rounded-3xl p-10 md:p-16 text-white shadow-2xl overflow-hidden"
        variants={animations.fadeIn}
        initial="initial"
        animate="animate"
        style={{
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1)'
        }}
      >
        {/* Animated Background Pattern */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-white/10 rounded-full blur-xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-white/10 rounded-full blur-xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-white/5 rounded-full blur-2xl animate-pulse delay-500"></div>
        </div>

        <div className="relative z-10 space-y-8">
          {/* Enhanced Icon with Circular Background */}
          <div className="flex justify-center">
            <motion.div 
              className="relative w-20 h-20 bg-gradient-to-br from-white/30 to-white/10 backdrop-blur-lg rounded-full flex items-center justify-center border border-white/20"
              whileHover={{ 
                scale: 1.15, 
                rotate: 10,
                boxShadow: "0 0 30px rgba(255, 255, 255, 0.3)"
              }}
              transition={{ duration: 0.4, type: "spring", stiffness: 300 }}
            >
              <motion.div
                animate={{ 
                  rotate: [0, 5, -5, 0],
                  scale: [1, 1.1, 1]
                }}
                transition={{ 
                  duration: 3,
                  repeat: Infinity,
                  repeatType: "reverse"
                }}
              >
                <Sparkles className="w-10 h-10 text-white drop-shadow-lg" />
              </motion.div>
              
              {/* Glow Effect */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/20 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
            </motion.div>
          </div>

          {/* Enhanced Typography */}
          <div className="space-y-4">
            <motion.h2 
              className="text-4xl md:text-5xl font-semibold mb-6 leading-tight"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              Ready to Get Started?
            </motion.h2>
            <motion.p 
              className="text-lg text-white/90 max-w-2xl mx-auto leading-relaxed font-light"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              Join thousands of users who have transformed their productivity with AI assistance.
            </motion.p>
          </div>

          {/* Enhanced Call-to-Action Button */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <motion.button
              onClick={() => onNavigate('chat')}
              className="group relative inline-flex items-center gap-3 px-10 py-5 bg-white text-blue-600 rounded-2xl font-semibold text-lg shadow-2xl hover:shadow-[0_20px_40px_rgba(0,0,0,0.3)] transition-all duration-500 overflow-hidden"
              whileHover={{ 
                scale: 1.08, 
                y: -3,
                boxShadow: "0 25px 50px rgba(0, 0, 0, 0.3)"
              }}
              whileTap={{ scale: 0.98 }}
            >
              {/* Button Background Gradient on Hover */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-50 to-purple-50 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              
              {/* Icon with Animation */}
              <motion.div
                className="relative z-10"
                whileHover={{ x: 3 }}
                transition={{ duration: 0.3 }}
              >
                <MessageCircle className="w-7 h-7" />
              </motion.div>
              
              {/* Text with Color Transition */}
              <span className="relative z-10 group-hover:text-purple-600 transition-colors duration-300">
                Unlock AI Superpowers
              </span>

              {/* Subtle Glow Border */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-400/20 to-purple-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-sm"></div>
            </motion.button>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

export default Home; 