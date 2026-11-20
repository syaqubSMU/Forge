"use client";
import { useState } from "react";
import { Alert, Button, Form, Input } from "antd";
import { track } from "@/lib/analytics";
export default function ResourceGate({ slug }: { slug: string }) {
  const [done, setDone] = useState(false);
  if (done) return <Alert type="info" showIcon message="Downloads aren’t live yet." description="This resource file is still being prepared. Your interest has been noted for the launch." />;
  return (
    <Form layout="vertical" size="large" onFinish={() => { track("resource_downloaded", { resource: slug, placeholder: true }); setDone(true); }}>
      <Form.Item name="email" label="Work email" rules={[{ required: true, type: "email", message: "Enter a valid email address." }]}><Input autoComplete="email" /></Form.Item>
      <Button type="primary" htmlType="submit" style={{ background: "#CF4126" }}>Get this resource</Button>
    </Form>
  );
}
