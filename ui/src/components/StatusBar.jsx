import { motion, AnimatePresence } from 'framer-motion';
import { Clock, Cpu, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import './StatusBar.css';

const STATUS_MAP = {
  idle: { label: 'Ready', icon: Cpu, className: 'statusbar-idle' },
  running: { label: 'Agents Working', icon: Loader2, className: 'statusbar-running' },
  complete: { label: 'Complete', icon: CheckCircle2, className: 'statusbar-complete' },
  error: { label: 'Error', icon: XCircle, className: 'statusbar-error' },
};

export default function StatusBar({ status, progress, elapsed, taskCount }) {
  const config = STATUS_MAP[status] || STATUS_MAP.idle;
  const StatusIcon = config.icon;

  return (
    <AnimatePresence>
      <motion.div
        className={`statusbar glass-card-static ${config.className}`}
        initial={{ y: 60, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      >
        <div className="statusbar-left">
          <motion.div
            className="statusbar-icon-wrap"
            animate={status === 'running' ? { rotate: 360 } : {}}
            transition={status === 'running' ? { duration: 2, repeat: Infinity, ease: 'linear' } : {}}
          >
            <StatusIcon size={16} />
          </motion.div>
          <span className="statusbar-label">{config.label}</span>
        </div>

        {status !== 'idle' && (
          <div className="statusbar-center">
            <div className="progress-bar statusbar-progress">
              <motion.div
                className="progress-bar-fill"
                initial={{ width: '0%' }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            <span className="statusbar-progress-text">
              {Math.round(progress)}%
            </span>
          </div>
        )}

        <div className="statusbar-right">
          {elapsed > 0 && (
            <span className="statusbar-meta">
              <Clock size={12} />
              {elapsed}s
            </span>
          )}
          {taskCount > 0 && (
            <span className="statusbar-meta">
              Tasks: {taskCount}/6
            </span>
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
