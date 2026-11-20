# FORGE website redesign — audit, decisions and handover

Branch: `redesign` (production on `main` is untouched until approved).

## Phase 1 — Audit (before the redesign)
- Stack: Next.js 14 (App Router, static export), React 18, TypeScript, Ant Design 5. Deployed to GitHub Pages by `.github/workflows/deploy.yml` from `main`, base path `/Forge`.
- Previous site: 14 routes positioned for nonprofits ("Grant Operations Solutions"), flat coral/blue palette, illustrated hero collage, intro-video poster, placeholder chat button.
- Reusable and kept: Next/AntD/GitHub Pages pipeline, forms with honeypot and prototype-mode honesty, Chatling inline embed (powers the free Travel Budget Calculator), analytics event helper, error/not-found pages, product catalogue structure.
- Replaced: brand, palette, typography, all page content and information architecture, hero, navigation, footer.
- Removed: nonprofit-positioned copy, illustrated collage, intro video section and its poster (its tagline conflicted with the new brand), floating chat placeholder (a non-functional control), resources/consultation routes (now Insights / Discovery call).
- Old URLs removed: `/resources/*`, `/book-consultation`, `/solutions/[slug]`, `/ai-automation/[slug]`, old product slugs. Static hosting cannot redirect; add redirects if old links matter.

## Brand and design system
- Logo system in `public/brand/` (SVG, Sora Bold letterforms converted to outlines): wordmark, compact icon, tile/favicon, horizontal and stacked lockups, light and dark versions. React component: `components/brand/Logo.tsx`.
- Tokens: `lib/tokens.ts` and CSS variables at the top of `app/globals.css`. Palette: Trust Blue #244B70, Forge Coral #E98262, Soft Blue #EFF4F8, Warm Neutral #F3F4F2, Slate #344452.
- Type: Sora (headings), Inter (body and dashboard), IBM Plex Mono (technical labels).
- Coral is an accent only. White text on #E98262 fails AA contrast, so primary buttons are Trust Blue and the accent button uses dark text. Small coral text uses a darker "coral ink" (#A4441F).

## Content decisions and assumptions (please confirm)
1. Statuses: the platform, its modules and all AI capabilities are labelled "In development". Nothing is described as operational or integrated. Products are "Available on request"; the Travel Budget Calculator is a "Free tool" (live via Chatling).
2. Prices are the indicative figures from the earlier product plan, remapped to the new product names. Confirm or remove (commercial decision). Online checkout does not exist; "Request this product" sends an inquiry.
3. Mini-course dropped (not in the new brief). Product list follows the brief.
4. Insights: five short general-practice guides were drafted with no statistics or regulatory claims. "Federal funding developments" shows a notice and has no articles until sourced content exists. Please review all copy.
5. About: founder profile is a clearly marked placeholder; no credentials, testimonials or case studies were invented.
6. Dashboard: all data is synthetic and labelled. Definitions: Available = Budget − Actual − Commitments; projection = estimate (trailing-3-month average × months remaining, or commitments if higher); utilization = (actual + commitments) / budget. Institutional data is shown as "imported <date>", never real time.
7. Named third-party systems (PeopleSoft, Cayuse, Concur, SharePoint) appear only as names in the architecture diagram with a non-affiliation disclaimer. No SMU branding is used.

## Outstanding
- Founder-approved copy, About profile, real contact email, privacy/terms (draft text, legal review needed).
- Form delivery endpoint (`NEXT_PUBLIC_INQUIRY_ENDPOINT`), analytics provider, optional site assistant (`NEXT_PUBLIC_CHATLING_CHATBOT_ID`).
- Chatling allowed-domain setting for the final domain.
- Confirm prices and product availability; decide on redirects for old URLs.

## Deployment
- Pushes to `redesign` run the build in CI but do not deploy (deploy job is limited to `main`).
- To go live: review, then merge `redesign` into `main`. The workflow publishes to GitHub Pages (Settings → Pages → Source: GitHub Actions).
- Local preview: `NEXT_PUBLIC_BASE_PATH=/Forge npm run build`, serve the `out/` folder under `/Forge`.
