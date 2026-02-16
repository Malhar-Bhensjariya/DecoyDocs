import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const DecoyDocs = () => {
  const { getToken, user } = useAuth();
  const [decoyDocs, setDecoyDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creatingDoc, setCreatingDoc] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newDocTitle, setNewDocTitle] = useState('');
  const [newDocTemplate, setNewDocTemplate] = useState('generic_report');
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');

  useEffect(() => {
    fetchDecoyDocs();
  }, []);

  const fetchDecoyDocs = async () => {
    try {
      const response = await axios.get('http://localhost:3001/api/decoydocs', {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setDecoyDocs(response.data);
    } catch (error) {
      console.error('Error fetching DecoyDocs:', error);
    } finally {
      setLoading(false);
    }
  };

  const createDecoyDoc = async (e) => {
    e.preventDefault();
    setCreatingDoc(true);
    try {
      await axios.post('http://localhost:3001/api/decoydocs/create', {
        title: newDocTitle,
        template: newDocTemplate
      }, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });

      setNewDocTitle('');
      setNewDocTemplate('generic_report');
      setShowCreateForm(false);
      fetchDecoyDocs(); // Refresh list
    } catch (error) {
      console.error('Error creating DecoyDoc:', error);
      alert('Failed to create document: ' + (error.response?.data?.error || error.message));
    } finally {
      setCreatingDoc(false);
    }
  };

  const viewDecoyDoc = async (docId) => {
    try {
      const response = await axios.get(`http://localhost:3001/api/decoydocs/${docId}`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setSelectedDoc(response.data);
    } catch (error) {
      console.error('Error fetching DecoyDoc details:', error);
    }
  };

  const editDecoyDoc = (doc) => {
    setSelectedDoc(doc);
    setEditTitle(doc.title);
    setEditContent(doc.content || '');
    setShowEditForm(true);
  };

  const updateDecoyDoc = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`http://localhost:3001/api/decoydocs/${selectedDoc.id}`, {
        title: editTitle,
        content: editContent
      }, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });

      setShowEditForm(false);
      setSelectedDoc(null);
      fetchDecoyDocs(); // Refresh list
    } catch (error) {
      console.error('Error updating DecoyDoc:', error);
    }
  };

  const deleteDecoyDoc = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this honeypot document?')) {
      return;
    }

    try {
      await axios.delete(`http://localhost:3001/api/decoydocs/${docId}`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      fetchDecoyDocs(); // Refresh list
    } catch (error) {
      console.error('Error deleting DecoyDoc:', error);
    }
  };

  const downloadFile = (docId, type) => {
    const url = `http://localhost:3001/api/decoydocs/${docId}/download/${type}`;
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', '');
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-red-50 to-orange-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-red-600 to-red-700 shadow-lg border-b border-red-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <div className="bg-white p-3 rounded-lg shadow-lg">
                <svg className="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">
                  DecoyDocs Management
                </h1>
                <p className="text-red-100">
                  Honeypot Documents - Admin Only
                </p>
              </div>
            </div>
            <div className="flex space-x-4">
              <a
                href="/dashboard"
                className="bg-white text-red-600 px-6 py-3 rounded-lg text-sm font-semibold hover:bg-gray-50 shadow-lg hover:shadow-xl transform transition-all duration-200 hover:scale-105 flex items-center"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to Dashboard
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Warning Banner */}
          <div className="bg-gradient-to-r from-yellow-400 to-orange-500 border-l-4 border-yellow-600 p-6 mb-8 rounded-2xl shadow-lg">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="h-8 w-8 text-yellow-800" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <div className="ml-4">
                <h3 className="text-lg font-semibold text-yellow-900 mb-2">
                  Security Notice
                </h3>
                <p className="text-yellow-800 font-medium">
                  These are honeypot documents designed to detect unauthorized access.
                  Only create documents when investigating suspicious activity.
                </p>
              </div>
            </div>
          </div>

          {/* Create New Document */}
          <div className="bg-white shadow-xl rounded-2xl mb-8 border border-gray-100 overflow-hidden">
            <div className="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-xl leading-6 font-bold text-gray-900 flex items-center">
                    <svg className="w-6 h-6 mr-3 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Create New Decoy Document
                  </h3>
                  <p className="mt-1 text-sm text-gray-600">
                    Generate honeypot documents to detect unauthorized access attempts
                  </p>
                </div>
                {user?.role === 'admin' ? (
                  <button
                    onClick={() => setShowCreateForm(!showCreateForm)}
                    className={`px-6 py-3 rounded-lg text-sm font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 ${
                      showCreateForm
                        ? 'bg-red-100 text-red-700 hover:bg-red-200'
                        : 'bg-red-100 text-red-700 hover:bg-red-200'
                    }`}
                  >
                    {showCreateForm ? 'Cancel' : 'Create Document'}
                  </button>
                ) : (
                  <div className="text-sm text-gray-500 px-4">Admin only</div>
                )}
              </div>
            </div>

            {user?.role === 'admin' && showCreateForm && (
              <div className="px-6 py-6 bg-gray-50">
                <form onSubmit={createDecoyDoc} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label htmlFor="title" className="block text-sm font-semibold text-gray-700 mb-2">
                        Document Title
                      </label>
                      <input
                        type="text"
                        id="title"
                        value={newDocTitle}
                        onChange={(e) => setNewDocTitle(e.target.value)}
                        disabled={creatingDoc}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-200 disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-500"
                        placeholder="Enter document title"
                        required
                      />
                    </div>
                    <div>
                      <label htmlFor="template" className="block text-sm font-semibold text-gray-700 mb-2">
                        Template Type
                      </label>
                      <select
                        id="template"
                        value={newDocTemplate}
                        onChange={(e) => setNewDocTemplate(e.target.value)}
                        disabled={creatingDoc}
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all duration-200 disabled:bg-gray-100 disabled:cursor-not-allowed disabled:text-gray-500"
                      >
                        <option value="generic_report">Generic Report</option>
                        <option value="employee_bonus">Employee Bonus</option>
                        <option value="q3_financial">Q3 Financial</option>
                        <option value="hr_review">HR Review</option>
                        <option value="sales_pipeline">Sales Pipeline</option>
                      </select>
                    </div>
                  </div>
                  <div className="flex justify-end gap-4">
                    {creatingDoc && (
                      <div className="flex items-center text-red-600 font-semibold">
                        <svg className="animate-spin h-5 w-5 mr-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Generating document...
                      </div>
                    )}
                    <button
                      type="submit"
                      disabled={creatingDoc}
                      className={`px-6 py-3 rounded-lg shadow-lg hover:shadow-xl transform transition-all duration-200 flex items-center font-semibold ${
                        creatingDoc
                          ? 'bg-gray-400 text-white cursor-not-allowed'
                          : 'bg-gradient-to-r from-red-600 to-red-700 text-white hover:from-red-700 hover:to-red-800 hover:scale-105'
                      }`}
                    >
                      {creatingDoc ? (
                        <>
                          <svg className="animate-spin h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Creating...
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                          </svg>
                          Create Honeypot Document
                        </>
                      )}
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>

          {/* Documents List */}
          <div className="bg-white shadow-xl rounded-2xl overflow-hidden border border-gray-100">
            <div className="px-6 py-5 border-b border-gray-200 bg-gradient-to-r from-gray-50 to-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-xl leading-6 font-bold text-gray-900 flex items-center">
                    <svg className="w-6 h-6 mr-3 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Active Honeypot Documents
                  </h3>
                  <p className="mt-1 max-w-2xl text-sm text-gray-600">
                    Documents that will trigger alerts when accessed by suspicious users
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="flex items-center space-x-1">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <span className="text-xs text-gray-500">Active</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                    <span className="text-xs text-gray-500">Inactive</span>
                  </div>
                </div>
              </div>
            </div>
            <ul className="divide-y divide-gray-200">
              {loading ? (
                <li className="px-6 py-8 text-center">
                  <div className="flex items-center justify-center">
                    <svg className="animate-spin h-8 w-8 text-red-600" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="ml-3 text-gray-600">Loading documents...</span>
                  </div>
                </li>
              ) : decoyDocs.length === 0 ? (
                <li className="px-6 py-8 text-center">
                  <div className="text-gray-500">
                    <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <h3 className="mt-2 text-sm font-medium text-gray-900">No honeypot documents</h3>
                    <p className="mt-1 text-sm text-gray-500">Create your first honeypot document above.</p>
                  </div>
                </li>
              ) : (
                decoyDocs.map((doc) => (
                  <li key={doc.id} className="px-6 py-4 hover:bg-gray-50 transition-colors duration-200">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 flex items-center">
                        <div className="w-12 h-12 bg-gradient-to-r from-red-100 to-red-200 rounded-xl flex items-center justify-center mr-4 shadow-lg">
                          <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between">
                            <p className="text-lg font-semibold text-gray-900">
                              {doc.title}
                            </p>
                            <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                              doc.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                            }`}>
                              {doc.status}
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            <span className="font-medium">Template:</span> {doc.template} |
                            <span className="font-medium ml-2">Created:</span> {new Date(doc.createdAt).toLocaleDateString()} |
                            <span className="font-medium ml-2">Access Count:</span> {doc.accessCount || 0}
                          </p>
                        </div>
                      </div>
                      {user?.role === 'admin' && (
                        <div className="flex space-x-3 ml-4">
                          <button
                            onClick={() => viewDecoyDoc(doc.id)}
                            className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-all duration-200 text-sm font-medium flex items-center"
                          >
                          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                          View
                        </button>
                          <button
                            onClick={() => editDecoyDoc(doc)}
                            className="px-4 py-2 bg-yellow-100 text-yellow-700 rounded-lg hover:bg-yellow-200 transition-all duration-200 text-sm font-medium flex items-center"
                          >
                            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            Edit
                          </button>
                          <button
                            onClick={() => deleteDecoyDoc(doc.id)}
                            className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-all duration-200 text-sm font-medium flex items-center"
                          >
                            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                            Delete
                          </button>
                        </div>
                      )}
                    </div>
                  </li>
                ))
              )}
            </ul>
          </div>
        </div>
      </main>

      {/* View Document Modal */}
      {selectedDoc && !showEditForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-bold text-gray-900">{selectedDoc.title}</h3>
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="mb-4">
                <p className="text-sm text-gray-600">
                  <strong>Created:</strong> {new Date(selectedDoc.createdAt).toLocaleString()}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Status:</strong> {selectedDoc.status}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Template:</strong> {selectedDoc.template}
                </p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <h4 className="font-semibold text-gray-900 mb-2">Document Content:</h4>
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">{selectedDoc.content}</pre>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => downloadFile(selectedDoc.id, 'docx')}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Download DOCX
                </button>
                <button
                  onClick={() => downloadFile(selectedDoc.id, 'json')}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  Download JSON
                </button>
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Document Modal */}
      {showEditForm && selectedDoc && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Edit Decoy Document</h3>
              <form onSubmit={updateDecoyDoc}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Title</label>
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                    required
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Content</label>
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    rows={10}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Enter document content..."
                  />
                </div>
                <div className="flex justify-end space-x-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowEditForm(false);
                      setSelectedDoc(null);
                    }}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                  >
                    Update Document
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DecoyDocs;