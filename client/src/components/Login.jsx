import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { loginUser } from "../api/auth";
import apiClient from "../api/apiClient";
import "../css/Login.css";

function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await loginUser(form);

      localStorage.setItem(
        "token",
        response.data.access_token
      );

      alert("Login Successful");
      try {
        const profileRes = await apiClient.get("/profile");
        if (profileRes.data && profileRes.data.phone) {
          navigate("/dashboard");
        } else {
          navigate("/profile");
        }
      } catch (err) {
        navigate("/profile");
      }

    } catch (error) {
      alert(
        error.response?.data?.detail ||
        "Login Failed"
      );

      console.error(error);
    }
  };

  return (
    <div className="container">
      <div className="card">

        <h1>Welcome Back</h1>
        <p>Login to continue</p>

        <form onSubmit={handleSubmit}>

          <input
            type="email"
            name="email"
            placeholder="Email Address"
            value={form.email}
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

          <button type="submit">
            Login
          </button>

        </form>

        <div className="bottom">
          Don't have an account?
          <Link to="/register"> Register</Link>
        </div>

      </div>
    </div>
  );
}

export default Login;