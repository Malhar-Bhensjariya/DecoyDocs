import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const Dashboard = () => {
  const { user, logout, getToken } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentView, setCurrentView] = useState('dashboard');
  const [decoyDocs, setDecoyDocs] = useState([]);

  useEffect(() => {
    fetchAlerts();
    if (user.role === 'admin') {
      fetchDecoyDocs();
    }
  }, [user]);

  const fetchAlerts = async () => {
    try {
      const endpoint = user.role === 'admin' ? '/api/ids/alerts' : '/api/ids/my-alerts';
      const response = await axios.get(`http://localhost:3001${endpoint}`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setAlerts(response.data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchDecoyDocs = async () => {
    try {
      const response = await axios.get('http://localhost:3001/api/decoydocs', {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setDecoyDocs(response.data);
    } catch (error) {
      console.error('Error fetching DecoyDocs:', error);
    }
  };

  const updateAlertStatus = async (alertId, status) => {
    if (user.role !== 'admin') return;

    try {
      await axios.patch(`http://localhost:3001/api/ids/alert/${alertId}`, { status }, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      fetchAlerts(); // Refresh alerts
    } catch (error) {
      console.error('Error updating alert:', error);
    }
  };

  // Office application data - this is what the bot will steal
  const officeData = {
    employees: [
      { id: 1, name: 'Arjun Sharma', position: 'Software Engineer', salary: '₹85,000', email: 'arjun.sharma@company.com', phone: '+91-98765-01234', ssn: '123-45-6789' },
      { id: 2, name: 'Priya Patel', position: 'Product Manager', salary: '₹95,000', email: 'priya.patel@company.com', phone: '+91-98765-01235', ssn: '234-56-7890' },
      { id: 3, name: 'Rohan Gupta', position: 'Designer', salary: '₹75,000', email: 'rohan.gupta@company.com', phone: '+91-98765-01236', ssn: '345-67-8901' },
      { id: 4, name: 'Ananya Singh', position: 'Data Analyst', salary: '₹70,000', email: 'ananya.singh@company.com', phone: '+91-98765-01237', ssn: '456-78-9012' },
      { id: 5, name: 'Vikram Kumar', position: 'DevOps Engineer', salary: '₹90,000', email: 'vikram.kumar@company.com', phone: '+91-98765-01238', ssn: '567-89-0123' },
    ],
    projects: [
      { id: 1, name: 'Project Alpha', status: 'In Progress', budget: '₹250,000', deadline: '2026-03-15', team: 'Arjun, Priya, Rohan', confidential: 'Contains trade secrets' },
      { id: 2, name: 'Project Beta', status: 'Planning', budget: '₹180,000', deadline: '2026-04-20', team: 'Ananya, Vikram', confidential: 'Patent pending technology' },
      { id: 3, name: 'Project Gamma', status: 'Completed', budget: '₹320,000', deadline: '2026-01-30', team: 'Arjun, Ananya, Vikram', confidential: 'Proprietary algorithms' },
    ],
    documents: [
      { id: 1, name: 'Q4 Financial Report.pdf', type: 'Financial', size: '2.4 MB', lastModified: '2026-01-15', content: 'Company financials showing ₹2.1M profit' },
      { id: 2, name: 'Employee Handbook.docx', type: 'HR', size: '1.8 MB', lastModified: '2026-01-20', content: 'Contains company policies and procedures' },
      { id: 3, name: 'Project Timeline.xlsx', type: 'Project', size: '956 KB', lastModified: '2026-01-25', content: 'Detailed project schedules and milestones' },
      { id: 4, name: 'Security Policy.pdf', type: 'Security', size: '3.2 MB', lastModified: '2026-01-28', content: 'Network security protocols and access controls' },
    ],
    credentials: {
      database: 'prod_db_server:5432, user: admin, pass: P@ssw0rd123!',
      api_keys: 'stripe: sk_live_123456789, aws: AKIA123456789',
      vpn: 'vpn.company.com, user: admin, pass: AdminPass2024!'
    }
  };

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Company Portal</h2>
        <p className="text-gray-600">Access your work resources, manage projects, and stay connected with your team.</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Team Members</p>
              <p className="text-2xl font-bold text-gray-900">{officeData.employees.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Projects</p>
              <p className="text-2xl font-bold text-gray-900">{officeData.projects.filter(p => p.status === 'In Progress').length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Documents</p>
              <p className="text-2xl font-bold text-gray-900">{officeData.documents.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Budget Used</p>
              <p className="text-2xl font-bold text-gray-900">₹750K</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <p className="text-sm text-gray-600">Project Alpha milestone completed</p>
            <span className="text-xs text-gray-400">2 hours ago</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <p className="text-sm text-gray-600">New employee onboarded: Rohan Gupta</p>
            <span className="text-xs text-gray-400">1 day ago</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
            <p className="text-sm text-gray-600">Q4 Financial Report uploaded</p>
            <span className="text-xs text-gray-400">3 days ago</span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderEmployees = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Employee Directory</h2>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
            Add Employee
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Position</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Salary</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {officeData.employees.map((employee) => (
                <tr key={employee.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{employee.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{employee.position}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {user.role === 'admin' ? employee.salary : '*****'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{employee.email}</div>
                    <div className="text-sm text-gray-500">{employee.phone}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      className={`mr-3 px-3 py-1 rounded text-sm ${
                        user.role === 'admin'
                          ? 'text-blue-600 hover:text-blue-900 hover:bg-blue-50'
                          : 'text-gray-400 cursor-not-allowed'
                      }`}
                      disabled={user.role !== 'admin'}
                    >
                      Edit
                    </button>
                    <button
                      className={`px-3 py-1 rounded text-sm ${
                        user.role === 'admin'
                          ? 'text-red-600 hover:text-red-900 hover:bg-red-50'
                          : 'text-gray-400 cursor-not-allowed'
                      }`}
                      disabled={user.role !== 'admin'}
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
  );

  const renderProjects = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Project Management</h2>
          <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium">
            New Project
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {officeData.projects.map((project) => (
            <div key={project.id} className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  project.status === 'Completed' ? 'bg-green-100 text-green-800' :
                  project.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {project.status}
                </span>
              </div>
              <div className="space-y-2 text-sm text-gray-600">
                <p><strong>Budget:</strong> {project.budget}</p>
                <p><strong>Deadline:</strong> {project.deadline}</p>
                <p><strong>Team:</strong> {project.team}</p>
              </div>
              <div className="mt-4 flex space-x-2">
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">View</button>
                <button className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm">Edit</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderDocuments = () => {
    // Filter documents based on user role
    const allowedDocuments = user.role === 'admin'
      ? [...officeData.documents, ...decoyDocs.map(doc => ({
          id: `decoy-${doc.id}`,
          name: doc.title,
          type: 'Decoy',
          size: 'N/A',
          lastModified: doc.createdAt,
          content: doc.content || 'Decoy document content'
        }))]
      : officeData.documents;

    return (
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Document Library</h2>
            {user.role === 'admin' && (
              <a
                href="/decoydocs"
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
              >
                Manage DecoyDocs
              </a>
            )}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {allowedDocuments.map((doc) => (
              <div key={doc.id} className={`bg-gray-50 rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow ${
                doc.type === 'Decoy' ? 'border-red-200 bg-red-50' : ''
              }`}>
                <div className="flex items-center mb-4">
                  <div className={`p-2 rounded-lg mr-3 ${
                    doc.type === 'Decoy' ? 'bg-red-100' : 'bg-blue-100'
                  }`}>
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-sm font-medium text-gray-900 truncate">{doc.name}</h3>
                    <p className="text-xs text-gray-500">{doc.type}</p>
                    {doc.type === 'Decoy' && (
                      <span className="inline-block px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full mt-1">
                        Honeypot
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-xs text-gray-600 space-y-1">
                  <p><strong>Size:</strong> {doc.size}</p>
                  <p><strong>Modified:</strong> {new Date(doc.lastModified).toLocaleDateString()}</p>
                </div>
                <div className="mt-4 flex space-x-2">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">Download</button>
                  <button className="bg-gray-600 hover:bg-gray-700 text-white px-3 py-1 rounded text-sm">Share</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="bg-blue-600 p-2 rounded-lg">
                <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Company Portal</h1>
                <p className="text-sm text-gray-600">Welcome back, {user.username}</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {user.role === 'admin' && (
                <a
                  href="/decoydocs"
                  className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
                >
                  Admin Panel
                </a>
              )}
              <button
                onClick={logout}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setCurrentView('dashboard')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                currentView === 'dashboard'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentView('employees')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                currentView === 'employees'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Employees
            </button>
            <button
              onClick={() => setCurrentView('projects')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                currentView === 'projects'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Projects
            </button>
            <button
              onClick={() => setCurrentView('documents')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                currentView === 'documents'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Documents
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {currentView === 'dashboard' && renderDashboard()}
        {currentView === 'employees' && renderEmployees()}
        {currentView === 'projects' && renderProjects()}
        {currentView === 'documents' && renderDocuments()}
      </main>
    </div>
  );
};

export default Dashboard;