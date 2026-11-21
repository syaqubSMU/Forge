# What is published, and how to publish more

**Published now:** Home (`/`), Products (`/products`, plus each product page) and AI & Automation (`/ai-automation`).

**Unpublished (kept in the repo, not built into the site):** everything in `app/_unpublished/`:
Platform, Solutions, Insights, About, Contact, Book a Discovery Call, Privacy and Terms.
Folders starting with `_` are ignored by Next.js routing, so these pages do not exist on the live site.
Their URLs return "Page not found" and they are not in the sitemap.

## To publish a page again
1. Move its folder out of `app/_unpublished/` into `app/` (for example `git mv app/_unpublished/platform app/platform`).
2. Add it to `nav` in `lib/content.ts` and to `pages` in `app/sitemap.ts`.
3. Check any buttons that linked to other unpublished pages (for example "Book a Discovery Call").
4. Build, test, then merge to `main`.

## Notes
- The "Request" form only appears when `NEXT_PUBLIC_INQUIRY_ENDPOINT` is set; otherwise a short notice is shown. If you switch it on, also publish `privacy` first (it is a draft that needs legal review).
- Home still shows the Financial Intelligence preview and "Beyond the Shadow Budget" as in development, so the story stays visible without a Platform page.
