import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { loginUser } from '../services/apiService'; // Import the API service function
import '../styles/LoginPage.css';

function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const response = await loginUser({ username, password }); // Use the new service
      const data = response.data;


      if (data.success && data.token) {
        login(data.token, data.user); // Pass user data if available from backend
        navigate('/'); // Redirect to the home page or desired route
      } else {
        setError(data.message || '登录失败，请检查您的凭据。');
      }
    } catch (err) {
      setError('登录失败，请检查您的网络连接。');
      console.error('Login error:', err);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <h2>用户登录</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">用户名</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="password">密码</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <div className="error-message">{error}</div>}
          <button type="submit" className="login-button">
            登录
          </button>
        </form>
        <div className="register-link">
          <p>还没有账户？ <Link to="/register">注册</Link></p>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;