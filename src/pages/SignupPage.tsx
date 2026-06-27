import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Button } from "@/components/Button";
import { useAuth } from "@/contexts/AuthContext";

export default function SignupPage() {
  const { signUp, session } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (session) {
    return <Navigate to="/onboarding" replace />;
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const { error: err } = await signUp(email, password);
    setLoading(false);
    if (err) {
      setError(err.message);
      return;
    }
    navigate("/onboarding");
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-4">
      <Link to="/" className="mb-8 text-sm text-teal-700 hover:underline">
        ← Back to SpeakLab
      </Link>
      <h1 className="text-2xl font-bold">Create your account</h1>
      <p className="mt-2 text-stone-600">
        Start with a free IELTS speaking mock.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-4">
        <label className="block">
          <span className="text-sm font-medium text-stone-700">Email</span>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2.5 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-stone-700">Password</span>
          <input
            type="password"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2.5 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
          />
        </label>
        {error && (
          <p className="text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        <Button type="submit" disabled={loading} className="w-full">
          {loading ? "Creating account…" : "Take your free mock"}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-stone-600">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-teal-700 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
