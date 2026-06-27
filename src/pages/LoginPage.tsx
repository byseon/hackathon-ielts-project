import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { Button } from "@/components/Button";
import { useAuth } from "@/contexts/AuthContext";

export default function LoginPage() {
  const { signIn, session } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (session) {
    return <Navigate to="/home" replace />;
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    const { error: err } = await signIn(email, password);
    setLoading(false);
    if (err) {
      setError(err.message);
      return;
    }
    navigate("/home");
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-4">
      <Link to="/" className="mb-8 text-sm text-teal-700 hover:underline">
        ← Back to SpeakLab
      </Link>
      <h1 className="text-2xl font-bold">Welcome back</h1>

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
          {loading ? "Signing in…" : "Log in"}
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-stone-600">
        New here?{" "}
        <Link to="/signup" className="font-medium text-teal-700 hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}
