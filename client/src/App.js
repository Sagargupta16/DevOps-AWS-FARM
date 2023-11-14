import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [users, setUsers] = useState([]);
  const [blogs, setBlogs] = useState([]);
  const [showUserForm, setShowUserForm] = useState(false);
  const [showBlogForm, setShowBlogForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [editingBlog, setEditingBlog] = useState(null);

  useEffect(() => {
    fetch("/user")
      .then((response) => response.json())
      .then((data) => setUsers(data));
    fetch("/blog")
      .then((response) => response.json())
      .then((data) => setBlogs(data));
  }, []);

  const addUser = (event) => {
    event.preventDefault();
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("pass").value;

    fetch("/user", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, email, password }),
    })
      .then((response) => response.json())
      .then((data) => {
        setUsers([
          ...users,
          {
            name: name,
            email: email,
            password: password,
          },
        ]);
        document.getElementById("name").value = "";
        document.getElementById("email").value = "";
        document.getElementById("pass").value = "";
        setShowUserForm(false);
      });
  };

  const updateUser = (id) => {
    const name = document.getElementById("name1").value;
    const email = document.getElementById("email1").value;
    const password = document.getElementById("pass1").value;
    fetch(`/user/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ name, email, password }),
    })
      .then((response) => response.json())
      .then((updatedUser) => {
        const updatedUsers = users.map((user) => {
          if (user.id === id) {
            return updatedUser;
          }
          return user;
        });
        setUsers(updatedUsers);
        setEditingUser(null);
        cancelEditUser();
      });
  };

  const deleteUser = (id) => {
    fetch(`/user/${id}`, {
      method: "DELETE",
    }).then(() => {
      const filteredUsers = users.filter((user) => user.id !== id);
      setUsers(filteredUsers);
    });
  };

  const editUser = (user) => {
    setEditingUser(user.id);
    document.getElementById("name").value = user.name;
    document.getElementById("email").value = user.email;
  };

  const cancelEditUser = () => {
    setEditingUser(null);
    document.getElementById("name").value = "";
    document.getElementById("email").value = "";
    document.getElementById("pass").value = "";
  };

  const addBlog = (event) => {
    event.preventDefault();
    const title = document.getElementById("title").value;
    const content = document.getElementById("content").value;
    const creator = document.getElementById("creator").value;

    fetch("/blog", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title, content, creator }),
    })
      .then((response) => response.json())
      .then((data) => {
        setBlogs([
          ...blogs,
          {
            title: title,
            content: content,
            creator: creator,
          },
        ]);
        document.getElementById("title").value = "";
        document.getElementById("content").value = "";
        document.getElementById("creator").value = "";
        setShowBlogForm(false);
      });
  };

  const updateBlog = (id) => {
    const title = document.getElementById("title1").value;
    const content = document.getElementById("content1").value;
    const creator = document.getElementById("creator1").value;
    fetch(`/blog/${id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ title, content, creator }),
    })
      .then((response) => response.json())
      .then((updatedBlog) => {
        const updatedBlogs = blogs.map((blog) => {
          if (blog.id === id) {
            return updatedBlog;
          }
          return blog;
        });
        setBlogs(updatedBlogs);
        setEditingBlog(null);
        cancelEditBlog();
      });
  };

  const deleteBlog = (id) => {
    fetch(`/blog/${id}`, {
      method: "DELETE",
    }).then(() => {
      const filteredBlogs = blogs.filter((blog) => blog.id !== id);
      setBlogs(filteredBlogs);
    });
  };

  const editBlog = (blog) => {
    setEditingBlog(blog.id);
    document.getElementById("title").value = blog.title;
    document.getElementById("content").value = blog.content;
    document.getElementById("creator").value = blog.creator;
  };

  const cancelEditBlog = () => {
    setEditingBlog(null);
    document.getElementById("title").value = "";
    document.getElementById("content").value = "";
    document.getElementById("creator").value = "";
  };

  return (
    <div className="App">
      <div className="main">
        <h1 className="heads">Users</h1>
        {showUserForm ? (
          <form className="form" onSubmit={addUser}>
            <input type="text" id="name" placeholder="Name" required />
            <input type="email" id="email" placeholder="Email" required />
            <input type="password" id="pass" placeholder="Password" required />
            <input className="btn" type="submit" value="Add" />
            <input
              className="btn"
              type="button"
              onClick={() => setShowUserForm(false)}
              value="Cancel"
            />
          </form>
        ) : (
          <button className="btn" onClick={() => setShowUserForm(true)}>
            Add User
          </button>
        )}

        {users.map((user) => (
          <div className="content" key={user.id}>
            {editingUser === user.id ? (
              <form className="form">
                <input type="text" id="name1" defaultValue={user.name} />
                <input type="email" id="email1" defaultValue={user.email} />
                <input
                  type="password"
                  id="pass1"
                  defaultValue={user.password}
                />
                <input
                  className="btn"
                  onClick={() => updateUser(user.id)}
                  type="button"
                  value="Save"
                />
                <input
                  className="btn"
                  onClick={() => cancelEditUser()}
                  type="button"
                  value="Cancel"
                />
              </form>
            ) : (
              <>
                <div>Name: {user.name}</div>
                <div>Email: {user.email}</div>
                <input
                  className="btn"
                  onClick={() => deleteUser(user.id)}
                  type="button"
                  value="Delete"
                />
                <input
                  className="btn"
                  onClick={() => editUser(user)}
                  type="button"
                  value="Update"
                />
              </>
            )}
          </div>
        ))}
      </div>
      <div className="main">
        <h1 className="heads">Blogs</h1>
        {showBlogForm ? (
          <form className="form" onSubmit={addBlog}>
            <input type="text" id="title" placeholder="Title" required />
            <input type="text" id="content" placeholder="Content" required />
            <input type="text" id="creator" placeholder="Author" required />
            <input className="btn" type="submit" value="Add" />
            <input
              onClick={() => setShowBlogForm(false)}
              className="btn"
              type="button"
              value="Cancel"
            />
          </form>
        ) : (
          <button className="btn" onClick={() => setShowBlogForm(true)}>
            Add Blog
          </button>
        )}

        {blogs.map((blog) => (
          <div className="content" key={blog.id}>
            {editingBlog === blog.id ? (
              <>
                <input type="text" id="title1" defaultValue={blog.title} />
                <input type="text" id="content1" defaultValue={blog.content} />
                <input type="text" id="creator1" defaultValue={blog.creator} />
                <input
                  className="btn"
                  onClick={() => updateBlog(blog.id)}
                  type="button"
                  value="Save"
                />
                <input
                  className="btn"
                  onClick={() => cancelEditBlog()}
                  type="button"
                  value="Cancel"
                />
              </>
            ) : (
              <>
                <div>Title: {blog.title}</div>
                <div>Content: {blog.content}</div>
                <div>Author: {blog.creator}</div>
                <input
                  onClick={() => deleteBlog(blog.id)}
                  className="btn"
                  type="button"
                  value="Delete"
                />
                <input
                  onClick={() => editBlog(blog)}
                  className="btn"
                  type="button"
                  value="Update"
                />
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
