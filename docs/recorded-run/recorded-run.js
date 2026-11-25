/* RECORDED RUN. Real output of the FORGE SIGNAL pipeline for a FICTIONAL researcher against the stored public
   Grants.gov copy. Same shape as the API response and as the sample data it replaces. Every quote was
   re-checked against its source before this file was written (see recorded_run.quote_check). */
window.MOCK = {
 "profile": {
  "investigator": "Dr. Sample Researcher (fictional)",
  "institution": "Sample University (fictional)",
  "career_stage": "Established investigator. Exclude programs restricted to early-career investigators.",
  "lanes": [
   "Cancer early detection and biomarkers",
   "Tumor imaging and image-guided therapy",
   "Artificial intelligence for cancer imaging and pathology"
  ],
  "positioning_rules": [
   "Clinical trials only where a named clinical collaborator is in place",
   "Population-science programs only where an imaging or biomarker component is central"
  ]
 },
 "settings": {
  "horizon_months": 3,
  "lead_time_days": 14,
  "funder_types": [
   "federal"
  ],
  "min_fit": "Low",
  "scope_level": "A named organization",
  "max_judgments": 15
 },
 "retrieved_at": "2026-11-25T14:34:02+00:00",
 "counters": {
  "opportunities_listed": 787,
  "in_horizon": 253,
  "details_fetched": 253,
  "judged": 15,
  "model_failures": 0,
  "model_call_failures": 0,
  "not_judged_due_to_cap": 46,
  "no_term_overlap": 192,
  "source_failures": 0,
  "latency_ms": 23723,
  "judging_ms": 23444,
  "judge_concurrency": 8,
  "input_tokens": 21479,
  "output_tokens": 19799,
  "cost_usd": 0.481896
 },
 "results": [
  {
   "title": "Academic-Industrial Partnerships (AIP) to Translate and Validate In Vivo Imaging Systems (R01 Clinical Trial Optional)",
   "sponsor": "National Institutes of Health",
   "number": "PAR-25-079",
   "url": "https://www.grants.gov/search-results-detail/357018",
   "close_date": "2027-01-07",
   "source_status": "posted",
   "cost_sharing": false,
   "days_to_deadline": 43,
   "award_floor": null,
   "award_ceiling": 500000,
   "currency_flags": [],
   "related_opportunity_ids": [],
   "tier": "Direct",
   "fit": "High",
   "eligibility": "Needs verification",
   "rationale": "The NCI opportunity seeks to translate imaging and data-science technologies into tools for cancer diagnosis and treatment. This matches the investigator's established work in tumor imaging and AI for cancer imaging. The provided excerpt lists only 'other' eligible applicant types and does not state whether the investigator's institution qualifies, so eligibility needs verification.",
   "how_calculated": {
    "factors": {
     "centrality": "central",
     "repositioning": "none",
     "pi_can_lead": "yes",
     "career_stage_excluded": "no",
     "positioning_violation": "no"
    },
    "rules_fired": [
     "R5"
    ],
    "reasons": [
     "Central science, no repositioning, investigator can lead: Direct."
    ],
    "adjustments": []
   },
   "citations": [
    {
     "source_id": "https://www.grants.gov/search-results-detail/357018",
     "quote": "translation of scientific discoveries and engineering developments in imaging, data science and/or spectroscopic technologies into methods or tools that address contemporary problems in understanding the fundamental biology, potential risk of development, diagnosis, treatment, and/or disease status for cancer or other disease",
     "for": "centrality"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Tumor imaging and image-guided therapy; Artificial intelligence for cancer imaging and pathology",
     "for": "centrality"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Cancer early detection and biomarkers; Tumor imaging and image-guided therapy; Artificial intelligence for cancer imaging and pathology",
     "for": "repositioning"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Career stage: Established investigator.",
     "for": "pi_can_lead"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/357018",
     "quote": "Other Eligible Applicants include the following:",
     "for": "eligibility"
    }
   ],
   "failed_citation_count": 0,
   "prefilter_shared_terms": [
    "cancer",
    "imag"
   ]
  },
  {
   "title": "National Cancer Institute's Investigator-Initiated Early Phase Clinical Trials for Cancer Treatment and Diagnosis (R01 Clinical Trial Required)",
   "sponsor": "National Institutes of Health",
   "number": "PAR-25-081",
   "url": "https://www.grants.gov/search-results-detail/357075",
   "close_date": "2027-01-07",
   "source_status": "posted",
   "cost_sharing": false,
   "days_to_deadline": 43,
   "award_floor": null,
   "award_ceiling": 499999,
   "currency_flags": [],
   "related_opportunity_ids": [],
   "tier": "Strong",
   "fit": "Medium",
   "eligibility": "Needs verification",
   "rationale": "The opportunity names the Cancer Imaging Program and Cancer Diagnosis Program, which overlap the investigator's imaging and biomarker work, but it requires an early phase clinical trial. The profile allows clinical trials only with a named clinical collaborator, and the sources do not show one is in place, so a clinical partner is needed. The sources list only 'other' eligible applicant types, so institutional eligibility needs verification.",
   "how_calculated": {
    "factors": {
     "centrality": "partial",
     "repositioning": "partner",
     "pi_can_lead": "yes",
     "career_stage_excluded": "no",
     "positioning_violation": "no"
    },
    "rules_fired": [
     "R9"
    ],
    "reasons": [
     "Partial overlap that depends on a topic, partner or bridge: Strong."
    ],
    "adjustments": []
   },
   "citations": [
    {
     "source_id": "https://www.grants.gov/search-results-detail/357075",
     "quote": "The proposed project must involve at least 1 clinical trial related to the scientific interests of one or more of the following research programs: Cancer Therapy Evaluation Program, Cancer Imaging Program, Cancer Diagnosis Program, Radiation Research Program, Complementary and Alternative Medicine Program and/or the HIV and AIDS Malignancies Research Programs.",
     "for": "centrality"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Established research areas: Cancer early detection and biomarkers; Tumor imaging and image-guided therapy; Artificial intelligence for cancer imaging and pathology.",
     "for": "centrality"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Positioning rule: Clinical trials only where a named clinical collaborator is in place",
     "for": "repositioning"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/357075",
     "quote": "seeks research projects that implement early phase (Phase 0, I, and II) investigator-initiated clinical trials focused on cancer-targeted diagnostic and therapeutic interventions",
     "for": "repositioning"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/357075",
     "quote": "investigator-initiated clinical trials",
     "for": "pi_can_lead"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Career stage: Established investigator.",
     "for": "career_stage_excluded"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Positioning rule: Clinical trials only where a named clinical collaborator is in place",
     "for": "positioning_violation"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/357075",
     "quote": "Other Eligible Applicants include the following:",
     "for": "eligibility"
    }
   ],
   "failed_citation_count": 0,
   "prefilter_shared_terms": [
    "cancer",
    "earli",
    "imag",
    "therapi"
   ]
  },
  {
   "title": "Cancer Prevention and Control Clinical Trials Grant Program (R01 Clinical Trial Required)",
   "sponsor": "National Institutes of Health",
   "number": "PAR-25-167",
   "url": "https://www.grants.gov/search-results-detail/357074",
   "close_date": "2027-01-07",
   "source_status": "posted",
   "cost_sharing": false,
   "days_to_deadline": 43,
   "award_floor": null,
   "award_ceiling": null,
   "currency_flags": [],
   "related_opportunity_ids": [],
   "tier": "Strong",
   "fit": "Medium",
   "eligibility": "Needs verification",
   "rationale": "The NOFO funds clinical trials in cancer early detection and screening. This overlaps the investigator's early-detection and biomarker work, but trials of cancer diagnosis or oncologic therapy in patients are excluded, and the profile allows clinical trials only with a named clinical collaborator in place, which the sources do not show. The sources list only 'Other Eligible Applicants' and do not confirm the university's applicant eligibility, so eligibility needs verification.",
   "how_calculated": {
    "factors": {
     "centrality": "partial",
     "repositioning": "partner",
     "pi_can_lead": "yes",
     "career_stage_excluded": "no",
     "positioning_violation": "no"
    },
    "rules_fired": [
     "R9"
    ],
    "reasons": [
     "Partial overlap that depends on a topic, partner or bridge: Strong."
    ],
    "adjustments": []
   },
   "citations": [
    {
     "source_id": "https://www.grants.gov/search-results-detail/357074",
     "quote": "improvements in early detection, screening, prevention and interception, healthcare delivery, quality of life, and/or survivorship related to cancer",
     "for": "centrality"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Established research areas: Cancer early detection and biomarkers; Tumor imaging and image-guided therapy; Artificial intelligence for cancer imaging and pathology.",
     "for": "centrality"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/357074",
     "quote": "This NOFO does not and will not support clinical trials for studies of cancer diagnosis and/or oncologic therapy in patients.",
     "for": "centrality"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Positioning rule: Clinical trials only where a named clinical collaborator is in place",
     "for": "repositioning"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/357074",
     "quote": "Applications submitted to this NOFO must include studies that meet the National Institutes of Health (NIH) definition of a clinical trial",
     "for": "repositioning"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Career stage: Established investigator.",
     "for": "pi_can_lead"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/357074",
     "quote": "invites applications for support of investigator-initiated clinical trials",
     "for": "pi_can_lead"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Positioning rule: Population-science programs only where an imaging or biomarker component is central",
     "for": "positioning_violation"
    }
   ],
   "failed_citation_count": 0,
   "prefilter_shared_terms": [
    "cancer",
    "detection",
    "earli",
    "therapi"
   ]
  },
  {
   "title": "Cancer Advancement through Partnerships in Research and Infrastructure (CAPRI) (U54 Clinical Trial Optional)",
   "sponsor": "National Institutes of Health",
   "number": "PAR-28-062",
   "url": "https://www.grants.gov/search-results-detail/360393",
   "close_date": "2027-01-25",
   "source_status": "posted",
   "cost_sharing": false,
   "days_to_deadline": 61,
   "award_floor": null,
   "award_ceiling": null,
   "currency_flags": [],
   "related_opportunity_ids": [],
   "tier": "Strong",
   "fit": "Medium",
   "eligibility": "Needs verification",
   "rationale": "CAPRI funds cancer research through institutional partnerships between Resource Limited Institutions and NCI-designated Cancer Centers, so the investigator's cancer imaging and biomarker science fits only as part of such a partnership. This is a limited competition, and the sources do not show whether the investigator's institution qualifies, so eligibility must be verified.",
   "how_calculated": {
    "factors": {
     "centrality": "partial",
     "repositioning": "partner",
     "pi_can_lead": "yes",
     "career_stage_excluded": "no",
     "positioning_violation": "no"
    },
    "rules_fired": [
     "R9"
    ],
    "reasons": [
     "Partial overlap that depends on a topic, partner or bridge: Strong."
    ],
    "adjustments": []
   },
   "citations": [
    {
     "source_id": "https://www.grants.gov/search-results-detail/360393",
     "quote": "The CAPRI Program establishes and strengthens comprehensive, mutually beneficial and meaningful partnerships between Resource Limited Institutions (RLIs) and NCI-designated Cancer Centers (CCs) to accelerate collaborative and innovative cancer.",
     "for": "centrality"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Established research areas: Cancer early detection and biomarkers; Tumor imaging and image-guided therapy; Artificial intelligence for cancer imaging and pathology.",
     "for": "centrality"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/360393",
     "quote": "partnerships between Resource Limited Institutions (RLIs) and NCI-designated Cancer Centers (CCs)",
     "for": "repositioning"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Career stage: Established investigator.",
     "for": "pi_can_lead"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Career stage: Established investigator. Exclude programs restricted to early-career investigators..",
     "for": "career_stage_excluded"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/360393",
     "quote": "cultivating the next generation of Early-Stage Investigators and trainees",
     "for": "career_stage_excluded"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/360393",
     "quote": "This is a Notice of Funding Opportunity (NOFO) for a Limited Competition that invites applications from eligible organizations to apply.",
     "for": "eligibility"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/360393",
     "quote": "Refer to Section III. Eligibility Information in the NOFO for additional information on eligibility.",
     "for": "eligibility"
    }
   ],
   "failed_citation_count": 0,
   "prefilter_shared_terms": [
    "cancer",
    "earli"
   ]
  },
  {
   "title": "NLM Institutional Grants for Research Training in Biomedical Informatics, Data Science, and AI (T15 Independent Clinical Trial Not Allowed)",
   "sponsor": "National Institutes of Health",
   "number": "RFA-LM-28-001",
   "url": "https://www.grants.gov/search-results-detail/361318",
   "close_date": "2027-02-11",
   "source_status": "posted",
   "cost_sharing": false,
   "days_to_deadline": 78,
   "award_floor": 500000,
   "award_ceiling": 775000,
   "currency_flags": [],
   "related_opportunity_ids": [],
   "tier": "Strong",
   "fit": "Medium",
   "eligibility": "Needs verification",
   "rationale": "The investigator's AI work in cancer imaging and pathology overlaps the AI/ML and biomedical informatics part of this NLM training-program scope. Competing would mean framing that expertise as an interdisciplinary predoctoral and postdoctoral training program. Eligibility needs verification because the sources only exclude foreign institutions and do not confirm the researcher's institution qualifies.",
   "how_calculated": {
    "factors": {
     "centrality": "partial",
     "repositioning": "framing",
     "pi_can_lead": "yes",
     "career_stage_excluded": "no",
     "positioning_violation": "no"
    },
    "rules_fired": [
     "R9"
    ],
    "reasons": [
     "Partial overlap that depends on a topic, partner or bridge: Strong."
    ],
    "adjustments": []
   },
   "citations": [
    {
     "source_id": "https://www.grants.gov/search-results-detail/361318",
     "quote": "prepare the next generation of researchers in biomedical informatics, data science, and artificial intelligence/machine learning (AI/ML)",
     "for": "centrality"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Artificial intelligence for cancer imaging and pathology.",
     "for": "centrality"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/361318",
     "quote": "The National Library of Medicine (NLM) invites applications for innovative predoctoral and postdoctoral training programs",
     "for": "repositioning"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/361318",
     "quote": "NLM seeks programs that integrate methods and perspectives across disciplines to advance biomedical informatics, data science, and AI/ML.",
     "for": "repositioning"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Career stage: Established investigator.",
     "for": "pi_can_lead"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/361318",
     "quote": "Applications may propose the creation of new training programs or the renewal of existing NLM-supported programs.",
     "for": "career_stage_excluded"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/361318",
     "quote": "Non-domestic (non-U.S.) Entities (Foreign Institutions) are not eligible to apply.",
     "for": "eligibility"
    }
   ],
   "failed_citation_count": 0,
   "prefilter_shared_terms": [
    "artifici",
    "intelligence"
   ]
  },
  {
   "title": "Discovery of the Genetic Basis of Childhood Cancers and of Congenital Anomalies: Gabriella Miller Kids First Pediatric Research Program (X01 Clinical Trial Not Allowed)",
   "sponsor": "National Institutes of Health",
   "number": "PAR-27-071",
   "url": "https://www.grants.gov/search-results-detail/361164",
   "close_date": "2027-01-11",
   "source_status": "posted",
   "cost_sharing": false,
   "days_to_deadline": 47,
   "award_floor": null,
   "award_ceiling": null,
   "currency_flags": [],
   "related_opportunity_ids": [],
   "tier": "Conditional",
   "fit": "Low",
   "eligibility": "Needs verification",
   "rationale": "The program funds genomic sequencing of existing pediatric cancer and congenital anomaly cohorts, while the investigator's established work is in cancer early detection, biomarkers, tumor imaging, and AI for imaging and pathology. The fit is adjacent and would need a partner who brings a pediatric cohort and a genomics component. The sources give only foreign-entity exclusions, so eligibility needs verification against Section III of the NOFO.",
   "how_calculated": {
    "factors": {
     "centrality": "adjacent",
     "repositioning": "partner",
     "pi_can_lead": "yes",
     "career_stage_excluded": "no",
     "positioning_violation": "no"
    },
    "rules_fired": [
     "R4"
    ],
    "reasons": [
     "Scientifically adjacent: Conditional, only with a clear topic or partner bridge."
    ],
    "adjustments": []
   },
   "citations": [
    {
     "source_id": "https://www.grants.gov/search-results-detail/361164",
     "quote": "Applicants are encouraged to propose sequencing of existing pediatric cancer or congenital anomaly cohorts to elucidate the genetic contribution (somatic and/or germline) to childhood cancers",
     "for": "centrality"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Established research areas: Cancer early detection and biomarkers; Tumor imaging and image-guided therapy; Artificial intelligence for cancer imaging and pathology.",
     "for": "centrality"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/361164",
     "quote": "the NIH invites applications to submit samples from pediatric cohorts for whole genome sequencing at a Kids First Program supported genomic data generating centers",
     "for": "repositioning"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Career stage: Established investigator.",
     "for": "pi_can_lead"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Career stage: Established investigator. Exclude programs restricted to early-career investigators..",
     "for": "career_stage_excluded"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/361164",
     "quote": "Refer to Section III. Eligibility Information in the NOFO for additional information on eligibility.",
     "for": "eligibility"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/361164",
     "quote": "Non-domestic (non-U.S.) Entities (Foreign Organizations) are not eligible to apply.",
     "for": "eligibility"
    }
   ],
   "failed_citation_count": 0,
   "prefilter_shared_terms": [
    "cancer",
    "tumor"
   ]
  },
  {
   "title": "Systems Biology of Infection and Inflammation in Chronic Diseases (U19 Clinical Trial Not Allowed)",
   "sponsor": "National Institutes of Health",
   "number": "RFA-AI-28-014",
   "url": "https://www.grants.gov/search-results-detail/362952",
   "close_date": "2027-02-18",
   "source_status": "posted",
   "cost_sharing": false,
   "days_to_deadline": 85,
   "award_floor": null,
   "award_ceiling": 2500000,
   "currency_flags": [],
   "related_opportunity_ids": [],
   "tier": "Conditional",
   "fit": "Low",
   "eligibility": "Needs verification",
   "rationale": "The opportunity's emphasis on AI and computational modeling fits the investigator's AI expertise. However, the core scope is how infectious pathogens and inflammation drive chronic disease, which sits next to the investigator's cancer imaging and biomarker work, so a partner with infection or inflammation expertise would be needed to bridge the topic. The excerpt lists only 'other' eligible applicant types and does not mention universities, so institutional eligibility needs to be checked in the full notice.",
   "how_calculated": {
    "factors": {
     "centrality": "adjacent",
     "repositioning": "partner",
     "pi_can_lead": "yes",
     "career_stage_excluded": "no",
     "positioning_violation": "no"
    },
    "rules_fired": [
     "R4"
    ],
    "reasons": [
     "Scientifically adjacent: Conditional, only with a clear topic or partner bridge."
    ],
    "adjustments": []
   },
   "citations": [
    {
     "source_id": "https://www.grants.gov/search-results-detail/362952",
     "quote": "The purpose of this notice of funding opportunity (NOFO) is to support the advancement of systems-level understanding of the link between infectious pathogens and inflammatory pathways that result in predisposition, onset and progression of chronic diseases.",
     "for": "centrality"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Established research areas: Cancer early detection and biomarkers; Tumor imaging and image-guided therapy; Artificial intelligence for cancer imaging and pathology.",
     "for": "centrality"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/362952",
     "quote": "The NOFO will stimulate integration of clinical and patient data, large-scale omics datasets, advanced Artificial Intelligence (AI) and computational modeling to prevent, treat, and mitigate the combined impact of chronic diseases, inflammation, and infections.",
     "for": "repositioning"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Career stage: Established investigator.",
     "for": "pi_can_lead"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/362952",
     "quote": "advanced Artificial Intelligence (AI) and computational modeling",
     "for": "pi_can_lead"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Career stage: Established investigator. Exclude programs restricted to early-career investigators..",
     "for": "career_stage_excluded"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Positioning rule: Clinical trials only where a named clinical collaborator is in place",
     "for": "positioning_violation"
    },
    {
     "source_id": "researcher-profile",
     "quote": "Positioning rule: Population-science programs only where an imaging or biomarker component is central",
     "for": "positioning_violation"
    },
    {
     "source_id": "https://www.grants.gov/search-results-detail/362952",
     "quote": "Other Eligible ApplicantsIndian/Native American Tribal Governments (Other than Federally Recognized);Eligible Agencies of the Federal Government;U.S. Territory or Possession;Faith-based or Community-based Organizations;Regional Organizations;Non-domestic (non-U.S.) Entities (Foreign Institutions).",
     "for": "eligibility"
    }
   ],
   "failed_citation_count": 0,
   "prefilter_shared_terms": [
    "artifici",
    "intelligence"
   ]
  }
 ],
 "excluded": [
  {
   "title": "Limited Competition: Biospecimen Banks to support NCI National Clinical Trials Network Biospecimen Banks (NCTN Biobanks) and the NCI Early-Phase and Experimental Clinical Trials Biospecimen Bank (EET Biobank) (U24 Clinical Trial Not Allowed)",
   "number": "RFA-CA-28-004",
   "url": "https://www.grants.gov/search-results-detail/361134",
   "reasons": [
    "Science would have to be stretched to fit: excluded (keyword overlap only)."
   ]
  },
  {
   "title": "Cooperative Agreement for affiliated Partner with the Great Lakes Northern Forrest Cooperative Ecosystem Studies Unit",
   "number": "G27AS00040",
   "url": "https://www.grants.gov/search-results-detail/364192",
   "reasons": [
    "Established science is not in the program scope: excluded."
   ]
  },
  {
   "title": "Science of Learning and Augmented Intelligence (SL)",
   "number": "PD-19-127Y",
   "url": "https://www.grants.gov/search-results-detail/320753",
   "reasons": [
    "Science would have to be stretched to fit: excluded (keyword overlap only)."
   ]
  },
  {
   "title": "Carcinogen Hazard Assessment Monographs Program (CHAMP) (R01 Clinical Trial Not Allowed)",
   "number": "RFA-CA-28-013",
   "url": "https://www.grants.gov/search-results-detail/360905",
   "reasons": [
    "Science would have to be stretched to fit: excluded (keyword overlap only)."
   ]
  },
  {
   "title": "Cybersecurity Innovation for Cyberinfrastructure (CICI)",
   "number": "25-531",
   "url": "https://www.grants.gov/search-results-detail/358004",
   "reasons": [
    "Science would have to be stretched to fit: excluded (keyword overlap only)."
   ]
  },
  {
   "title": "Cooperative Agreement for affiliated Partner with Chesapeake Watershed Cooperative Ecosystem Studies Unit",
   "number": "G27AS00047",
   "url": "https://www.grants.gov/search-results-detail/364229",
   "reasons": [
    "Established science is not in the program scope: excluded."
   ]
  },
  {
   "title": "Cooperative Agreement for affiliated Partner with Great Rivers Cooperative Ecosystem Studies Unit",
   "number": "G27AS00059",
   "url": "https://www.grants.gov/search-results-detail/364233",
   "reasons": [
    "Established science is not in the program scope: excluded."
   ]
  },
  {
   "title": "BRAIN Initiative: Exploratory Research Opportunities Using Invasive Neural Recording and Stimulating Technologies in the Human Brain (R61 Clinical Trial Not Allowed)",
   "number": "RFA-DC-27-004",
   "url": "https://www.grants.gov/search-results-detail/359649",
   "reasons": [
    "Established science is not in the program scope: excluded."
   ]
  }
 ],
 "source_failures": [],
 "recorded_run": {
  "label": "Recorded run: real model output on a fictional researcher, from the stored public Grants.gov copy.",
  "run_id": "6790215da1be4254867d055862a987a4",
  "recorded_at": "2026-11-25T16:20:42+00:00",
  "as_of_date": "2026-11-25",
  "deadline_flags_as_of": "2026-11-25",
  "code_commit": "1a1bd5cf3b8f64640ff5fc6c615f2d465dd6fbfa",
  "run_detail": {
   "sha256": "707eb752981e2f683a019106941a6b89604d849747110ab38839abaf61d12237",
   "note": "sha256 of the run's full logged detail (sources hashes, matches, citations, failures), exported next to this file"
  },
  "model": "claude-opus-5-5",
  "effort": null,
  "rubric_version": "3288f1c309d6",
  "researcher_is_fictional": true,
  "source": {
   "system": "Grants.gov",
   "api": "https://api.grants.gov/v1/api (public)",
   "mode": "stored copy",
   "retrieved_at": "2026-11-25T14:34:02+00:00",
   "records": 1376
  },
  "quote_check": {
   "quotes_checked": 52,
   "quotes_supported": 52,
   "quotes_failed": 0
  },
  "cost_note": "estimate from reported token usage",
  "redactions": [],
  "input_sent": {
   "profile": {
    "career_stage": "Established investigator. Exclude programs restricted to early-career investigators.",
    "lanes": [
     "Cancer early detection and biomarkers",
     "Tumor imaging and image-guided therapy",
     "Artificial intelligence for cancer imaging and pathology"
    ],
    "positioning_rules": [
     "Clinical trials only where a named clinical collaborator is in place",
     "Population-science programs only where an imaging or biomarker component is central"
    ]
   },
   "question": "Does this opportunity fit this researcher?",
   "evidence_text_of_profile": "Career stage: Established investigator. Exclude programs restricted to early-career investigators..\nEstablished research areas: Cancer early detection and biomarkers; Tumor imaging and image-guided therapy; Artificial intelligence for cancer imaging and pathology.\nPositioning rule: Clinical trials only where a named clinical collaborator is in place\nPositioning rule: Population-science programs only where an imaging or biomarker component is central",
   "max_judgments": 15
  },
  "deadline_note": "days_to_deadline and any 'closing soon' style flag are as of 2026-11-25, the day this was recorded. Recompute from close_date, and say so, before showing it on a later day; a deadline that has passed since must be shown as passed.",
  "integrity": {
   "results_sha256": "7bb030a59c948127332032fc7c635e9c9d2fdde488ed8aec0dc2fae0a92b6005",
   "note": "Hash of the results exactly as produced by the pipeline. It only detects accidental edits: anyone can recompute it after changing the results. The commit that adds this file must carry the run-detail sha256 and the code commit id in its message."
  }
 }
};
