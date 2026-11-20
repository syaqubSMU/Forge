"use client";
import { Suspense } from "react";
import InquiryForm from "./InquiryForm";
export function GeneralForm() { return <Suspense><InquiryForm mode="general" /></Suspense>; }
export function DiscoveryForm() { return <Suspense><InquiryForm mode="discovery" /></Suspense>; }
