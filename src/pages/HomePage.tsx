import { Link } from "react-router-dom";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/Button";
import { useAuth } from "@/contexts/AuthContext";

const criteria = [
  { label: "Fluency", score: 5.5 },
  { label: "Lexical", score: 5.0 },
  { label: "Grammar", score: 5.5 },
  { label: "Pronunciation", score: 6.0 },
];

export default function HomePage() {
  const { profile } = useAuth();
  const name = profile?.display_name?.split(" ")[0] ?? "there";

  return (
    <AppShell>
      <p className="text-sm text-stone-500">Day 1 of your plan</p>
      <h1 className="mt-1 text-2xl font-bold">Good morning, {name}</h1>

      <div className="mt-8 rounded-2xl border border-teal-200 bg-white p-5 shadow-sm">
        <span className="inline-block rounded-full bg-teal-50 px-3 py-1 text-xs font-medium text-teal-800">
          Because Mock #1: Lexical resource 5.0
        </span>
        <h2 className="mt-4 text-xl font-semibold">
          Build vocabulary for Part 2
        </h2>
        <p className="mt-2 text-sm text-stone-600">~12 min · 2 activities</p>
        <Button to="/session/preview" className="mt-6 w-full">
          Start today&apos;s session
        </Button>
      </div>

      <div className="mt-8">
        <h3 className="text-sm font-medium text-stone-500">
          Mock #1 — 4 criteria
        </h3>
        <div className="mt-3 grid grid-cols-2 gap-3">
          {criteria.map(({ label, score }) => (
            <div
              key={label}
              className="rounded-xl border border-stone-200 bg-white p-3"
            >
              <p className="text-xs text-stone-500">{label}</p>
              <p className="text-lg font-bold">{score.toFixed(1)}</p>
            </div>
          ))}
        </div>
      </div>

      <Link
        to="/practice"
        className="mt-8 block text-center text-sm text-teal-700 hover:underline"
      >
        Explore practice by part
      </Link>
    </AppShell>
  );
}
