import React from 'react';

// Lightweight deceptive dashboard — static/fake content meant to look real to an intruder.
const DecoyLanding = () => {
  const fakeStats = {
    employees: 28,
    activeProjects: 5,
    documents: 42,
    budget: '₹1.2M'
  };

  const fakeRecent = [
    { text: 'Q2 Financial summary uploaded', time: '2 hours ago' },
    { text: 'Contract signed with Acme Corp', time: '1 day ago' },
    { text: 'New employee: S. Kumar', time: '3 days ago' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
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
                <p className="text-sm text-gray-600">Welcome back</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium">Logout</button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Team Members</p>
            <p className="text-2xl font-bold text-gray-900">{fakeStats.employees}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Active Projects</p>
            <p className="text-2xl font-bold text-gray-900">{fakeStats.activeProjects}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Documents</p>
            <p className="text-2xl font-bold text-gray-900">{fakeStats.documents}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-sm font-medium text-gray-600">Budget Used</p>
            <p className="text-2xl font-bold text-gray-900">{fakeStats.budget}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <ul className="space-y-3 text-sm text-gray-600">
            {fakeRecent.map((r, i) => (
              <li key={i} className="flex justify-between">
                <span>{r.text}</span>
                <span className="text-gray-400">{r.time}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Document Library</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">Q4 Financial Report.pdf</div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">Employee Handbook.docx</div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">Project Timeline.xlsx</div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DecoyLanding;
