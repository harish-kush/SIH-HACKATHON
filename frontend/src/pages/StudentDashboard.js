import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { 
  AcademicCapIcon, 
  ChartBarIcon, 
  ExclamationTriangleIcon,
  ChatBubbleLeftRightIcon,
  CalendarDaysIcon,
  PhoneIcon,
  ChatBubbleOvalLeftEllipsisIcon,
  DocumentChartBarIcon
} from '@heroicons/react/24/outline';
import RiskGauge from '../components/RiskGauge';
import { predictionsService, performanceService } from '../services/api';
import toast from 'react-hot-toast';

const StudentDashboard = () => {
  const [riskData, setRiskData] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [performanceStats, setPerformanceStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    
    // Listen for sidebar actions
    const handleSidebarAction = (event) => {
      const { action, role } = event.detail;
      if (role === 'student') {
        switch (action) {
          case 'progress':
            setShowProgressModal(true);
            break;
          case 'contact':
            setShowContactModal(true);
            break;
          case 'chat':
            setShowChatModal(true);
            break;
          case 'resources':
            // Could open a resources modal or redirect
            toast.info('Academic resources feature coming soon!');
            break;
          default:
            break;
        }
      }
    };
    
    window.addEventListener('sidebarAction', handleSidebarAction);
    
    return () => {
      window.removeEventListener('sidebarAction', handleSidebarAction);
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      // For demo purposes, using a mock student ID
      const studentId = 'STU0001';
      
      // Load risk prediction
      try {
        const prediction = await predictionsService.predictStudentRisk(studentId);
        setRiskData(prediction);
      } catch (error) {
        console.error('Failed to load risk prediction:', error);
      }

      // Load timeline
      try {
        const timelineData = await predictionsService.getStudentTimeline(studentId);
        setTimeline(timelineData.timeline || []);
      } catch (error) {
        console.error('Failed to load timeline:', error);
      }

      // Load performance stats
      try {
        const stats = await performanceService.getStudentPerformanceStats(studentId);
        setPerformanceStats(stats);
      } catch (error) {
        console.error('Failed to load performance stats:', error);
      }

    } catch (error) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const mockRiskData = {
    risk_score_1_10: 4,
    risk_bucket: 'moderate',
    top_risk_factors: [
      { feature_name: 'attendance_percentage', shap_value: -0.3 },
      { feature_name: 'engagement_score', shap_value: -0.2 },
      { feature_name: 'avg_assignment_score', shap_value: -0.15 }
    ],
    recommendations: [
      'Focus on improving attendance',
      'Participate more actively in class',
      'Seek help with assignments'
    ]
  };

  const mockTimeline = [
    { date: '2024-01-01', risk_score: 3.2 },
    { date: '2024-01-08', risk_score: 3.8 },
    { date: '2024-01-15', risk_score: 4.1 },
    { date: '2024-01-22', risk_score: 3.9 },
    { date: '2024-01-29', risk_score: 4.2 },
  ];

  const mockPerformanceStats = {
    avg_attendance: 78.5,
    avg_assignment_score: 72.3,
    avg_semester_marks: 75.8,
    avg_engagement: 6.2,
    trend_direction: 'stable'
  };

  const displayRiskData = riskData || mockRiskData;
  const displayTimeline = timeline.length > 0 ? timeline : mockTimeline;
  const displayStats = performanceStats || mockPerformanceStats;

  // Progress Report Modal
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [showContactModal, setShowContactModal] = useState(false);
  const [showChatModal, setShowChatModal] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [mentorContact, setMentorContact] = useState(null);

  const loadMentorContact = async () => {
    try {
      const response = await fetch('/api/v1/mentors/contact', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setMentorContact(data.mentor_contact);
    } catch (error) {
      console.error('Failed to load mentor contact:', error);
    }
  };

  const sendChatMessage = async () => {
    if (!currentMessage.trim()) return;
    
    const userMessage = { type: 'user', message: currentMessage, timestamp: new Date() };
    setChatMessages(prev => [...prev, userMessage]);
    
    try {
      const response = await fetch('/api/v1/chatbot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ message: currentMessage })
      });
      const data = await response.json();
      
      const aiMessage = { type: 'ai', message: data.response, suggestions: data.suggestions, timestamp: new Date() };
      setChatMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      toast.error('Failed to get AI response');
    }
    
    setCurrentMessage('');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900">My Dashboard</h1>
        <p className="text-gray-600 mt-2">Track your academic progress and get personalized insights</p>
      </motion.div>

      {/* Risk Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8"
      >
        {/* Risk Gauge */}
        <div className="card text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Risk Level</h3>
          <RiskGauge riskScore={displayRiskData.risk_score_1_10} size="large" />
          <p className="text-sm text-gray-600 mt-4">
            Based on recent academic performance and engagement
          </p>
        </div>

        {/* Key Metrics */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Attendance</span>
              <span className="font-medium">{displayStats.avg_attendance.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Assignment Avg</span>
              <span className="font-medium">{displayStats.avg_assignment_score.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Semester Marks</span>
              <span className="font-medium">{displayStats.avg_semester_marks.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Engagement</span>
              <span className="font-medium">{displayStats.avg_engagement.toFixed(1)}/10</span>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h3>
          <div className="space-y-3">
            {displayRiskData.recommendations.slice(0, 3).map((recommendation, index) => (
              <div key={index} className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                <p className="text-sm text-gray-700">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Risk Timeline Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card mb-8"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">30-Day Risk Timeline</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={displayTimeline}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => new Date(value).toLocaleDateString()}
              />
              <YAxis domain={[0, 10]} />
              <Tooltip 
                labelFormatter={(value) => new Date(value).toLocaleDateString()}
                formatter={(value) => [value.toFixed(1), 'Risk Score']}
              />
              <Line 
                type="monotone" 
                dataKey="risk_score" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Action Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        <ProgressReportCard onClick={() => setShowProgressModal(true)} />
        <ContactMentorCard onClick={() => setShowContactModal(true)} />
        <AIChatbotCard onClick={() => setShowChatModal(true)} />
      </motion.div>

      {/* Progress Report Modal */}
      {showProgressModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Detailed Progress Report</h2>
              <button 
                onClick={() => setShowProgressModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Academic Performance</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Overall GPA:</span>
                    <span className="font-medium">3.2/4.0</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Attendance Rate:</span>
                    <span className="font-medium">{displayStats.avg_attendance.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Assignment Average:</span>
                    <span className="font-medium">{displayStats.avg_assignment_score.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Semester Marks:</span>
                    <span className="font-medium">{displayStats.avg_semester_marks.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-4">
                <h3 className="text-lg font-semibold">Subject-wise Performance</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Mathematics:</span>
                    <span className="font-medium">72%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Physics:</span>
                    <span className="font-medium">68%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Programming:</span>
                    <span className="font-medium">85%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>English:</span>
                    <span className="font-medium">78%</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">Improvement Areas</h3>
              <ul className="space-y-2">
                {displayRiskData.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-gray-700">{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Contact Mentor Modal */}
      {showContactModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-gray-900">Contact Your Mentor</h2>
              <button 
                onClick={() => setShowContactModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="text-center">
                <div className="w-16 h-16 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <span className="text-xl font-bold text-gray-600">DJ</span>
                </div>
                <h3 className="font-semibold text-gray-900">Dr. Sarah Johnson</h3>
                <p className="text-gray-600">Computer Science Department</p>
                <p className="text-sm text-gray-500">Academic Counselor</p>
              </div>
              
              <div className="space-y-3">
                <a 
                  href="tel:+1234567890"
                  className="flex items-center justify-center space-x-2 bg-blue-100 text-blue-700 px-4 py-3 rounded-lg hover:bg-blue-200 transition-colors"
                >
                  <PhoneIcon className="h-5 w-5" />
                  <span>Call Now</span>
                </a>
                
                <a 
                  href="https://wa.me/1234567890?text=Hello%20Dr.%20Johnson,%20I%20would%20like%20to%20discuss%20my%20academic%20progress."
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center space-x-2 bg-green-100 text-green-700 px-4 py-3 rounded-lg hover:bg-green-200 transition-colors"
                >
                  <ChatBubbleLeftRightIcon className="h-5 w-5" />
                  <span>WhatsApp</span>
                </a>
                
                <a 
                  href="mailto:mentor@example.com?subject=Academic Support Request"
                  className="flex items-center justify-center space-x-2 bg-gray-100 text-gray-700 px-4 py-3 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <span>📧</span>
                  <span>Send Email</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* AI Chatbot Modal */}
      {showChatModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 h-[600px] flex flex-col">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-gray-900">AI Academic Assistant</h2>
              <button 
                onClick={() => setShowChatModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto mb-4 space-y-4">
              {chatMessages.length === 0 && (
                <div className="text-center text-gray-500 mt-8">
                  <ChatBubbleOvalLeftEllipsisIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Hi! I'm your AI academic assistant. Ask me about study strategies, time management, or any academic concerns.</p>
                </div>
              )}
              
              {chatMessages.map((msg, index) => (
                <div key={index} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    msg.type === 'user' 
                      ? 'bg-primary-500 text-white' 
                      : 'bg-gray-100 text-gray-900'
                  }`}>
                    <p>{msg.message}</p>
                    {msg.suggestions && (
                      <div className="mt-2 space-y-1">
                        {msg.suggestions.map((suggestion, idx) => (
                          <button
                            key={idx}
                            onClick={() => setCurrentMessage(suggestion)}
                            className="block w-full text-left text-xs bg-white bg-opacity-20 px-2 py-1 rounded hover:bg-opacity-30"
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="flex space-x-2">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                placeholder="Type your message..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button
                onClick={sendChatMessage}
                className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
              >
                Send
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Component for Progress Report Card
const ProgressReportCard = ({ onClick }) => {
  return (
    <div 
      className="card hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
        <div className="flex items-center">
          <div className="p-2 bg-success-100 rounded-lg">
            <DocumentChartBarIcon className="h-6 w-6 text-success-600" />
          </div>
          <div className="ml-4">
            <h4 className="font-medium text-gray-900">Progress Report</h4>
            <p className="text-sm text-gray-600">View detailed analytics</p>
          </div>
        </div>
      </div>
  );
};

// Component for Contact Mentor Card
const ContactMentorCard = ({ onClick }) => {
  return (
    <div 
      className="card hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
        <div className="flex items-center">
          <div className="p-2 bg-warning-100 rounded-lg">
            <PhoneIcon className="h-6 w-6 text-warning-600" />
          </div>
          <div className="ml-4">
            <h4 className="font-medium text-gray-900">Contact Mentor</h4>
            <p className="text-sm text-gray-600">Get guidance & support</p>
          </div>
        </div>
      </div>
  );
};

// Component for AI Chatbot Card
const AIChatbotCard = ({ onClick }) => {
  return (
    <div 
      className="card hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
        <div className="flex items-center">
          <div className="p-2 bg-purple-100 rounded-lg">
            <ChatBubbleOvalLeftEllipsisIcon className="h-6 w-6 text-purple-600" />
          </div>
          <div className="ml-4">
            <h4 className="font-medium text-gray-900">AI Assistant</h4>
            <p className="text-sm text-gray-600">Chat for academic help</p>
          </div>
        </div>
      </div>
  );
};

export default StudentDashboard;
