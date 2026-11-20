import type { ThemeConfig } from "antd";

export const colors = {
  offWhite: "#F6F5F2",
  blue: "#174A82",
  blueDark: "#0F355F",
  coral: "#CF4126", // AA-contrast coral for buttons with white text
  coralBright: "#F25C3C", // decorative accents only
  tangerine: "#F4A261",
  text: "#1F2D3A",
  muted: "#51606E",
  border: "#E2E0DA",
};

export const theme: ThemeConfig = {
  token: {
    colorPrimary: colors.blue,
    colorInfo: colors.blue,
    colorLink: colors.blue,
    colorText: colors.text,
    colorBgLayout: colors.offWhite,
    borderRadius: 10,
    fontFamily: "var(--font-sans), system-ui, -apple-system, 'Segoe UI', sans-serif",
    fontSize: 16,
  },
  components: {
    Button: { fontWeight: 600, controlHeightLG: 48 },
    Card: { borderRadiusLG: 14 },
    Menu: { itemSelectedColor: colors.blue },
    Steps: { colorPrimary: colors.blue },
  },
};
