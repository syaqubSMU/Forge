/**
 * Single source of truth for editable site content (services, products, FAQs, resources, video, contact).
 * All prices are INDICATIVE and can be edited here (or later moved to a CMS) without touching layout code.
 */

export const site = {
  name: "Forge",
  short: "Forge",
  tagline: "Better Systems. Stronger Grant Operations.",
  // Set once a business mailbox exists. Do not publish personal phone/address.
  contactEmail: "" as string,
  responseTime: "" as string, // e.g. "We respond within two business days." once operationally defined
  video: {
    url: process.env.NEXT_PUBLIC_INTRO_VIDEO_URL ?? "",
    captionsUrl: process.env.NEXT_PUBLIC_INTRO_VIDEO_CAPTIONS_URL ?? "",
    headline: "The Problem Isn't Winning Grants. It's Managing Them Well.",
    description:
      "Grant-funded organizations need more than funding. They need the systems and processes to manage that funding effectively. Discover how Forge helps turn fragmented grant administration into structured, visible, and manageable operations.",
  },
  // Forge assistant (floating chat). Leave empty until a Forge-trained Chatling bot exists.
  chatbotId: process.env.NEXT_PUBLIC_CHATLING_CHATBOT_ID ?? "",
  // Free "Travel Calculator" tool: a separate Chatling bot embedded inline on its resource page.
  travelCalculatorBotId: "6621135586",
  // Optional real photos for the hero collage (licensed images placed in /public/images, e.g. "/images/scientists.jpg").
  // Leave empty to show the illustrations.
  heroPhotos: { scientists: "", economists: "" },
  chatWelcome:
    "Welcome to Forge. I can help you understand our services, explore grant-management resources, and find the right solution for your organization. What would you like help with?",
};

export const nav = [
  { label: "Home", href: "/" },
  { label: "Solutions", href: "/solutions" },
  { label: "Products", href: "/products" },
  { label: "AI & Automation", href: "/ai-automation" },
  { label: "Resources", href: "/resources" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

export const problems = [
  { title: "Fragmented grant information", text: "Award details live in inboxes, folders and one-off spreadsheets." },
  { title: "Limited financial visibility", text: "Hard to see balances, burn rates and commitments across awards." },
  { title: "Missed deadlines and obligations", text: "Reporting dates and award conditions are tracked from memory." },
  { title: "Manual reporting workloads", text: "Staff re-key the same data for every funder report." },
];

export type Pillar = { slug: string; title: string; summary: string; includes: string[]; href: string };
export const pillars: Pillar[] = [
  {
    slug: "infrastructure",
    title: "Grant Operations Infrastructure",
    summary: "Build a structured grant-management environment.",
    includes: ["Grant master trackers", "Award registers", "Compliance calendars", "Grant lifecycle workflows", "Standard operating procedures"],
    href: "/solutions",
  },
  {
    slug: "financial",
    title: "Financial Management",
    summary: "Improve visibility into grant-funded financial activity.",
    includes: ["Budget monitoring", "Budget versus actual reporting", "Burn-rate analysis", "Commitments and encumbrances", "Financial exception monitoring"],
    href: "/solutions",
  },
  {
    slug: "compliance",
    title: "Compliance & Reporting",
    summary: "Create better visibility into grant obligations.",
    includes: ["Reporting calendars", "Award-condition tracking", "Deliverable monitoring", "Documentation registers", "Closeout workflows"],
    href: "/solutions",
  },
  {
    slug: "ai",
    title: "AI & Workflow Automation",
    summary: "Reduce repetitive administrative work through intelligent workflows.",
    includes: ["Award document extraction", "Reporting assistance", "Compliance tracking", "Automated reminders", "Document classification and data extraction"],
    href: "/ai-automation",
  },
];

export const steps = [
  { title: "Assess", text: "Understand the organization's existing grant operations." },
  { title: "Design", text: "Develop the appropriate systems and workflows." },
  { title: "Implement", text: "Configure trackers, dashboards, and processes." },
  { title: "Automate", text: "Introduce AI and workflow automation where appropriate." },
  { title: "Support", text: "Provide ongoing monitoring, training, and improvements." },
];

export const whyGos = [
  { title: "Practical grant operations experience", text: "Systems built around how grants are actually administered day to day." },
  { title: "Designed around nonprofit capacity", text: "Right-sized for small teams, with tools you already use such as Excel and Microsoft 365." },
  { title: "Financial and compliance visibility", text: "A clear view of balances, deadlines and obligations across your portfolio." },
  { title: "Responsible AI-enabled efficiency", text: "Automation supports staff; people stay accountable for financial and compliance decisions." },
];

export type Service = {
  slug: string; title: string; price: string; purpose: string; deliverables: string[]; cta: string; audience: string;
};
export const services: Service[] = [
  {
    slug: "grant-operations-diagnostic", title: "Grant Operations Diagnostic", price: "$495",
    purpose: "Assess an organization's existing grant-management practices.",
    audience: "Organizations that want an honest baseline before investing in new systems.",
    deliverables: ["Current-state assessment", "Process and systems review", "Gap analysis", "Operational risk register", "Prioritized recommendations", "30–90 day improvement roadmap"],
    cta: "Request a Diagnostic",
  },
  {
    slug: "grant-operations-starter", title: "Grant Operations Starter", price: "$995",
    purpose: "Establish a basic grant-management infrastructure.",
    audience: "Teams with no central tracker or a patchwork of spreadsheets.",
    deliverables: ["Grant register", "Award tracker", "Compliance calendar", "Basic budget monitoring", "Document register", "User guidance"],
    cta: "Get Started",
  },
  {
    slug: "grant-operations-professional", title: "Grant Operations Professional", price: "$1,995",
    purpose: "Implement a more comprehensive grant operations environment.",
    audience: "Growing organizations managing multiple concurrent awards.",
    deliverables: ["Advanced grant and award tracking", "Financial monitoring framework", "Management dashboard", "Compliance and reporting workflows", "SOP library", "Training and handover"],
    cta: "Discuss Implementation",
  },
  {
    slug: "institutional-solutions", title: "Institutional Solutions", price: "$3,500+",
    purpose: "Customized systems for larger or more complex organizations.",
    audience: "Larger or multi-program organizations with complex workflows.",
    deliverables: ["Workflow assessment", "Systems architecture", "Customized dashboards", "Microsoft 365 implementation", "Automation design", "Staff training"],
    cta: "Request a Consultation",
  },
];

export type Product = {
  slug: string; title: string; price: string; category: string; blurb: string; description: string;
  includes: string[]; audience: string; faqs: { q: string; a: string }[];
};
const deliveryFaq = {
  q: "How is the product delivered?",
  a: "Digital products are delivered as downloadable files after purchase. Secure delivery and purchase confirmation arrive with checkout in a later release; until then, please contact Forge to request a product.",
};
export const productCategories = [
  "Grant Management", "Financial Management", "Compliance and Reporting", "Closeout and Documentation", "AI and Automation", "Training and Education",
];
export const products: Product[] = [
  {
    slug: "grant-master-tracker", title: "Grant Master Tracker", price: "$29", category: "Grant Management",
    blurb: "One place for every award, funder, amount and date.",
    description: "A structured workbook for recording every grant in your portfolio — funder, award number, amounts, period of performance, contacts and status — so nothing lives only in someone's inbox.",
    includes: ["Portfolio overview sheet", "Award register", "Status and stage tracking", "Quick-start guide"],
    audience: "Small teams moving from scattered files to one source of truth.",
    faqs: [{ q: "What software does it use?", a: "It is designed for Excel and compatible with Google Sheets and Microsoft 365." }, deliveryFaq],
  },
  {
    slug: "budget-monitoring-workbook", title: "Budget Monitoring Workbook", price: "$49", category: "Financial Management",
    blurb: "Budget versus actual, balances and burn rate by grant.",
    description: "Track approved budgets against expenditures, see remaining balances and monitor burn rate so you spot overspending or underspending early.",
    includes: ["Budget vs. actual by grant", "Burn-rate view", "Commitments tracker", "Variance flags", "Instructions"],
    audience: "Finance directors and operations managers monitoring several awards.",
    faqs: [{ q: "Does it replace our accounting system?", a: "No. It is a monitoring aid. Your accounting records remain the system of record." }, deliveryFaq],
  },
  {
    slug: "compliance-calendar", title: "Compliance Calendar", price: "$29", category: "Compliance and Reporting",
    blurb: "Reporting deadlines and award conditions in one calendar.",
    description: "A calendar-driven tracker for reports, deliverables and recurring obligations with owners and reminders.",
    includes: ["Reporting calendar", "Deliverables log", "Owner assignments", "Reminder-ready date columns"],
    audience: "Program directors and grant administrators.",
    faqs: [{ q: "Does it guarantee we meet funder requirements?", a: "No. It helps you organize and see obligations; you remain responsible for reviewing award terms." }, deliveryFaq],
  },
  {
    slug: "grant-closeout-toolkit", title: "Grant Closeout Toolkit", price: "$39", category: "Closeout and Documentation",
    blurb: "A structured checklist for closing out awards cleanly.",
    description: "Checklists and templates that walk your team through final reporting, reconciliation and record retention at the end of an award.",
    includes: ["Closeout checklist", "Final reconciliation worksheet", "Documentation register", "Record-retention notes"],
    audience: "Teams closing out awards without a defined process.",
    faqs: [deliveryFaq],
  },
  {
    slug: "sop-library", title: "SOP Library", price: "$79", category: "Grant Management",
    blurb: "Editable standard operating procedures for grant administration.",
    description: "A starter library of editable SOP templates covering the grant lifecycle so processes are written down and repeatable.",
    includes: ["Lifecycle SOP templates", "Roles and responsibilities template", "Review and approval workflow templates"],
    audience: "Organizations formalizing how grants are administered.",
    faqs: [{ q: "Can we edit the templates?", a: "Yes. They are editable so you can adapt them to your organization." }, deliveryFaq],
  },
  {
    slug: "complete-grant-operations-toolkit", title: "Complete Grant Operations Toolkit", price: "$199", category: "Grant Management",
    blurb: "The full starter system, bundled.",
    description: "Everything you need to start building a grant operations system: trackers, budget monitoring, compliance calendar, closeout checklist and SOP templates.",
    includes: ["Grant Master Tracker", "Award Register", "Budget Monitoring Workbook", "Compliance Calendar", "Closeout Checklist", "SOP Templates"],
    audience: "Organizations that want a complete, ready-to-use starting point.",
    faqs: [{ q: "Which product should I start with?", a: "If you are unsure, the complete toolkit covers every area. Ask the Forge assistant or book a consultation for a recommendation." }, deliveryFaq],
  },
  {
    slug: "ai-for-grant-administrators-mini-course", title: "AI for Grant Administrators Mini-Course", price: "$99", category: "Training and Education",
    blurb: "Use AI practically and responsibly in grant administration.",
    description: "A short course on where AI can help with grant administration, where it should not, and how to keep human review in the loop.",
    includes: ["Short lessons", "Practical examples", "Responsible-use checklist"],
    audience: "Grant administrators curious about practical AI use.",
    faqs: [{ q: "Does the course teach me to avoid review?", a: "No. It emphasizes human review for financial, contractual and compliance decisions." }, deliveryFaq],
  },
];

export type Automation = { slug: string; title: string; summary: string; detail: string };
export const automations: Automation[] = [
  { slug: "award-intelligence", title: "Award Intelligence Assistant", summary: "Extract key terms from award documents into structured records.", detail: "Award agreements contain information administrators must manually transfer into tracking systems. Upload an award document and extract structured fields, with source-page references and uncertain items flagged for human review." },
  { slug: "reporting-assistant", title: "Reporting Assistant", summary: "Organize reporting information and prepare draft reports.", detail: "Helps gather the information needed for funder reports and prepare drafts that staff review and finalize." },
  { slug: "compliance-assistant", title: "Compliance Assistant", summary: "Identify and track award conditions and reporting obligations.", detail: "Surfaces conditions and obligations from award documents into a trackable list for staff to confirm." },
  { slug: "workflow-automation", title: "Grant Workflow Automation", summary: "Automate reminders, document routing and recurring tasks.", detail: "Automates reminders, document routing, task assignments and recurring workflows so routine work happens on time." },
];
export const budgetMonitor = { title: "Budget Exception Monitor", summary: "Highlights budget variances and unusual spending patterns for staff review." };
export const awardFields = ["Award number", "Funder", "Award amount", "Project start and end dates", "Reporting deadlines", "Special conditions", "Spending restrictions", "Deliverables", "Contact information"];
export const governance = [
  "AI-generated information requires appropriate human review.",
  "AI does not independently approve expenditures.",
  "AI does not make legal or compliance determinations.",
  "Customer information is handled according to agreed security and confidentiality requirements.",
  "Customer documents are not exposed to other customers.",
];

export type Resource = { slug: string; title: string; category: string; summary: string };
export const resourceCategories = ["Grant Operations", "Grant Financial Management", "Compliance and Reporting", "Nonprofit Administration", "AI in Grant Management"];
export const resources: Resource[] = [
  { slug: "travel-calculator", title: "Travel Calculator", category: "Grant Financial Management", summary: "A free interactive tool to help estimate travel costs." },
  { slug: "nonprofit-grant-management-checklist", title: "The Nonprofit Grant Management Checklist", category: "Grant Operations", summary: "A quick self-check of the core practices in managing grants." },
  { slug: "grant-compliance-calendar-template", title: "Grant Compliance Calendar Template", category: "Compliance and Reporting", summary: "A simple template for tracking reporting dates and obligations." },
  { slug: "budget-monitoring-workbook-sample", title: "Budget Monitoring Workbook", category: "Grant Financial Management", summary: "Monitor budgets against actuals across awards." },
  { slug: "grant-closeout-checklist", title: "Grant Closeout Checklist", category: "Nonprofit Administration", summary: "Steps to close out a grant cleanly." },
  { slug: "guide-to-building-a-grant-operations-system", title: "Guide to Building a Grant Operations System", category: "Grant Operations", summary: "How to move from scattered spreadsheets to a managed system." },
];

export const challenges = [
  "No central grant tracker", "Limited budget visibility", "Difficulty tracking deadlines", "Manual award-document processing", "Preparing for reporting or closeout", "Other",
];
export const interests = ["Grant Operations Diagnostic", "Grant Operations Starter", "Grant Operations Professional", "Institutional Solutions", "Digital products", "AI & Automation", "Not sure yet"];
