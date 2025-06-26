import React from 'react';
import { motion } from 'framer-motion';
import { User, Mail, Calendar, Shield, Settings, Activity, CheckCircle } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import { animations } from '../styles/design-system';

const Profile = () => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <motion.div
        className="text-center py-12"
        variants={animations.fadeIn}
        initial="initial"
        animate="animate"
      >
        <div className="max-w-md mx-auto">
          <div className="w-24 h-24 mx-auto mb-6 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full flex items-center justify-center">
            <User className="w-12 h-12 text-gray-400" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Sign In Required</h2>
          <p className="text-gray-600 mb-6">
            Please sign in to view your profile and access personalized features.
          </p>
        </div>
      </motion.div>
    );
  }

  const userDisplayName = user.user_metadata?.full_name || user.email?.split('@')[0] || 'User';
  const userEmail = user.email;
  const userAvatar = user.user_metadata?.avatar_url;
  const joinDate = new Date(user.created_at).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  const features = [
    {
      icon: CheckCircle,
      title: 'Persistent Chat History',
      description: 'Your conversations are saved and synced across devices',
      enabled: true
    },
    {
      icon: Activity,
      title: 'Task Management',
      description: 'Create, organize, and track your AI-generated tasks',
      enabled: true
    },
    {
      icon: Settings,
      title: 'Personalized Settings',
      description: 'Customize your AI assistant preferences',
      enabled: true
    },
    {
      icon: Shield,
      title: 'Secure Data Storage',
      description: 'Your data is encrypted and securely stored',
      enabled: true
    }
  ];

  return (
    <motion.div
      className="max-w-4xl mx-auto space-y-8"
      variants={animations.staggerChildren}
      initial="initial"
      animate="animate"
    >
      {/* Profile Header */}
      <motion.div
        className="bg-white/80 backdrop-blur-md rounded-3xl shadow-lg border border-gray-200/60 overflow-hidden"
        variants={animations.fadeIn}
      >
        <div className="bg-gradient-to-r from-blue-50/80 to-purple-50/80 p-8">
          <div className="flex items-center space-x-6">
            {/* User Avatar */}
            <div className="relative">
              {userAvatar ? (
                <img
                  src={userAvatar}
                  alt={userDisplayName}
                  className="w-24 h-24 rounded-full border-4 border-white shadow-lg"
                />
              ) : (
                <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center border-4 border-white shadow-lg">
                  <User className="w-12 h-12 text-white" />
                </div>
              )}
              {/* Online indicator */}
              <div className="absolute bottom-2 right-2 w-6 h-6 bg-green-500 border-4 border-white rounded-full"></div>
            </div>

            {/* User Info */}
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{userDisplayName}</h1>
              <div className="flex items-center space-x-4 text-gray-600">
                <div className="flex items-center space-x-2">
                  <Mail className="w-4 h-4" />
                  <span>{userEmail}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Calendar className="w-4 h-4" />
                  <span>Member since {joinDate}</span>
                </div>
              </div>
              <div className="mt-4 flex items-center space-x-2">
                <Shield className="w-4 h-4 text-green-600" />
                <span className="text-sm text-green-600 font-medium">Verified Account</span>
              </div>
            </div>
          </div>
        </div>

        {/* Account Stats */}
        <div className="p-8 border-t border-gray-200/60">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">∞</div>
              <div className="text-sm text-gray-600 mt-1">Chat Messages</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">∞</div>
              <div className="text-sm text-gray-600 mt-1">Tasks Created</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">∞</div>
              <div className="text-sm text-gray-600 mt-1">Files Processed</div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Features */}
      <motion.div
        className="bg-white/80 backdrop-blur-md rounded-3xl shadow-lg border border-gray-200/60 overflow-hidden"
        variants={animations.fadeIn}
      >
        <div className="p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Your IntelliAssist.AI Benefits</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                className="flex items-start space-x-4 p-4 rounded-2xl bg-gradient-to-r from-blue-50/50 to-purple-50/50 border border-gray-200/60"
                variants={animations.slideUp}
                transition={{ delay: index * 0.1 }}
              >
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                  feature.enabled ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
                }`}>
                  <feature.icon className="w-5 h-5" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">{feature.title}</h3>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                  {feature.enabled && (
                    <div className="mt-2 flex items-center space-x-1">
                      <CheckCircle className="w-3 h-3 text-green-600" />
                      <span className="text-xs text-green-600 font-medium">Active</span>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Additional Info */}
      <motion.div
        className="bg-gradient-to-r from-blue-50/80 to-purple-50/80 backdrop-blur-md rounded-2xl p-6 border border-gray-200/60"
        variants={animations.fadeIn}
      >
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">🎉 Welcome to IntelliAssist.AI!</h3>
          <p className="text-gray-600">
            You're all set! Your account is verified and ready to use all features.
            Enjoy unlimited access to our AI-powered task management system.
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Profile; 