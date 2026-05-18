import { motion } from 'framer-motion';
import { Bot, Zap, Globe } from 'lucide-react';
import './HeroBanner.css';

const floatingParticles = Array.from({ length: 20 }, (_, i) => ({
  id: i,
  x: Math.random() * 100,
  y: Math.random() * 100,
  size: Math.random() * 3 + 1,
  duration: Math.random() * 10 + 15,
  delay: Math.random() * 5,
}));

export default function HeroBanner() {
  return (
    <div className="hero-banner">
      {/* Floating particles */}
      <div className="hero-particles">
        {floatingParticles.map((p) => (
          <motion.div
            key={p.id}
            className="hero-particle"
            style={{
              left: `${p.x}%`,
              top: `${p.y}%`,
              width: p.size,
              height: p.size,
            }}
            animate={{
              y: [-20, 20, -20],
              x: [-10, 10, -10],
              opacity: [0.2, 0.6, 0.2],
            }}
            transition={{
              duration: p.duration,
              delay: p.delay,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
          />
        ))}
      </div>

      <motion.div
        className="hero-content"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.25, 0.46, 0.45, 0.94] }}
      >
        <motion.div
          className="hero-badge"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2, duration: 0.5 }}
        >
          <Zap size={14} />
          <span>Powered by CrewAI + Sarvam AI + 99acres</span>
        </motion.div>

        <motion.h1
          className="hero-title"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.7 }}
        >
          <span className="hero-title-gradient">Multi-Agent</span>
          <br />
          Real Estate Intelligence
        </motion.h1>

        <motion.p
          className="hero-subtitle"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.6 }}
        >
          6 AI agents working in concert to research, analyze, and deliver
          comprehensive property insights across US & India with crew-level supervision.
        </motion.p>

        <motion.div
          className="hero-stats"
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.6 }}
        >
          <div className="hero-stat">
            <Bot size={18} className="hero-stat-icon" />
            <span className="hero-stat-value">6</span>
            <span className="hero-stat-label">Agents</span>
          </div>
          <div className="hero-stat-divider" />
          <div className="hero-stat">
            <Zap size={18} className="hero-stat-icon" />
            <span className="hero-stat-value">5</span>
            <span className="hero-stat-label">Custom Tools</span>
          </div>
          <div className="hero-stat-divider" />
          <div className="hero-stat">
            <Globe size={18} className="hero-stat-icon" />
            <span className="hero-stat-value">4</span>
            <span className="hero-stat-label">API Sources</span>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
