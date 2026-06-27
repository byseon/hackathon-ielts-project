import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/Button";
import { useAuth } from "@/contexts/AuthContext";

export default function OnboardingPage() {
  const { upsertProfile, profile } = useAuth();
  const navigate = useNavigate();
  const [displayName, setDisplayName] = useState(profile?.display_name ?? "");
  const [targetBand, setTargetBand] = useState(
    profile?.target_band?.toString() ?? "6.5",
  );
  const [examDate, setExamDate] = useState(profile?.exam_date ?? "");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const { error: err } = await upsertProfile({
      display_name: displayName || null,
      target_band: targetBand ? parseFloat(targetBand) : null,
      exam_date: examDate || null,
    });
    if (err) {
      setError(err.message);
      return;
    }
    navigate("/mock");
  };

  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-4">
      <h1 className="text-2xl font-bold">Set your goal</h1>
      <p className="mt-2 text-stone-600">
        Optional — helps personalize your study plan.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-4">
        <label className="block">
          <span className="text-sm font-medium text-stone-700">Your name</span>
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Anna"
            className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2.5 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-stone-700">
            Target band (optional)
          </span>
          <input
            type="number"
            step="0.5"
            min="4"
            max="9"
            value={targetBand}
            onChange={(e) => setTargetBand(e.target.value)}
            className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2.5 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
          />
        </label>
        <label className="block">
          <span className="text-sm font-medium text-stone-700">
            Exam date (optional)
          </span>
          <input
            type="date"
            value={examDate}
            onChange={(e) => setExamDate(e.target.value)}
            className="mt-1 w-full rounded-lg border border-stone-300 px-3 py-2.5 focus:border-teal-500 focus:outline-none focus:ring-2 focus:ring-teal-500/20"
          />
        </label>
        {error && (
          <p className="text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        <Button type="submit" className="w-full">
          Start first mock
        </Button>
      </form>
    </div>
  );
}
