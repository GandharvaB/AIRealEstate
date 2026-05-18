import { motion, AnimatePresence } from 'framer-motion';
import { BarChart3, AlertCircle } from 'lucide-react';
import PropertyCard from './PropertyCard';
import './ResultsDashboard.css';

export default function ResultsDashboard({ results, isVisible }) {
  if (!isVisible) return null;

  const properties = results?.properties || [];
  const metadata = results?.metadata || {};

  return (
    <AnimatePresence>
      <motion.div
        className="section"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
      >
        <div className="section-header">
          <BarChart3 size={20} className="section-icon" />
          <h2 className="section-title">Analysis Results</h2>
          {properties.length > 0 && (
            <span className="results-count-badge">
              {properties.length} Properties Found
            </span>
          )}
        </div>

        {/* Summary Stats */}
        {metadata && (
          <motion.div
            className="results-summary glass-card-static"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <div className="results-stat">
              <span className="results-stat-value">{properties.length}</span>
              <span className="results-stat-label">Properties</span>
            </div>
            <div className="results-stat-divider" />
            <div className="results-stat">
              <span className="results-stat-value">
                {metadata.avg_score ? `${metadata.avg_score}` : '—'}
              </span>
              <span className="results-stat-label">Avg Score</span>
            </div>
            <div className="results-stat-divider" />
            <div className="results-stat">
              <span className="results-stat-value">{metadata.location || '—'}</span>
              <span className="results-stat-label">Location</span>
            </div>
            <div className="results-stat-divider" />
            <div className="results-stat">
              <span className="results-stat-value">{metadata.api_sources || '—'}</span>
              <span className="results-stat-label">API Sources</span>
            </div>
          </motion.div>
        )}

        {/* Property Cards Grid */}
        {properties.length > 0 ? (
          <motion.div
            className="results-grid"
            initial="hidden"
            animate="visible"
            variants={{
              hidden: { opacity: 0 },
              visible: {
                opacity: 1,
                transition: { staggerChildren: 0.08, delayChildren: 0.3 },
              },
            }}
          >
            {properties.map((property, index) => (
              <PropertyCard key={property.plot_id || index} property={property} index={index} />
            ))}
          </motion.div>
        ) : (
          <motion.div
            className="results-empty glass-card-static"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
          >
            <AlertCircle size={32} className="results-empty-icon" />
            <p>No properties found matching your criteria.</p>
            <p className="results-empty-hint">Try adjusting your search parameters.</p>
          </motion.div>
        )}

        {/* Presentation Output */}
        {results?.presentation && (
          <motion.div
            className="results-presentation glass-card-static"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <h3 className="results-presentation-title">📄 Client Presentation</h3>
            <div className="results-presentation-content">
              {results.presentation}
            </div>
          </motion.div>
        )}

        {/* Supervisor Report */}
        {results?.supervisor_report && (
          <motion.div
            className="results-presentation glass-card-static"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <h3 className="results-presentation-title">👁️ Supervisor Report</h3>
            <div className="results-presentation-content">
              {results.supervisor_report}
            </div>
          </motion.div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
