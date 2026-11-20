import type { ThemeConfig } from "antd";
import { tokens as t } from "./tokens";

export const theme: ThemeConfig = {
  token: {
    colorPrimary: t.color.blue, colorInfo: t.color.blue, colorLink: t.color.blue,
    colorText: t.color.slate, colorBgLayout: t.color.warm,
    borderRadius: t.radius.md, fontSize: 16,
    fontFamily: "var(--font-sans), system-ui, -apple-system, 'Segoe UI', sans-serif",
  },
  components: {
    Button: { fontWeight: 600, controlHeightLG: 48, borderRadiusLG: t.radius.md },
    Collapse: { headerBg: "#fff" },
  },
};
