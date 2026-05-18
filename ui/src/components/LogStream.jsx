import { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Terminal, Pause, Play, Trash2 } from 'lucide-react';
import './LogStream.css';

const AGENT_COLORS = {
  'Data Researcher': '#3b82f6',
  'Dev Analyst': '#10b981',
  'API Manager': '#f59e0b',
  'Info Collector': '#8b5cf6',
  'Presentation': '#f43f5e',
  'Supervisor': '#06b6d4',
  'System': '#6b6b80',
};

export default function LogStream({ logs }) {
  const containerRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [isExpanded, setIsExpanded] = useState(true);

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const handleScroll = () => {
    if (!containerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 40;
    setAutoScroll(isAtBottom);
  };

  if (!isExpanded) {
    return (
      <motion.div
        className="log-stream-minimized glass-card-static"
        onClick={() => setIsExpanded(true)}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <Terminal size={16} />
        <span>Agent Logs ({logs.length})</span>
        <div className="log-stream-dot-indicator">
          {logs.length > 0 && (
            <motion.div
              className="status-dot status-working"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
          )}
        </div>
      </motion.div>
    );
  }

  return (
    <div className="section">
      <div className="section-header">
        <Terminal size={20} className="section-icon" />
        <h2 className="section-title">Agent Activity Log</h2>
        <div className="log-stream-actions">
          <button
            className="log-action-btn"
            onClick={() => setAutoScroll(!autoScroll)}
            title={autoScroll ? 'Pause auto-scroll' : 'Resume auto-scroll'}
          >
            {autoScroll ? <Pause size={14} /> : <Play size={14} />}
          </button>
          <button
            className="log-action-btn"
            onClick={() => setIsExpanded(false)}
            title="Minimize"
          >
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      <div
        className="log-stream-container glass-card-static"
        ref={containerRef}
        onScroll={handleScroll}
      >
        <AnimatePresence initial={false}>
          {logs.length === 0 ? (
            <div className="log-stream-empty">
              <Terminal size={20} className="log-stream-empty-icon" />
              <p>Waiting for agent activity...</p>
            </div>
          ) : (
            logs.map((log, index) => (
              <motion.div
                key={index}
                className="log-entry"
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2 }}
              >
                <span className="log-time">{log.time}</span>
                <span
                  className="log-agent"
                  style={{ color: AGENT_COLORS[log.agent] || AGENT_COLORS.System }}
                >
                  [{log.agent}]
                </span>
                <span className="log-message">{log.message}</span>
              </motion.div>
            ))
          )}
        </AnimatePresence>

        {!autoScroll && logs.length > 0 && (
          <motion.button
            className="log-scroll-btn"
            onClick={() => {
              setAutoScroll(true);
              containerRef.current?.scrollTo({
                top: containerRef.current.scrollHeight,
                behavior: 'smooth',
              });
            }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            ↓ Scroll to bottom
          </motion.button>
        )}
      </div>
    </div>
  );
}
