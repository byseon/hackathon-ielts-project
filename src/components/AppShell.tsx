import { Link, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";

const navItems = [
  { label: "Home", path: "/home" },
  { label: "Practice", path: "/practice" },
  { label: "Mock", path: "/mock" },
  { label: "Progress", path: "/progress" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation();
  const { signOut, profile } = useAuth();

  return (
    <div className="mx-auto flex min-h-screen max-w-lg flex-col px-4 pb-24 pt-6">
      <header className="mb-6 flex items-center justify-between">
        <Link to="/home" className="text-lg font-bold text-stone-900">
          SpeakLab
        </Link>
        <button
          type="button"
          onClick={() => signOut()}
          className="text-sm text-stone-500 hover:text-stone-700"
        >
          Log out
        </button>
      </header>

      <main className="flex-1">{children}</main>

      <nav className="fixed bottom-0 left-0 right-0 border-t border-stone-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-lg justify-around px-2 py-3">
          {navItems.map((item) => {
            const active = pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`rounded-lg px-3 py-2 text-xs font-medium ${
                  active
                    ? "bg-teal-50 text-teal-800"
                    : "text-stone-500 hover:text-stone-800"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>

      {profile?.display_name && (
        <p className="sr-only">Signed in as {profile.display_name}</p>
      )}
    </div>
  );
}
