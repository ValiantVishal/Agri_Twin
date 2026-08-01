import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./components/Login";
import Register from "./components/Registration";
import ProfileSetup from "./components/ProfileSetup";
import Dashboard from "./components/Dashboard";
import PlotMappingPage from "./components/PlotMappingPage";
import ActivityLogPage from "./components/ActivityLogPage";
import AIAssistantPage from "./components/AIAssistantPage";

function App() {
  return (
    <BrowserRouter>
      <div className="contour-bg"></div>
      <Routes>
        <Route
          path="/"
          element={<Login />}
        />
        <Route
          path="/register"
          element={<Register />}
        />
        <Route
          path="/profile"
          element={<ProfileSetup />}
        />
        <Route
          path="/dashboard"
          element={<Dashboard />}
        />
        <Route
          path="/plots"
          element={<PlotMappingPage />}
        />
        <Route
          path="/activity-log"
          element={<ActivityLogPage />}
        />
        <Route
          path="/assistant"
          element={<AIAssistantPage />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;