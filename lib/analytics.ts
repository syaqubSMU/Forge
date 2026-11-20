/** Provider-agnostic event helper. Events go to window.dataLayer; wire a provider (GA4, Plausible, etc.) later. */
export type GosEvent =
  | "consultation_cta_clicked" | "consultation_form_submitted" | "product_viewed" | "purchase_completed"
  | "chatbot_opened" | "chatbot_lead_submitted" | "resource_downloaded" | "intro_video_played";

export function track(event: GosEvent, props: Record<string, unknown> = {}) {
  if (typeof window === "undefined") return;
  const w = window as unknown as { dataLayer?: unknown[] };
  (w.dataLayer = w.dataLayer || []).push({ event, ...props, path: window.location.pathname });
  if (process.env.NODE_ENV !== "production") console.debug("[analytics]", event, props);
}
