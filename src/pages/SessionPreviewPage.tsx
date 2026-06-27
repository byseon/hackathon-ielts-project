import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/Button";

const activities = [
  {
    title: "Part 2 cue card",
    detail: 'Describe a place you like to visit (~7 min)',
  },
  {
    title: "Part 3 discussion",
    detail: "Follow-ups on travel and places (~5 min)",
  },
];

export default function SessionPreviewPage() {
  return (
    <AppShell>
      <h1 className="text-2xl font-bold">Today&apos;s session</h1>
      <p className="mt-2 text-stone-600">
        12 min · 2 activities · Focus: Lexical resource + Part 2
      </p>

      <p className="mt-6 rounded-xl bg-stone-100 p-4 text-sm text-stone-700">
        We picked these because your Part 2 answers were short and vocabulary
        was your lowest score in Mock #1.
      </p>

      <ul className="mt-8 space-y-4">
        {activities.map((a, i) => (
          <li
            key={a.title}
            className="flex gap-4 rounded-xl border border-stone-200 bg-white p-4"
          >
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-teal-100 font-bold text-teal-800">
              {i + 1}
            </span>
            <div>
              <p className="font-semibold">{a.title}</p>
              <p className="text-sm text-stone-600">{a.detail}</p>
            </div>
          </li>
        ))}
      </ul>

      <Button to="/session/part2" className="mt-10 w-full">
        Begin
      </Button>
    </AppShell>
  );
}
