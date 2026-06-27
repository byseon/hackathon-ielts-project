import { createClient } from "@supabase/supabase-js";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.warn(
    "Supabase env vars missing. Copy .env.example to .env and add Lovable Cloud credentials.",
  );
}

export const supabase = createClient(
  supabaseUrl ?? "https://placeholder.supabase.co",
  supabaseKey ?? "placeholder-key",
);

export type Profile = {
  id: string;
  user_id: string;
  display_name: string | null;
  target_band: number | null;
  exam_date: string | null;
  created_at: string;
};
