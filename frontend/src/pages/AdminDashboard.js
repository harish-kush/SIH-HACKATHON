import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  UserGroupIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  AcademicCapIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from "@heroicons/react/24/outline";
import { studentsService, alertsService } from "../services/api";
import toast from "react-hot-toast";

const AdminDashboard = () => {
  const [stats, setStats] = useState({});
  const [students, setStudents] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showStudentsModal, setShowStudentsModal] = useState(false);
  const [showAlertsModal, setShowAlertsModal] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [allStudents, setAllStudents] = useState([]);
  const [mentors, setMentors] = useState([]);
  const [systemSettings, setSystemSettings] = useState(null);
  const [editingStudent, setEditingStudent] = useState(null);
  const [showCreateStudent, setShowCreateStudent] = useState(false);

  useEffect(() => {
    loadDashboardData();
    
    // Listen for sidebar actions
    const handleSidebarAction = (event) => {
      const { action, role } = event.detail;
      if (role === 'admin') {
        switch (action) {
          case 'manage-students':
            handleManageStudents();
            break;
          case 'manage-alerts':
            handleManageAlerts();
            break;
          case 'system-analytics':
            toast.info('System analytics feature coming soon!');
            break;
          case 'manage-mentors':
            toast.info('Mentor management feature coming soon!');
            break;
          case 'system-settings':
            handleSystemSettings();
            break;
          case 'reports':
            toast.info('Reports & exports feature coming soon!');
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

      // Load students
      const studentsData = await studentsService.getStudents({ limit: 1000 });
      setStudents(studentsData);

      // Load alerts
      const alertsData = await alertsService.getAlerts({ limit: 1000 });
      setAlerts(alertsData);

      // Load alert stats
      const statsData = await alertsService.getAlertStats();
      setStats(statsData);
    } catch (error) {
      console.error("Failed to load dashboard data:", error);
      toast.error("Failed to load dashboard data");
    } finally {
      setLoading(false);
    }
  };

  const loadAllStudents = async () => {
    try {
      const response = await fetch('/api/v1/admin/students', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setAllStudents(data);
    } catch (error) {
      toast.error('Failed to load students');
    }
  };

  const loadMentors = async () => {
    try {
      const response = await fetch('/api/v1/admin/mentors', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setMentors(data);
    } catch (error) {
      toast.error('Failed to load mentors');
    }
  };

  const loadSystemSettings = async () => {
    try {
      const response = await fetch('/api/v1/admin/settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      setSystemSettings(data);
    } catch (error) {
      toast.error('Failed to load system settings');
    }
  };

  const handleManageStudents = async () => {
    await loadAllStudents();
    await loadMentors();
    setShowStudentsModal(true);
  };

  const handleManageAlerts = () => {
    setShowAlertsModal(true);
  };

  const handleSystemSettings = async () => {
    await loadSystemSettings();
    setShowSettingsModal(true);
  };

  const handleDeleteStudent = async (studentId) => {
    if (window.confirm('Are you sure you want to delete this student?')) {
      try {
        await fetch(`/api/v1/admin/students/${studentId}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        toast.success('Student deleted successfully');
        loadAllStudents();
      } catch (error) {
        toast.error('Failed to delete student');
      }
    }
  };

  const handleUpdateSettings = async (newSettings) => {
    try {
      await fetch('/api/v1/admin/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(newSettings)
      });
      toast.success('Settings updated successfully');
      setSystemSettings(newSettings);
    } catch (error) {
      toast.error('Failed to update settings');
    }
  };

  // Mock data for charts
  const riskDistributionData = [
    { name: "Low Risk (1-3)", value: 65, color: "#10b981" },
    { name: "Moderate Risk (4-6)", value: 25, color: "#f59e0b" },
    { name: "High Risk (7-10)", value: 10, color: "#ef4444" },
  ];

  const branchPerformanceData = [
    { branch: "CSE", students: 180, atRisk: 15 },
    { branch: "ECE", students: 150, atRisk: 12 },
    { branch: "EEE", students: 120, atRisk: 18 },
    { branch: "MECH", students: 140, atRisk: 20 },
    { branch: "CIVIL", students: 110, atRisk: 8 },
    { branch: "IT", students: 100, atRisk: 10 },
  ];

  const monthlyTrendsData = [
    { month: "Jan", predictions: 45, interventions: 38, success: 32 },
    { month: "Feb", predictions: 52, interventions: 45, success: 39 },
    { month: "Mar", predictions: 38, interventions: 35, success: 30 },
    { month: "Apr", predictions: 61, interventions: 55, success: 48 },
    { month: "May", predictions: 49, interventions: 42, success: 36 },
    { month: "Jun", predictions: 44, interventions: 40, success: 35 },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600 mt-2">
          System-wide analytics and management overview
        </p>
      </motion.div>

      {/* Key Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        {/* Total Students */}
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-primary-100 rounded-lg">
              <UserGroupIcon className="h-6 w-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Students</p>
              <p className="text-2xl font-bold text-gray-900">
                {students.length}
              </p>
            </div>
          </div>
        </div>

        {/* Active Alerts */}
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-danger-100 rounded-lg">
              <ExclamationTriangleIcon className="h-6 w-6 text-danger-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Alerts</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.active_alerts || 0}
              </p>
            </div>
          </div>
        </div>

        {/* Success Rate */}
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-success-100 rounded-lg">
              <CheckCircleIcon className="h-6 w-6 text-success-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">78%</p>
            </div>
          </div>
        </div>

        {/* Avg Response Time */}
        <div className="card">
          <div className="flex items-center">
            <div className="p-2 bg-warning-100 rounded-lg">
              <ArrowTrendingUpIcon className="h-6 w-6 text-warning-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">
                Avg Response Time
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.avg_response_time_hours
                  ? `${stats.avg_response_time_hours.toFixed(1)}h`
                  : "N/A"}
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Risk Distribution */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            Risk Distribution
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={riskDistributionData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {riskDistributionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value}%`, "Students"]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {riskDistributionData.map((item, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="text-sm text-gray-600">{item.name}</span>
                </div>
                <span className="text-sm font-medium">{item.value}%</span>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Branch Performance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            Branch-wise At-Risk Students
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={branchPerformanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="branch" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="students" fill="#e5e7eb" name="Total Students" />
                <Bar dataKey="atRisk" fill="#ef4444" name="At Risk" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* Monthly Trends */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card mb-8"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-6">
          Monthly Intervention Trends
        </h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthlyTrendsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="predictions" fill="#3b82f6" name="Predictions" />
              <Bar
                dataKey="interventions"
                fill="#f59e0b"
                name="Interventions"
              />
              <Bar dataKey="success" fill="#10b981" name="Successful" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Recent Alerts */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card mb-8"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">
            Recent High-Priority Alerts
          </h3>
          <button className="text-primary-600 hover:text-primary-800 text-sm font-medium">
            View All
          </button>
        </div>
        <div className="space-y-4">
          {alerts.slice(0, 5).map((alert) => (
            <div
              key={alert.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
            >
              <div className="flex items-center space-x-4">
                <div
                  className={`w-3 h-3 rounded-full ${
                    alert.severity === "high"
                      ? "bg-danger-500"
                      : alert.severity === "moderate"
                      ? "bg-warning-500"
                      : "bg-success-500"
                  }`}
                ></div>
                <div>
                  <p className="font-medium text-gray-900">
                    Student ID: {alert.student_id}
                  </p>
                  <p className="text-sm text-gray-600">{alert.message}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  Risk: {alert.risk_score}/10
                </p>
                <p className="text-xs text-gray-500">
                  {new Date(alert.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-6"
      >
        {/* Manage Students */}
        <div 
          className="card hover:shadow-md transition-shadow cursor-pointer"
          onClick={handleManageStudents}
        >
          <div className="text-center">
            <div className="mx-auto w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
              <UserGroupIcon className="h-6 w-6 text-primary-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-2">Manage Students</h4>
            <p className="text-sm text-gray-600">
              Add, edit, and assign mentors to students
            </p>
          </div>
        </div>

        {/* Alert Management */}
        <div 
          className="card hover:shadow-md transition-shadow cursor-pointer"
          onClick={handleManageAlerts}
        >
          <div className="text-center">
            <div className="mx-auto w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center mb-4">
              <ExclamationTriangleIcon className="h-6 w-6 text-warning-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-2">Alert Management</h4>
            <p className="text-sm text-gray-600">
              Monitor and escalate critical alerts
            </p>
          </div>
        </div>

        {/* System Settings */}
        <div 
          className="card hover:shadow-md transition-shadow cursor-pointer"
          onClick={handleSystemSettings}
        >
          <div className="text-center">
            <div className="mx-auto w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mb-4">
              <Cog6ToothIcon className="h-6 w-6 text-success-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-2">System Settings</h4>
            <p className="text-sm text-gray-600">
              Configure thresholds and notifications
            </p>
          </div>
        </div>
      </motion.div>
      {/* Manage Students Modal */}
      {showStudentsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-7xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Manage Students</h2>
              <div className="flex space-x-2">
                <button 
                  onClick={() => setShowCreateStudent(true)}
                  className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600"
                >
                  Add Student
                </button>
                <button 
                  onClick={() => setShowStudentsModal(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Student</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Scholar ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Branch</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mentor</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {allStudents.map((student) => (
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
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{student.mentor_name || 'Unassigned'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          student.status === 'active' ? 'bg-green-100 text-green-800' :
                          student.status === 'at_risk' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {student.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button 
                          onClick={() => setEditingStudent(student)}
                          className="text-primary-600 hover:text-primary-900 mr-3"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => handleDeleteStudent(student.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Delete
                        </button>
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
          <div className="bg-white rounded-lg p-6 max-w-6xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Alert Management</h2>
              <button 
                onClick={() => setShowAlertsModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="mb-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-red-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-red-600">High Priority</h3>
                  <p className="text-2xl font-bold text-red-900">{alerts.filter(a => a.severity === 'high').length}</p>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-yellow-600">Medium Priority</h3>
                  <p className="text-2xl font-bold text-yellow-900">{alerts.filter(a => a.severity === 'moderate').length}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-green-600">Low Priority</h3>
                  <p className="text-2xl font-bold text-green-900">{alerts.filter(a => a.severity === 'low').length}</p>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="text-sm font-medium text-blue-600">Total Alerts</h3>
                  <p className="text-2xl font-bold text-blue-900">{alerts.length}</p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              {alerts.map((alert) => (
                <div key={alert.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          alert.severity === 'high' ? 'bg-red-100 text-red-800' :
                          alert.severity === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
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
                      <button className="text-xs bg-primary-100 text-primary-700 px-3 py-2 rounded hover:bg-primary-200">
                        Escalate
                      </button>
                      <button className="text-xs bg-success-100 text-success-700 px-3 py-2 rounded hover:bg-success-200">
                        Resolve
                      </button>
                      <button className="text-xs bg-gray-100 text-gray-700 px-3 py-2 rounded hover:bg-gray-200">
                        Assign Mentor
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* System Settings Modal */}
      {showSettingsModal && systemSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">System Settings</h2>
              <button 
                onClick={() => setShowSettingsModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="space-y-8">
              {/* Risk Thresholds */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Risk Thresholds</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Low Risk Max</label>
                    <input 
                      type="number" 
                      step="0.1"
                      defaultValue={systemSettings.risk_thresholds.low_risk_max}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Moderate Risk Max</label>
                    <input 
                      type="number" 
                      step="0.1"
                      defaultValue={systemSettings.risk_thresholds.moderate_risk_max}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">High Risk Min</label>
                    <input 
                      type="number" 
                      step="0.1"
                      defaultValue={systemSettings.risk_thresholds.high_risk_min}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
              </div>
              
              {/* Alert Settings */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Alert Settings</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Auto Alert Threshold</label>
                    <input 
                      type="number" 
                      step="0.1"
                      defaultValue={systemSettings.alert_settings.auto_alert_threshold}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Alert Frequency (hours)</label>
                    <input 
                      type="number"
                      defaultValue={systemSettings.alert_settings.alert_frequency_hours}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>
              </div>
              
              {/* Notification Settings */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Notification Settings</h3>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input 
                      type="checkbox" 
                      defaultChecked={systemSettings.notification_settings.email_notifications}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Email Notifications</span>
                  </label>
                  <label className="flex items-center">
                    <input 
                      type="checkbox" 
                      defaultChecked={systemSettings.notification_settings.sms_notifications}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">SMS Notifications</span>
                  </label>
                  <label className="flex items-center">
                    <input 
                      type="checkbox" 
                      defaultChecked={systemSettings.notification_settings.push_notifications}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Push Notifications</span>
                  </label>
                </div>
              </div>
              
              <div className="flex justify-end space-x-3">
                <button 
                  onClick={() => setShowSettingsModal(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => {
                    // In a real implementation, collect form data and call handleUpdateSettings
                    toast.success('Settings updated successfully');
                    setShowSettingsModal(false);
                  }}
                  className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600"
                >
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
