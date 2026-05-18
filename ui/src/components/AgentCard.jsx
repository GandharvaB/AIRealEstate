import { motion } from 'framer-motion';
import { Wrench } from 'lucide-react';
import './AgentCard.css';

const STATUS_CONFIG = {
  idle: { label: 'Idle', className: 'status-idle', glow: false },
  working: { label: 'Working', className: 'status-working', glow: true },
  complete: { label: 'Complete', className: 'status-complete', glow: false },
  error: { label: 'Error', className: 'status-error', glow: false },
};

export default function AgentCard({ agent, status, index }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.idle;

  return (
    <motion.div
      className={`agent-card glass-card ${config.glow ? 'agent-card-glow' : ''}`}
      style={{ '--agent-color': agent.color }}
      variants={{
        hidden: { opacity: 0, y: 20, scale: 0.95 },
        visible: { opacity: 1, y: 0, scale: 1 },
      }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      whileHover={{ y: -4, boxShadow: `0 8px 30px ${agent.color}20` }}
    >
      {config.glow && (
        <motion.div
          className="agent-card-ring"
          style={{ borderColor: agent.color }}
          animate={{ opacity: [0.3, 0.7, 0.3] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}

      <div className="agent-card-header">
        <span className="agent-card-icon">{agent.icon}</span>
        <div className={`status-dot ${config.className}`} />
      </div>

      <h3 className="agent-card-name">{agent.name}</h3>
      <p className="agent-card-desc">{agent.description}</p>

      <div className="agent-card-tools">
        {agent.tools.map((tool) => (
          <span key={tool} className="agent-tool-badge">
            <Wrench size={10} />
            {tool}
          </span>
        ))}
      </div>

      <div className="agent-card-status">
        <span className={`agent-status-label agent-status-${status}`}>
          {config.label}
        </span>
      </div>
    </motion.div>
  );
}
