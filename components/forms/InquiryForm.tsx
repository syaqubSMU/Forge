"use client";
import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { Alert, Button, Checkbox, Form, Input, Select } from "antd";
import { challengesForForm, interestsForForm, rolesForForm, teamSizes } from "@/lib/content";
import { track } from "@/lib/analytics";

type Mode = "discovery" | "general";

export default function InquiryForm({ mode, prefill: prefillProp }: { mode: Mode; prefill?: string }) {
  const [form] = Form.useForm();
  const [state, setState] = useState<"idle" | "sending" | "ok" | "proto" | "error">("idle");
  const params = useSearchParams();
  const discovery = mode === "discovery";
  const prefill = prefillProp ?? params.get("interest");

  const onFinish = async (values: Record<string, unknown>) => {
    setState("sending");
    try {
      const hp = (document.querySelector("input[name=website_hp]") as HTMLInputElement | null)?.value;
      if (hp) { setState("ok"); return; } // honeypot
      const endpoint = process.env.NEXT_PUBLIC_INQUIRY_ENDPOINT; // e.g. a Formspree or CRM form URL
      let delivered = false;
      if (endpoint) {
        const res = await fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json", Accept: "application/json" },
          body: JSON.stringify({ ...values, formType: mode, page: window.location.pathname, utm: Object.fromEntries(params.entries()) }) });
        if (!res.ok) throw new Error(String(res.status));
        delivered = true;
      }
      if (discovery) track("consultation_form_submitted");
      setState(delivered ? "ok" : "proto"); form.resetFields();
    } catch { setState("error"); }
  };

  if (state === "ok" || state === "proto")
    return (
      <div role="status" className="stack">
        <Alert type="success" showIcon message="Thank you. Your message has been submitted." description="Someone from FORGE will follow up using the email you provided." />
        {state === "proto" && <div className="note"><b>Preview mode:</b> form delivery is not connected yet, so this submission was not sent anywhere. Set <code>NEXT_PUBLIC_INQUIRY_ENDPOINT</code> to forward inquiries.</div>}
      </div>
    );
  return (
    <Form form={form} layout="vertical" requiredMark="optional" onFinish={onFinish} size="large"
      initialValues={{ interests: discovery && prefill ? [prefill] : undefined, message: !discovery && prefill ? `I'm interested in: ${prefill}` : undefined }}>
      {state === "error" && <Alert type="error" showIcon style={{ marginBottom: 16 }} message="We couldn't send your message." description="Please check the form and try again." />}
      <Form.Item name="name" label="Name" rules={[{ required: true, message: "Please enter your name." }]}><Input autoComplete="name" /></Form.Item>
      <Form.Item name="email" label="Work email" rules={[{ required: true, message: "Please enter your work email." }, { type: "email", message: "Enter a valid email address." }]}><Input autoComplete="email" /></Form.Item>
      {discovery && (<>
        <Form.Item name="organization" label="Institution or organization" rules={[{ required: true, message: "Please enter your institution or organization." }]}><Input autoComplete="organization" /></Form.Item>
        <Form.Item name="role" label="Your role"><Select placeholder="Select" options={rolesForForm.map((v) => ({ value: v, label: v }))} /></Form.Item>
        <Form.Item name="team" label="Size of your research administration team"><Select placeholder="Select" options={teamSizes.map((v) => ({ value: v, label: v }))} /></Form.Item>
        <Form.Item name="interests" label="What would you like to discuss?"><Select mode="multiple" placeholder="Select" options={interestsForForm.map((v) => ({ value: v, label: v }))} /></Form.Item>
        <Form.Item name="challenge" label="Main challenge"><Select placeholder="Select" options={challengesForForm.map((v) => ({ value: v, label: v }))} /></Form.Item>
      </>)}
      <Form.Item name="message" label={discovery ? "Anything else we should know?" : "How can we help?"} rules={discovery ? [] : [{ required: true, message: "Please enter a message." }]}><Input.TextArea rows={4} maxLength={2000} /></Form.Item>
      <div style={{ position: "absolute", left: -9999 }} aria-hidden><label>Leave blank<input name="website_hp" tabIndex={-1} autoComplete="off" /></label></div>
      <Form.Item name="consent" valuePropName="checked" rules={[{ validator: (_, v) => (v ? Promise.resolve() : Promise.reject(new Error("Please confirm to continue."))) }]}>
        <Checkbox>I agree that FORGE may use this information to respond to my message, only to respond to this request, and not to share it. I will not include confidential or restricted data (such as health, financial account or student record information) in this form.</Checkbox>
      </Form.Item>
      <Button type="primary" htmlType="submit" loading={state === "sending"} size="large" style={{ height: 48, paddingInline: 28 }}>{discovery ? "Request a Discovery Call" : "Request a Demo"}</Button>
    </Form>
  );
}
