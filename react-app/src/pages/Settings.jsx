import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings as SettingsIcon, 
  Bell, 
  Shield, 
  Palette, 
  Globe, 
  Download, 
  Trash2, 
  Key, 
  Eye, 
  EyeOff,
  Save,
  RefreshCw,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { animations } from '../styles/design-system';

const Settings = () => {
  const { user, isAuthenticated, resetPassword, signOut } = useAuth();
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState({
    notifications: {
      email: true,
      push: false,
      taskReminders: true,
      weeklyDigest: true
    },
    privacy: {
      profileVisibility: 'private',
      dataCollection: false,
      analytics: true
    },
    preferences: {
      theme: 'light',
      language: 'en',
      timezone: 'auto',
      dateFormat: 'MM/DD/YYYY'
    }
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Load settings from localStorage on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('userSettings');
    if (savedSettings) {
      try {
        setSettings(JSON.parse(savedSettings));
      } catch (error) {
        console.error('Error loading settings:', error);
      }
    }
  }, []);

  const saveSettings = () => {
    setIsLoading(true);
    try {
      localStorage.setItem('userSettings', JSON.stringify(settings));
      toast.success('Settings saved successfully!');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordReset = async () => {
    if (!user?.email) {
      toast.error('No email address found');
      return;
    }

    setIsLoading(true);
    try {
      const { error } = await resetPassword(user.email);
      
      if (error) {
        throw error;
      }

      toast.success('Password reset email sent! Check your inbox.');
    } catch (error) {
      console.error('Error sending password reset:', error);
      toast.error(error.message || 'Failed to send password reset email');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAccountDeletion = async () => {
    if (!showDeleteConfirm) {
      setShowDeleteConfirm(true);
      return;
    }

    // In a real app, you'd call an API to delete the account
    toast.error('Account deletion is not implemented yet');
    setShowDeleteConfirm(false);
  };

  const exportData = () => {
    // In a real app, you'd fetch user data from the API
    const userData = {
      profile: user,
      settings: settings,
      exportDate: new Date().toISOString()
    };

    const dataStr = JSON.stringify(userData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `intelliassist-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    toast.success('Data exported successfully!');
  };

  if (!isAuthenticated()) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
            <SettingsIcon className="w-8 h-8 text-gray-400" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Authentication Required</h2>
          <p className="text-gray-600">Please sign in to access settings.</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'general', label: 'General', icon: SettingsIcon },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy & Security', icon: Shield },
    { id: 'account', label: 'Account', icon: Key }
  ];

  const ToggleSwitch = ({ enabled, onChange, disabled = false }) => (
    <button
      onClick={() => !disabled && onChange(!enabled)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        enabled ? 'bg-blue-600' : 'bg-gray-200'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      disabled={disabled}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          className="text-center mb-8"
          variants={animations.fadeIn}
          initial="initial"
          animate="animate"
        >
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
          <p className="text-gray-600">Manage your account preferences and security settings</p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <motion.div
            className="lg:col-span-1"
            variants={animations.slideUp}
            initial="initial"
            animate="animate"
          >
            <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-sm border border-gray-200/60 p-4">
              <nav className="space-y-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                        activeTab === tab.id
                          ? 'bg-blue-100 text-blue-700 border border-blue-200'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="font-medium">{tab.label}</span>
                    </button>
                  );
                })}
              </nav>
            </div>
          </motion.div>

          {/* Content */}
          <motion.div
            className="lg:col-span-3"
            variants={animations.slideUp}
            initial="initial"
            animate="animate"
            transition={{ delay: 0.1 }}
          >
            <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-sm border border-gray-200/60">
              {/* General Settings */}
              {activeTab === 'general' && (
                <div className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">General Preferences</h2>
                    <motion.button
                      onClick={saveSettings}
                      disabled={isLoading}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Save className="w-4 h-4" />
                      {isLoading ? 'Saving...' : 'Save Changes'}
                    </motion.button>
                  </div>

                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Theme
                      </label>
                      <select
                        value={settings.preferences.theme}
                        onChange={(e) => setSettings({
                          ...settings,
                          preferences: { ...settings.preferences, theme: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="light">Light</option>
                        <option value="dark">Dark</option>
                        <option value="auto">Auto (System)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Language
                      </label>
                      <select
                        value={settings.preferences.language}
                        onChange={(e) => setSettings({
                          ...settings,
                          preferences: { ...settings.preferences, language: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Date Format
                      </label>
                      <select
                        value={settings.preferences.dateFormat}
                        onChange={(e) => setSettings({
                          ...settings,
                          preferences: { ...settings.preferences, dateFormat: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                        <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                        <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Timezone
                      </label>
                      <select
                        value={settings.preferences.timezone}
                        onChange={(e) => setSettings({
                          ...settings,
                          preferences: { ...settings.preferences, timezone: e.target.value }
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="auto">Auto-detect</option>
                        <option value="UTC">UTC</option>
                        <option value="America/New_York">Eastern Time</option>
                        <option value="America/Chicago">Central Time</option>
                        <option value="America/Denver">Mountain Time</option>
                        <option value="America/Los_Angeles">Pacific Time</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {/* Notifications */}
              {activeTab === 'notifications' && (
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">Notification Preferences</h2>
                  
                  <div className="space-y-4">
                    <div className="flex items-center justify-between py-3">
                      <div>
                        <h3 className="font-medium text-gray-900">Email Notifications</h3>
                        <p className="text-sm text-gray-600">Receive updates via email</p>
                      </div>
                      <ToggleSwitch
                        enabled={settings.notifications.email}
                        onChange={(value) => setSettings({
                          ...settings,
                          notifications: { ...settings.notifications, email: value }
                        })}
                      />
                    </div>

                    <div className="flex items-center justify-between py-3">
                      <div>
                        <h3 className="font-medium text-gray-900">Task Reminders</h3>
                        <p className="text-sm text-gray-600">Get reminded about upcoming tasks</p>
                      </div>
                      <ToggleSwitch
                        enabled={settings.notifications.taskReminders}
                        onChange={(value) => setSettings({
                          ...settings,
                          notifications: { ...settings.notifications, taskReminders: value }
                        })}
                      />
                    </div>

                    <div className="flex items-center justify-between py-3">
                      <div>
                        <h3 className="font-medium text-gray-900">Weekly Digest</h3>
                        <p className="text-sm text-gray-600">Weekly summary of your activity</p>
                      </div>
                      <ToggleSwitch
                        enabled={settings.notifications.weeklyDigest}
                        onChange={(value) => setSettings({
                          ...settings,
                          notifications: { ...settings.notifications, weeklyDigest: value }
                        })}
                      />
                    </div>

                    <div className="flex items-center justify-between py-3">
                      <div>
                        <h3 className="font-medium text-gray-900">Push Notifications</h3>
                        <p className="text-sm text-gray-600">Browser push notifications</p>
                      </div>
                      <ToggleSwitch
                        enabled={settings.notifications.push}
                        onChange={(value) => setSettings({
                          ...settings,
                          notifications: { ...settings.notifications, push: value }
                        })}
                      />
                    </div>
                  </div>

                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <motion.button
                      onClick={saveSettings}
                      disabled={isLoading}
                      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Save className="w-4 h-4" />
                      {isLoading ? 'Saving...' : 'Save Preferences'}
                    </motion.button>
                  </div>
                </div>
              )}

              {/* Privacy & Security */}
              {activeTab === 'privacy' && (
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">Privacy & Security</h2>
                  
                  <div className="space-y-6">
                    <div>
                      <h3 className="font-medium text-gray-900 mb-3">Profile Visibility</h3>
                      <div className="space-y-2">
                        <label className="flex items-center">
                          <input
                            type="radio"
                            value="public"
                            checked={settings.privacy.profileVisibility === 'public'}
                            onChange={(e) => setSettings({
                              ...settings,
                              privacy: { ...settings.privacy, profileVisibility: e.target.value }
                            })}
                            className="mr-3 text-blue-600"
                          />
                          <span>Public - Anyone can see your profile</span>
                        </label>
                        <label className="flex items-center">
                          <input
                            type="radio"
                            value="private"
                            checked={settings.privacy.profileVisibility === 'private'}
                            onChange={(e) => setSettings({
                              ...settings,
                              privacy: { ...settings.privacy, profileVisibility: e.target.value }
                            })}
                            className="mr-3 text-blue-600"
                          />
                          <span>Private - Only you can see your profile</span>
                        </label>
                      </div>
                    </div>

                    <div className="flex items-center justify-between py-3">
                      <div>
                        <h3 className="font-medium text-gray-900">Data Collection</h3>
                        <p className="text-sm text-gray-600">Allow collection of usage data for improvements</p>
                      </div>
                      <ToggleSwitch
                        enabled={settings.privacy.dataCollection}
                        onChange={(value) => setSettings({
                          ...settings,
                          privacy: { ...settings.privacy, dataCollection: value }
                        })}
                      />
                    </div>

                    <div className="flex items-center justify-between py-3">
                      <div>
                        <h3 className="font-medium text-gray-900">Analytics</h3>
                        <p className="text-sm text-gray-600">Help us improve with anonymous analytics</p>
                      </div>
                      <ToggleSwitch
                        enabled={settings.privacy.analytics}
                        onChange={(value) => setSettings({
                          ...settings,
                          privacy: { ...settings.privacy, analytics: value }
                        })}
                      />
                    </div>

                    <div className="mt-6 pt-6 border-t border-gray-200">
                      <motion.button
                        onClick={exportData}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors mr-4"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <Download className="w-4 h-4" />
                        Export My Data
                      </motion.button>
                    </div>
                  </div>
                </div>
              )}

              {/* Account */}
              {activeTab === 'account' && (
                <div className="p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">Account Management</h2>
                  
                  <div className="space-y-6">
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <div className="flex items-center space-x-2 mb-2">
                        <CheckCircle className="w-5 h-5 text-blue-600" />
                        <h3 className="font-medium text-blue-900">Account Status</h3>
                      </div>
                      <p className="text-blue-800">Your account is active and verified.</p>
                    </div>

                    <div>
                      <h3 className="font-medium text-gray-900 mb-3">Password</h3>
                      <p className="text-sm text-gray-600 mb-4">
                        Reset your password to maintain account security.
                      </p>
                      <motion.button
                        onClick={handlePasswordReset}
                        disabled={isLoading}
                        className="flex items-center gap-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 transition-colors"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <RefreshCw className="w-4 h-4" />
                        {isLoading ? 'Sending...' : 'Reset Password'}
                      </motion.button>
                    </div>

                    <div className="border-t border-gray-200 pt-6">
                      <h3 className="font-medium text-red-900 mb-3">Danger Zone</h3>
                      
                      {!showDeleteConfirm ? (
                        <div>
                          <p className="text-sm text-gray-600 mb-4">
                            Permanently delete your account and all associated data. This action cannot be undone.
                          </p>
                          <motion.button
                            onClick={handleAccountDeletion}
                            className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <Trash2 className="w-4 h-4" />
                            Delete Account
                          </motion.button>
                        </div>
                      ) : (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                          <div className="flex items-center space-x-2 mb-3">
                            <AlertTriangle className="w-5 h-5 text-red-600" />
                            <h4 className="font-medium text-red-900">Confirm Account Deletion</h4>
                          </div>
                          <p className="text-red-800 text-sm mb-4">
                            Are you absolutely sure? This will permanently delete your account and cannot be undone.
                          </p>
                          <div className="flex space-x-3">
                            <motion.button
                              onClick={handleAccountDeletion}
                              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                            >
                              Yes, Delete My Account
                            </motion.button>
                            <motion.button
                              onClick={() => setShowDeleteConfirm(false)}
                              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition-colors"
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                            >
                              Cancel
                            </motion.button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 