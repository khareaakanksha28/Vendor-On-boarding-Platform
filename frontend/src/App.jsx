import React, { useState, useEffect } from 'react';
import { Shield, User, AlertTriangle, CheckCircle, XCircle, Loader, TrendingUp, Activity, Lock, Eye, BarChart3, Zap, Sparkles, ArrowRight, Building2, Mail, Phone, MapPin, FileText, Settings, EyeOff, Search, Download, MessageSquare, Send, Users, Upload, Trash2, Edit } from 'lucide-react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001/api/v1';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Form states
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ username: '', email: '', password: '', confirmPassword: '' });
  const [showRegister, setShowRegister] = useState(false);
  const [onboardingData, setOnboardingData] = useState({
    // Company information (required)
    company_name: '',
    email: '',
    phone: '',
    address: '',
    city: '',
    state: '',
    zip: '',
    tax_id: '',
    industry: '',
    description: '',
    // Security controls
    mfaEnabled: false,
    ssoSupport: false,
    rbacImplemented: false,
    encryptionAtRest: false,
    encryptionInTransit: false,
    keyManagement: false,
    firewallEnabled: false,
    vpnRequired: false,
    ipWhitelisting: false,
    auditLogging: false,
    siemIntegration: false,
    alertingEnabled: false,
    gdprCompliant: false,
    soc2Certified: false,
    isoCompliant: false,
    // Legacy fields for fraud detection
    age: '',
    account_age_years: '',
    annual_income: '',
    credit_score: '',
    num_devices: '1',
    hours_since_registration: '0',
    failed_login_attempts: '0',
    transaction_amount: '0'
  });
  const [fraudResult, setFraudResult] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [showSecurityControls, setShowSecurityControls] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [selectedView, setSelectedView] = useState(null); // null, 'all', 'pending', 'approved', 'flagged'
  const [applications, setApplications] = useState([]);
  const [loadingApplications, setLoadingApplications] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewComment, setReviewComment] = useState('');
  const [reviewStatus, setReviewStatus] = useState('');
  const [newComment, setNewComment] = useState('');
  const [showUserManagement, setShowUserManagement] = useState(false);
  const [users, setUsers] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFileType, setSelectedFileType] = useState('document');
  const [uploadingFile, setUploadingFile] = useState(false);
  const [documents, setDocuments] = useState([]);

  useEffect(() => {
    if (token) {
      checkAuth();
      fetchDashboard();
    }
  }, [token]);

  const fetchDashboard = async () => {
    try {
      const response = await fetch(`${API_URL}/analytics/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setDashboardData(data);
      }
    } catch (err) {
      console.error('Failed to fetch dashboard:', err);
    }
  };

  const fetchApplications = async (status = null, search = '') => {
    setLoadingApplications(true);
    try {
      let url = `${API_URL}/applications?per_page=50`;
      
      if (status) {
        url += `&status=${status}`;
      }
      if (search) {
        url += `&search=${encodeURIComponent(search)}`;
      }
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setApplications(data.applications || []);
      }
    } catch (err) {
      console.error('Failed to fetch applications:', err);
      setApplications([]);
    } finally {
      setLoadingApplications(false);
    }
  };

  const fetchApplicationDetails = async (appId) => {
    try {
      const response = await fetch(`${API_URL}/applications/${appId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSelectedApplication(data);
      }
    } catch (err) {
      console.error('Failed to fetch application details:', err);
    }
  };

  const handleCardClick = (view) => {
    setSelectedView(view);
    setSelectedApplication(null);
    setSearchQuery('');
    
    // Map view to status
    const statusMap = {
      'all': null,
      'pending': 'pending_review',
      'approved': 'approved',
      'flagged': 'flagged'
    };
    
    fetchApplications(statusMap[view], '');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    const statusMap = {
      'all': null,
      'pending': 'pending_review',
      'approved': 'approved',
      'flagged': 'flagged'
    };
    fetchApplications(statusMap[selectedView] || null, searchQuery);
  };

  const handleStatusUpdate = async (appId, newStatus, comment = '') => {
    try {
      const response = await fetch(`${API_URL}/applications/${appId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          status: newStatus,
          comment: comment
        })
      });

      if (response.ok) {
        setSuccess(`Application ${newStatus} successfully!`);
        setShowReviewModal(false);
        setReviewComment('');
        setReviewStatus('');
        
        // Refresh applications and details
        const statusMap = {
          'all': null,
          'pending': 'pending_review',
          'approved': 'approved',
          'flagged': 'flagged'
        };
        fetchApplications(statusMap[selectedView] || null, searchQuery);
        if (selectedApplication && selectedApplication.id === appId) {
          fetchApplicationDetails(appId);
        }
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to update status');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleAddComment = async (appId) => {
    if (!newComment.trim()) {
      setError('Comment cannot be empty');
      return;
    }

    try {
      const response = await fetch(`${API_URL}/applications/${appId}/comments`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ comment: newComment })
      });

      if (response.ok) {
        setSuccess('Comment added successfully!');
        setNewComment('');
        fetchApplicationDetails(appId);
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to add comment');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch(`${API_URL}/users`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data.users || []);
      }
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setUsers([]);
    }
  };

  const handleUpdateUser = async (userId, updates) => {
    try {
      const response = await fetch(`${API_URL}/users/${userId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updates)
      });

      if (response.ok) {
        setSuccess('User updated successfully!');
        fetchUsers();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to update user');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSuccess('User deleted successfully!');
        fetchUsers();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to delete user');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleFileUpload = async (appId, file, fileType = 'document') => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File too large. Maximum size: 10MB');
      return;
    }

    setUploadingFile(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('file_type', fileType);

      const response = await fetch(`${API_URL}/applications/${appId}/documents`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        setSuccess('Document uploaded successfully!');
        setSelectedFile(null);
        fetchApplicationDetails(appId);
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to upload document');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setUploadingFile(false);
    }
  };

  const fetchApplicationDocuments = async (appId) => {
    try {
      const response = await fetch(`${API_URL}/applications/${appId}/documents`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      }
    } catch (err) {
      console.error('Failed to fetch documents:', err);
      setDocuments([]);
    }
  };

  const handleDownloadDocument = async (docId, filename) => {
    try {
      const response = await fetch(`${API_URL}/documents/${docId}/download`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
        setSuccess('Document downloaded!');
      } else {
        setError('Failed to download document');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleDeleteDocument = async (docId, appId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/documents/${docId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        setSuccess('Document deleted successfully!');
        fetchApplicationDetails(appId);
        fetchApplicationDocuments(appId);
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to delete document');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleExportCSV = async () => {
    try {
      const statusMap = {
        'all': null,
        'pending': 'pending_review',
        'approved': 'approved',
        'flagged': 'flagged'
      };
      const status = statusMap[selectedView] || null;
      
      let url = `${API_URL}/applications/export/csv`;
      const params = [];
      if (status) params.push(`status=${status}`);
      if (searchQuery) params.push(`search=${encodeURIComponent(searchQuery)}`);
      if (params.length) url += '?' + params.join('&');
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `applications_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(downloadUrl);
        setSuccess('Applications exported successfully!');
      } else {
        setError('Failed to export applications');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    }
  };

  const handleImportKaggleData = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const response = await fetch(`${API_URL}/import/kaggle-data`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        const breakdown = data.status_breakdown || {};
        setSuccess(`Successfully imported ${data.imported} applications! (${breakdown.flagged || 0} flagged, ${breakdown.pending || 0} pending, ${breakdown.approved || 0} approved)`);
        // Refresh dashboard to show new stats
        setTimeout(() => {
          fetchDashboard();
        }, 500);
        // Show all applications after a short delay
        setTimeout(() => {
          handleCardClick('all');
        }, 1500);
      } else {
        setError(data.error || 'Failed to import data');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const checkAuth = async () => {
    try {
      // Try to verify token by checking root endpoint (no auth required)
      const baseUrl = API_URL.replace('/api/v1', '');
      const response = await fetch(`${baseUrl}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        // Token exists, assume authenticated (token validation happens on API calls)
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('token');
        setToken('');
        setIsAuthenticated(false);
      }
    } catch (err) {
      console.error('Auth check failed:', err);
      // If token exists, assume authenticated (token validation happens on API calls)
      if (token) {
        setIsAuthenticated(true);
      }
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(loginForm)
      });

      const data = await response.json();

      if (response.ok) {
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
        setUser(data.user);
        setIsAuthenticated(true);
        setSuccess('Login successful!');
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    if (registerForm.password !== registerForm.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
        setUser(data.user);
        setIsAuthenticated(true);
        setSuccess('Registration successful!');
        setShowRegister(false);
      } else {
        setError(data.error || 'Registration failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
    setUser(null);
    setIsAuthenticated(false);
    setFraudResult(null);
    setSuccess('Logged out successfully');
  };

  const handleFraudCheck = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    setFraudResult(null);

    try {
      // Validate required fields
      if (!onboardingData.company_name || !onboardingData.email) {
        setError('Company name and email are required fields');
        setLoading(false);
        return;
      }
      
      // Format data for the new applications endpoint
      const dataToSend = {
        type: 'vendor',
        company_name: onboardingData.company_name,
        email: onboardingData.email,
        phone: onboardingData.phone || '',
        address: onboardingData.address || '',
        city: onboardingData.city || '',
        state: onboardingData.state || '',
        zip: onboardingData.zip || '',
        tax_id: onboardingData.tax_id || '',
        industry: onboardingData.industry || '',
        description: onboardingData.description || '',
        // Security controls
        mfaEnabled: onboardingData.mfaEnabled || false,
        ssoSupport: onboardingData.ssoSupport || false,
        rbacImplemented: onboardingData.rbacImplemented || false,
        encryptionAtRest: onboardingData.encryptionAtRest || false,
        encryptionInTransit: onboardingData.encryptionInTransit || false,
        keyManagement: onboardingData.keyManagement || false,
        firewallEnabled: onboardingData.firewallEnabled || false,
        vpnRequired: onboardingData.vpnRequired || false,
        ipWhitelisting: onboardingData.ipWhitelisting || false,
        auditLogging: onboardingData.auditLogging || false,
        siemIntegration: onboardingData.siemIntegration || false,
        alertingEnabled: onboardingData.alertingEnabled || false,
        gdprCompliant: onboardingData.gdprCompliant || false,
        soc2Certified: onboardingData.soc2Certified || false,
        isoCompliant: onboardingData.isoCompliant || false,
        // Legacy fields for fraud detection
        age: parseInt(onboardingData.age) || 30,
        account_age_years: parseFloat(onboardingData.account_age_years) || 0,
        annual_income: parseFloat(onboardingData.annual_income) || 50000,
        credit_score: parseInt(onboardingData.credit_score) || 650,
        num_devices: parseInt(onboardingData.num_devices) || 1,
        hours_since_registration: parseFloat(onboardingData.hours_since_registration) || 0,
        failed_login_attempts: parseInt(onboardingData.failed_login_attempts) || 0,
        transaction_amount: parseFloat(onboardingData.transaction_amount) || 0
      };

      const response = await fetch(`${API_URL}/applications`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(dataToSend)
      });

      const data = await response.json();

      if (response.ok) {
        setFraudResult(data.fraud_detection || {
          is_fraud: data.fraud_score < 0.5 ? false : true,
          fraud_score: data.fraud_score || 0,
          risk_level: data.fraud_score < 0.3 ? 'low' : data.fraud_score < 0.7 ? 'medium' : 'high'
        });
        setSuccess(`Application created! Status: ${data.status}, Risk Score: ${data.risk_score}`);
      } else {
        setError(data.error || 'Application submission failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4" style={{ 
        background: 'linear-gradient(to bottom right, #f5f3ff, #faf5ff)' 
      }}>
        <div className="rounded-2xl shadow-xl p-8 w-full max-w-md" style={{ 
          background: 'var(--card)',
          boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
        }}>
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-xl mb-4" style={{ 
              background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
              boxShadow: '0 4px 6px -1px rgba(139, 92, 246, 0.3)'
            }}>
              <Shield className="w-8 h-8" style={{ color: '#ffffff' }} />
            </div>
            <h1 className="text-2xl font-bold mb-1" style={{ color: 'var(--foreground)' }}>Vendor Onboarding Platform</h1>
            <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>Fraud Detection & Security</p>
          </div>

          {/* Tabs */}
          <div className="flex gap-2 mb-6 bg-gray-100 p-1 rounded-lg" style={{ background: 'var(--muted)' }}>
            <button
              onClick={() => setShowRegister(false)}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                !showRegister ? 'shadow-sm' : ''
              }`}
              style={!showRegister ? {
                background: 'var(--card)',
                color: 'var(--foreground)',
                boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
              } : {
                color: 'var(--muted-foreground)',
                background: 'transparent'
              }}
            >
              Login
            </button>
            <button
              onClick={() => setShowRegister(true)}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
                showRegister ? 'shadow-sm' : ''
              }`}
              style={showRegister ? {
                background: 'var(--card)',
                color: 'var(--foreground)',
                boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
              } : {
                color: 'var(--muted-foreground)',
                background: 'transparent'
              }}
            >
              Register
            </button>
          </div>

          {showRegister ? (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>Username</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                  <input
                    type="text"
                    required
                    value={registerForm.username}
                    onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg transition-all duration-200"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                    placeholder="Enter username"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                  <input
                    type="email"
                    required
                    value={registerForm.email}
                    onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg transition-all duration-200"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                    placeholder="Enter your email"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    value={registerForm.password}
                    onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                    className="w-full pl-10 pr-10 py-2.5 rounded-lg transition-all duration-200"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2"
                    style={{ color: 'var(--muted-foreground)' }}
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    value={registerForm.confirmPassword}
                    onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg transition-all duration-200"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                    placeholder="Confirm your password"
                  />
                </div>
              </div>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
                  <XCircle className="w-5 h-5" />
                  <span>{error}</span>
                </div>
              )}
              {success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  <span>{success}</span>
                </div>
              )}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-lg focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all duration-200 hover:opacity-90 font-medium"
                style={{ 
                  background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                  color: '#ffffff',
                  boxShadow: '0 4px 6px -1px rgba(139, 92, 246, 0.3)'
                }}
              >
                {loading ? <Loader className="w-5 h-5 animate-spin" /> : 'Sign Up'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>Username</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                  <input
                    type="text"
                    required
                    value={loginForm.username}
                    onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg transition-all duration-200"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                    placeholder="Enter username"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                    className="w-full pl-10 pr-10 py-2.5 rounded-lg transition-all duration-200"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2"
                    style={{ color: 'var(--muted-foreground)' }}
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              <p className="text-xs text-center" style={{ color: 'var(--muted-foreground)' }}>
                Trial credentials: admin / admin123
              </p>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
                  <XCircle className="w-5 h-5" />
                  <span>{error}</span>
                </div>
              )}
              {success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  <span>{success}</span>
                </div>
              )}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-lg focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-all duration-200 hover:opacity-90 font-medium"
                style={{ 
                  background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                  color: '#ffffff',
                  boxShadow: '0 4px 6px -1px rgba(139, 92, 246, 0.3)'
                }}
              >
                {loading ? <Loader className="w-5 h-5 animate-spin" /> : 'Sign In'}
              </button>
            </form>
          )}

          {/* Security Footer */}
          <div className="mt-6 pt-6 border-t flex items-center justify-center gap-2" style={{ 
            borderColor: 'var(--border)'
          }}>
            <Shield className="w-4 h-4" style={{ color: 'var(--muted-foreground)' }} />
            <p className="text-xs" style={{ color: 'var(--muted-foreground)' }}>
              Secured with enterprise-grade encryption
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ 
      background: 'linear-gradient(to bottom right, #f5f3ff, #faf5ff)' 
    }}>
      {/* Navbar - Enhanced Design matching login */}
      <nav className="sticky top-0 z-50 border-b backdrop-blur-sm" style={{ 
        background: 'rgba(255, 255, 255, 0.9)', 
        borderColor: 'var(--border)',
        boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
      }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="inline-flex items-center justify-center w-10 h-10 rounded-lg" style={{ 
                background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                boxShadow: '0 4px 6px -1px rgba(139, 92, 246, 0.3)'
              }}>
                <Shield className="w-6 h-6" style={{ color: '#ffffff' }} />
              </div>
              <span className="text-xl font-bold" style={{ color: 'var(--foreground)' }}>Onboarding Hub</span>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 px-4 py-2 rounded-lg" style={{ 
                background: 'var(--muted)' 
              }}>
                <User className="w-4 h-4" style={{ color: 'var(--muted-foreground)' }} />
                <span className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>
                  {user?.username || user?.email}
                </span>
                {user?.role && (
                  <span className="text-xs px-2 py-0.5 rounded-full" style={{ 
                    background: 'var(--accent)',
                    color: 'var(--foreground)'
                  }}>
                    {user.role}
                  </span>
                )}
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 hover:opacity-80"
                style={{ 
                  color: '#ffffff',
                  background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                  boxShadow: '0 4px 6px -1px rgba(139, 92, 246, 0.3)'
                }}
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Admin Actions - Admin Only */}
        {user?.role === 'admin' && !selectedView && (
          <div className="mb-6 flex justify-end gap-3">
            <button
              onClick={() => {
                setShowUserManagement(true);
                fetchUsers();
              }}
              className="px-4 py-2 rounded-lg font-medium transition-all hover:opacity-80 flex items-center gap-2"
              style={{ 
                background: 'var(--accent)',
                color: 'var(--foreground)',
                border: '1px solid var(--border)'
              }}
            >
              <Users className="w-4 h-4" />
              Manage Users
            </button>
            <button
              onClick={handleImportKaggleData}
              disabled={loading}
              className="px-4 py-2 rounded-lg font-medium transition-all hover:opacity-80 disabled:opacity-50 flex items-center gap-2"
              style={{ 
                background: 'var(--accent)',
                color: 'var(--foreground)',
                border: '1px solid var(--border)'
              }}
            >
              {loading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Importing...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  Import Kaggle Data
                </>
              )}
            </button>
          </div>
        )}

        {/* Success/Error Messages */}
        {success && (
          <div className="mb-6 p-4 rounded-lg flex items-center gap-2" style={{ 
            background: '#f0fdf4',
            border: '1px solid #bbf7d0',
            color: '#16a34a'
          }}>
            <CheckCircle className="w-5 h-5" />
            <span>{success}</span>
          </div>
        )}
        {error && (
          <div className="mb-6 p-4 rounded-lg flex items-center gap-2" style={{ 
            background: '#fef2f2',
            border: '1px solid #fecaca',
            color: '#dc2626'
          }}>
            <XCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}

        {/* Dashboard Stats - Clickable Cards */}
        {dashboardData && !selectedView && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <button
              onClick={() => handleCardClick('all')}
              className="p-6 rounded-xl transform hover:scale-105 transition-all duration-200 shadow-sm text-left cursor-pointer hover:shadow-md" 
              style={{ 
                background: 'var(--card)',
                border: '1px solid var(--border)'
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 rounded-lg" style={{ background: 'var(--muted)' }}>
                  <Activity className="w-6 h-6" style={{ color: 'var(--primary)' }} />
                </div>
                <TrendingUp className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
              </div>
              <p className="text-sm font-medium mb-1" style={{ color: 'var(--muted-foreground)' }}>Total Applications</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--foreground)' }}>{dashboardData.summary?.total || 0}</p>
            </button>
            <button
              onClick={() => handleCardClick('pending')}
              className="p-6 rounded-xl transform hover:scale-105 transition-all duration-200 shadow-sm text-left cursor-pointer hover:shadow-md" 
              style={{ 
                background: 'var(--card)',
                border: '1px solid var(--border)'
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 rounded-lg" style={{ background: 'var(--muted)' }}>
                  <AlertTriangle className="w-6 h-6" style={{ color: 'var(--primary)' }} />
                </div>
                <BarChart3 className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
              </div>
              <p className="text-sm font-medium mb-1" style={{ color: 'var(--muted-foreground)' }}>Pending Review</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--foreground)' }}>{dashboardData.summary?.pending || 0}</p>
            </button>
            <button
              onClick={() => handleCardClick('approved')}
              className="p-6 rounded-xl transform hover:scale-105 transition-all duration-200 shadow-sm text-left cursor-pointer hover:shadow-md" 
              style={{ 
                background: 'var(--card)',
                border: '1px solid var(--border)'
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 rounded-lg" style={{ background: 'var(--muted)' }}>
                  <CheckCircle className="w-6 h-6" style={{ color: 'var(--primary)' }} />
                </div>
                <Sparkles className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
              </div>
              <p className="text-sm font-medium mb-1" style={{ color: 'var(--muted-foreground)' }}>Approved</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--foreground)' }}>{dashboardData.summary?.approved || 0}</p>
            </button>
            <button
              onClick={() => handleCardClick('flagged')}
              className="p-6 rounded-xl transform hover:scale-105 transition-all duration-200 shadow-sm text-left cursor-pointer hover:shadow-md" 
              style={{ 
                background: 'var(--card)',
                border: '1px solid var(--border)'
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 rounded-lg" style={{ background: 'var(--muted)' }}>
                  <XCircle className="w-6 h-6" style={{ color: 'var(--destructive)' }} />
                </div>
                <Zap className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
              </div>
              <p className="text-sm font-medium mb-1" style={{ color: 'var(--muted-foreground)' }}>Flagged</p>
              <p className="text-3xl font-bold" style={{ color: 'var(--foreground)' }}>{dashboardData.summary?.flagged || 0}</p>
            </button>
          </div>
        )}

        {/* Applications List View */}
        {selectedView && !selectedApplication && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold mb-1" style={{ color: 'var(--foreground)' }}>
                  {selectedView === 'all' ? 'All Applications' :
                   selectedView === 'pending' ? 'Pending Review' :
                   selectedView === 'approved' ? 'Approved Applications' :
                   'Flagged Applications'}
                </h2>
                <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>
                  {applications.length} {applications.length === 1 ? 'application' : 'applications'} found
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleExportCSV}
                  className="px-4 py-2 rounded-lg font-medium transition-all hover:opacity-80 flex items-center gap-2"
                  style={{ 
                    background: 'var(--accent)',
                    color: 'var(--foreground)',
                    border: '1px solid var(--border)'
                  }}
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </button>
                <button
                  onClick={() => {
                    setSelectedView(null);
                    setApplications([]);
                    setSearchQuery('');
                  }}
                  className="px-4 py-2 rounded-lg font-medium transition-all hover:opacity-80"
                  style={{ 
                    background: 'var(--accent)',
                    color: 'var(--foreground)'
                  }}
                >
                  ← Back to Dashboard
                </button>
              </div>
            </div>

            {/* Search Bar */}
            <form onSubmit={handleSearch} className="mb-6">
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search by company name, email, or industry..."
                    className="w-full pl-10 pr-4 py-2.5 rounded-lg transition-all duration-200"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                  />
                </div>
                <button
                  type="submit"
                  className="px-6 py-2.5 rounded-lg font-medium transition-all hover:opacity-80 flex items-center gap-2"
                  style={{ 
                    background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                    color: '#ffffff',
                    boxShadow: '0 4px 6px -1px rgba(139, 92, 246, 0.3)'
                  }}
                >
                  <Search className="w-4 h-4" />
                  Search
                </button>
              </div>
            </form>

            {loadingApplications ? (
              <div className="flex items-center justify-center py-12">
                <Loader className="w-8 h-8 animate-spin" style={{ color: 'var(--primary)' }} />
              </div>
            ) : applications.length === 0 ? (
              <div className="text-center py-12 rounded-xl" style={{ background: 'var(--card)', border: '1px solid var(--border)' }}>
                <Shield className="w-16 h-16 mx-auto mb-4" style={{ color: 'var(--muted-foreground)' }} />
                <p className="text-lg font-medium mb-2" style={{ color: 'var(--foreground)' }}>No applications found</p>
                <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>
                  {selectedView === 'all' 
                    ? 'Submit a new application to get started'
                    : `No ${selectedView} applications at this time`}
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {applications.map((app) => (
                  <div
                    key={app.id}
                    onClick={() => fetchApplicationDetails(app.id)}
                    className="p-6 rounded-xl cursor-pointer transition-all hover:shadow-lg transform hover:scale-[1.02]"
                    style={{ 
                      background: 'var(--card)',
                      border: '1px solid var(--border)'
                    }}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-bold" style={{ color: 'var(--foreground)' }}>
                            {app.company_name}
                          </h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            app.status === 'approved' ? 'bg-green-100 text-green-800' :
                            app.status === 'flagged' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {app.status.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                          <div>
                            <p className="text-xs mb-1" style={{ color: 'var(--muted-foreground)' }}>Email</p>
                            <p className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>{app.email}</p>
                          </div>
                          {app.phone && (
                            <div>
                              <p className="text-xs mb-1" style={{ color: 'var(--muted-foreground)' }}>Phone</p>
                              <p className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>{app.phone}</p>
                            </div>
                          )}
                          {app.risk_score !== null && (
                            <div>
                              <p className="text-xs mb-1" style={{ color: 'var(--muted-foreground)' }}>Risk Score</p>
                              <p className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>
                                {app.risk_score?.toFixed(1) || 'N/A'}
                              </p>
                            </div>
                          )}
                          {app.fraud_score !== null && (
                            <div>
                              <p className="text-xs mb-1" style={{ color: 'var(--muted-foreground)' }}>Fraud Score</p>
                              <p className="text-sm font-medium" style={{ 
                                color: app.fraud_score > 0.7 ? 'var(--destructive)' : 'var(--foreground)' 
                              }}>
                                {(app.fraud_score * 100).toFixed(1)}%
                              </p>
                            </div>
                          )}
                        </div>
                        {app.submitted_date && (
                          <p className="text-xs mt-3" style={{ color: 'var(--muted-foreground)' }}>
                            Submitted: {new Date(app.submitted_date).toLocaleDateString()}
                          </p>
                        )}
                      </div>
                      <ArrowRight className="w-5 h-5 ml-4" style={{ color: 'var(--muted-foreground)' }} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Application Detail View */}
        {selectedApplication && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>
                Application Details
              </h2>
              <button
                onClick={() => setSelectedApplication(null)}
                className="px-4 py-2 rounded-lg font-medium transition-all hover:opacity-80"
                style={{ 
                  background: 'var(--accent)',
                  color: 'var(--foreground)'
                }}
              >
                ← Back to List
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Company Information */}
              <div className="p-6 rounded-xl" style={{ background: 'var(--card)', border: '1px solid var(--border)' }}>
                <h3 className="text-lg font-bold mb-4" style={{ color: 'var(--foreground)' }}>Company Information</h3>
                <div className="space-y-3">
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--muted-foreground)' }}>Company Name</p>
                    <p className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>{selectedApplication.company_name}</p>
                  </div>
                  <div>
                    <p className="text-xs mb-1" style={{ color: 'var(--muted-foreground)' }}>Email</p>
                    <p className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>{selectedApplication.email}</p>
                  </div>
                  {selectedApplication.phone && (
                    <div>
                      <p className="text-xs mb-1" style={{ color: 'var(--muted-foreground)' }}>Phone</p>
                      <p className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>{selectedApplication.phone}</p>
                    </div>
                  )}
                  {selectedApplication.industry && (
                    <div>
                      <p className="text-xs mb-1" style={{ color: 'var(--muted-foreground)' }}>Industry</p>
                      <p className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>{selectedApplication.industry}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Risk & Fraud Detection */}
              <div className="p-6 rounded-xl" style={{ background: 'var(--card)', border: '1px solid var(--border)' }}>
                <h3 className="text-lg font-bold mb-4" style={{ color: 'var(--foreground)' }}>Risk Assessment</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>Risk Score</p>
                      <p className="text-sm font-bold" style={{ color: 'var(--foreground)' }}>
                        {selectedApplication.risk_score?.toFixed(1) || 'N/A'}
                      </p>
                    </div>
                    <div className="w-full h-2 rounded-full" style={{ background: 'var(--muted)' }}>
                      <div
                        className="h-2 rounded-full"
                        style={{
                          width: `${selectedApplication.risk_score || 0}%`,
                          background: selectedApplication.risk_score >= 70 ? '#10b981' :
                                     selectedApplication.risk_score >= 50 ? '#f59e0b' : '#ef4444'
                        }}
                      />
                    </div>
                  </div>
                  {selectedApplication.fraud_score !== null && (
                    <div>
                      <div className="flex justify-between mb-2">
                        <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>Fraud Score</p>
                        <p className="text-sm font-bold" style={{ 
                          color: selectedApplication.fraud_score > 0.7 ? 'var(--destructive)' : 'var(--foreground)' 
                        }}>
                          {(selectedApplication.fraud_score * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div className="w-full h-2 rounded-full" style={{ background: 'var(--muted)' }}>
                        <div
                          className="h-2 rounded-full"
                          style={{
                            width: `${(selectedApplication.fraud_score || 0) * 100}%`,
                            background: selectedApplication.fraud_score > 0.7 ? '#ef4444' :
                                       selectedApplication.fraud_score > 0.4 ? '#f59e0b' : '#10b981'
                          }}
                        />
                      </div>
                    </div>
                  )}
                  {selectedApplication.fraud_detection && (
                    <div className="mt-4 p-3 rounded-lg" style={{ 
                      background: selectedApplication.fraud_detection.is_fraud ? '#fef2f2' : '#f0fdf4',
                      border: `1px solid ${selectedApplication.fraud_detection.is_fraud ? '#fecaca' : '#bbf7d0'}`
                    }}>
                      <p className="text-sm font-medium mb-1" style={{ 
                        color: selectedApplication.fraud_detection.is_fraud ? '#dc2626' : '#16a34a'
                      }}>
                        {selectedApplication.fraud_detection.is_fraud ? '⚠️ Fraud Detected' : '✓ No Fraud Detected'}
                      </p>
                      <p className="text-xs" style={{ color: 'var(--muted-foreground)' }}>
                        Risk Level: {selectedApplication.fraud_detection.risk_level?.toUpperCase() || 'UNKNOWN'}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Review Actions - For Reviewers/Admins */}
            {(user?.role === 'reviewer' || user?.role === 'admin') && selectedApplication.status !== 'approved' && (
              <div className="mt-6 p-6 rounded-xl" style={{ background: 'var(--card)', border: '1px solid var(--border)' }}>
                <h3 className="text-lg font-bold mb-4" style={{ color: 'var(--foreground)' }}>Review Actions</h3>
                <div className="flex gap-3">
                  <button
                    onClick={() => {
                      setReviewStatus('approved');
                      setShowReviewModal(true);
                    }}
                    className="flex-1 px-4 py-3 rounded-lg font-medium transition-all hover:opacity-90 flex items-center justify-center gap-2"
                    style={{ 
                      background: '#10b981',
                      color: '#ffffff',
                      boxShadow: '0 4px 6px -1px rgba(16, 185, 129, 0.3)'
                    }}
                  >
                    <CheckCircle className="w-5 h-5" />
                    Approve
                  </button>
                  <button
                    onClick={() => {
                      setReviewStatus('flagged');
                      setShowReviewModal(true);
                    }}
                    className="flex-1 px-4 py-3 rounded-lg font-medium transition-all hover:opacity-90 flex items-center justify-center gap-2"
                    style={{ 
                      background: 'var(--destructive)',
                      color: '#ffffff',
                      boxShadow: '0 4px 6px -1px rgba(212, 24, 61, 0.3)'
                    }}
                  >
                    <XCircle className="w-5 h-5" />
                    Reject/Flag
                  </button>
                </div>
              </div>
            )}

            {/* Documents Section */}
            <div className="mt-6 p-6 rounded-xl" style={{ background: 'var(--card)', border: '1px solid var(--border)' }}>
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--foreground)' }}>
                <FileText className="w-5 h-5" />
                Documents & Certificates
              </h3>
              
              {/* Upload Document */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>
                  Upload Document
                </label>
                <div className="flex gap-3">
                  <input
                    type="file"
                    onChange={(e) => setSelectedFile(e.target.files[0])}
                    accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.txt"
                    className="flex-1 px-4 py-2 rounded-lg"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                  />
                  <select
                    value={selectedFileType}
                    onChange={(e) => setSelectedFileType(e.target.value)}
                    className="px-4 py-2 rounded-lg"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                  >
                    <option value="document">Document</option>
                    <option value="certificate">Certificate</option>
                    <option value="contract">Contract</option>
                    <option value="other">Other</option>
                  </select>
                  <button
                    onClick={() => {
                      if (selectedFile) {
                        handleFileUpload(selectedApplication.id, selectedFile, selectedFileType);
                      }
                    }}
                    disabled={!selectedFile || uploadingFile}
                    className="px-4 py-2 rounded-lg font-medium transition-all hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    style={{ 
                      background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                      color: '#ffffff',
                      boxShadow: '0 4px 6px -1px rgba(139, 92, 246, 0.3)'
                    }}
                  >
                    {uploadingFile ? (
                      <>
                        <Loader className="w-4 h-4 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4" />
                        Upload
                      </>
                    )}
                  </button>
                </div>
                <p className="text-xs mt-2" style={{ color: 'var(--muted-foreground)' }}>
                  Supported: PDF, DOC, DOCX, JPG, PNG, TXT (Max 10MB)
                </p>
              </div>

              {/* Documents List */}
              <div className="space-y-3">
                {selectedApplication.documents && selectedApplication.documents.length > 0 ? (
                  selectedApplication.documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="p-4 rounded-lg flex items-center justify-between"
                      style={{ 
                        background: 'var(--muted)',
                        border: '1px solid var(--border)'
                      }}
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <FileText className="w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                        <div className="flex-1">
                          <p className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>
                            {doc.filename}
                          </p>
                          <p className="text-xs" style={{ color: 'var(--muted-foreground)' }}>
                            {doc.file_type} • {(doc.file_size / 1024).toFixed(1)} KB
                            {doc.uploaded_at && ` • ${new Date(doc.uploaded_at).toLocaleDateString()}`}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleDownloadDocument(doc.id, doc.filename)}
                          className="p-2 rounded-lg transition-all hover:opacity-80"
                          style={{ 
                            background: 'var(--accent)',
                            color: 'var(--foreground)'
                          }}
                          title="Download"
                        >
                          <Download className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteDocument(doc.id, selectedApplication.id)}
                          className="p-2 rounded-lg transition-all hover:opacity-80"
                          style={{ 
                            background: 'var(--destructive)',
                            color: '#ffffff'
                          }}
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-center py-4" style={{ color: 'var(--muted-foreground)' }}>
                    No documents uploaded yet.
                  </p>
                )}
              </div>
            </div>

            {/* Comments Section */}
            <div className="mt-6 p-6 rounded-xl" style={{ background: 'var(--card)', border: '1px solid var(--border)' }}>
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2" style={{ color: 'var(--foreground)' }}>
                <MessageSquare className="w-5 h-5" />
                Comments & Notes
              </h3>
              
              {/* Add Comment */}
              <div className="mb-6">
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Add a comment or note..."
                  rows={3}
                  className="w-full px-4 py-3 rounded-lg transition-all duration-200 mb-3"
                  style={{ 
                    background: 'var(--input-background)',
                    border: '1px solid var(--border)',
                    color: 'var(--foreground)',
                    resize: 'vertical'
                  }}
                />
                <button
                  onClick={() => handleAddComment(selectedApplication.id)}
                  disabled={!newComment.trim()}
                  className="px-4 py-2 rounded-lg font-medium transition-all hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  style={{ 
                    background: 'linear-gradient(135deg, #8b5cf6, #6366f1)',
                    color: '#ffffff',
                    boxShadow: '0 4px 6px -1px rgba(139, 92, 246, 0.3)'
                  }}
                >
                  <Send className="w-4 h-4" />
                  Add Comment
                </button>
              </div>

              {/* Comments List */}
              <div className="space-y-4">
                {selectedApplication.comments && selectedApplication.comments.length > 0 ? (
                  selectedApplication.comments.map((comment) => (
                    <div
                      key={comment.id}
                      className="p-4 rounded-lg"
                      style={{ 
                        background: 'var(--muted)',
                        border: '1px solid var(--border)'
                      }}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4" style={{ color: 'var(--muted-foreground)' }} />
                          <span className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>
                            {comment.username || 'Unknown User'}
                          </span>
                        </div>
                        <span className="text-xs" style={{ color: 'var(--muted-foreground)' }}>
                          {comment.created_at ? new Date(comment.created_at).toLocaleString() : ''}
                        </span>
                      </div>
                      <p className="text-sm" style={{ color: 'var(--foreground)' }}>{comment.comment}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-center py-4" style={{ color: 'var(--muted-foreground)' }}>
                    No comments yet. Be the first to add one!
                  </p>
                )}
              </div>
            </div>

            {/* Review Modal */}
            {showReviewModal && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                <div className="bg-white rounded-xl p-6 max-w-md w-full" style={{ background: 'var(--card)' }}>
                  <h3 className="text-xl font-bold mb-4" style={{ color: 'var(--foreground)' }}>
                    {reviewStatus === 'approved' ? 'Approve Application' : 'Reject/Flag Application'}
                  </h3>
                  <div className="mb-4">
                    <label className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>
                      Comment (Optional)
                    </label>
                    <textarea
                      value={reviewComment}
                      onChange={(e) => setReviewComment(e.target.value)}
                      placeholder="Add a comment explaining your decision..."
                      rows={4}
                      className="w-full px-4 py-2 rounded-lg"
                      style={{ 
                        background: 'var(--input-background)',
                        border: '1px solid var(--border)',
                        color: 'var(--foreground)',
                        resize: 'vertical'
                      }}
                    />
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={() => {
                        setShowReviewModal(false);
                        setReviewComment('');
                        setReviewStatus('');
                      }}
                      className="flex-1 px-4 py-2 rounded-lg font-medium transition-all hover:opacity-80"
                      style={{ 
                        background: 'var(--accent)',
                        color: 'var(--foreground)'
                      }}
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleStatusUpdate(selectedApplication.id, reviewStatus, reviewComment)}
                      className="flex-1 px-4 py-2 rounded-lg font-medium transition-all hover:opacity-90"
                      style={{ 
                        background: reviewStatus === 'approved' ? '#10b981' : 'var(--destructive)',
                        color: '#ffffff'
                      }}
                    >
                      Confirm
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* User Management Modal - Admin Only */}
        {showUserManagement && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto" style={{ background: 'var(--card)' }}>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>
                  User Management
                </h3>
                <button
                  onClick={() => {
                    setShowUserManagement(false);
                    setUsers([]);
                  }}
                  className="p-2 rounded-lg transition-all hover:opacity-80"
                  style={{ 
                    background: 'var(--accent)',
                    color: 'var(--foreground)'
                  }}
                >
                  <XCircle className="w-5 h-5" />
                </button>
              </div>

              {users.length === 0 ? (
                <div className="text-center py-8">
                  <Loader className="w-8 h-8 animate-spin mx-auto mb-4" style={{ color: 'var(--primary)' }} />
                  <p style={{ color: 'var(--muted-foreground)' }}>Loading users...</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {users.map((u) => (
                    <div
                      key={u.id}
                      className="p-4 rounded-lg flex items-center justify-between"
                      style={{ 
                        background: 'var(--muted)',
                        border: '1px solid var(--border)'
                      }}
                    >
                      <div className="flex items-center gap-4 flex-1">
                        <div className="p-2 rounded-lg" style={{ background: 'var(--accent)' }}>
                          <User className="w-5 h-5" style={{ color: 'var(--foreground)' }} />
                        </div>
                        <div className="flex-1">
                          <p className="font-medium" style={{ color: 'var(--foreground)' }}>
                            {u.username}
                          </p>
                          <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>
                            {u.email}
                          </p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          u.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                          u.role === 'reviewer' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {u.role}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <select
                          value={u.role}
                          onChange={(e) => handleUpdateUser(u.id, { role: e.target.value })}
                          className="px-3 py-1 rounded-lg text-sm"
                          style={{ 
                            background: 'var(--input-background)',
                            border: '1px solid var(--border)',
                            color: 'var(--foreground)'
                          }}
                        >
                          <option value="user">User</option>
                          <option value="reviewer">Reviewer</option>
                          <option value="admin">Admin</option>
                        </select>
                        {u.id !== user?.id && (
                          <button
                            onClick={() => handleDeleteUser(u.id)}
                            className="p-2 rounded-lg transition-all hover:opacity-80"
                            style={{ 
                              background: 'var(--destructive)',
                              color: '#ffffff'
                            }}
                            title="Delete User"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Main Content - Only show when no view is selected */}
        {!selectedView && !showUserManagement && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Onboarding Form - Figma Design */}
          <div className="p-8 rounded-xl shadow-sm transform transition-all duration-300" style={{ 
            background: 'var(--card)',
            border: '1px solid var(--border)'
          }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl" style={{ background: 'var(--muted)' }}>
                <Building2 className="w-6 h-6" style={{ color: 'var(--primary)' }} />
              </div>
              <div>
                <h2 className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>Onboarding Application</h2>
                <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>Submit vendor/client information</p>
              </div>
            </div>
            <form onSubmit={handleFraudCheck} className="space-y-6">
              {/* Required Company Information */}
              <div className="space-y-4 pb-6 border-b" style={{ borderColor: 'var(--border)' }}>
                <div className="relative">
                  <label className="block text-sm font-semibold mb-2 flex items-center gap-2" style={{ color: 'var(--foreground)' }}>
                    <Building2 className="w-4 h-4" style={{ color: 'var(--primary)' }} />
                    Company Name <span style={{ color: 'var(--destructive)' }}>*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={onboardingData.company_name}
                    onChange={(e) => setOnboardingData({ ...onboardingData, company_name: e.target.value })}
                    className="w-full px-4 py-3 pl-11 rounded-lg transition-all duration-200"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                    placeholder="Acme Corporation"
                  />
                  <Building2 className="absolute left-3 top-9 w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                </div>
                <div className="relative">
                  <label className="block text-sm font-semibold mb-2 flex items-center gap-2" style={{ color: 'var(--foreground)' }}>
                    <Mail className="w-4 h-4" style={{ color: 'var(--primary)' }} />
                    Email <span style={{ color: 'var(--destructive)' }}>*</span>
                  </label>
                  <input
                    type="email"
                    required
                    value={onboardingData.email}
                    onChange={(e) => setOnboardingData({ ...onboardingData, email: e.target.value })}
                    className="w-full px-4 py-3 pl-11 rounded-lg transition-all duration-200"
                    style={{ 
                      background: 'var(--input-background)',
                      border: '1px solid var(--border)',
                      color: 'var(--foreground)'
                    }}
                    placeholder="contact@company.com"
                  />
                  <Mail className="absolute left-3 top-9 w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="relative">
                    <label className="block text-sm font-semibold mb-2 flex items-center gap-2" style={{ color: 'var(--foreground)' }}>
                      <Phone className="w-4 h-4" style={{ color: 'var(--primary)' }} />
                      Phone
                    </label>
                    <input
                      type="tel"
                      value={onboardingData.phone}
                      onChange={(e) => setOnboardingData({ ...onboardingData, phone: e.target.value })}
                      className="w-full px-4 py-3 pl-11 rounded-lg transition-all duration-200"
                      style={{ 
                        background: 'var(--input-background)',
                        border: '1px solid var(--border)',
                        color: 'var(--foreground)'
                      }}
                      placeholder="+1-555-123-4567"
                    />
                    <Phone className="absolute left-3 top-9 w-5 h-5" style={{ color: 'var(--muted-foreground)' }} />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2 flex items-center gap-2" style={{ color: 'var(--foreground)' }}>
                      <FileText className="w-4 h-4" style={{ color: 'var(--primary)' }} />
                      Industry
                    </label>
                    <input
                      type="text"
                      value={onboardingData.industry}
                      onChange={(e) => setOnboardingData({ ...onboardingData, industry: e.target.value })}
                      className="w-full px-4 py-3 rounded-lg transition-all duration-200"
                      style={{ 
                        background: 'var(--input-background)',
                        border: '1px solid var(--border)',
                        color: 'var(--foreground)'
                      }}
                      placeholder="Technology"
                    />
                  </div>
                </div>
              </div>
              
              {/* Security Controls Toggle */}
              <div 
                className="flex items-center justify-between p-4 rounded-xl cursor-pointer transition-all duration-200 hover:opacity-80" 
                style={{ background: 'var(--accent)' }}
                onClick={() => setShowSecurityControls(!showSecurityControls)}
              >
                <div className="flex items-center gap-3">
                  <Lock className="w-5 h-5" style={{ color: 'var(--primary)' }} />
                  <span className="font-semibold" style={{ color: 'var(--foreground)' }}>Security Controls</span>
                </div>
                <ArrowRight className={`w-5 h-5 transition-transform duration-200 ${showSecurityControls ? 'rotate-90' : ''}`} style={{ color: 'var(--primary)' }} />
              </div>

              {showSecurityControls && (
                <div className="grid grid-cols-2 gap-3 p-4 rounded-xl animate-fadeIn" style={{ 
                  background: 'var(--muted)',
                  border: '1px solid var(--border)'
                }}>
                  {[
                    { key: 'mfaEnabled', label: 'MFA Enabled', icon: Shield },
                    { key: 'ssoSupport', label: 'SSO Support', icon: Lock },
                    { key: 'encryptionAtRest', label: 'Encryption at Rest', icon: Eye },
                    { key: 'encryptionInTransit', label: 'Encryption in Transit', icon: Zap },
                    { key: 'firewallEnabled', label: 'Firewall', icon: Shield },
                    { key: 'gdprCompliant', label: 'GDPR Compliant', icon: CheckCircle },
                  ].map(({ key, label, icon: Icon }) => (
                    <label 
                      key={key} 
                      className="flex items-center gap-2 p-3 rounded-lg cursor-pointer transition-colors hover:opacity-80"
                      style={{ background: 'var(--card)' }}
                    >
                      <input
                        type="checkbox"
                        checked={onboardingData[key]}
                        onChange={(e) => setOnboardingData({ ...onboardingData, [key]: e.target.checked })}
                        className="w-4 h-4 rounded"
                        style={{ accentColor: 'var(--primary)' }}
                      />
                      <Icon className="w-4 h-4" style={{ color: 'var(--primary)' }} />
                      <span className="text-sm font-medium" style={{ color: 'var(--foreground)' }}>{label}</span>
                    </label>
                  ))}
                </div>
              )}

              {/* Fraud Detection Fields */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
                  <input
                    type="number"
                    value={onboardingData.age}
                    onChange={(e) => setOnboardingData({ ...onboardingData, age: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="30"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Account Age (years)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={onboardingData.account_age_years}
                    onChange={(e) => setOnboardingData({ ...onboardingData, account_age_years: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="0"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Annual Income</label>
                  <input
                    type="number"
                    value={onboardingData.annual_income}
                    onChange={(e) => setOnboardingData({ ...onboardingData, annual_income: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="50000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Credit Score</label>
                  <input
                    type="number"
                    value={onboardingData.credit_score}
                    onChange={(e) => setOnboardingData({ ...onboardingData, credit_score: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="650"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Number of Devices</label>
                  <input
                    type="number"
                    value={onboardingData.num_devices}
                    onChange={(e) => setOnboardingData({ ...onboardingData, num_devices: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Hours Since Registration</label>
                  <input
                    type="number"
                    step="0.1"
                    value={onboardingData.hours_since_registration}
                    onChange={(e) => setOnboardingData({ ...onboardingData, hours_since_registration: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="0"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Failed Login Attempts</label>
                  <input
                    type="number"
                    value={onboardingData.failed_login_attempts}
                    onChange={(e) => setOnboardingData({ ...onboardingData, failed_login_attempts: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="0"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Transaction Amount</label>
                  <input
                    type="number"
                    step="0.01"
                    value={onboardingData.transaction_amount}
                    onChange={(e) => setOnboardingData({ ...onboardingData, transaction_amount: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    placeholder="0"
                  />
                </div>
              </div>
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
                  <XCircle className="w-5 h-5" />
                  <span>{error}</span>
                </div>
              )}
              {success && (
                <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg flex items-center gap-2">
                  <CheckCircle className="w-5 h-5" />
                  <span>{success}</span>
                </div>
              )}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 px-6 rounded-lg focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-semibold text-lg transform hover:scale-[1.02] transition-all duration-200"
                style={{ 
                  background: 'var(--primary)',
                  color: 'var(--primary-foreground)'
                }}
              >
                {loading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    Run Fraud Detection
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Fraud Detection Results - Figma Design */}
          <div className="p-8 rounded-xl shadow-sm transform transition-all duration-300" style={{ 
            background: 'var(--card)',
            border: '1px solid var(--border)'
          }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="p-3 rounded-xl" style={{ background: 'var(--muted)' }}>
                <AlertTriangle className="w-6 h-6" style={{ color: 'var(--primary)' }} />
              </div>
              <div>
                <h2 className="text-2xl font-bold" style={{ color: 'var(--foreground)' }}>Fraud Detection Results</h2>
                <p className="text-sm" style={{ color: 'var(--muted-foreground)' }}>Real-time ML-powered analysis</p>
              </div>
            </div>
            {fraudResult ? (
              <div className="space-y-6 animate-fadeIn">
                <div className={`relative p-8 rounded-2xl border-2 overflow-hidden ${
                  fraudResult.is_fraud 
                    ? 'bg-gradient-to-br from-red-50 to-rose-50 border-red-300' 
                    : fraudResult.risk_level === 'high'
                    ? 'bg-gradient-to-br from-yellow-50 to-orange-50 border-yellow-300'
                    : 'bg-gradient-to-br from-green-50 to-emerald-50 border-green-300'
                }`}>
                  <div className="absolute top-0 right-0 w-32 h-32 opacity-10">
                    <div className={`w-full h-full rounded-full ${
                      fraudResult.is_fraud ? 'bg-red-500' : fraudResult.risk_level === 'high' ? 'bg-yellow-500' : 'bg-green-500'
                    }`}></div>
                  </div>
                  <div className="relative z-10">
                    <div className="flex items-center justify-between mb-6">
                      <span className="text-xl font-bold text-gray-900">Status</span>
                      {fraudResult.is_fraud ? (
                        <span className="px-4 py-2 bg-gradient-to-r from-red-500 to-rose-600 text-white rounded-full text-sm font-bold flex items-center gap-2 shadow-lg animate-pulse">
                          <XCircle className="w-5 h-5" />
                          Fraud Detected
                        </span>
                      ) : (
                        <span className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-full text-sm font-bold flex items-center gap-2 shadow-lg">
                          <CheckCircle className="w-5 h-5" />
                          No Fraud
                        </span>
                      )}
                    </div>
                    <div className="space-y-3">
                      <div>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm text-gray-700">Risk Level</span>
                          <span className={`text-sm font-medium ${
                            fraudResult.risk_level === 'high' ? 'text-red-600' :
                            fraudResult.risk_level === 'medium' ? 'text-yellow-600' :
                            'text-green-600'
                          }`}>
                            {(fraudResult.risk_level || 'unknown').toUpperCase()}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                          <div
                            className={`h-full rounded-full transition-all duration-1000 ease-out ${
                              fraudResult.risk_level === 'high' ? 'bg-gradient-to-r from-red-500 to-rose-600' :
                              fraudResult.risk_level === 'medium' ? 'bg-gradient-to-r from-yellow-400 to-orange-500' :
                              'bg-gradient-to-r from-green-500 to-emerald-600'
                            }`}
                            style={{ width: `${((fraudResult.fraud_score || 0) * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4 pt-4">
                      <div className="p-4 bg-white/60 rounded-xl backdrop-blur-sm border border-white/80">
                        <div className="flex items-center gap-2 mb-2">
                          <BarChart3 className="w-4 h-4 text-indigo-600" />
                          <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">Fraud Score</span>
                        </div>
                        <p className="text-3xl font-bold text-gray-900">
                          {((fraudResult.fraud_score || 0) * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div className="p-4 bg-white/60 rounded-xl backdrop-blur-sm border border-white/80">
                        <div className="flex items-center gap-2 mb-2">
                          <Activity className="w-4 h-4 text-indigo-600" />
                          <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">
                            {fraudResult.anomaly_score !== undefined ? 'Anomaly Score' : 'Model Type'}
                          </span>
                        </div>
                        <p className="text-3xl font-bold text-gray-900">
                          {fraudResult.anomaly_score !== undefined 
                            ? fraudResult.anomaly_score.toFixed(3)
                            : fraudResult.model_type?.replace('_', ' ').toUpperCase() || 'N/A'}
                        </p>
                      </div>
                    </div>
                    </div>
                  </div>
                </div>
                <div className={`p-6 rounded-xl border-2 ${
                  fraudResult.is_fraud || fraudResult.risk_level === 'high'
                    ? 'bg-gradient-to-r from-red-50 to-rose-50 border-red-200'
                    : 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200'
                }`}>
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-lg ${
                      fraudResult.is_fraud || fraudResult.risk_level === 'high' ? 'bg-red-100' : 'bg-green-100'
                    }`}>
                      {fraudResult.is_fraud || fraudResult.risk_level === 'high' ? (
                        <AlertTriangle className="w-5 h-5 text-red-600" />
                      ) : (
                        <CheckCircle className="w-5 h-5 text-green-600" />
                      )}
                    </div>
                    <div>
                      <h3 className="font-bold text-gray-900 mb-1">Recommendation</h3>
                      <p className="text-sm text-gray-700">
                        {fraudResult.is_fraud || fraudResult.risk_level === 'high'
                          ? 'This application requires manual review before approval. Additional verification may be needed.'
                          : 'This application appears legitimate and can be approved for onboarding.'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-16">
                <div className="relative inline-block mb-6">
                  <div className="absolute inset-0 bg-indigo-200 rounded-full blur-2xl opacity-50"></div>
                  <div className="relative p-6 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full">
                    <Shield className="w-16 h-16 text-indigo-400" />
                  </div>
                </div>
                <h3 className="text-lg font-semibold text-gray-700 mb-2">No Results Yet</h3>
                <p className="text-sm text-gray-500">Submit an onboarding application to see fraud detection results</p>
              </div>
            )}
          </div>
        </div>
        )}
      </main>
    </div>
  );
}

export default App;

