import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';

function App() {
  const [users, setUsers] = useState([]);
  const [blogs, setBlogs] = useState([]);
  const [activeTab, setActiveTab] = useState('users');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // User form states
  const [userForm, setUserForm] = useState({
    name: '',
    email: '',
    password: ''
  });
  const [editingUser, setEditingUser] = useState(null);

  // Blog form states
  const [blogForm, setBlogForm] = useState({
    title: '',
    content: '',
    creator: ''
  });
  const [editingBlog, setEditingBlog] = useState(null);

  useEffect(() => {
    fetchUsers();
    fetchBlogs();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/user`);
      setUsers(response.data);
    } catch (err) {
      setError('Error fetching users');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchBlogs = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/blog`);
      setBlogs(response.data);
    } catch (err) {
      setError('Error fetching blogs');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // User CRUD operations
  const handleUserSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      if (editingUser) {
        await axios.put(`${API_BASE_URL}/user/${editingUser.id}`, userForm);
        setEditingUser(null);
      } else {
        await axios.post(`${API_BASE_URL}/user`, userForm);
      }
      setUserForm({ name: '', email: '', password: '' });
      fetchUsers();
    } catch (err) {
      setError('Error saving user');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUserEdit = (user) => {
    setEditingUser(user);
    setUserForm({
      name: user.name,
      email: user.email,
      password: ''
    });
  };

  const handleUserDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      try {
        setLoading(true);
        await axios.delete(`${API_BASE_URL}/user/${id}`);
        fetchUsers();
      } catch (err) {
        setError('Error deleting user');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  // Blog CRUD operations
  const handleBlogSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      if (editingBlog) {
        await axios.put(`${API_BASE_URL}/blog/${editingBlog.id}`, blogForm);
        setEditingBlog(null);
      } else {
        await axios.post(`${API_BASE_URL}/blog`, blogForm);
      }
      setBlogForm({ title: '', content: '', creator: '' });
      fetchBlogs();
    } catch (err) {
      setError('Error saving blog');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleBlogEdit = (blog) => {
    setEditingBlog(blog);
    setBlogForm({
      title: blog.title,
      content: blog.content,
      creator: blog.creator
    });
  };

  const handleBlogDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this blog?')) {
      try {
        setLoading(true);
        await axios.delete(`${API_BASE_URL}/blog/${id}`);
        fetchBlogs();
      } catch (err) {
        setError('Error deleting blog');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  const cancelEdit = () => {
    setEditingUser(null);
    setEditingBlog(null);
    setUserForm({ name: '', email: '', password: '' });
    setBlogForm({ title: '', content: '', creator: '' });
  };

  return (
    <div className="App">
      <div className="header">
        <h1>DevOps Farm - Management System</h1>
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Users
          </button>
          <button 
            className={`tab ${activeTab === 'blogs' ? 'active' : ''}`}
            onClick={() => setActiveTab('blogs')}
          >
            Blogs
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {loading && <div className="loading">Loading...</div>}

      {activeTab === 'users' && (
        <div className="section">
          <h2>User Management</h2>
          
          <form className="form" onSubmit={handleUserSubmit}>
            <div className="form-group">
              <input
                type="text"
                placeholder="Name"
                value={userForm.name}
                onChange={(e) => setUserForm({...userForm, name: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="email"
                placeholder="Email"
                value={userForm.email}
                onChange={(e) => setUserForm({...userForm, email: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <input
                type="password"
                placeholder="Password"
                value={userForm.password}
                onChange={(e) => setUserForm({...userForm, password: e.target.value})}
                required
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {editingUser ? 'Update User' : 'Add User'}
              </button>
              {editingUser && (
                <button type="button" className="btn btn-secondary" onClick={cancelEdit}>
                  Cancel
                </button>
              )}
            </div>
          </form>

          <div className="items-grid">
            {users.map((user) => (
              <div key={user.id} className="card">
                <div className="card-content">
                  <h3>{user.name}</h3>
                  <p><strong>Email:</strong> {user.email}</p>
                </div>
                <div className="card-actions">
                  <button 
                    className="btn btn-edit" 
                    onClick={() => handleUserEdit(user)}
                  >
                    Edit
                  </button>
                  <button 
                    className="btn btn-delete" 
                    onClick={() => handleUserDelete(user.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'blogs' && (
        <div className="section">
          <h2>Blog Management</h2>
          
          <form className="form" onSubmit={handleBlogSubmit}>
            <div className="form-group">
              <input
                type="text"
                placeholder="Title"
                value={blogForm.title}
                onChange={(e) => setBlogForm({...blogForm, title: e.target.value})}
                required
              />
            </div>
            <div className="form-group">
              <textarea
                placeholder="Content"
                value={blogForm.content}
                onChange={(e) => setBlogForm({...blogForm, content: e.target.value})}
                rows="4"
                required
              />
            </div>
            <div className="form-group">
              <input
                type="text"
                placeholder="Author"
                value={blogForm.creator}
                onChange={(e) => setBlogForm({...blogForm, creator: e.target.value})}
                required
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {editingBlog ? 'Update Blog' : 'Add Blog'}
              </button>
              {editingBlog && (
                <button type="button" className="btn btn-secondary" onClick={cancelEdit}>
                  Cancel
                </button>
              )}
            </div>
          </form>

          <div className="items-grid">
            {blogs.map((blog) => (
              <div key={blog.id} className="card">
                <div className="card-content">
                  <h3>{blog.title}</h3>
                  <p className="blog-content">{blog.content}</p>
                  <p><strong>Author:</strong> {blog.creator}</p>
                </div>
                <div className="card-actions">
                  <button 
                    className="btn btn-edit" 
                    onClick={() => handleBlogEdit(blog)}
                  >
                    Edit
                  </button>
                  <button 
                    className="btn btn-delete" 
                    onClick={() => handleBlogDelete(blog.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
export default App;
