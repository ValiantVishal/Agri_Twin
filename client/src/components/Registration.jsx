import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerUser } from "../api/auth";
import "../css/Login.css"

function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (form.password !== form.confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    try {
      const response = await registerUser({
        name: form.name,
        email: form.email,
        password: form.password,
      });

      console.log(response.data);

      alert("Registration Successful!");

      // Redirect to login page
      navigate("/");

    } catch (error) {
      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Registration Failed"
      );
    }
  };

  return (
    <div className="container">
      <div className="card">

        <h1>Create Account</h1>
        <p>Register to continue</p>

        <form onSubmit={handleSubmit}>

          <input
            type="text"
            name="name"
            placeholder="Full Name"
            value={form.name}
            onChange={handleChange}
            required
          />

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

          <input
            type="password"
            name="confirmPassword"
            placeholder="Confirm Password"
            value={form.confirmPassword}
            onChange={handleChange}
            required
          />

          <button type="submit">
            Register
          </button>

        </form>

        <div className="bottom">
          Already have an account?
          <Link to="/"> Login</Link>
        </div>

      </div>
    </div>
  );
}

export default Register;