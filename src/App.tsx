import { Routes, Route, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import LandingPage from "@/pages/LandingPage";
import SignupPage from "@/pages/SignupPage";
import LoginPage from "@/pages/LoginPage";
import OnboardingPage from "@/pages/OnboardingPage";
import HomePage from "@/pages/HomePage";
import SessionPreviewPage from "@/pages/SessionPreviewPage";
import PlaceholderPage from "@/pages/PlaceholderPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/login" element={<LoginPage />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/home" element={<HomePage />} />
        <Route path="/session/preview" element={<SessionPreviewPage />} />
        <Route
          path="/session/part2"
          element={
            <PlaceholderPage
              title="Part 2 practice"
              description="Cue card + 60s prep + 2 min speak — AI video examiner."
            />
          }
        />
        <Route
          path="/mock"
          element={
            <PlaceholderPage
              title="Full mock exam"
              description="Parts 1–3 timed simulation with AI video examiner."
            />
          }
        />
        <Route
          path="/practice"
          element={
            <PlaceholderPage
              title="Practice by part"
              description="Self-directed Part 1, 2, or 3 drills."
            />
          }
        />
        <Route
          path="/progress"
          element={
            <PlaceholderPage
              title="Progress"
              description="Band trends and criteria over time."
            />
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
