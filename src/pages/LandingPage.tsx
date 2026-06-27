import { PrimaryCta } from "@/components/Button";

const faqs = [
  {
    q: "Is this like the real IELTS Speaking test?",
    a: "We simulate the same three-part structure, timing, and face-to-face format. The AI examiner asks follow-up questions without showing text during Parts 1 and 3.",
  },
  {
    q: "How is my band score calculated?",
    a: "Your mock is scored on Fluency, Lexical resource, Grammar, and Pronunciation — the four official IELTS Speaking criteria.",
  },
  {
    q: "Do I need a camera and microphone?",
    a: "Yes. Speaking practice requires a microphone. A camera is recommended for the video examiner experience.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-4xl items-center justify-between px-4 py-6">
        <span className="text-lg font-bold">SpeakLab</span>
        <PrimaryCta className="!py-2 !px-4 text-sm" />
      </header>

      <section className="mx-auto max-w-4xl px-4 pb-16 pt-8 text-center">
        <h1 className="text-4xl font-bold tracking-tight text-stone-900 sm:text-5xl">
          Practice IELTS Speaking with a real AI examiner
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-stone-600">
          Face-to-face video practice for Parts 1, 2, and 3. Get a band score
          and a plan built from your mock.
        </p>
        <div className="mt-10 flex justify-center">
          <PrimaryCta />
        </div>
      </section>

      <section className="border-y border-stone-200 bg-white py-6">
        <p className="text-center text-sm font-medium text-stone-600">
          Built for IELTS · Official 4 criteria · AI video · Student-first
        </p>
      </section>

      <section className="mx-auto max-w-3xl px-4 py-16">
        <h2 className="text-2xl font-bold">
          The speaking test is the one you can&apos;t cram
        </h2>
        <p className="mt-4 text-stone-600 leading-relaxed">
          The IELTS Speaking test is an 11–14 minute face-to-face interview.
          There is no text to read. The examiner listens, follows up, and reacts
          to what you say.
        </p>
      </section>

      <section className="bg-white py-16">
        <div className="mx-auto max-w-3xl px-4">
          <h2 className="text-2xl font-bold">How it works</h2>
          <ol className="mt-8 space-y-6">
            {[
              "Take a full mock — Parts 1, 2, and 3 with an AI video examiner.",
              "See your band on 4 criteria — Fluency, Lexical resource, Grammar, Pronunciation.",
              "Follow your daily plan — practice targets your weak areas from each mock.",
            ].map((step, i) => (
              <li key={step} className="flex gap-4">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-teal-100 text-sm font-bold text-teal-800">
                  {i + 1}
                </span>
                <span className="text-stone-700">{step}</span>
              </li>
            ))}
          </ol>
          <div className="mt-10">
            <PrimaryCta />
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-3xl px-4 py-16">
        <h2 className="text-2xl font-bold">
          Not audio flashcards — a person asks you questions
        </h2>
        <p className="mt-4 text-stone-600 leading-relaxed">
          SpeakLab puts you in a video conversation with an AI examiner. You
          hear the question, you answer out loud, and you get feedback on what
          you actually said.
        </p>
      </section>

      <section className="bg-stone-100 py-16">
        <div className="mx-auto max-w-3xl px-4">
          <h2 className="text-2xl font-bold">Every mock updates your plan</h2>
          <p className="mt-4 text-stone-600">
            After each mock, SpeakLab finds your weakest criterion and part. Your
            daily sessions focus there — Part 2 cue cards, Part 3 discussions,
            or vocabulary drills.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-3xl px-4 py-16">
        <h2 className="text-2xl font-bold">FAQ</h2>
        <dl className="mt-8 space-y-6">
          {faqs.map(({ q, a }) => (
            <div key={q}>
              <dt className="font-semibold text-stone-900">{q}</dt>
              <dd className="mt-2 text-stone-600">{a}</dd>
            </div>
          ))}
        </dl>
      </section>

      <section className="border-t border-stone-200 bg-teal-900 px-4 py-16 text-center text-white">
        <h2 className="text-2xl font-bold">
          Your next mock is 14 minutes away
        </h2>
        <p className="mx-auto mt-4 max-w-md text-teal-100">
          Sign up, take your free mock, and get a plan built for you.
        </p>
        <div className="mt-8 flex justify-center">
          <PrimaryCta className="!bg-white !text-teal-900 hover:!bg-teal-50" />
        </div>
      </section>
    </div>
  );
}
