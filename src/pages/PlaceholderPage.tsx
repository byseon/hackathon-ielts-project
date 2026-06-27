import { AppShell } from "@/components/AppShell";

export default function PlaceholderPage({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <AppShell>
      <h1 className="text-2xl font-bold">{title}</h1>
      <p className="mt-4 text-stone-600">{description}</p>
      <p className="mt-8 rounded-xl border border-dashed border-stone-300 p-6 text-center text-sm text-stone-500">
        Tavus AI video integration coming next. See documentation/flows.md.
      </p>
    </AppShell>
  );
}
