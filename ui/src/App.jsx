import { useState, useCallback, useRef } from 'react';
import { AnimatePresence } from 'framer-motion';
import HeroBanner from './components/HeroBanner';
import SearchPanel from './components/SearchPanel';
import AgentPipeline from './components/AgentPipeline';
import ResultsDashboard from './components/ResultsDashboard';
import LogStream from './components/LogStream';
import StatusBar from './components/StatusBar';
import './App.css';

const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : '';

const AGENT_ORDER = [
  'real_estate_data_researcher',
  'property_development_analyst',
  'api_response_manager',
  'information_collector',
  'client_presentation_specialist',
  'workflow_supervisor',
];

const DEMO_PROPERTIES = [
  {
    plot_id: 'PROP-001',
    address: '1234 Innovation Drive, San Francisco, CA 94102',
    price: 2850000,
    size_in_acres: 3.5,
    zoning_classification: 'Mixed-Use',
    listing_url: 'https://zillow.com/homedetails/1234_zpid/',
    development_score: 87,
    risk_level: 'Low',
    suitability_summary: 'EXCELLENT development opportunity at 1234 Innovation Drive. Outstanding value at $814,286 per acre. Good-sized 3.5-acre parcel offers substantial development flexibility. Mixed-Use zoning provides maximum development flexibility. Investment risk level: Low. Located near tech hub and business district with high growth potential.',
    analysis_details: {
      key_factors: {
        strengths: ['Excellent price per acre value', 'Favorable zoning classification', 'Strong location desirability', 'Near major transportation hub'],
        concerns: [],
        recommendations: ['Strong candidate for development - consider fast-tracking due diligence'],
      },
    },
  },
  {
    plot_id: 'PROP-002',
    address: '567 Waterfront Blvd, San Francisco, CA 94158',
    price: 5200000,
    size_in_acres: 2.1,
    zoning_classification: 'Commercial',
    listing_url: 'https://zillow.com/homedetails/567_zpid/',
    development_score: 72,
    risk_level: 'Medium-Low',
    suitability_summary: 'STRONG development potential at 567 Waterfront Blvd. Premium pricing at $2,476,190 per acre may limit returns. Moderate 2.1-acre size allows for focused development. Commercial zoning offers good development options. Investment risk level: Medium-Low.',
    analysis_details: {
      key_factors: {
        strengths: ['Favorable zoning classification', 'Strong location desirability', 'Waterfront premium location'],
        concerns: ['High price per acre may impact ROI'],
        recommendations: ['Consider detailed market analysis before proceeding'],
      },
    },
  },
  {
    plot_id: 'PROP-003',
    address: '890 Valley Road, Daly City, CA 94015',
    price: 980000,
    size_in_acres: 5.8,
    zoning_classification: 'Residential',
    listing_url: 'https://zillow.com/homedetails/890_zpid/',
    development_score: 68,
    risk_level: 'Medium',
    suitability_summary: 'GOOD development opportunity at 890 Valley Road. Good value proposition at $168,966 per acre. Good-sized 5.8-acre property supports meaningful development. Residential zoning offers good development options. Investment risk level: Medium.',
    analysis_details: {
      key_factors: {
        strengths: ['Excellent price per acre value', 'Good development scale potential'],
        concerns: ['Below-average overall development potential'],
        recommendations: ['Investigate zoning variance or rezoning opportunities'],
      },
    },
  },
  {
    plot_id: 'PROP-004',
    address: '2100 Tech Park Way, South San Francisco, CA 94080',
    price: 4100000,
    size_in_acres: 8.2,
    zoning_classification: 'Industrial',
    listing_url: 'https://zillow.com/homedetails/2100_zpid/',
    development_score: 78,
    risk_level: 'Medium-Low',
    suitability_summary: 'STRONG development potential at 2100 Tech Park Way. Good value proposition at $500,000 per acre. Large 8.2-acre parcel offers substantial development flexibility. Industrial zoning with proximity to biotech corridor. Investment risk level: Medium-Low.',
    analysis_details: {
      key_factors: {
        strengths: ['Good development scale potential', 'Favorable zoning classification', 'Near growth corridor'],
        concerns: [],
        recommendations: ['Strong candidate for development - consider fast-tracking due diligence'],
      },
    },
  },
  {
    plot_id: 'PROP-005',
    address: '445 Sunset Heights, Pacifica, CA 94044',
    price: 1650000,
    size_in_acres: 12.3,
    zoning_classification: 'Agricultural',
    listing_url: 'https://zillow.com/homedetails/445_zpid/',
    development_score: 52,
    risk_level: 'Medium-High',
    suitability_summary: 'MODERATE development potential at 445 Sunset Heights. Outstanding value at $134,146 per acre. Large 12.3-acre parcel offers substantial development flexibility. Agricultural zoning may limit development scope. Investment risk level: Medium-High.',
    analysis_details: {
      key_factors: {
        strengths: ['Excellent price per acre value', 'Good development scale potential'],
        concerns: ['Below-average overall development potential', 'Limited size constrains development options'],
        recommendations: ['Investigate zoning variance or rezoning opportunities', 'Consider detailed market analysis before proceeding'],
      },
    },
  },
];

const DEMO_LOGS = [
  { agent: 'System', message: 'Crew kickoff initiated with sequential process', delay: 0 },
  { agent: 'Data Researcher', message: 'Starting property search for San Francisco, CA (5 mile radius)', delay: 800 },
  { agent: 'Data Researcher', message: 'Geocoded target location: 37.7749, -122.4194', delay: 1600 },
  { agent: 'Data Researcher', message: 'Querying Zillow API via RapidAPI...', delay: 2400 },
  { agent: 'Data Researcher', message: 'Querying ATTOM Data API...', delay: 3200 },
  { agent: 'Data Researcher', message: 'Found 12 properties, filtered to 5 matching criteria', delay: 4500 },
  { agent: 'Data Researcher', message: '\u2713 Task complete: research_properties_data', delay: 5500 },
  { agent: 'Dev Analyst', message: 'Starting development potential analysis for 5 properties', delay: 6500 },
  { agent: 'Dev Analyst', message: 'Calculating composite scores (price, size, zoning, location, trends)', delay: 7500 },
  { agent: 'Dev Analyst', message: 'Calling Sarvam AI for suitability summaries...', delay: 8500 },
  { agent: 'Dev Analyst', message: 'Analysis complete: scores range 52-87, avg 71.4', delay: 10000 },
  { agent: 'Dev Analyst', message: '\u2713 Task complete: analyze_development_potential', delay: 11000 },
  { agent: 'API Manager', message: 'Formatting RESTful JSON API response', delay: 12000 },
  { agent: 'API Manager', message: 'Generating professional summary via Sarvam AI...', delay: 13000 },
  { agent: 'API Manager', message: 'Response structure: 200 OK, 5 properties, full metadata', delay: 14000 },
  { agent: 'API Manager', message: '\u2713 Task complete: generate_api_response', delay: 15000 },
  { agent: 'Info Collector', message: 'Aggregating outputs from 3 upstream agents', delay: 16000 },
  { agent: 'Info Collector', message: 'Cross-referencing data completeness...', delay: 17000 },
  { agent: 'Info Collector', message: '\u2713 Task complete: collect_agent_information', delay: 18500 },
  { agent: 'Presentation', message: 'Generating client-ready presentation for Property Developer', delay: 19500 },
  { agent: 'Presentation', message: 'Formatting executive summary with key highlights', delay: 20500 },
  { agent: 'Presentation', message: '\u2713 Task complete: format_client_presentation', delay: 22000 },
  { agent: 'Supervisor', message: 'Monitoring workflow quality and completeness', delay: 23000 },
  { agent: 'Supervisor', message: 'All 6 tasks completed successfully. No errors detected.', delay: 24000 },
  { agent: 'Supervisor', message: 'Quality assessment: HIGH - all outputs meet standards', delay: 25000 },
  { agent: 'Supervisor', message: '\u2713 Task complete: supervise_and_monitor_workflow', delay: 26000 },
  { agent: 'System', message: 'Crew execution completed successfully in 26.2s', delay: 27000 },
];

const DEMO_PROPERTIES_INDIA = [
  {
    plot_id: '99A-G86505820',
    address: 'Uran, Navi Mumbai, Maharashtra',
    price: 45000000,
    size_in_acres: null,
    size: '2057 sq.yd',
    zoning_classification: 'Residential',
    listing_url: 'https://www.99acres.com/residential-land-plot-for-sale-in-uran-navi-mumbai-2057-sqyd-r1-spid-G86505820',
    development_score: 84,
    risk_level: 'Low',
    suitability_summary: 'EXCELLENT development opportunity in Uran, Navi Mumbai. Located near the upcoming Navi Mumbai International Airport (NMIA) and Atal Setu (MTHL). Part of the MMRDA development corridor with strong infrastructure support. Proximity to Reliance SEZ adds commercial value. Investment risk: Low.',
    analysis_details: {
      key_factors: {
        strengths: ['Near new international airport', 'MMRDA corridor location', 'Multiple transport links', 'Proximity to SEZ'],
        concerns: [],
        recommendations: ['Fast-track due diligence — high growth corridor'],
      },
    },
    source: '99acres.com',
    country: 'India',
  },
  {
    plot_id: '99A-W90799694',
    address: 'Borivali West, Mumbai, Maharashtra',
    price: 4000000,
    size_in_acres: null,
    size: '200 sq.ft',
    zoning_classification: 'Residential',
    listing_url: 'https://www.99acres.com/residential-land-plot-for-sale-in-borivali-west-mumbai-andheri-dahisar-22-sqyd-spid-W90799694',
    development_score: 62,
    risk_level: 'Medium',
    suitability_summary: 'GOOD compact residential plot in Borivali West. Freehold property at ₹40 Lakhs. Small plot area (200 sq.ft) suitable for individual home construction. Well-connected locality with metro and suburban rail access. Investment risk: Medium.',
    analysis_details: {
      key_factors: {
        strengths: ['Freehold ownership', 'Good connectivity (metro + rail)', 'Established residential area'],
        concerns: ['Compact plot limits development scope'],
        recommendations: ['Suitable for individual home, not large-scale development'],
      },
    },
    source: '99acres.com',
    country: 'India',
  },
  {
    plot_id: '99A-Q90363772',
    address: 'Walkeshwar, Malabar Hill, South Mumbai',
    price: 15000000000,
    size_in_acres: null,
    size: '1357 sq.yd',
    zoning_classification: 'Residential',
    listing_url: 'https://www.99acres.com/residential-land-plot-for-sale-in-walkeshwar-south-mumbai-1357-sqyd-spid-Q90363772',
    development_score: 95,
    risk_level: 'Low',
    suitability_summary: 'EXCEPTIONAL ultra-premium plot in Walkeshwar, Malabar Hill — the most prestigious address in South Mumbai. Unrestricted panoramic sea views. ~40,000 sq.ft construction potential. Only such plot available in South Mumbai. Asking: ₹1,500 Crores. Investment risk: Low (ultra-luxury segment).',
    analysis_details: {
      key_factors: {
        strengths: ['Most prestigious Mumbai location', 'Panoramic sea views', 'Massive construction potential', 'One-of-a-kind availability'],
        concerns: ['Ultra-high price point limits buyer pool'],
        recommendations: ['Target UHNW investors or luxury developers'],
      },
    },
    source: '99acres.com',
    country: 'India',
  },
  {
    plot_id: '99A-B86005830',
    address: 'Sion West, Mumbai, Maharashtra',
    price: 250000000,
    size_in_acres: null,
    size: '937.30 sq.mt',
    zoning_classification: 'Mixed-Use',
    listing_url: 'https://www.99acres.com/residential-land-plot-for-sale-in-sion-west-central-mumbai-suburbs-1121-sqyd-spid-B86005830',
    development_score: 79,
    risk_level: 'Medium-Low',
    suitability_summary: 'STRONG redevelopment opportunity in Sion West. Strategically situated near major highways, educational institutions, hospitals, and public transport. 937.30 sq.mt plot ideal for residential/commercial redevelopment. Investment risk: Medium-Low.',
    analysis_details: {
      key_factors: {
        strengths: ['Prime redevelopment potential', 'Excellent public transport access', 'Near railway station & bus depot', 'Established neighborhood'],
        concerns: ['Redevelopment approval process may take time'],
        recommendations: ['Commission site assessment and FSI study'],
      },
    },
    source: '99acres.com',
    country: 'India',
  },
  {
    plot_id: '99A-A91218710',
    address: 'Madh Island, Malad West, Mumbai',
    price: 2000000,
    size_in_acres: null,
    size: '1000 sq.ft',
    zoning_classification: 'Residential',
    listing_url: 'https://www.99acres.com/residential-land-plot-for-sale-in-madh-mumbai-andheri-dahisar-111-sqyd-spid-A91218710',
    development_score: 55,
    risk_level: 'Medium-High',
    suitability_summary: 'MODERATE potential at Madh Island. Freehold plot at ₹20 Lakhs — excellent entry price. Ready to move, 1000 sq.ft area. Scenic coastal location. Investment risk: Medium-High due to remote access and limited infrastructure.',
    analysis_details: {
      key_factors: {
        strengths: ['Very affordable entry price', 'Freehold ownership', 'Scenic coastal location'],
        concerns: ['Remote access', 'Limited infrastructure', 'CRZ regulations may apply'],
        recommendations: ['Verify CRZ clearances before purchase'],
      },
    },
    source: '99acres.com',
    country: 'India',
  },
];

const INDIA_CITIES = [
  'mumbai', 'delhi', 'bangalore', 'bengaluru', 'hyderabad', 'pune', 'chennai',
  'kolkata', 'ahmedabad', 'jaipur', 'lucknow', 'noida', 'gurgaon', 'gurugram',
  'thane', 'navi mumbai', 'goa', 'chandigarh', 'indore', 'bhopal', 'nagpur',
  'nashik', 'surat', 'vadodara', 'kochi', 'coimbatore', 'mysore', 'mysuru',
  'dehradun', 'mangalore', 'trivandrum', 'india', 'visakhapatnam',
];

function isIndiaLocation(location) {
  const loc = (location || '').toLowerCase().trim();
  return INDIA_CITIES.some((city) => loc.includes(city));
}

function formatINR(amount) {
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)} Cr`;
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)} L`;
  return `₹${amount.toLocaleString('en-IN')}`;
}

const DEMO_LOGS_INDIA = [
  { agent: 'System', message: 'Crew kickoff initiated with sequential process', delay: 0 },
  { agent: 'Data Researcher', message: 'Detected India location — activating 99acres.com pipeline', delay: 800 },
  { agent: 'Data Researcher', message: 'Connecting to 99acres.com India property portal...', delay: 1600 },
  { agent: 'Data Researcher', message: 'Fetching property listings from 99acres.com...', delay: 2400 },
  { agent: 'Data Researcher', message: 'Fetching price trends and locality data...', delay: 3200 },
  { agent: 'Data Researcher', message: 'Found 25 properties, filtered to 5 matching criteria', delay: 4500 },
  { agent: 'Data Researcher', message: '\u2713 Task complete: research_properties_data (via 99acres)', delay: 5500 },
  { agent: 'Dev Analyst', message: 'Starting development potential analysis for 5 Indian properties', delay: 6500 },
  { agent: 'Dev Analyst', message: 'Calculating scores: price/sqft, FSI potential, location, connectivity', delay: 7500 },
  { agent: 'Dev Analyst', message: 'Calling Sarvam AI for India-specific suitability analysis...', delay: 8500 },
  { agent: 'Dev Analyst', message: 'Analysis complete: scores range 55-95, avg 75.0', delay: 10000 },
  { agent: 'Dev Analyst', message: '\u2713 Task complete: analyze_development_potential', delay: 11000 },
  { agent: 'API Manager', message: 'Formatting RESTful JSON response with INR pricing', delay: 12000 },
  { agent: 'API Manager', message: 'Generating professional summary via Sarvam AI...', delay: 13000 },
  { agent: 'API Manager', message: 'Response: 200 OK, 5 properties, 99acres source metadata', delay: 14000 },
  { agent: 'API Manager', message: '\u2713 Task complete: generate_api_response', delay: 15000 },
  { agent: 'Info Collector', message: 'Aggregating outputs from 3 upstream agents', delay: 16000 },
  { agent: 'Info Collector', message: 'Cross-referencing 99acres data with price trends...', delay: 17000 },
  { agent: 'Info Collector', message: '\u2713 Task complete: collect_agent_information', delay: 18500 },
  { agent: 'Presentation', message: 'Generating client presentation with INR formatting', delay: 19500 },
  { agent: 'Presentation', message: 'Formatting executive summary with India market insights', delay: 20500 },
  { agent: 'Presentation', message: '\u2713 Task complete: format_client_presentation', delay: 22000 },
  { agent: 'Supervisor', message: 'Monitoring workflow quality and completeness', delay: 23000 },
  { agent: 'Supervisor', message: 'All 6 tasks completed. 99acres pipeline verified.', delay: 24000 },
  { agent: 'Supervisor', message: 'Quality assessment: HIGH — India data validated', delay: 25000 },
  { agent: 'Supervisor', message: '\u2713 Task complete: supervise_and_monitor_workflow', delay: 26000 },
  { agent: 'System', message: 'Crew execution completed successfully in 26.4s', delay: 27000 },
];

export default function App() {
  const [runStatus, setRunStatus] = useState('idle');
  const [agentStatuses, setAgentStatuses] = useState({});
  const [logs, setLogs] = useState([]);
  const [results, setResults] = useState(null);
  const [progress, setProgress] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [taskCount, setTaskCount] = useState(0);
  const timerRef = useRef(null);
  const demoTimeouts = useRef([]);

  const addLog = useCallback((agent, message) => {
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', {
      hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit',
    });
    setLogs((prev) => [...prev, { time, agent, message }]);
  }, []);

  const runDemoMode = useCallback((inputs) => {
    setRunStatus('running');
    setLogs([]);
    setResults(null);
    setProgress(0);
    setElapsed(0);
    setTaskCount(0);
    setAgentStatuses({});

    const isIndia = isIndiaLocation(inputs.target_location);
    const demoLogs = isIndia ? DEMO_LOGS_INDIA : DEMO_LOGS;
    const demoProps = isIndia ? DEMO_PROPERTIES_INDIA : DEMO_PROPERTIES;

    const startTime = Date.now();
    timerRef.current = setInterval(() => {
      setElapsed(Math.round((Date.now() - startTime) / 1000));
    }, 1000);

    demoLogs.forEach((log) => {
      const t = setTimeout(() => addLog(log.agent, log.message), log.delay);
      demoTimeouts.current.push(t);
    });

    const agentTimings = [
      { id: AGENT_ORDER[0], start: 800, end: 5500 },
      { id: AGENT_ORDER[1], start: 6500, end: 11000 },
      { id: AGENT_ORDER[2], start: 12000, end: 15000 },
      { id: AGENT_ORDER[3], start: 16000, end: 18500 },
      { id: AGENT_ORDER[4], start: 19500, end: 22000 },
      { id: AGENT_ORDER[5], start: 23000, end: 26000 },
    ];

    agentTimings.forEach(({ id, start, end }, index) => {
      const t1 = setTimeout(() => {
        setAgentStatuses((prev) => ({ ...prev, [id]: 'working' }));
        setProgress(((index) / 6) * 100 + 5);
        setTaskCount(index);
      }, start);

      const t2 = setTimeout(() => {
        setAgentStatuses((prev) => ({ ...prev, [id]: 'complete' }));
        setProgress(((index + 1) / 6) * 100);
        setTaskCount(index + 1);
      }, end);

      demoTimeouts.current.push(t1, t2);
    });

    const finalT = setTimeout(() => {
      clearInterval(timerRef.current);
      setRunStatus('complete');
      setProgress(100);
      setTaskCount(6);

      const loc = inputs.target_location || (isIndia ? 'Mumbai, India' : 'San Francisco, CA');
      const cityName = loc.split(',')[0].trim();

      if (isIndia) {
        setResults({
          properties: demoProps.map((p) => ({
            ...p,
            address: p.address.includes('Mumbai') ? p.address : p.address.replace(/^[^,]+/, cityName),
          })),
          metadata: {
            avg_score: 75,
            location: loc,
            api_sources: '99acres.com',
            currency: 'INR',
          },
          presentation: [
            'EXECUTIVE SUMMARY — India Property Development Analysis',
            '',
            `Target Area: ${loc}`,
            `Client Type: ${inputs.client_type || 'Property Developer'}`,
            `Data Source: 99acres.com (India)`,
            `Date: ${new Date().toLocaleDateString('en-IN')}`,
            '',
            'KEY FINDINGS',
            '• 5 properties identified from 99acres.com',
            '• Average development score: 75.0/100',
            '• Top property: Walkeshwar, Malabar Hill (Score: 95)',
            '• Price range: ₹20 Lakhs – ₹1,500 Crores',
            '• 3 properties rated Low to Medium-Low risk',
            '',
            'MARKET INSIGHTS (99acres Price Trends)',
            '• Avg price/sq.ft: ₹22,000 – ₹46,000',
            '• Highest growth: Navi Mumbai (airport corridor)',
            '• Premium locations: South Mumbai, Bandra, Powai',
            '',
            'RECOMMENDATIONS',
            '1. Fast-track Uran plot near NMIA corridor (Score: 84)',
            '2. Target UHNW investors for Walkeshwar opportunity',
            '3. Commission FSI study for Sion West redevelopment',
          ].join('\n'),
          supervisor_report: [
            'WORKFLOW MONITORING REPORT',
            '',
            'STATUS: All 6 agents completed successfully',
            'DATA SOURCE: 99acres.com (India Real Estate Portal)',
            'QUALITY: All outputs meet professional standards',
            '',
            'INDIA PIPELINE DETAILS',
            '• 99acres listings fetched: 25',
            '• Filtered results: 5 matching criteria',
            '• Price trends data: Available',
            '• Currency: Indian Rupees (INR)',
            '',
            'AGENT PERFORMANCE',
            '1. Data Researcher: 5.5s — 99acres India pipeline active',
            '2. Dev Analyst: 5.5s — India-specific scoring completed',
            '3. API Manager: 3s — INR-formatted response generated',
            '4. Info Collector: 2.5s — Full aggregation, no gaps',
            '5. Presentation: 2.5s — India market presentation ready',
            '6. Supervisor: 3s — Quality verified',
            '',
            'ALERTS: None',
            'OVERALL HEALTH: EXCELLENT',
          ].join('\n'),
        });
      } else {
        setResults({
          properties: demoProps.map((p) => ({
            ...p,
            address: p.address.replace('San Francisco', cityName),
          })),
          metadata: {
            avg_score: 71,
            location: loc,
            api_sources: 'Zillow, ATTOM',
          },
          presentation: [
            'EXECUTIVE SUMMARY — Property Development Analysis',
            '',
            `Target Area: ${loc} (${inputs.search_radius_miles || 5} mile radius)`,
            `Client Type: ${inputs.client_type || 'Property Developer'}`,
            `Date: ${new Date().toLocaleDateString()}`,
            '',
            'KEY FINDINGS',
            '• 5 properties identified matching search criteria',
            '• Average development score: 71.4/100',
            '• Top property: 1234 Innovation Drive (Score: 87)',
            '• Price range: $980K – $5.2M',
            '• 3 properties rated Low-Medium risk',
            '',
            'INVESTMENT HIGHLIGHTS',
            '• Best value: 445 Sunset Heights at $134K/acre (12.3 acres)',
            '• Highest potential: 1234 Innovation Drive with Mixed-Use zoning',
            '• Growth corridor: 2100 Tech Park Way near biotech hub',
            '',
            'RECOMMENDATIONS',
            '1. Fast-track due diligence on Innovation Drive (Score: 87)',
            '2. Explore rezoning for Sunset Heights agricultural parcel',
            '3. Commission detailed market study for Waterfront Blvd',
          ].join('\n'),
          supervisor_report: [
            'WORKFLOW MONITORING REPORT',
            '',
            'STATUS: All 6 agents completed successfully',
            'QUALITY: All outputs meet professional standards',
            'DATA INTEGRITY: No duplicates or data gaps detected',
            '',
            'PERFORMANCE METRICS',
            '• Total execution time: ~27 seconds',
            '• API calls: 4 (Zillow, ATTOM, Sarvam AI x2)',
            '• Properties processed: 12 found → 5 filtered',
            '• Analysis confidence: 0.92',
            '',
            'AGENT PERFORMANCE',
            '1. Data Researcher: 5.5s — Efficient multi-API search',
            '2. Dev Analyst: 5.5s — Comprehensive scoring completed',
            '3. API Manager: 3s — Clean JSON response generated',
            '4. Info Collector: 2.5s — Full aggregation, no gaps',
            '5. Presentation: 2.5s — Professional output formatted',
            '6. Supervisor: 3s — Quality verified',
            '',
            'ALERTS: None',
            'OVERALL HEALTH: EXCELLENT',
          ].join('\n'),
        });
      }
    }, 27500);
    demoTimeouts.current.push(finalT);
  }, [addLog]);

  const handleLaunch = useCallback(async (inputs) => {
    try {
      const response = await fetch(`${API_BASE}/api/status`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000),
      });
      if (response.ok) {
        const statusData = await response.json();
        if (statusData.mode === 'demo') {
          runDemoMode(inputs);
          return;
        }
        handleRealRun(inputs);
        return;
      }
    } catch {
      // Backend not available
    }
    runDemoMode(inputs);
  }, [runDemoMode]);

  const handleRealRun = async (inputs) => {
    setRunStatus('running');
    setLogs([]);
    setResults(null);
    setProgress(0);
    setElapsed(0);
    setTaskCount(0);
    setAgentStatuses({});

    const startTime = Date.now();
    timerRef.current = setInterval(() => {
      setElapsed(Math.round((Date.now() - startTime) / 1000));
    }, 1000);

    try {
      const runRes = await fetch(`${API_BASE}/api/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputs),
      });
      const { run_id } = await runRes.json();

      const eventSource = new EventSource(`${API_BASE}/api/stream/${run_id}`);

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.type === 'log') {
          addLog(data.agent || 'System', data.message);
        } else if (data.type === 'agent_status') {
          setAgentStatuses((prev) => ({ ...prev, [data.agent_id]: data.status }));
          if (data.task_index !== undefined) {
            setTaskCount(data.task_index + 1);
            setProgress(((data.task_index + 1) / 6) * 100);
          }
        } else if (data.type === 'complete') {
          clearInterval(timerRef.current);
          setRunStatus('complete');
          setProgress(100);
          setTaskCount(6);
          setResults(data.results);
          eventSource.close();
        } else if (data.type === 'error') {
          clearInterval(timerRef.current);
          setRunStatus('error');
          addLog('System', `Error: ${data.message}`);
          eventSource.close();
        }
      };

      eventSource.onerror = () => {
        clearInterval(timerRef.current);
        setRunStatus('error');
        addLog('System', 'Connection to backend lost');
        eventSource.close();
      };
    } catch (err) {
      clearInterval(timerRef.current);
      setRunStatus('error');
      addLog('System', `Failed to start crew: ${err.message}`);
    }
  };

  return (
    <>
      <div className="mesh-bg" />
      <div className="app-container">
        <HeroBanner />
        <SearchPanel onLaunch={handleLaunch} isRunning={runStatus === 'running'} />
        <AgentPipeline agentStatuses={agentStatuses} />
        <AnimatePresence>
          {logs.length > 0 && <LogStream logs={logs} />}
        </AnimatePresence>
        <ResultsDashboard results={results} isVisible={runStatus === 'complete'} />
        <div style={{ height: '60px' }} />
      </div>
      <StatusBar
        status={runStatus}
        progress={progress}
        elapsed={elapsed}
        taskCount={taskCount}
      />
    </>
  );
}
