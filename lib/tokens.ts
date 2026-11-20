/** Centralised design tokens. CSS variables in app/globals.css mirror these values. */
export const tokens = {
  color: {
    blue: "#244B70",       // Trust Blue (primary)
    blueDeep: "#1B3A58",   // hover / pressed
    coral: "#E98262",      // Forge Coral (restrained accent)
    coralInk: "#A4441F",   // coral for small text on light (AA)
    soft: "#EFF4F8",       // Soft Blue surface
    white: "#FFFFFF",
    warm: "#F3F4F2",       // Warm Neutral surface
    slate: "#344452",      // body text / dark surfaces
    muted: "#566878",
    border: "#D9E2EA",
  },
  radius: { sm: 6, md: 10, lg: 14 },
  font: { head: "Sora", body: "Inter", mono: "IBM Plex Mono" },
} as const;
