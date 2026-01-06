import React from "react";
import { motion } from "framer-motion";
import {
  User,
  Mail,
  MapPin,
  Globe,
  Building,
  Users,
  GitBranch,
  LogOut,
} from "lucide-react";
import { useAuth } from "../contexts/AuthContext";

export const UserProfile: React.FC = () => {
  const { user, userProfile, logout } = useAuth();

  if (!user || !userProfile) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading profile...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-black/40 backdrop-blur-xl border border-green-500/20 rounded-2xl overflow-hidden"
      >
        {/* Header */}
        <div className="relative">
          <div className="h-32 bg-gradient-to-r from-green-400/20 to-emerald-500/20"></div>
          <div className="absolute -bottom-16 left-6">
            <img
              src={user.photoURL || "/default-avatar.png"}
              alt="Profile"
              className="w-32 h-32 rounded-full border-4 border-green-500/30 bg-gray-800"
            />
          </div>
          <div className="absolute top-4 right-4 flex gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={logout}
              className="p-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </motion.button>
          </div>
        </div>

        {/* Profile Content */}
        <div className="pt-20 pb-6 px-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Basic Info */}
            <div className="lg:col-span-2 space-y-6">
              <div>
                <h1 className="text-2xl font-bold text-white">
                  {userProfile.displayName || "No name set"}
                </h1>

                <p className="text-green-400 font-medium">
                  @{userProfile.githubUsername}
                </p>
                <div className="flex items-center gap-2 text-gray-400 text-sm mt-1">
                  <Mail className="w-4 h-4" />
                  {user.email}
                </div>
              </div>

              {/* Bio */}
              <div>
                <h3 className="text-lg font-semibold text-white mb-2">About</h3>

                <p className="text-gray-300">
                  {userProfile.bio || "No bio available"}
                </p>
              </div>

              {/* Additional Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Location
                  </label>

                  <div className="flex items-center gap-2 text-gray-300">
                    <MapPin className="w-4 h-4" />
                    {userProfile.location || "Not specified"}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Website
                  </label>

                  <div className="flex items-center gap-2 text-gray-300">
                    <Globe className="w-4 h-4" />
                    {userProfile.website ? (
                      <a
                        href={userProfile.website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-green-400 hover:underline"
                      >
                        {userProfile.website}
                      </a>
                    ) : (
                      "Not specified"
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-400 mb-1">
                    Company
                  </label>

                  <div className="flex items-center gap-2 text-gray-300">
                    <Building className="w-4 h-4" />
                    {userProfile.company || "Not specified"}
                  </div>
                </div>
              </div>
            </div>

            {/* Stats Sidebar */}
            <div className="space-y-4">
              <div className="bg-gray-800/30 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-4">
                  GitHub Stats
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <GitBranch className="w-4 h-4 text-green-400" />
                      <span className="text-gray-300">Repositories</span>
                    </div>
                    <span className="text-white font-medium">
                      {userProfile.publicRepos || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Users className="w-4 h-4 text-green-400" />
                      <span className="text-gray-300">Followers</span>
                    </div>
                    <span className="text-white font-medium">
                      {userProfile.followers || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-green-400" />
                      <span className="text-gray-300">Following</span>
                    </div>
                    <span className="text-white font-medium">
                      {userProfile.following || 0}
                    </span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/30 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Account Info
                </h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-400">Joined:</span>
                    <span className="text-gray-300 ml-2">
                      {userProfile.createdAt
                        ? new Date(
                            userProfile.createdAt.toDate()
                          ).toLocaleDateString()
                        : "Unknown"}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400">Last login:</span>
                    <span className="text-gray-300 ml-2">
                      {userProfile.lastLoginAt
                        ? new Date(
                            userProfile.lastLoginAt.toDate()
                          ).toLocaleDateString()
                        : "Unknown"}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
