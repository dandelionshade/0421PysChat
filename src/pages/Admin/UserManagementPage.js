import React, { useState, useEffect, useCallback } from 'react';
import { adminGetUserList, adminDeleteUser, adminUpdateUser } from '../../services/apiService'; // Import specific functions
import '../../styles/Admin/UserManagementPage.css';

function UserManagementPage() {
  const [users, setUsers] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [editingUser, setEditingUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [usersPerPage] = useState(10); // Or make this configurable

  const fetchUsers = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await adminGetUserList({ page: currentPage, limit: usersPerPage, search: searchTerm });
      setUsers(response.data.users || response.data); // Adjust based on actual API response structure
      // Potentially set totalPages if API provides it for pagination
    } catch (err) {
      setError(err.response?.data?.message || '获取用户列表失败');
      console.error("Error fetching users:", err);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage, usersPerPage, searchTerm]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleDeleteUser = async (userId) => {
    if (window.confirm('确定要删除该用户吗？')) {
      try {
        await adminDeleteUser(userId);
        setUsers(users.filter(user => user.id !== userId));
        alert('用户删除成功');
      } catch (err) {
        setError(err.response?.data?.message || '删除用户失败');
        console.error("Error deleting user:", err);
      }
    }
  };

  const handleEditUser = (user) => {
    setEditingUser({ ...user });
  };

  const handleSaveUser = async () => {
    if (!editingUser) return;
    try {
      const response = await adminUpdateUser(editingUser.id, editingUser);
      setUsers(users.map(user => (user.id === editingUser.id ? response.data.user || response.data : user)));
      setEditingUser(null);
      alert('用户信息更新成功');
    } catch (err) {
      setError(err.response?.data?.message || '更新用户信息失败');
      console.error("Error updating user:", err);
    }
  };

  return (
    <div className="user-management-page">
      <h1>用户管理</h1>
      {error && <div className="error-message">{error}</div>}
      <div className="user-search">
        <input
          type="text"
          placeholder="搜索用户..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button onClick={fetchUsers}>搜索</button>
      </div>
      {isLoading ? (
        <div>加载中...</div>
      ) : (
        <table className="user-table">
          <thead>
            <tr>
              <th>用户名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {users.length === 0 ? (
              <tr>
                <td colSpan="4">没有找到用户</td>
              </tr>
            ) : (
              users.map(user => (
                <tr key={user.id}>
                  {editingUser && editingUser.id === user.id ? (
                    <>
                      <td><input type="text" value={editingUser.username} onChange={(e) => setEditingUser({...editingUser, username: e.target.value })} /></td>
                      <td><input type="email" value={editingUser.email} onChange={(e) => setEditingUser({...editingUser, email: e.target.value })} /></td>
                      <td><input type="text" value={editingUser.role} onChange={(e) => setEditingUser({...editingUser, role: e.target.value })} /></td>
                      {/* Add other editable fields as necessary */}
                      <td>
                        <button onClick={handleSaveUser} className="save-btn">保存</button>
                        <button onClick={() => setEditingUser(null)} className="cancel-btn">取消</button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td>{user.username}</td>
                      <td>{user.email}</td>
                      <td>{user.role}</td>
                      {/* Display other user fields */}
                      <td>
                        <button onClick={() => handleEditUser(user)} className="edit-btn">编辑</button>
                        <button onClick={() => handleDeleteUser(user.id)} className="delete-btn">删除</button>
                      </td>
                    </>
                  )}
                </tr>
              ))
            )}
          </tbody>
        </table>
      )}
      {/* Pagination and other components can be added here */}
    </div>
  );
}

export default UserManagementPage;