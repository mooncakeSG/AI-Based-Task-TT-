import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, MessageSquare, Upload, CheckCircle, Clock, Users, Zap, Brain, Target, Mail, Github, Globe } from 'lucide-react';
import { animations } from '../styles/design-system';

const About = () => {
  const technologies = [
    {
      name: 'React',
      description: 'Modern frontend framework',
      icon: Globe,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100/80'
    },
    {
      name: 'FastAPI',
      description: 'High-performance backend',
      icon: Zap,
      color: 'text-green-600',
      bgColor: 'bg-green-100/80'
    },
    {
      name: 'Groq LLaMA',
      description: 'Advanced AI language model',
      icon: Brain,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100/80'
    },
    {
      name: 'Hugging Face',
      description: 'Multimodal AI capabilities',
      icon: Sparkles,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100/80'
    }
  ];

  const features = [
    {
      icon: MessageSquare,
      title: 'Intelligent Conversations',
      description: 'Powered by state-of-the-art language models for natural, context-aware interactions.'
    },
    {
      icon: Upload,
      title: 'Multimodal Processing',
      description: 'Analyze images, transcribe audio, and process documents with advanced AI capabilities.'
    },
    {
      icon: Target,
      title: 'Task Management',
      description: 'Organize and track your tasks with AI-powered insights and recommendations.'
    },
    {
      icon: Zap,
      title: 'Real-time Performance',
      description: 'Sub-2 second response times with 99.9% uptime for reliable assistance.'
    }
  ];

  const stats = [
    { icon: CheckCircle, label: 'Tasks Completed', value: '10,000+', color: 'text-green-600' },
    { icon: Clock, label: 'Avg Response Time', value: '< 2s', color: 'text-blue-600' },
    { icon: Users, label: 'Active Users', value: '5,000+', color: 'text-purple-600' },
    { icon: Zap, label: 'Uptime', value: '99.9%', color: 'text-yellow-600' }
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
            About{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              IntelliAssist.AI
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            We're building the future of AI-powered productivity tools, combining cutting-edge technology 
            with intuitive design to help you accomplish more.
          </p>
        </motion.div>
      </motion.div>

      {/* Mission Section */}
      <motion.div 
        className="bg-gradient-to-r from-blue-50/80 to-purple-50/80 backdrop-blur-sm rounded-3xl p-8 md:p-12 border border-gray-200/60"
        variants={animations.fadeIn}
        initial="initial"
        animate="animate"
      >
        <div className="text-center space-y-6">
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-blue-100/80 backdrop-blur-sm rounded-2xl flex items-center justify-center">
              <Target className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Our Mission</h2>
            <p className="text-gray-600 max-w-3xl mx-auto text-lg leading-relaxed">
              To democratize access to advanced AI capabilities, making intelligent assistance available to everyone. 
              We believe that AI should enhance human creativity and productivity, not replace it.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Features Section */}
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
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Core Features</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Discover the powerful capabilities that make IntelliAssist.AI your ideal productivity companion.
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
                <div className="w-12 h-12 bg-blue-100/80 backdrop-blur-sm rounded-xl flex items-center justify-center flex-shrink-0">
                  <feature.icon className="w-6 h-6 text-blue-600" />
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

      {/* Technology Stack */}
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
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Technology Stack</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Built with modern, reliable technologies for optimal performance and scalability.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {technologies.map((tech, index) => (
            <motion.div
              key={index}
              className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-lg border border-gray-200/60 hover:shadow-xl transition-all duration-300 text-center"
              variants={animations.fadeIn}
              whileHover={{ scale: 1.05, y: -4 }}
            >
              <div className={`w-12 h-12 ${tech.bgColor} backdrop-blur-sm rounded-xl flex items-center justify-center mx-auto mb-4`}>
                <tech.icon className={`w-6 h-6 ${tech.color}`} />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{tech.name}</h3>
              <p className="text-gray-600 text-sm">{tech.description}</p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Performance Stats */}
      <motion.div 
        className="bg-gradient-to-r from-gray-900 to-blue-900 rounded-3xl p-8 md:p-12 text-white"
        variants={animations.fadeIn}
        initial="initial"
        animate="animate"
      >
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-4">Performance Metrics</h2>
          <p className="text-blue-100">Real-time statistics showcasing our platform's reliability and performance.</p>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              className="text-center space-y-3"
              variants={animations.fadeIn}
              whileHover={{ scale: 1.05 }}
            >
              <div className="flex justify-center">
                <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <div className="text-2xl md:text-3xl font-bold">{stat.value}</div>
                <div className="text-sm text-blue-100 font-medium">{stat.label}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Contact Section */}
      <motion.div 
        className="bg-white/80 backdrop-blur-md rounded-3xl p-8 md:p-12 shadow-lg border border-gray-200/60"
        variants={animations.fadeIn}
        initial="initial"
        animate="animate"
      >
        <div className="text-center space-y-8">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Get in Touch</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Have questions, feedback, or want to collaborate? We'd love to hear from you.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <motion.a
              href="mailto:contact@intelliassist.ai"
              className="flex items-center gap-3 px-6 py-3 bg-blue-600 text-white rounded-2xl font-semibold hover:bg-blue-700 transition-all duration-300 shadow-lg hover:shadow-xl"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              <Mail className="w-5 h-5" />
              Contact Us
            </motion.a>
            
            <motion.a
              href="https://github.com/mooncakeSG/AI-Based-Task-TT-.git"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 px-6 py-3 bg-gray-800 text-white rounded-2xl font-semibold hover:bg-gray-900 transition-all duration-300 shadow-lg hover:shadow-xl"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              <Github className="w-5 h-5" />
              View on GitHub
            </motion.a>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default About; 