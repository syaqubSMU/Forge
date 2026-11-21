# Forge assistant (Chatling) — setup and design brief

The site already loads a floating assistant on every page except the Travel Budget Calculator page (which has its own bot).
Currently it uses the same bot as the calculator (6621135586). To use a separate Forge-trained bot, follow the steps below.

## Switch it on
1. In Chatling, create the bot and publish it. Under the bot's website/domain settings, allow `syaqubsmu.github.io` (and your own domain later).
2. Copy the bot ID from the embed snippet (`data-id="..."`).
3. Either send the ID to the developer to set as the default in `lib/content.ts`, or in GitHub go to
   Settings → Secrets and variables → Actions → Variables → New repository variable:
   name `NEXT_PUBLIC_CHATLING_CHATBOT_ID`, value = the ID. Then Actions → "Deploy to GitHub Pages" → Run workflow.

## Suggested design
- Name: "Forge Assistant" (or "Ask Forge"). Position: bottom right, keep it clear of the main buttons.
- Welcome message: "Hi, I'm the Forge assistant. I can explain our products, the free Travel Budget Calculator and what we're building in AI & automation. What would you like to know?"
- Knowledge: only approved Forge content: the Home, Products and AI & Automation pages, the product catalogue and FAQs, and the "FORGE is / is not" statements.
- Must say, not guess: platform and AI capabilities are in development; online ordering is not available; prices are indicative; FORGE does not replace official university financial systems.
- Must not: give legal or compliance advice, approve spending, present projections as actual balances, invent features, prices, testimonials or integrations, or collect confidential award documents or restricted data (health, financial account, student records).
- Fallback when unsure: say so and point to the request form on the Products page.
- Lead capture: only send people to the site's request form unless the chat tool's own submissions are configured and covered by the privacy notice.
