import { access, readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

const projectFile = (path: string) => resolve(process.cwd(), path);

describe("Lemon Grove style contract", () => {
  it("uses the finished Chinese metadata", async () => {
    const layout = await readFile(projectFile("app/layout.tsx"), "utf8");

    expect(layout).toMatch(/title:\s*["']柠檬林 · Lemon Grove["']/);
    expect(layout).toMatch(
      /description:\s*["']从 GitHub 知识库读取概念、工具与学习路线的个人知识存档站。["']/,
    );
    expect(layout).toMatch(/<html\s+lang=["']zh-CN["']>/);
  });

  it("defines the exact palette and console foundations", async () => {
    const css = await readFile(projectFile("app/globals.css"), "utf8");
    const palette = {
      paper: "#f3ebdd",
      panel: "#fff9ed",
      ink: "#17130f",
      red: "#c7352a",
      muted: "#756b60",
      line: "#d8c7a9",
    } as const;

    for (const [token, value] of Object.entries(palette)) {
      expect(css).toMatch(new RegExp(`--${token}:\\s*${value}`, "i"));
    }

    expect(css).toMatch(/--shadow:\s*7px 7px 0 var\(--ink\);/);
    expect(css).toMatch(
      /body\s*\{[^}]*background-image:\s*radial-gradient\([^;]*rgba\(117,\s*107,\s*96,\s*0\.2\)\s*1px,[^;]*transparent\s*1px[^;]*\);[^}]*background-size:\s*18px 18px;/,
    );

    for (const [selector, width] of [
      ["top-bar", 4],
      ["intro-panel", 4],
      ["search-panel", 3],
      ["reader-panel", 4],
    ] as const) {
      expect(css).toMatch(
        new RegExp(
          `\\.${selector}\\s*\\{[^}]*border:\\s*${width}px solid var\\(--ink\\);`,
        ),
      );
    }
  });

  it("keeps the required desktop grid and reader measure", async () => {
    const css = await readFile(projectFile("app/globals.css"), "utf8");

    expect(css).toMatch(
      /\.archive-console\s*\{[^}]*display:\s*grid;[^}]*grid-template-columns:\s*minmax\(280px,\s*\.8fr\)\s+minmax\(0,\s*1\.4fr\);[^}]*gap:\s*24px;/,
    );
    expect(css).toMatch(/\.reader-body\s*\{[^}]*max-width:\s*72ch;/);
    expect(css).not.toMatch(/\.reader-body\s*\{[^}]*max-width:\s*none;/);
  });

  it("stacks the archive and unsticks the reader at 820px", async () => {
    const css = await readFile(projectFile("app/globals.css"), "utf8");
    const tabletStart = css.search(/@media\s*\(max-width:\s*820px\)/);
    const searchStackStart = css.search(/@media\s*\(max-width:\s*640px\)/);

    expect(tabletStart).toBeGreaterThan(-1);
    expect(searchStackStart).toBeGreaterThan(tabletStart);

    const tabletCss = css.slice(tabletStart, searchStackStart);
    expect(tabletCss).toMatch(
      /\.archive-console\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\);/,
    );
    expect(tabletCss).toMatch(/\.reader-panel\s*\{[^}]*position:\s*static;/);
  });

  it("preserves focus-ring space in the scrolling category navigation", async () => {
    const css = await readFile(projectFile("app/globals.css"), "utf8");
    const tabletStart = css.search(/@media\s*\(max-width:\s*820px\)/);
    const searchStackStart = css.search(/@media\s*\(max-width:\s*640px\)/);
    const tabletCss = css.slice(tabletStart, searchStackStart);

    expect(tabletCss).toMatch(
      /\.category-nav\s*\{[^}]*padding:\s*8px;[^}]*overflow-x:\s*auto;/,
    );
  });

  it("stacks search controls before their minimum widths can overflow", async () => {
    const css = await readFile(projectFile("app/globals.css"), "utf8");
    const searchStackStart = css.search(/@media\s*\(max-width:\s*640px\)/);
    const mobileStart = css.search(/@media\s*\(max-width:\s*540px\)/);

    expect(searchStackStart).toBeGreaterThan(-1);
    expect(mobileStart).toBeGreaterThan(searchStackStart);

    const searchStackCss = css.slice(searchStackStart, mobileStart);
    expect(searchStackCss).toMatch(
      /\.search-panel\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\);/,
    );
  });

  it("keeps the phone layout structural at 540px", async () => {
    const css = await readFile(projectFile("app/globals.css"), "utf8");
    const mobileStart = css.search(/@media\s*\(max-width:\s*540px\)/);
    const reducedMotionStart = css.search(
      /@media\s*\(prefers-reduced-motion:\s*reduce\)/,
    );

    expect(mobileStart).toBeGreaterThan(-1);
    expect(reducedMotionStart).toBeGreaterThan(mobileStart);

    const mobileCss = css.slice(mobileStart, reducedMotionStart);
    expect(mobileCss).toMatch(
      /\.savepoint-shell\s*\{[^}]*padding:\s*14px 12px 28px;/,
    );
    expect(mobileCss).toMatch(
      /\.intro-metrics\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*1fr\);/,
    );
  });

  it("keeps controls, focus, transitions, and reduced motion accessible", async () => {
    const css = await readFile(projectFile("app/globals.css"), "utf8");
    const reducedMotionStart = css.search(
      /@media\s*\(prefers-reduced-motion:\s*reduce\)/,
    );

    expect(css).toMatch(
      /:focus-visible\s*\{[^}]*outline:\s*3px solid #2563eb;[^}]*outline-offset:\s*3px;/,
    );
    expect(css).toMatch(
      /\.category-nav button,\s*\.reset-button,\s*\.empty-state button\s*\{[^}]*min-height:\s*44px;[^}]*transform 180ms ease-out;/,
    );
    expect(css).toMatch(
      /\.search-control input\s*\{[^}]*min-height:\s*44px;/,
    );
    expect(css).toMatch(
      /\.note-card\s*\{[^}]*min-height:\s*44px;[^}]*transform 180ms ease-out;/,
    );

    expect(reducedMotionStart).toBeGreaterThan(-1);
    const reducedMotionCss = css.slice(reducedMotionStart);
    expect(reducedMotionCss).toMatch(
      /html\s*\{[^}]*scroll-behavior:\s*auto;/,
    );
    expect(reducedMotionCss).toMatch(
      /\*,\s*\*::before,\s*\*::after\s*\{[^}]*scroll-behavior:\s*auto !important;[^}]*transition:\s*none !important;/,
    );
  });

  it("removes starter-only styling, preview code, dependency, and identity", async () => {
    const [css, packageJsonText, packageLockText, readme] = await Promise.all([
      readFile(projectFile("app/globals.css"), "utf8"),
      readFile(projectFile("package.json"), "utf8"),
      readFile(projectFile("package-lock.json"), "utf8"),
      readFile(projectFile("README.md"), "utf8"),
    ]);
    const packageJson = JSON.parse(packageJsonText) as { name?: string };
    const packageLock = JSON.parse(packageLockText) as {
      name?: string;
      packages?: Record<string, { name?: string }>;
    };
    let starterFaviconExists = true;

    try {
      await access(projectFile("public/favicon.svg"));
    } catch {
      starterFaviconExists = false;
    }

    expect(css).not.toMatch(/prefers-color-scheme:\s*dark/);
    expect(packageJsonText).not.toContain("react-loading-skeleton");
    await expect(access(projectFile("app/_sites-preview"))).rejects.toThrow();
    expect.soft(readme).toMatch(/^# 柠檬林 · Lemon Grove$/m);
    expect.soft(readme).toContain(
      "柠檬林（Lemon Grove）从 GitHub 仓库 `luyunfeng/lemon-grove` 的 `main` 分支读取个人知识库。",
    );
    expect.soft(packageJson.name).toBe("savepoint-notes-site");
    expect.soft(packageLock.name).toBe("savepoint-notes-site");
    expect.soft(packageLock.packages?.[""]?.name).toBe(
      "savepoint-notes-site",
    );
    expect.soft(starterFaviconExists).toBe(false);
  });
});
