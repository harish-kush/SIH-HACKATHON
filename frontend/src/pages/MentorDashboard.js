import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  UserGroupIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  ChartBarIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import RiskGauge from '../components/RiskGauge';
import { studentsService, alertsService, predictionsService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const MentorDashboard = () => {
  const { user } = useAuth();
  const [students, setStudents] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [showStudentsModal, setShowStudentsModal] = useState(false);
  const [showAlertsModal, setShowAlertsModal] = useState(false);
  const [showAnalyticsModal, setShowAnalyticsModal] = useState(false);
  const [analyticsData, setAnalyticsData] = useState(null);

  useEffect(() => {
    loadDashboardData();
    
    // Listen for sidebar actions
    const handleSidebarAction = (event) => {
      const { action, role } = event.detail;
      if (role === 'mentor') {
        switch (action) {
          case 'students':
            setShowStudentsModal(true);
            break;
          case 'alerts':
            setShowAlertsModal(true);
            break;
          case 'analytics':
            loadAnalyticsData();
            break;
          case 'communications':
            toast.info('Student communications feature coming soon!');
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
      
      // Load mentor's students
      const studentsData = await studentsService.getStudentsByMentor(user.id);
      setStudents(studentsData);

      // Load active alerts
      const alertsData = await alertsService.getAlerts({ 
        status: 'active',
        limit: 10 
      });
      setAlerts(alertsData);

      // Load alert stats
      const statsData = await alertsService.getAlertStats();
      setStats(statsData);

    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledgeAlert = async (alertId) => {
    try {
      await alertsService.acknowledgeAlert(alertId, 'Alert acknowledged by mentor');
      toast.success('Alert acknowledged');
      loadDashboardData(); // Refresh data
    } catch (error) {
      toast.error('Failed to acknowledge alert');
    }
  };

  const handleResolveAlert = async (alertId) => {
    try {
      await alertsService.resolveAlert(alertId, 'Issue resolved through intervention');
      toast.success('Alert resolved');
      loadDashboardData(); // Refresh data
    } catch (error) {
      toast.error('Failed to resolve alert');
    }
  };

  const loadAnalyticsData = async () => {
    try {
      const response = await fetch('/api/v1/mentors/analytics', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setAnalyticsData(data);
      setShowAnalyticsModal(true);
    } catch (error) {
      toast.error('Failed to load analytics data');
    }
  };

  const getRiskColor = (riskScore) => {
    if (riskScore <= 3) return 'text-success-600 bg-success-50';
    if (riskScore <= 6) return 'text-warning-600 bg-warning-50';
    return 'text-danger-600 bg-danger-50';
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-danger-600 bg-danger-50';
      case 'moderate': return 'text-warning-600 bg-warning-50';
      case 'low': return 'text-success-600 bg-success-50';
      default: return 'text-gray-600 bg-gray-50';
    }
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
        <h1 className="text-3xl font-bold text-gray-900">Mentor Dashboard</h1>
        <p className="text-gray-600 mt-2">Monitor your assigned students and manage interventions</p>
      </motion.div>

      {/* Stats Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <UserGroupIcon className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Assigned Students</p>
              <p className="text-2xl font-bold text-gray-900">{students.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-danger-100 rounded-lg">
              <ExclamationTriangleIcon className="h-6 w-6 text-danger-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Alerts</p>
              <p className="text-2xl font-bold text-gray-900">{stats.active_alerts || 0}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-success-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-success-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Resolved This Week</p>
              <p className="text-2xl font-bold text-gray-900">{stats.resolved_alerts || 0}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-warning-100 rounded-lg">
              <ClockIcon className="h-6 w-6 text-warning-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.avg_response_time_hours ? `${stats.avg_response_time_hours.toFixed(1)}h` : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Active Alerts */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Active Alerts</h3>
            <span className="text-sm text-gray-500">{alerts.length} pending</span>
          </div>
          
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {alerts.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No active alerts</p>
            ) : (
              alerts.map((alert) => (
                <div key={alert.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(alert.severity)}`}>
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className="text-sm text-gray-500">
                          Risk Score: {alert.risk_score}/10
                        </span>
                      </div>
                      <p className="text-sm text-gray-900 mb-2">{alert.message}</p>
                      <p className="text-xs text-gray-500">
                        Created: {new Date(alert.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex flex-col space-y-2 ml-4">
                      <button
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                        className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded hover:bg-primary-200"
                      >
                        Acknowledge
                      </button>
                      <button
                        onClick={() => handleResolveAlert(alert.id)}
                        className="text-xs bg-success-100 text-success-700 px-2 py-1 rounded hover:bg-success-200"
                      >
                        Resolve
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </motion.div>

        {/* Student Risk Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Student Risk Overview</h3>
            <span className="text-sm text-gray-500">{students.length} students</span>
          </div>
          
          <div className="space-y-4 max-h-96 overflow-y-auto">
            {students.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No students assigned</p>
            ) : (
              students.map((student) => (
                <div key={student.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-700">
                        {student.name.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{student.name}</p>
                      <p className="text-sm text-gray-500">{student.scholar_id}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    {student.current_risk_score && (
                      <RiskGauge 
                        riskScore={Math.round(student.current_risk_score * 10)} 
                        size="small" 
                        showLabel={false} 
                      />
                    )}
                    <button className="text-primary-600 hover:text-primary-800">
                      <ChatBubbleLeftRightIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        <div 
          className="card hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => setShowStudentsModal(true)}
        >
          <div className="text-center">
            <div className="mx-auto w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <UserGroupIcon className="h-6 w-6 text-primary-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-2">View All Students</h4>
            <p className="text-sm text-gray-600">Manage student profiles and assignments</p>
          </div>
        </div>

        <div 
          className="card hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => setShowAlertsModal(true)}
        >
          <div className="text-center">
            <div className="mx-auto w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center mb-4">
              <ExclamationTriangleIcon className="h-6 w-6 text-warning-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-2">Alert Management</h4>
            <p className="text-sm text-gray-600">Review and respond to all alerts</p>
          </div>
        </div>

        <div 
          className="card hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => loadAnalyticsData()}
        >
          <div className="text-center">
            <div className="mx-auto w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mb-4">
              <ChartBarIcon className="h-6 w-6 text-success-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-2">Performance Analytics</h4>
            <p className="text-sm text-gray-600">View detailed performance insights</p>
          </div>
        </div>
      </motion.div>
      {/* View All Students Modal */}
      {showStudentsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">All Students</h2>
              <button 
                onClick={() => setShowStudentsModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Student</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scholar ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Branch</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Risk Score</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Attendance</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {students.map((student) => (
                    <tr key={student.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                            <span className="text-sm font-medium text-gray-700">
                              {student.name.charAt(0)}
                            </span>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{student.name}</div>
                            <div className="text-sm text-gray-500">{student.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{student.scholar_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{student.branch}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <RiskGauge 
                          riskScore={Math.round(student.current_risk_score * 10)} 
                          size="small" 
                          showLabel={false} 
                        />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{student.attendance_percentage}%</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          student.status === 'excellent' ? 'bg-green-100 text-green-800' :
                          student.status === 'at_risk' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {student.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-primary-600 hover:text-primary-900 mr-3">Contact</button>
                        <button className="text-green-600 hover:text-green-900">View Details</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Alert Management Modal */}
      {showAlertsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Alert Management</h2>
              <button 
                onClick={() => setShowAlertsModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-4">
              {alerts.map((alert) => (
                <div key={alert.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(alert.severity)}`}>
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className="text-sm text-gray-500">
                          Student: {alert.student_id}
                        </span>
                        <span className="text-sm text-gray-500">
                          Risk Score: {alert.risk_score}/10
                        </span>
                      </div>
                      <p className="text-sm text-gray-900 mb-2">{alert.message}</p>
                      <p className="text-xs text-gray-500">
                        Created: {new Date(alert.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex flex-col space-y-2 ml-4">
                      <button
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                        className="text-xs bg-primary-100 text-primary-700 px-3 py-2 rounded hover:bg-primary-200"
                      >
                        Acknowledge
                      </button>
                      <button
                        onClick={() => handleResolveAlert(alert.id)}
                        className="text-xs bg-success-100 text-success-700 px-3 py-2 rounded hover:bg-success-200"
                      >
                        Resolve
                      </button>
                      <button className="text-xs bg-gray-100 text-gray-700 px-3 py-2 rounded hover:bg-gray-200">
                        Contact Student
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Performance Analytics Modal */}
      {showAnalyticsModal && analyticsData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Performance Analytics</h2>
              <button 
                onClick={() => setShowAnalyticsModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-blue-600">Total Students</h3>
                <p className="text-2xl font-bold text-blue-900">{analyticsData.total_students}</p>
              </div>
              <div className="bg-red-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-red-600">At Risk</h3>
                <p className="text-2xl font-bold text-red-900">{analyticsData.at_risk_students}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-green-600">Excellent</h3>
                <p className="text-2xl font-bold text-green-900">{analyticsData.excellent_students}</p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-yellow-600">Average</h3>
                <p className="text-2xl font-bold text-yellow-900">{analyticsData.average_students}</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">Overall Performance</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Average Attendance:</span>
                    <span className="font-medium">{analyticsData.overall_performance.avg_attendance.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average Marks:</span>
                    <span className="font-medium">{analyticsData.overall_performance.avg_marks.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average Risk Score:</span>
                    <span className="font-medium">{analyticsData.overall_performance.avg_risk_score.toFixed(2)}</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold mb-4">Subject Performance</h3>
                <div className="space-y-3">
                  {analyticsData.subject_performance.map((subject, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span>{subject.subject}:</span>
                      <div className="text-right">
                        <span className="font-medium">{subject.avg_score.toFixed(1)}%</span>
                        <span className="text-sm text-red-600 ml-2">({subject.at_risk_count} at risk)</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="mt-8">
              <h3 className="text-lg font-semibold mb-4">Monthly Trends</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Month</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">At Risk</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Interventions</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Success Rate</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {analyticsData.monthly_stats.map((stat, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{stat.month}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{stat.at_risk}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{stat.interventions}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{stat.success_rate}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MentorDashboard;
