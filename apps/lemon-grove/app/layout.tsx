import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "柠檬林 · Lemon Grove",
  description: "从 GitHub 知识库读取概念、工具与学习路线的个人知识存档站。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
