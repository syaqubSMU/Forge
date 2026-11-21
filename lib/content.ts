/**
 * Single source of truth for editable site content.
 * STATUS RULE: nothing is described as operational unless it is. Platform and AI capabilities are "In development".
 * Prices are INDICATIVE placeholders carried over from the earlier product plan; confirm before publishing.
 */
export const site = {
  name: "FORGE",
  descriptor: "Connected research operations",
  tagline: "Research administration, made simpler.",
  contactEmail: "" as string, // set once a business mailbox exists
  travelCalculatorBotId: "6621135586", // Chatling bot powering the free Travel Budget Calculator
  // Site-wide floating assistant. Currently the same Chatling bot as the calculator; set NEXT_PUBLIC_CHATLING_CHATBOT_ID (or edit here) to use a separate Forge-trained bot.
  chatbotId: process.env.NEXT_PUBLIC_CHATLING_CHATBOT_ID || "6621135586",
  syntheticNote: "Illustrative synthetic data. Not real awards, people or institutions.",
};

/** Published pages only. The full site (Platform, Solutions, AI, Insights, About, Contact, ...) lives in app/_unpublished. */
export const nav = [
  { label: "Home", href: "/" },
  { label: "Products", href: "/products" },
  { label: "AI & Automation", href: "/ai-automation" },
];
/** True when a form endpoint is configured; the request form is hidden until messages can actually be delivered. */
export const requestsOpen = Boolean(process.env.NEXT_PUBLIC_INQUIRY_ENDPOINT);

export const challenges = [
  { t: "Better award visibility", d: "Know what you manage, where each award stands and what needs attention, without opening five files." },
  { t: "More reliable budget monitoring", d: "See what has posted, what is committed and what remains available, kept clearly separate." },
  { t: "Easier deadline tracking", d: "Reports, end dates and award conditions in one calendar instead of in someone's memory." },
  { t: "Less duplicate data entry", d: "Enter award information once and reuse it across trackers, reports and reminders." },
  { t: "Clearer PI communication", d: "Give principal investigators a plain view of their awards without a stack of emailed spreadsheets." },
  { t: "Fewer repetitive tasks", d: "Let intelligent automation prepare the routine work while people review and decide." },
];

export const approach = [
  { t: "Connect", d: "Bring award, budget and document information together, using approved imports, exports and APIs from your existing systems." },
  { t: "Organize", d: "Give every award one structured record: budget, commitments, deadlines, documents and notes." },
  { t: "Monitor & reconcile", d: "Track the financial position, compare against institutional reports and flag what does not match." },
  { t: "Automate", d: "Introduce reminders, extraction and reporting assistance where they genuinely save time." },
];

export type Module = { slug: string; title: string; text: string; flagship?: boolean };
export const modules: Module[] = [
  { slug: "financial-intelligence", title: "FORGE Financial Intelligence", text: "Award budgets, posted expenditures, commitments, available balances, forecasts and reconciliation: beyond the shadow budget.", flagship: true },
  { slug: "awards", title: "Award tracking", text: "One record per award: sponsor, terms, dates, amounts, contacts and status." },
  { slug: "compliance", title: "Compliance & reporting calendar", text: "Deadlines, reporting obligations and award conditions with owners and reminders." },
  { slug: "pi", title: "PI & portfolio visibility", text: "Plain, role-appropriate views for investigators, managers and directors." },
  { slug: "documents", title: "Document intelligence", text: "Organize award documents and extract key terms for human review." },
  { slug: "assistant", title: "AI research administration assistant", text: "Ask questions across your own award records and documents." },
  { slug: "funding", title: "Funding discovery", text: "Surface opportunities and match them to investigator interests." },
];

export const systemsLeft = ["PeopleSoft", "Cayuse", "Concur", "SharePoint and document repositories", "Institutional spreadsheets", "Approved APIs and data sources"];
export const workspaceItems = ["Award and grant tracking", "Budget and financial monitoring", "Compliance and reporting calendar", "PI and portfolio visibility", "Document intelligence", "AI research administration assistant", "Funding discovery"];
export const usersRight = ["Research administrators", "Department managers", "Principal investigators", "Research teams"];

export const whyForge = [
  { t: "Built for small teams", d: "Designed so a two-person team can learn and manage it without a dedicated systems administrator." },
  { t: "Works alongside your systems", d: "Integration-oriented by design. It complements official systems instead of competing with them." },
  { t: "Research-administration specific", d: "Shaped around awards, budgets, commitments, reporting and PI communication, not generic project management." },
  { t: "Modular and able to grow", d: "Start with the tools you need today and add capability as your portfolio and team grow." },
];

export const services = [
  { slug: "assessment", n: "01", t: "Research operations assessment", d: "A practical review of how awards, budgets, deadlines and documents are handled today, with a prioritized roadmap.", items: ["Current-state process and tools review", "Gap and risk summary", "Prioritized recommendations", "30–90 day improvement plan"] },
  { slug: "process", n: "02", t: "Grants management process design", d: "Clear, right-sized processes from award setup through closeout.", items: ["Award intake and setup workflow", "Roles and handoffs between department and central office", "Review and approval points", "Closeout checklist"] },
  { slug: "financial", n: "03", t: "Budget and financial oversight", d: "A reliable method for monitoring posted expenditures, commitments and available balances.", items: ["Budget monitoring approach and templates", "Commitment tracking method", "Forecasting and variance review routine", "Reconciliation routine against institutional reports"] },
  { slug: "sop", n: "04", t: "SOP development", d: "Written procedures your team can actually follow and hand to a new colleague.", items: ["Procedure drafting and review", "Checklists and decision aids", "Training notes", "Maintenance guidance"] },
  { slug: "implementation", n: "05", t: "Systems and workflow implementation", d: "Configure trackers, calendars and dashboards using tools your team already has, or FORGE as it becomes available.", items: ["Tracker and dashboard setup", "Data import and clean-up", "Staff training and handover", "Integration planning with approved data sources"] },
  { slug: "ai-readiness", n: "06", t: "AI readiness and automation", d: "Identify where automation helps, where it does not, and how to introduce it responsibly.", items: ["Use-case selection", "Data handling and review requirements", "Pilot design", "Human-in-the-loop checkpoints"] },
];

export type Product = { slug: string; title: string; price: string; category: string; status: "Free tool" | "Available on request"; blurb: string; description: string; includes: string[]; audience: string; faqs: { q: string; a: string }[]; visual: "tracker" | "budget" | "travel" | "calendar" | "templates" | "sop" | "toolkit" };
const deliveryFaq = { q: "How is this delivered?", a: "Products are delivered as downloadable files. Online checkout is not available yet; request a product and FORGE will follow up with delivery details." };
export const products: Product[] = [
  { slug: "award-tracker", title: "Award Tracker", price: "$29", category: "Grants management", status: "Available on request", visual: "tracker", blurb: "One workbook for every award, sponsor, amount and date.", description: "A structured workbook for recording each award in a portfolio: sponsor, award number, amounts, period of performance, contacts and status.", includes: ["Portfolio overview", "Award register", "Status tracking", "Quick-start guide"], audience: "Departmental grant managers moving from scattered files to one record per award.", faqs: [{ q: "What software does it use?", a: "Excel, and it is compatible with Google Sheets and Microsoft 365." }, deliveryFaq] },
  { slug: "budget-monitor", title: "Budget Monitor", price: "$49", category: "Financial management", status: "Available on request", visual: "budget", blurb: "Budget, posted spending, commitments and available balance.", description: "A workbook that keeps award budget, posted expenditures and commitments separate, calculates the available balance and highlights variances. It is a monitoring aid and does not replace official institutional records.", includes: ["Budget vs. actual by award", "Commitment tracker", "Available balance calculation", "Variance flags", "Instructions"], audience: "Research administrators maintaining departmental budget tracking.", faqs: [{ q: "Does it replace the university financial system?", a: "No. Official institutional records remain the system of record. This workbook supports departmental monitoring and reconciliation." }, deliveryFaq] },
  { slug: "travel-budget-calculator", title: "Travel Budget Calculator", price: "Free", category: "Financial management", status: "Free tool", visual: "travel", blurb: "A free interactive tool to help estimate travel costs.", description: "A free interactive tool to help plan and estimate travel costs for sponsored projects. Use it below, no sign-up required.", includes: ["Interactive estimate", "No account needed"], audience: "Anyone budgeting travel for a proposal or award.", faqs: [{ q: "Are the results official?", a: "No. Results are planning estimates. Confirm allowable costs against the sponsor terms and your institution's travel policy." }] },
  { slug: "compliance-calendar", title: "Compliance Calendar", price: "$29", category: "Compliance & reporting", status: "Available on request", visual: "calendar", blurb: "Reporting deadlines and award conditions in one calendar.", description: "A calendar-driven tracker for reports, deliverables and recurring obligations with owners and reminder-ready dates.", includes: ["Reporting calendar", "Deliverables log", "Owner assignments", "Reminder-ready dates"], audience: "Research administrators and center managers tracking multiple deadlines.", faqs: [{ q: "Does it guarantee we meet sponsor requirements?", a: "No. It helps you organize and see obligations; you remain responsible for reviewing award terms." }, deliveryFaq] },
  { slug: "grant-management-templates", title: "Grant Management Templates", price: "$39", category: "Grants management", status: "Available on request", visual: "templates", blurb: "Editable templates for award setup, review and closeout.", description: "Checklists and templates that walk a team through award setup, periodic review and closeout.", includes: ["Award setup checklist", "Periodic review template", "Closeout checklist", "Documentation register"], audience: "Teams without a defined award lifecycle process.", faqs: [deliveryFaq] },
  { slug: "sop-library", title: "SOP Library", price: "$79", category: "Grants management", status: "Available on request", visual: "sop", blurb: "Editable standard operating procedures for research administration.", description: "A starter library of editable procedures covering the research administration lifecycle, so processes are written down and repeatable.", includes: ["Lifecycle SOP templates", "Roles and responsibilities template", "Review and approval templates"], audience: "Teams formalizing how awards are administered.", faqs: [{ q: "Can we edit the templates?", a: "Yes. They are editable so you can adapt them to institutional policy." }, deliveryFaq] },
  { slug: "research-operations-toolkit", title: "Research Operations Toolkit", price: "$199", category: "Toolkits", status: "Available on request", visual: "toolkit", blurb: "The complete starter set, bundled.", description: "Award Tracker, Budget Monitor, Compliance Calendar, templates and SOP Library together, as a complete starting point for a small team.", includes: ["Award Tracker", "Budget Monitor", "Compliance Calendar", "Grant Management Templates", "SOP Library"], audience: "Small teams that want everything in one package.", faqs: [{ q: "Which should I start with?", a: "If unsure, the toolkit covers every area. A discovery call can help you decide." }, deliveryFaq] },
];

export const aiItems = [
  { t: "Award document intelligence", d: "Read an award agreement and prepare a structured record: sponsor, award number, amount, dates, reporting requirements, special conditions and deliverables, each tied to its source page." },
  { t: "AI-assisted document extraction", d: "Pull key fields from budgets, amendments and correspondence into a reviewable draft. Uncertain items are flagged, not guessed." },
  { t: "Funding discovery and PI matching", d: "Surface funding opportunities and suggest matches to investigator interests for a person to evaluate." },
  { t: "Budget intelligence", d: "Highlight variances, unusual spending patterns and awards likely to over- or under-spend, for administrator review." },
  { t: "Compliance reminders", d: "Turn extracted dates and obligations into reminders with owners, so deadlines do not live in memory." },
  { t: "Reporting assistance", d: "Organize the information behind a report and prepare a draft that staff review and finalize." },
];
export const governance = [
  "AI-generated output is a draft and requires human review.",
  "AI does not approve expenditures or make compliance or legal determinations.",
  "Every extracted value links back to its source so it can be verified.",
  "Customer documents are handled under agreed confidentiality and data-handling requirements and are never exposed to other customers.",
  "Do not share restricted data through public forms or chat.",
];

export type Article = { slug: string; title: string; category: string; summary: string; body: { h?: string; p?: string; ul?: string[] }[] };
export const articleCategories = ["Research administration", "Federal funding developments", "Grants management", "Research finance", "AI in research administration", "Practical operational guides"];
export const articles: Article[] = [
  { slug: "what-is-a-shadow-budget", title: "What a shadow budget is, and why it eventually breaks", category: "Research finance", summary: "Departmental spreadsheets fill a real gap. Here is where they work and where they start to fail.",
    body: [{ p: "A shadow budget is the departmental spreadsheet (or set of spreadsheets) that research administrators keep alongside the institution's official financial system. It exists because the official system answers questions about what has posted, while administrators also need to know what is committed, what is coming and what is left." }, { h: "Why teams build them", p: "They are fast, flexible and under the team's control. For one or two awards, they work well." }, { h: "Where they start to break", ul: ["Each new award adds another tab and another set of formulas to maintain.", "Updates depend on one person remembering to refresh them.", "Commitments and posted expenses get mixed together, so balances are double counted or missed.", "Nobody else can easily check or take over the file.", "Differences from the official report are found late."] }, { h: "What to keep", p: "The idea is right: departments need a monitoring layer. The weakness is the manual, disconnected way it is usually maintained. A better approach keeps the official system as the record, and gives the team a structured, reconciled view alongside it." }] },
  { slug: "posted-committed-available", title: "Posted, committed, available: keeping three numbers separate", category: "Research finance", summary: "Most balance errors come from blending expenditures and commitments. A simple discipline prevents it.",
    body: [{ p: "Three figures describe an award's financial position. Keeping them separate prevents most double counting." }, { ul: ["Actual (posted) expenditures: costs that have posted to the institutional ledger.", "Outstanding commitments: costs expected but not yet posted, such as open purchase orders, payroll projections and planned travel.", "Available balance: what remains after both."] }, { h: "The calculation", p: "Available balance = award budget − actual expenditures − outstanding commitments." }, { h: "Avoiding double counting", p: "When a purchase order is invoiced and posts, remove it from commitments. If it appears in both columns, the available balance is understated. Review commitments against the latest institutional report each month." }, { h: "Projections are not balances", p: "A forecast of end-of-award position is an estimate. Label it as a projection and never present it as an actual balance." }] },
  { slug: "thirty-minute-monthly-award-review", title: "A monthly award review that takes thirty minutes", category: "Grants management", summary: "A short, repeatable routine for catching problems while they are still easy to fix.",
    body: [{ p: "A consistent monthly check catches more than an occasional deep dive. For each active award:" }, { ul: ["Compare actual expenditures with the budget and with the expected burn for this point in the award.", "Review open commitments: are any stale, duplicated or already posted?", "Check the next three months of reporting deadlines and the end date.", "Note anything that needs a conversation with the investigator.", "Reconcile totals with the institutional report and record any differences."] }, { h: "Make it routine", p: "Pick a recurring time, use the same checklist and keep a short note per award. Consistency matters more than detail." }] },
  { slug: "questions-before-using-ai-on-award-documents", title: "Questions to ask before using AI on award documents", category: "AI in research administration", summary: "Automation can save time on extraction and reminders, but only with the right safeguards.",
    body: [{ p: "AI can prepare drafts from long agreements, but a few questions should be answered first." }, { ul: ["What data classification applies to these documents, and is this tool approved for it?", "Where are documents processed and stored, and who can see them?", "Does every extracted value link to its source page so it can be verified?", "Who reviews the output, and what happens when the tool is uncertain?", "Does the tool make decisions, or does it only prepare drafts?"] }, { h: "A sensible default", p: "Use AI to prepare structured drafts and reminders. Keep approvals, financial decisions and compliance determinations with people." }] },
  { slug: "lightweight-reconciliation-routine", title: "Setting up a lightweight reconciliation routine", category: "Practical operational guides", summary: "Compare your departmental records with the institutional report on a schedule, and make differences visible.",
    body: [{ p: "Reconciliation is the habit that keeps a departmental view trustworthy." }, { h: "A simple routine", ul: ["Pull the institutional report for the period and record its date.", "Compare totals by award, then by category if totals differ.", "List missing or mismatched transactions with their source.", "Decide who corrects what: your records or a request to the central office.", "Record the result and the date of the last successful match."] }, { h: "What to watch", p: "Timing differences are normal. Differences that persist across periods are the ones to investigate." }] },
];

export const challengesForForm = ["No single view of all awards", "Budget and commitment tracking", "Deadline and reporting tracking", "Award document handling", "Preparing for a new team member or growth", "Exploring automation or AI", "Other"];
export const interestsForForm = ["FORGE platform", "Consulting and implementation", "Digital products and templates", "AI and automation", "Not sure yet"];
export const rolesForForm = ["Departmental grant manager", "Research administrator", "Research center manager", "Principal investigator", "Director of research administration", "Nonprofit grants lead", "Other"];
export const teamSizes = ["Just me", "2–3 people", "4–10 people", "11+ people"];
