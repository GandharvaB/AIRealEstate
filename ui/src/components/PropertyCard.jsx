import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  MapPin, DollarSign, Maximize2, Building2,
  ExternalLink, ChevronDown, TrendingUp, AlertTriangle, Shield
} from 'lucide-react';
import './PropertyCard.css';

const RISK_CONFIG = {
  Low: { badge: 'badge-emerald', icon: Shield },
  'Medium-Low': { badge: 'badge-cyan', icon: Shield },
  Medium: { badge: 'badge-amber', icon: AlertTriangle },
  'Medium-High': { badge: 'badge-amber', icon: AlertTriangle },
  High: { badge: 'badge-rose', icon: AlertTriangle },
};

function ScoreMeter({ score, size = 64 }) {
  const radius = (size - 8) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const getColor = (s) => {
    if (s >= 80) return '#10b981';
    if (s >= 60) return '#3b82f6';
    if (s >= 40) return '#f59e0b';
    return '#f43f5e';
  };

  return (
    <div className="score-meter" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          className="score-meter-bg"
          cx={size / 2}
          cy={size / 2}
          r={radius}
        />
        <motion.circle
          className="score-meter-fill"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={getColor(score)}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, delay: 0.3, ease: [0.4, 0, 0.2, 1] }}
        />
      </svg>
      <span className="score-meter-value" style={{ color: getColor(score) }}>
        {score}
      </span>
    </div>
  );
}

export default function PropertyCard({ property, index }) {
  const [expanded, setExpanded] = useState(false);

  const score = property.development_score || 0;
  const risk = property.risk_level || 'Medium';
  const riskConfig = RISK_CONFIG[risk] || RISK_CONFIG.Medium;
  const RiskIcon = riskConfig.icon;

  const isIndia = property.country === 'India' || (property.source || '').includes('99acres') || (property.source || '').includes('magicbricks');

  const formatPrice = (price) => {
    if (!price) return '—';
    if (isIndia) {
      if (price >= 10000000) return `₹${(price / 10000000).toFixed(1)} Cr`;
      if (price >= 100000) return `₹${(price / 100000).toFixed(1)} L`;
      return `₹${price.toLocaleString('en-IN')}`;
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
    }).format(price);
  };

  const sizeDisplay = property.size_in_acres
    ? `${property.size_in_acres} acres`
    : property.size || '—';

  return (
    <motion.div
      className="property-card glass-card"
      variants={{
        hidden: { opacity: 0, y: 20, scale: 0.97 },
        visible: { opacity: 1, y: 0, scale: 1 },
      }}
      transition={{ type: 'spring', stiffness: 250, damping: 22 }}
      layout
    >
      <div className="property-card-top">
        <div className="property-card-info">
          <div className="property-address">
            <MapPin size={14} className="property-icon-muted" />
            <span>{property.address || 'Unknown Address'}</span>
          </div>

          <div className="property-meta">
            <span className="property-meta-item">
              <DollarSign size={12} />
              {formatPrice(property.price)}
            </span>
            <span className="property-meta-item">
              <Maximize2 size={12} />
              {sizeDisplay}
            </span>
            <span className="property-meta-item">
              <Building2 size={12} />
              {property.zoning_classification || '—'}
            </span>
          </div>
        </div>

        <ScoreMeter score={score} />
      </div>

      {/* Risk & Score Badges */}
      <div className="property-badges">
        <span className={`badge ${riskConfig.badge}`}>
          <RiskIcon size={10} />
          {risk} Risk
        </span>
        <span className="badge badge-blue">
          <TrendingUp size={10} />
          Score: {score}/100
        </span>
      </div>

      {/* Suitability Summary */}
      {property.suitability_summary && (
        <div className="property-summary">
          <p className={`property-summary-text ${expanded ? '' : 'property-summary-clamped'}`}>
            {property.suitability_summary}
          </p>
          {property.suitability_summary.length > 150 && (
            <button
              className="property-expand-btn"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? 'Show less' : 'Show more'}
              <ChevronDown
                size={14}
                style={{ transform: expanded ? 'rotate(180deg)' : 'none', transition: '0.2s' }}
              />
            </button>
          )}
        </div>
      )}

      {/* Analysis Details (expanded) */}
      {expanded && property.analysis_details && (
        <motion.div
          className="property-details"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          {property.analysis_details.key_factors && (
            <>
              {property.analysis_details.key_factors.strengths?.length > 0 && (
                <div className="property-detail-section">
                  <h4 className="property-detail-title">✅ Strengths</h4>
                  <ul className="property-detail-list">
                    {property.analysis_details.key_factors.strengths.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}
              {property.analysis_details.key_factors.concerns?.length > 0 && (
                <div className="property-detail-section">
                  <h4 className="property-detail-title">⚠️ Concerns</h4>
                  <ul className="property-detail-list">
                    {property.analysis_details.key_factors.concerns.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                  </ul>
                </div>
              )}
              {property.analysis_details.key_factors.recommendations?.length > 0 && (
                <div className="property-detail-section">
                  <h4 className="property-detail-title">💡 Recommendations</h4>
                  <ul className="property-detail-list">
                    {property.analysis_details.key_factors.recommendations.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          )}
        </motion.div>
      )}

      {/* Footer */}
      {property.listing_url && (
        <a
          href={property.listing_url}
          target="_blank"
          rel="noopener noreferrer"
          className="property-link"
        >
          {isIndia
            ? (property.source || '').includes('magicbricks')
              ? 'View on MagicBricks'
              : 'View on 99acres'
            : 'View Listing'}{' '}
          <ExternalLink size={12} />
        </a>
      )}
    </motion.div>
  );
}
