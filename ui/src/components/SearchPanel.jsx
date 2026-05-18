import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MapPin, Ruler, DollarSign, Building2, Trees,
  Users, Rocket, RotateCcw, ChevronDown
} from 'lucide-react';
import './SearchPanel.css';

const ZONING_OPTIONS = [
  { value: '', label: 'All Zoning Types' },
  { value: 'residential', label: 'Residential' },
  { value: 'commercial', label: 'Commercial' },
  { value: 'industrial', label: 'Industrial' },
  { value: 'mixed-use', label: 'Mixed-Use' },
  { value: 'agricultural', label: 'Agricultural' },
  { value: 'recreational', label: 'Recreational' },
];

const CLIENT_OPTIONS = [
  { value: 'developer', label: 'Property Developer' },
  { value: 'investor', label: 'Real Estate Investor' },
  { value: 'corporate', label: 'Corporate Client' },
  { value: 'individual', label: 'Individual Buyer' },
];

const defaultInputs = {
  target_location: '',
  search_radius_miles: '5',
  min_price: '',
  max_price: '',
  zoning_type: '',
  minimum_acres: '',
  source_agents: 'Real Estate Data Researcher, Property Development Analyst, API Response Manager',
  client_type: 'developer',
};

export default function SearchPanel({ onLaunch, isRunning }) {
  const [inputs, setInputs] = useState(defaultInputs);
  const [isExpanded, setIsExpanded] = useState(true);

  const handleChange = (field, value) => {
    setInputs((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputs.target_location.trim()) return;
    onLaunch(inputs);
  };

  const handleReset = () => {
    setInputs(defaultInputs);
  };

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        staggerChildren: 0.06,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 12 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      className="search-panel glass-card-static"
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <motion.div
        className="search-panel-header"
        variants={itemVariants}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="search-panel-title-group">
          <Rocket size={20} className="section-icon" />
          <h2 className="section-title">Configure Search</h2>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <ChevronDown size={20} className="search-panel-toggle" />
        </motion.div>
      </motion.div>

      <AnimatePresence>
        {isExpanded && (
          <motion.form
            className="search-form"
            onSubmit={handleSubmit}
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.35, ease: 'easeInOut' }}
          >
            <div className="search-grid">
              <motion.div className="form-group search-col-2" variants={itemVariants}>
                <label className="form-label" htmlFor="target_location">
                  <MapPin size={12} /> Target Location
                </label>
                <input
                  id="target_location"
                  className="form-input"
                  type="text"
                  placeholder="e.g., Mumbai, India or San Francisco, CA"
                  value={inputs.target_location}
                  onChange={(e) => handleChange('target_location', e.target.value)}
                  required
                />
              </motion.div>

              <motion.div className="form-group" variants={itemVariants}>
                <label className="form-label" htmlFor="search_radius">
                  <Ruler size={12} /> Radius (miles)
                </label>
                <input
                  id="search_radius"
                  className="form-input"
                  type="number"
                  placeholder="5"
                  min="1"
                  max="100"
                  value={inputs.search_radius_miles}
                  onChange={(e) => handleChange('search_radius_miles', e.target.value)}
                />
              </motion.div>

              <motion.div className="form-group" variants={itemVariants}>
                <label className="form-label" htmlFor="min_price">
                  <DollarSign size={12} /> Min Price
                </label>
                <input
                  id="min_price"
                  className="form-input"
                  type="number"
                  placeholder="e.g., 100000"
                  value={inputs.min_price}
                  onChange={(e) => handleChange('min_price', e.target.value)}
                />
              </motion.div>

              <motion.div className="form-group" variants={itemVariants}>
                <label className="form-label" htmlFor="max_price">
                  <DollarSign size={12} /> Max Price
                </label>
                <input
                  id="max_price"
                  className="form-input"
                  type="number"
                  placeholder="e.g., 5000000"
                  value={inputs.max_price}
                  onChange={(e) => handleChange('max_price', e.target.value)}
                />
              </motion.div>

              <motion.div className="form-group" variants={itemVariants}>
                <label className="form-label" htmlFor="zoning_type">
                  <Building2 size={12} /> Zoning Type
                </label>
                <select
                  id="zoning_type"
                  className="form-select"
                  value={inputs.zoning_type}
                  onChange={(e) => handleChange('zoning_type', e.target.value)}
                >
                  {ZONING_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </motion.div>

              <motion.div className="form-group" variants={itemVariants}>
                <label className="form-label" htmlFor="minimum_acres">
                  <Trees size={12} /> Min Acres
                </label>
                <input
                  id="minimum_acres"
                  className="form-input"
                  type="number"
                  step="0.1"
                  placeholder="e.g., 1.0"
                  value={inputs.minimum_acres}
                  onChange={(e) => handleChange('minimum_acres', e.target.value)}
                />
              </motion.div>

              <motion.div className="form-group" variants={itemVariants}>
                <label className="form-label" htmlFor="client_type">
                  <Users size={12} /> Client Type
                </label>
                <select
                  id="client_type"
                  className="form-select"
                  value={inputs.client_type}
                  onChange={(e) => handleChange('client_type', e.target.value)}
                >
                  {CLIENT_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </motion.div>
            </div>

            <motion.div className="search-actions" variants={itemVariants}>
              <button
                type="button"
                className="btn btn-ghost"
                onClick={handleReset}
                disabled={isRunning}
              >
                <RotateCcw size={16} />
                Reset
              </button>
              <button
                type="submit"
                className="btn btn-primary btn-lg"
                disabled={isRunning || !inputs.target_location.trim()}
              >
                {isRunning ? (
                  <>
                    <motion.div
                      className="btn-spinner"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    />
                    Agents Working...
                  </>
                ) : (
                  <>
                    <Rocket size={18} />
                    Launch Agents
                  </>
                )}
              </button>
            </motion.div>
          </motion.form>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
