/** Decorative infinity mark echoing the Forge logo. Purely visual (aria-hidden). */
export default function Infinity({ className, tone = "light" }: { className?: string; tone?: "light" | "dark" }) {
  const id = `inf-${tone}`;
  const a = tone === "light" ? "#FFFFFF" : "#174A82";
  const b = tone === "light" ? "#F4A261" : "#F25C3C";
  return (
    <svg className={className} viewBox="0 0 200 100" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id={id} x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor={a} />
          <stop offset=".48" stopColor={a} />
          <stop offset=".52" stopColor={b} />
          <stop offset="1" stopColor={b} />
        </linearGradient>
      </defs>
      <path d="M100 50 C128 8 190 8 190 50 C190 92 128 92 100 50 C72 8 10 8 10 50 C10 92 72 92 100 50 Z"
        fill="none" stroke={`url(#${id})`} strokeWidth="13" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
