"use client";
import { useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Alert, Button, Checkbox, Form, Input, Select } from "antd";
import { challenges, interests } from "@/lib/content";
import { track } from "@/lib/analytics";

type Mode = "consultation" | "general";

export default function InquiryForm({ mode }: { mode: Mode }) {
  const [form] = Form.useForm();
  const [state, setState] = useState<"idle" | "sending" | "ok" | "proto" | "error">("idle");
  const params = useSearchParams();
  const consult = mode === "consultation";
  const prefill = params.get("interest");

  const onFinish = async (values: Record<string, unknown>) => {
    setState("sending");
    try {
      const hp = (document.querySelector("input[name=website_hp]") as HTMLInputElement | null)?.value;
      const endpoint = process.env.NEXT_PUBLIC_INQUIRY_ENDPOINT; // e.g. a Formspree/CRM form URL
      let delivered = false;
      if (hp) { setState("ok"); return; } // honeypot: pretend success to bots
      if (endpoint) {
        const res = await fetch(endpoint, {
          method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({ ...values, formType: mode, sourcePage: document.referrer || window.location.pathname, utm: Object.fromEntries(params.entries()) }),
        });
        if (!res.ok) throw new Error(String(res.status));
        delivered = true;
      }
      if (consult) track("consultation_form_submitted");
      setState(delivered ? "ok" : "proto");
      form.resetFields();
    } catch { setState("error"); }
  };

  if (state === "ok" || state === "proto") {
    return (
      <div role="status">
        <Alert type="success" showIcon message="Thank you — your inquiry has been submitted."
          description="Someone from Forge will follow up using the email you provided." />
        {state === "proto" && <div className="note-box" style={{ marginTop: 12 }}><strong>Prototype mode:</strong> form delivery isn’t connected yet, so this submission was not sent anywhere. Set <code>NEXT_PUBLIC_INQUIRY_ENDPOINT</code> to forward inquiries.</div>}
      </div>
    );
  }
  return (
    <Form form={form} layout="vertical" requiredMark="optional" onFinish={onFinish} size="large"
      initialValues={{ services: consult && prefill ? [prefill] : undefined, message: !consult && prefill ? `I'm interested in: ${prefill}` : undefined }}>
      {state === "error" && <Alert type="error" showIcon style={{ marginBottom: 16 }} message="We couldn’t send your inquiry." description="Please check the form and try again." />}
      <Form.Item name="name" label="Name" rules={[{ required: true, message: "Please enter your name." }]}><Input autoComplete="name" /></Form.Item>
      <Form.Item name="email" label="Work email" rules={[{ required: true, message: "Please enter your work email." }, { type: "email", message: "Enter a valid email address." }]}><Input autoComplete="email" /></Form.Item>
      {consult && (<>
        <Form.Item name="organization" label="Organization" rules={[{ required: true, message: "Please enter your organization." }]}><Input autoComplete="organization" /></Form.Item>
        <Form.Item name="title" label="Job title"><Input autoComplete="organization-title" /></Form.Item>
        <Form.Item name="website" label="Organization website"><Input inputMode="url" /></Form.Item>
        <Form.Item name="activeGrants" label="Number of active grants"><Select placeholder="Select" options={["1–2", "3–5", "6–10", "11–25", "26+"].map((v) => ({ value: v, label: v }))} /></Form.Item>
        <Form.Item name="challenge" label="Primary operational challenge" rules={[{ required: true, message: "Please choose a challenge." }]}><Select placeholder="Select" options={challenges.map((v) => ({ value: v, label: v }))} /></Form.Item>
        <Form.Item name="services" label="Services of interest"><Select mode="multiple" placeholder="Select" options={interests.map((v) => ({ value: v, label: v }))} /></Form.Item>
      </>)}
      <Form.Item name="message" label={consult ? "Additional information" : "How can we help?"} rules={consult ? [] : [{ required: true, message: "Please enter a message." }]}><Input.TextArea rows={4} maxLength={2000} showCount /></Form.Item>
      <div style={{ position: "absolute", left: -9999 }} aria-hidden><label>Leave blank<input name="website_hp" tabIndex={-1} autoComplete="off" /></label></div>
      <Form.Item name="consent" valuePropName="checked" rules={[{ validator: (_, v) => (v ? Promise.resolve() : Promise.reject(new Error("Please confirm to continue."))) }]}>
        <Checkbox>I agree that Forge may use the information I provide to respond to this inquiry, as described in the <Link href="/privacy" target="_blank">Privacy Notice</Link>. Please do not include confidential award documents or sensitive financial information.</Checkbox>
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={state === "sending"} className="btn-shine">{consult ? "Request a Consultation" : "Send Message"}</Button>
    </Form>
  );
}
