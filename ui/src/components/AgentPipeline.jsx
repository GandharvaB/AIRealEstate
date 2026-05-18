import { motion } from 'framer-motion';
import { Workflow } from 'lucide-react';
import AgentCard from './AgentCard';
import './AgentPipeline.css';

const AGENTS = [
  {
    id: 'real_estate_data_researcher',
    name: 'Data Researcher',
    role: 'Real Estate Data Researcher',
    tools: ['RealEstateApiTool', '99acresIndiaTool'],
    icon: '🔍',
    color: '#3b82f6',
    description: 'Searches US & India APIs for listings',
  },
  {
    id: 'property_development_analyst',
    name: 'Dev Analyst',
    role: 'Property Development Analyst',
    tools: ['PropertyScoringTool', 'SarvamAnalysisTool'],
    icon: '📊',
    color: '#10b981',
    description: 'Scores development potential',
  },
  {
    id: 'api_response_manager',
    name: 'API Manager',
    role: 'API Response Manager',
    tools: ['SarvamResponseGenerator'],
    icon: '🔌',
    color: '#f59e0b',
    description: 'Formats RESTful JSON responses',
  },
  {
    id: 'information_collector',
    name: 'Info Collector',
    role: 'Information Collector',
    tools: ['FileReadTool'],
    icon: '📦',
    color: '#8b5cf6',
    description: 'Aggregates all agent outputs',
  },
  {
    id: 'client_presentation_specialist',
    name: 'Presentation',
    role: 'Client Presentation Specialist',
    tools: ['FileReadTool'],
    icon: '📄',
    color: '#f43f5e',
    description: 'Creates client-ready reports',
  },
  {
    id: 'workflow_supervisor',
    name: 'Supervisor',
    role: 'Workflow Supervisor',
    tools: ['FileReadTool'],
    icon: '👁️',
    color: '#06b6d4',
    description: 'Monitors quality & workflow',
  },
];

export default function AgentPipeline({ agentStatuses }) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.2 },
    },
  };

  return (
    <div className="section">
      <motion.div
        className="section-header"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Workflow size={20} className="section-icon" />
        <h2 className="section-title">Agent Pipeline</h2>
        <span className="pipeline-process-badge">Sequential Process</span>
      </motion.div>

      <motion.div
        className="pipeline-container"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {AGENTS.map((agent, index) => (
          <div key={agent.id} className="pipeline-node">
            <AgentCard
              agent={agent}
              status={agentStatuses[agent.id] || 'idle'}
              index={index}
            />
            {index < AGENTS.length - 1 && (
              <motion.div
                className="pipeline-connector"
                initial={{ scaleX: 0 }}
                animate={{ scaleX: 1 }}
                transition={{ delay: 0.3 + index * 0.1, duration: 0.4 }}
              >
                <div
                  className={`pipeline-connector-line ${
                    agentStatuses[AGENTS[index + 1]?.id] === 'complete' ||
                    agentStatuses[AGENTS[index + 1]?.id] === 'working'
                      ? 'pipeline-connector-active'
                      : ''
                  }`}
                />
                <motion.div
                  className="pipeline-connector-dot"
                  animate={
                    agentStatuses[AGENTS[index + 1]?.id] === 'working'
                      ? { scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }
                      : {}
                  }
                  transition={{ duration: 1.2, repeat: Infinity }}
                />
              </motion.div>
            )}
          </div>
        ))}
      </motion.div>
    </div>
  );
}
