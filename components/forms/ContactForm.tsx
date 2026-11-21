"use client";
import { Suspense } from "react";
import InquiryForm from "./InquiryForm";
export function GeneralForm({ prefill }: { prefill?: string }) { return <Suspense><InquiryForm mode="general" prefill={prefill} /></Suspense>; }
export function DiscoveryForm() { return <Suspense><InquiryForm mode="discovery" /></Suspense>; }
