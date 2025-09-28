// src/Auth.js
import React, { useState } from "react";
import "./Board.css";

function Auth({ onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const url = isLogin
        ? "http://127.0.0.1:8002/auth/login"
        : "http://127.0.0.1:8002/auth/register";

      const body = new URLSearchParams();
      body.append("username", form.username);
      body.append("password", form.password);
      
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body
      });
      
      if (!res.ok) {
        const msg = await res.json();
        throw new Error(msg.detail || "Request failed");
      }

      const data = await res.json();

      if (isLogin) {
        // store JWT token
        localStorage.setItem("token", data.access_token);
        onAuthSuccess(form.username);
      } else {
        alert("✅ Registration successful! Please login.");
        setIsLogin(true);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="bowling-app">
      <div className="auth-card">
        <h1>{isLogin ? "🎳 Login" : "🎳 Register"}</h1>

        <form className="auth-form" onSubmit={handleSubmit}>
          <input
            type="text"
            name="username"
            placeholder="Username"
            value={form.username}
            onChange={handleChange}
            required
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            required
          />
          <button type="submit" className="auth-btn">
            {isLogin ? "Login" : "Register"}
          </button>
        </form>

        {error && <p className="error-msg">{error}</p>}

        <p className="switch">
          {isLogin ? "No account?" : "Already registered?"}{" "}
          <button
            type="button"
            onClick={() => setIsLogin(!isLogin)}
            className="link-btn"
          >
            {isLogin ? "Register here" : "Login here"}
          </button>
        </p>
      </div>
    </div>
  );
}

export default Auth;
