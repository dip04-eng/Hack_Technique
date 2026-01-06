import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, Award, TreesIcon, Leaf, Code, GitBranch, Shield, Cpu, Zap, X } from 'lucide-react';
import ReactConfetti from 'react-confetti';

// --- TypeScript Interfaces ---
interface Analytics {
  totalCO2SavedKg: number;
  totalOptimizations: number;
  averagePerformanceImprovement: number;
  totalSecurityIssuesFixed: number;
  averageBuildTimeReduction: number;
  totalRepositoriesOptimized: number;
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  target: number;
  currentValue: number;
  color: keyof typeof colorMap;
  reward: string;
  analyticsKey: keyof Analytics | 'calculated';
}

// --- Helper Data for Tailwind CSS ---
const colorMap = {
  emerald: { border: 'border-emerald-500', bg: 'bg-emerald-500', bgOpacity: 'bg-emerald-500/20', bgOverlay: 'bg-emerald-500/10', text: 'text-emerald-400', confetti: ['#34d399', '#10b981', '#059669', '#a7f3d0'] },
  green: { border: 'border-green-500', bg: 'bg-green-500', bgOpacity: 'bg-green-500/20', bgOverlay: 'bg-green-500/10', text: 'text-green-400', confetti: ['#22c55e', '#16a34a', '#15803d', '#bbf7d0'] },
  blue: { border: 'border-blue-500', bg: 'bg-blue-500', bgOpacity: 'bg-blue-500/20', bgOverlay: 'bg-blue-500/10', text: 'text-blue-400', confetti: ['#38bdf8', '#0ea5e9', '#0284c7', '#bfdbfe'] },
  yellow: { border: 'border-yellow-500', bg: 'bg-yellow-500', bgOpacity: 'bg-yellow-500/20', bgOverlay: 'bg-yellow-500/10', text: 'text-yellow-400', confetti: ['#facc15', '#eab308', '#ca8a04', '#fef08a'] },
  red: { border: 'border-red-500', bg: 'bg-red-500', bgOpacity: 'bg-red-500/20', bgOverlay: 'bg-red-500/10', text: 'text-red-400', confetti: ['#f87171', '#ef4444', '#dc2626', '#fecaca'] },
  purple: { border: 'border-purple-500', bg: 'bg-purple-500', bgOpacity: 'bg-purple-500/20', bgOverlay: 'bg-purple-500/10', text: 'text-purple-400', confetti: ['#a78bfa', '#8b5cf6', '#7c3aed', '#ddd6fe'] },
  orange: { border: 'border-orange-500', bg: 'bg-orange-500', bgOpacity: 'bg-orange-500/20', bgOverlay: 'bg-orange-500/10', text: 'text-orange-400', confetti: ['#fb923c', '#f97316', '#ea580c', '#fed7aa'] },
  amber: { border: 'border-amber-500', bg: 'bg-amber-500', bgOpacity: 'bg-amber-500/20', bgOverlay: 'bg-amber-500/10', text: 'text-amber-400', confetti: ['#fbbf24', '#f59e0b', '#d97706', '#fef3c7'] },
  // FIX: Added the missing bgOverlay property to the gray object.
  gray: { border: 'border-gray-500/20', bg: 'bg-gray-600', bgOpacity: 'bg-gray-800', bgOverlay: 'bg-gray-500/10', text: 'text-gray-400', confetti: [] }
};

// --- Reward Modal Component ---
interface RewardModalProps {
  achievement: Achievement | null;
  onClose: () => void;
}
const RewardModal: React.FC<RewardModalProps> = ({ achievement, onClose }) => {
  if (!achievement) return null;

  const colors = colorMap[achievement.color];

  return (
    <AnimatePresence>
      {achievement && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.9, y: 20 }}
            className={`relative bg-gray-900 border ${colors.border} rounded-2xl p-8 w-full max-w-md text-center shadow-2xl`}
            onClick={(e) => e.stopPropagation()}
          >
            <button onClick={onClose} className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors">
              <X size={24} />
            </button>
            <div className={`mx-auto w-20 h-20 rounded-full flex items-center justify-center ${colors.bgOpacity} mb-6 border-2 ${colors.border}`}>
              {achievement.icon}
            </div>
            <h2 className="text-2xl font-bold text-white">Achievement Unlocked!</h2>
            <h3 className={`text-xl font-semibold ${colors.text} mt-1 mb-4`}>{achievement.title}</h3>
            <p className="text-gray-300 mb-6">Congratulations! You've earned a reward:</p>
            <div className="bg-gray-800 p-4 rounded-lg">
              <p className="text-lg font-medium text-white">{achievement.reward}</p>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

// --- Individual Achievement Card Component ---
interface AchievementCardProps {
  achievement: Achievement;
  previousValue: number;
  onUnlock: (achievement: Achievement) => void;
}
const AchievementCard: React.FC<AchievementCardProps> = ({ achievement, previousValue, onUnlock }) => {
  const [showConfetti, setShowConfetti] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });

  const currentValue = typeof achievement.currentValue === 'number' ? achievement.currentValue : 0;
  const progress = Math.min((currentValue / achievement.target) * 100, 100);
  const isUnlocked = progress >= 100;
  const wasUnlocked = Math.min(((typeof previousValue === 'number' ? previousValue : 0) / achievement.target) * 100, 100) >= 100;

  useEffect(() => {
    if (isUnlocked && !wasUnlocked) {
      setShowConfetti(true);
      if (typeof onUnlock === 'function') {
          onUnlock(achievement);
      }
      setTimeout(() => setShowConfetti(false), 5000);
    }
  }, [isUnlocked, wasUnlocked, achievement, onUnlock]);

  useEffect(() => {
    const handleResize = () => {
        if (cardRef.current) {
            setDimensions({
                width: cardRef.current.offsetWidth,
                height: cardRef.current.offsetHeight
            });
        }
    }
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const colors = colorMap[achievement.color] || colorMap.gray;
  const unlockedColors = isUnlocked ? colors : colorMap.gray;

  return (
    <motion.div
      ref={cardRef}
      key={achievement.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className={`bg-black/40 backdrop-blur-sm border ${unlockedColors.border} rounded-2xl p-6 relative overflow-hidden h-full flex flex-col`}
    >
      {showConfetti && cardRef.current && (
        <ReactConfetti width={dimensions.width} height={dimensions.height} numberOfPieces={200} recycle={false} gravity={0.15} colors={colors.confetti} style={{ position: 'absolute', top: 0, left: 0 }} />
      )}
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${unlockedColors.bgOpacity}`}>{achievement.icon}</div>
        {isUnlocked && <Award className={`w-6 h-6 ${colors.text}`} />}
      </div>
      <h3 className="text-lg font-bold text-white mb-2">{achievement.title}</h3>
      <p className="text-gray-400 text-sm mb-4 flex-grow">{achievement.description}</p>
      <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden mt-auto">
        <motion.div initial={{ width: 0 }} animate={{ width: `${progress}%` }} transition={{ duration: 1, ease: "easeOut" }} className={`h-full ${unlockedColors.bg}`} />
      </div>
      <div className="mt-2 flex justify-between text-sm">
        <span className={unlockedColors.text}>{currentValue.toFixed(0)} / {achievement.target}</span>
        <span className={unlockedColors.text}>{progress.toFixed(0)}%</span>
      </div>
      {isUnlocked && <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className={`absolute inset-0 ${colors.bgOverlay} pointer-events-none`} />}
    </motion.div>
  );
};

// --- Main Milestone Component ---
interface MilestoneProps {
  analytics: Analytics;
  previousAnalytics: Analytics | undefined;
  onAchievementUnlock?: (achievement: Achievement) => void;
}
export const Milestone: React.FC<MilestoneProps> = ({ 
  analytics, 
  previousAnalytics, 
  onAchievementUnlock = () => {} 
}) => {
  const baseAchievements: Omit<Achievement, 'currentValue'>[] = [
    { id: 'co2-saver-1', title: 'Carbon Warrior', description: 'Save 1,000 kg of CO₂.', icon: <Leaf className="w-8 h-8 text-emerald-400" />, target: 1000, color: 'emerald', reward: "You've earned a 'Green Commute' badge!", analyticsKey: 'totalCO2SavedKg' },
    { id: 'co2-saver-2', title: 'Climate Guardian', description: 'Save 5,000 kg of CO₂.', icon: <TreesIcon className="w-8 h-8 text-green-400" />, target: 5000, color: 'green', reward: 'Free subscription to an eco-magazine!', analyticsKey: 'totalCO2SavedKg' },
    { id: 'optimization-master', title: 'Optimization Master', description: 'Complete 100 code optimizations.', icon: <Code className="w-8 h-8 text-blue-400" />, target: 100, color: 'blue', reward: 'Unlock the exclusive "Code Artisan" theme.', analyticsKey: 'totalOptimizations' },
    { id: 'performance-guru', title: 'Performance Guru', description: 'Achieve 50% performance improvement.', icon: <Zap className="w-8 h-8 text-yellow-400" />, target: 50, color: 'yellow', reward: 'Access to our advanced performance workshop.', analyticsKey: 'averagePerformanceImprovement' },
    { id: 'security-expert', title: 'Security Expert', description: 'Fix 50 security issues.', icon: <Shield className="w-8 h-8 text-red-400" />, target: 50, color: 'red', reward: 'You are now a "Digital Sentinel"!', analyticsKey: 'totalSecurityIssuesFixed' },
    { id: 'build-optimizer', title: 'Build Optimizer', description: 'Reduce build time by 30%.', icon: <Cpu className="w-8 h-8 text-purple-400" />, target: 30, color: 'purple', reward: 'Gain priority access to build servers.', analyticsKey: 'averageBuildTimeReduction' },
    { id: 'git-master', title: 'Git Master', description: 'Optimize 20 different repositories.', icon: <GitBranch className="w-8 h-8 text-orange-400" />, target: 20, color: 'orange', reward: 'Your profile now features the "Repo Wrangler" title.', analyticsKey: 'totalRepositoriesOptimized' },
  ];

  const achievements: Achievement[] = baseAchievements.map(a => ({
    ...a,
    currentValue: a.analyticsKey !== 'calculated' ? analytics[a.analyticsKey] : 0,
  }));

  const completedAchievementsCount = achievements.filter(a => a.currentValue >= a.target).length;

  const legendaryAchievement: Achievement = {
    id: 'legendary-optimizer', title: 'Legendary Optimizer', description: 'Complete all other achievements.', icon: <Trophy className="w-8 h-8 text-amber-400" />, target: achievements.length, currentValue: completedAchievementsCount, color: 'amber', reward: 'You are a true legend! All features unlocked.', analyticsKey: 'calculated',
  };

  const allAchievements = [...achievements, legendaryAchievement];

  const getPreviousValue = (achievement: Achievement): number => {
    if (!previousAnalytics) return 0;
    if (achievement.analyticsKey === 'calculated') {
        return baseAchievements.filter(a => a.analyticsKey !== 'calculated' && (previousAnalytics[a.analyticsKey] || 0) >= a.target).length;
    }
    return previousAnalytics[achievement.analyticsKey] || 0;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {allAchievements.map((achievement) => (
        <AchievementCard
          key={achievement.id}
          achievement={achievement}
          previousValue={getPreviousValue(achievement)}
          onUnlock={onAchievementUnlock}
        />
      ))}
    </div>
  );
};

// --- Main App Component to control and simulate data ---
export default function App() {
  const [analytics, setAnalytics] = useState<Analytics>({
    totalCO2SavedKg: 0, totalOptimizations: 0, averagePerformanceImprovement: 0, totalSecurityIssuesFixed: 0, averageBuildTimeReduction: 0, totalRepositoriesOptimized: 0,
  });
  const [unlockedReward, setUnlockedReward] = useState<Achievement | null>(null);

  const previousAnalyticsRef = useRef<Analytics>();
  useEffect(() => {
    previousAnalyticsRef.current = analytics;
  });
  const previousAnalytics = previousAnalyticsRef.current;

  const handleProgress = (key: keyof Analytics, value: number) => {
    setAnalytics(prev => ({ ...prev, [key]: prev[key] + value }));
  };

  const resetProgress = () => {
    setAnalytics({ totalCO2SavedKg: 0, totalOptimizations: 0, averagePerformanceImprovement: 0, totalSecurityIssuesFixed: 0, averageBuildTimeReduction: 0, totalRepositoriesOptimized: 0 });
  };

  return (
    <div className="bg-gray-900 text-white min-h-screen p-4 sm:p-6 lg:p-8 font-sans">
      <RewardModal achievement={unlockedReward} onClose={() => setUnlockedReward(null)} />
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl">Your Achievements</h1>
          <p className="mt-4 text-lg text-gray-400">Track your progress and unlock new milestones. Complete a milestone to see a surprise!</p>
        </header>

        <main>
          <Milestone analytics={analytics} previousAnalytics={previousAnalytics} onAchievementUnlock={setUnlockedReward} />
        </main>

        <footer className="mt-12 pt-8 border-t border-gray-800">
          <h2 className="text-xl font-bold mb-4">Simulation Controls</h2>
          <p className="text-gray-400 mb-6">Use these buttons to simulate progress and test the animations.</p>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <button onClick={() => handleProgress('totalCO2SavedKg', 500)} className="bg-emerald-600 hover:bg-emerald-700 p-3 rounded-lg transition-colors">Add 500 CO₂ Saved</button>
            <button onClick={() => handleProgress('totalOptimizations', 10)} className="bg-blue-600 hover:bg-blue-700 p-3 rounded-lg transition-colors">Add 10 Optimizations</button>
            <button onClick={() => handleProgress('averagePerformanceImprovement', 5)} className="bg-yellow-600 hover:bg-yellow-700 p-3 rounded-lg transition-colors">Add 5% Performance</button>
            <button onClick={() => handleProgress('totalSecurityIssuesFixed', 5)} className="bg-red-600 hover:bg-red-700 p-3 rounded-lg transition-colors">Fix 5 Security Issues</button>
            <button onClick={() => handleProgress('averageBuildTimeReduction', 3)} className="bg-purple-600 hover:bg-purple-700 p-3 rounded-lg transition-colors">Add 3% Build Reduction</button>
            <button onClick={() => handleProgress('totalRepositoriesOptimized', 2)} className="bg-orange-600 hover:bg-orange-700 p-3 rounded-lg transition-colors">Optimize 2 Repos</button>
            <button onClick={resetProgress} className="bg-gray-600 hover:bg-gray-700 p-3 rounded-lg transition-colors col-span-2 md:col-span-1 lg:col-span-2">Reset All Progress</button>
          </div>
        </footer>
      </div>
    </div>
  );
}
