import { useState } from "react";
import { Link } from "react-router-dom";
import "../css/Login.css";

function Login() {
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

  const handleSubmit = (e) => {
    e.preventDefault();

    console.log(form);

    // API Call Here
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