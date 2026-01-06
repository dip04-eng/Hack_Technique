import React, { useState } from "react";
import { motion } from "framer-motion";
import { useTheme } from "../contexts/ThemeContext";
import { Palette, Plug, Bell, Save, RotateCcw } from "lucide-react";

interface SettingSection {
  id: string;
  title: string;
  icon: React.ComponentType<any>;
  description: string;
}

export const SettingsPanel: React.FC = () => {
  const [activeSection, setActiveSection] = useState("appearance");
  const { isDarkMode, toggleDarkMode } = useTheme();
  const [settings, setSettings] = useState({
    greenMode: true,
    notifications: true,
    soundEnabled: true,
    language: "en",
    autoSave: true,
    aiModel: "gpt-4",
    apiKey: "",
    enablePlugins: true,
  });

  const sections: SettingSection[] = [
    {
      id: "appearance",
      title: "Appearance",
      icon: Palette,
      description: "Customize your interface",
    },
    {
      id: "plugins",
      title: "Plugins",
      icon: Plug,
      description: "Enable and configure plugins",
    },
    {
      id: "notifications",
      title: "Notifications",
      icon: Bell,
      description: "Configure alerts and updates",
    },
  ];

  const handleSettingChange = (key: string, value: any) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    // Simulate save action
    console.log("Settings saved:", settings);
  };

  const handleReset = () => {
    setSettings({
      greenMode: true,
      notifications: true,
      soundEnabled: true,
      language: "en",
      autoSave: true,
      aiModel: "gpt-4",
      apiKey: "",
      enablePlugins: true,
    });
  };

  const renderSectionContent = () => {
    switch (activeSection) {
      case "appearance":
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-white mb-4">
                Theme Preferences
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Dark Mode</p>
                    <p className="text-gray-400 text-sm">
                      Use dark theme across the interface
                    </p>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={toggleDarkMode}
                    className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                      isDarkMode ? "bg-green-500" : "bg-gray-600"
                    }`}
                  >
                    <motion.div
                      layout
                      className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg"
                      style={{ left: isDarkMode ? "26px" : "2px" }}
                    />
                  </motion.button>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium text-white mb-4">
                System Preferences
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Enable Notifications</p>
                    <p className="text-gray-400 text-sm">
                      Receive alerts and updates
                    </p>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      handleSettingChange(
                        "notifications",
                        !settings.notifications
                      )
                    }
                    className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                      settings.notifications ? "bg-green-500" : "bg-gray-600"
                    }`}
                  >
                    <motion.div
                      layout
                      className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg"
                      style={{ left: settings.notifications ? "26px" : "2px" }}
                    />
                  </motion.button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Sound Effects</p>
                    <p className="text-gray-400 text-sm">
                      Play sounds for notifications
                    </p>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      handleSettingChange(
                        "soundEnabled",
                        !settings.soundEnabled
                      )
                    }
                    className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                      settings.soundEnabled ? "bg-green-500" : "bg-gray-600"
                    }`}
                  >
                    <motion.div
                      layout
                      className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg"
                      style={{ left: settings.soundEnabled ? "26px" : "2px" }}
                    />
                  </motion.button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Auto Save</p>
                    <p className="text-gray-400 text-sm">
                      Automatically save changes
                    </p>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      handleSettingChange("autoSave", !settings.autoSave)
                    }
                    className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                      settings.autoSave ? "bg-green-500" : "bg-gray-600"
                    }`}
                  >
                    <motion.div
                      layout
                      className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg"
                      style={{ left: settings.autoSave ? "26px" : "2px" }}
                    />
                  </motion.button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Enable Plugins</p>
                    <p className="text-gray-400 text-sm">
                      Enable and configure plugins
                    </p>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      handleSettingChange(
                        "enablePlugins",
                        !settings.enablePlugins
                      )
                    }
                    className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                      settings.enablePlugins ? "bg-green-500" : "bg-gray-600"
                    }`}
                  >
                    <motion.div
                      layout
                      className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg"
                      style={{ left: settings.enablePlugins ? "26px" : "2px" }}
                    />
                  </motion.button>
                </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium text-white mb-4">
                AI Configuration
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-white mb-2">AI Model</label>
                  <select
                    value={settings.aiModel}
                    onChange={(e) =>
                      handleSettingChange("aiModel", e.target.value)
                    }
                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-green-500"
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="claude-3">Claude 3</option>
                    <option value="gemini-pro">Gemini Pro</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        );

      case "plugins":
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-medium text-white">
                  Plugin Management
                </h3>
                <p className="text-gray-400">
                  Enable and configure available plugins
                </p>
              </div>
              <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={() =>
                  handleSettingChange("enablePlugins", !settings.enablePlugins)
                }
                className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                  settings.enablePlugins ? "bg-green-500" : "bg-gray-600"
                }`}
              >
                <motion.div
                  layout
                  className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg"
                  style={{ left: settings.enablePlugins ? "26px" : "2px" }}
                />
              </motion.button>
            </div>

            <div className="space-y-3">
              {[
                {
                  name: "Code Optimizer",
                  description: "AI-powered code optimization",
                  enabled: true,
                },
                {
                  name: "Test Generator",
                  description: "Automatic test case generation",
                  enabled: true,
                },
                {
                  name: "Documentation AI",
                  description: "Smart documentation writer",
                  enabled: false,
                },
                {
                  name: "Security Scanner",
                  description: "Vulnerability detection",
                  enabled: true,
                },
                {
                  name: "Performance Monitor",
                  description: "Real-time performance tracking",
                  enabled: false,
                },
              ].map((plugin, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-600"
                >
                  <div>
                    <h4 className="text-white font-medium">{plugin.name}</h4>
                    <p className="text-gray-400 text-sm">
                      {plugin.description}
                    </p>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                      plugin.enabled ? "bg-green-500" : "bg-gray-600"
                    }`}
                  >
                    <motion.div
                      layout
                      className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg"
                      style={{ left: plugin.enabled ? "26px" : "2px" }}
                    />
                  </motion.button>
                </div>
              ))}
            </div>
          </div>
        );

      case "notifications":
        return (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-white mb-4">
                Notification Preferences
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Enable Notifications</p>
                    <p className="text-gray-400 text-sm">
                      Receive alerts and updates
                    </p>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      handleSettingChange(
                        "notifications",
                        !settings.notifications
                      )
                    }
                    className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                      settings.notifications ? "bg-green-500" : "bg-gray-600"
                    }`}
                  >
                    <motion.div
                      layout
                      className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg"
                      style={{ left: settings.notifications ? "26px" : "2px" }}
                    />
                  </motion.button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Sound Effects</p>
                    <p className="text-gray-400 text-sm">
                      Play sounds for notifications
                    </p>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      handleSettingChange(
                        "soundEnabled",
                        !settings.soundEnabled
                      )
                    }
                    className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                      settings.soundEnabled ? "bg-green-500" : "bg-gray-600"
                    }`}
                  >
                    <motion.div
                      layout
                      className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg"
                      style={{ left: settings.soundEnabled ? "26px" : "2px" }}
                    />
                  </motion.button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white">Auto Save</p>
                    <p className="text-gray-400 text-sm">
                      Automatically save changes
                    </p>
                  </div>
                  <motion.button
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      handleSettingChange("autoSave", !settings.autoSave)
                    }
                    className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                      settings.autoSave ? "bg-green-500" : "bg-gray-600"
                    }`}
                  >
                    <motion.div
                      layout
                      className="absolute top-1 w-4 h-4 bg-white rounded-full shadow-lg"
                      style={{ left: settings.autoSave ? "26px" : "2px" }}
                    />
                  </motion.button>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center text-gray-400 py-12">
            Select a settings category
          </div>
        );
    }
  };

  return (
    <div className="h-full flex bg-theme-primary">
      {/* Settings Navigation */}
      <div className="w-80 border-r border-theme bg-theme-secondary">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="p-6"
        >
          <h2 className="text-xl font-bold text-theme-primary mb-6">
            Settings
          </h2>
          <div className="space-y-2">
            {sections.map((section) => (
              <motion.button
                key={section.id}
                whileHover={{ scale: 1.02, x: 4 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setActiveSection(section.id)}
                className={`w-full flex items-center gap-3 p-4 rounded-xl transition-all duration-300 ${
                  activeSection === section.id
                    ? "bg-accent-theme text-theme-primary font-medium shadow-lg"
                    : "hover:bg-theme-secondary text-theme-secondary hover:text-theme-primary"
                }`}
              >
                <section.icon className="w-5 h-5" />
                <div className="text-left">
                  <p className="font-medium">{section.title}</p>
                  <p
                    className={`text-xs ${
                      activeSection === section.id
                        ? "text-black/70"
                        : "text-gray-500"
                    }`}
                  >
                    {section.description}
                  </p>
                </div>
              </motion.button>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Settings Content */}
      <div className="flex-1 flex flex-col">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 border-b border-theme bg-theme-secondary"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-theme-primary">
                {sections.find((s) => s.id === activeSection)?.title}
              </h3>
              <p className="text-theme-secondary">
                {sections.find((s) => s.id === activeSection)?.description}
              </p>
            </div>
            <div className="flex gap-3">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleReset}
                className="flex items-center gap-2 px-4 py-2 bg-theme-secondary hover:bg-theme-secondary/80 rounded-lg text-theme-primary transition-all duration-300"
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSave}
                className="flex items-center gap-2 px-4 py-2 bg-accent-theme hover:opacity-90 rounded-lg text-theme-primary font-medium transition-all duration-300"
              >
                <Save className="w-4 h-4" />
                Save Changes
              </motion.button>
            </div>
          </div>
        </motion.div>

        <motion.div
          key={activeSection}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
          className="flex-1 p-6 overflow-y-auto"
        >
          {renderSectionContent()}
        </motion.div>
      </div>
    </div>
  );
};
