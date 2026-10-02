# SAVEPOINT Notes Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Build and privately publish a responsive, read-only personal notes showcase whose interface feels like a cream, black, and brick-red retro game console.

**Architecture:** Use the Sites Vinext starter as a single-page React application. Keep the nine-note dataset and pure filtering logic in app/notes.ts, interactive presentation in app/page.tsx, and the visual system in app/globals.css. No persistence, external data, authentication, or additional routes are required.

**Tech Stack:** Sites Vinext starter, React, TypeScript, CSS, Vitest, Testing Library, Cloudflare Workers-compatible ESM output.

## Global Constraints

- The product name is SAVEPOINT / 存档点, with the headline 把日常存进这里.
- Include exactly nine complete Chinese example notes: three work, three learning, and three life notes.
- Use #F3EBDD, #FFF9ED, #17130F, #C7352A, #756B60, and #D8C7A9 as the core palette.
- Use CSS shapes, borders, typography, and layout for the game-console treatment; do not add decorative SVGs or image dependencies.
- Provide category filtering, full-text search, note selection, a clear-filter action, and a no-results state.
- Do not add persistence, accounts, a database, uploads, multiple routes, comments, sharing, or collaboration.
- The deployed site must remain private.

## File Map

- app/notes.ts: note types, nine-note dataset, labels, and pure filtering function.
- app/notes.test.ts: dataset and filtering tests.
- app/page.tsx: state plus focused UI components for navigation, cards, reader, search, and empty state.
- app/page.test.tsx: interaction and accessibility tests.
- app/globals.css: reset, tokens, console surfaces, responsive layout, focus states, and reduced motion.
- app/layout.tsx: finished title and description metadata.
- vitest.config.ts: jsdom test environment.
- vitest.setup.ts: Testing Library matchers.
- .openai/hosting.json: Sites project metadata.

---

### Task 1: Initialize Sites and add the note domain

**Files:**
- Create: app/notes.ts
- Create: app/notes.test.ts
- Create: vitest.config.ts
- Create: vitest.setup.ts
- Modify: package.json and package-lock.json
- Preserve: .openai/hosting.json

**Interfaces:**
- Produces: Category = "all" | "work" | "learning" | "life".
- Produces: Note with id, slot, category, title, excerpt, date, readTime, tags, featured, and body.
- Produces: NOTES, CATEGORY_LABELS, and filterNotes(notes, category, query): Note[].

- [ ] **Step 1: Initialize and preview the starter**

Run the Sites initializer once against the repository root. Wait for installation, start npm run dev in a retained session, and open the exact printed local URL once in Codex.

- [ ] **Step 2: Configure tests**

Run:

~~~bash
npm install --save-dev vitest jsdom @testing-library/react @testing-library/user-event @testing-library/jest-dom
npm pkg set scripts.test="vitest run"
~~~

Create vitest.config.ts:

~~~ts
import path from "node:path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: { alias: { "@": path.resolve(__dirname, ".") } },
  test: {
    environment: "jsdom",
    setupFiles: ["./vitest.setup.ts"],
  },
});
~~~

Create vitest.setup.ts:

~~~ts
import "@testing-library/jest-dom/vitest";
~~~

- [ ] **Step 3: Write the failing domain tests**

Create app/notes.test.ts:

~~~ts
import { describe, expect, it } from "vitest";
import { NOTES, filterNotes } from "./notes";

describe("SAVEPOINT notes", () => {
  it("contains three complete notes in each category", () => {
    expect(NOTES).toHaveLength(9);
    expect(NOTES.filter((note) => note.category === "work")).toHaveLength(3);
    expect(NOTES.filter((note) => note.category === "learning")).toHaveLength(3);
    expect(NOTES.filter((note) => note.category === "life")).toHaveLength(3);
    expect(NOTES.every((note) => note.body.length >= 3)).toBe(true);
  });

  it("combines category and normalized full-text search", () => {
    expect(filterNotes(NOTES, "work", "")).toHaveLength(3);
    expect(filterNotes(NOTES, "all", "  雨天  ").map((note) => note.title))
      .toEqual(["雨天散步路线"]);
    expect(filterNotes(NOTES, "learning", "行动").map((note) => note.title))
      .toEqual(["卡片笔记法小实验"]);
    expect(filterNotes(NOTES, "life", "项目")).toEqual([]);
  });
});
~~~

Run npm test -- app/notes.test.ts.

Expected: FAIL because app/notes.ts does not exist.

- [ ] **Step 4: Implement the typed note module**

Create the Category and Note types, CATEGORY_LABELS, nine records, and filterNotes. Use this exact filter implementation:

~~~ts
export function filterNotes(
  notes: readonly Note[],
  category: Category,
  query: string,
): Note[] {
  const needle = query.trim().toLocaleLowerCase("zh-CN");
  return notes.filter((note) => {
    const inCategory = category === "all" || note.category === category;
    const text = [note.title, note.excerpt, ...note.body, ...note.tags]
      .join(" ")
      .toLocaleLowerCase("zh-CN");
    return inCategory && (!needle || text.includes(needle));
  });
}
~~~

Use slots 01–09 and these complete note identities:

| Slot | Category | Title | Required body theme |
| --- | --- | --- | --- |
| 01 | work | 项目启动清单 | 目标与不做事项；第一周三个假设；负责人和检查时间 |
| 02 | work | 会议记录不等于决策 | 选择、理由、下一步；原样记录分歧；指定补证据的人 |
| 03 | work | 一周复盘：把重要的事做轻 | 整块时间；集中沟通；轻不是少做 |
| 04 | learning | 卡片笔记法小实验 | 一个问题；自己的回答；可验证行动；具体连接关系 |
| 05 | learning | 《禅与摩托车维修艺术》摘记 | 公路旅行；理性与感受；维护机器时的完整注意力 |
| 06 | learning | CSS 布局练习记录 | 内容关系；Flex 与 Grid；由拥挤决定断点 |
| 07 | life | 雨天散步路线 | 旧书店；骑楼与面包店；小公园收尾 |
| 08 | life | 周末咖啡清单 | 清晨小店；午后烘焙店；傍晚在家 |
| 09 | life | 这个月想记住的五件事 | 长谈与晚饭；道歉；普通夜晚 |

Each record must contain a natural excerpt, date, read time, two tags, featured boolean, and three finished Chinese body paragraphs. Put the word 行动 in note 04 so the specified search test passes.

- [ ] **Step 5: Verify and commit the domain**

Run:

~~~bash
npm test -- app/notes.test.ts
git add package.json package-lock.json vitest.config.ts vitest.setup.ts app/notes.ts app/notes.test.ts .openai/hosting.json
git commit -m "feat: add savepoint note domain"
~~~

Expected: 2 tests PASS and the commit succeeds.

---

### Task 2: Build the accessible interactive console

**Files:**
- Create: app/page.test.tsx
- Modify: app/page.tsx

**Interfaces:**
- Consumes: NOTES, CATEGORY_LABELS, Category, Note, and filterNotes.
- Produces: Page with category, query, and selectedId state.
- Produces accessible controls named 全部, 工作, 学习, 生活, 搜索存档, 清除筛选, and 打开：笔记标题.

- [ ] **Step 1: Write the failing page test**

Create app/page.test.tsx:

~~~tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import Page from "./page";

describe("SAVEPOINT page", () => {
  it("filters, searches, resets, and selects notes", async () => {
    const user = userEvent.setup();
    render(<Page />);

    expect(screen.getByRole("heading", { name: "把日常存进这里" })).toBeInTheDocument();
    expect(screen.getByText("显示 9 个存档")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "工作" }));
    expect(screen.getByText("显示 3 个存档")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "全部" }));
    await user.type(screen.getByRole("searchbox", { name: "搜索存档" }), "雨天");
    expect(screen.getByText("显示 1 个存档")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "打开：雨天散步路线" }));
    expect(screen.getByRole("heading", { name: "雨天散步路线" })).toBeInTheDocument();

    await user.clear(screen.getByRole("searchbox", { name: "搜索存档" }));
    await user.type(screen.getByRole("searchbox", { name: "搜索存档" }), "不存在的存档");
    expect(screen.getByRole("heading", { name: "没有找到这个存档" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "清除筛选" }));
    expect(screen.getByText("显示 9 个存档")).toBeInTheDocument();
  });

  it("renders the finished read-only console identity", () => {
    render(<Page />);
    expect(screen.getByText("SAVEPOINT")).toBeInTheDocument();
    expect(screen.getByText("存档点")).toBeInTheDocument();
    expect(screen.getByText("09 SLOTS")).toBeInTheDocument();
    expect(screen.getAllByText("READ ONLY").length).toBeGreaterThan(0);
    expect(screen.getByRole("navigation", { name: "笔记分类" })).toBeInTheDocument();
  });
});
~~~

Run npm test -- app/page.test.tsx.

Expected: FAIL because the starter page does not expose the interface.

- [ ] **Step 2: Implement focused components in app/page.tsx**

Use a client component. Keep these state transitions exact:

~~~tsx
const [category, setCategory] = useState<Category>("all");
const [query, setQuery] = useState("");
const visibleNotes = useMemo(
  () => filterNotes(NOTES, category, query),
  [category, query],
);
const [selectedId, setSelectedId] = useState(NOTES[0].id);
const selectedNote =
  visibleNotes.find((note) => note.id === selectedId) ?? visibleNotes[0] ?? null;
~~~

Define TopBar, IntroPanel, SearchPanel, NoteCard, ReaderPanel, and EmptyState in the same file.

- TopBar uses a nav named 笔记分类 and native buttons for all four categories.
- IntroPanel renders 把日常存进这里 plus 09 notes, 03 channels, and 04 featured metrics.
- SearchPanel uses label 搜索存档, input type search, visible result text 显示 N 个存档, and 清除筛选.
- NoteCard is a button whose accessible name is 打开： followed by the title and whose aria-pressed value tracks selection.
- ReaderPanel is an article with the selected title as a heading and every body paragraph rendered.
- EmptyState uses heading 没有找到这个存档 and a 清除筛选 button.
- Filtering selects the first remaining note when the current selection disappears.
- Reset restores category all, an empty query, and slot 01.
- The footer renders END OF LOG, the visible count, and DEMO · READ ONLY.

Run npm test -- app/page.test.tsx.

Expected: 2 tests PASS.

- [ ] **Step 3: Commit the interaction layer**

~~~bash
git add app/page.tsx app/page.test.tsx
git commit -m "feat: build interactive notes console"
~~~

---

### Task 3: Apply the game-console visual system

**Files:**
- Modify: app/globals.css
- Modify: app/layout.tsx
- Delete: app/_sites-preview/**
- Modify: package.json and package-lock.json only to remove an unused starter dependency.

**Interfaces:**
- Consumes: class names from app/page.tsx.
- Produces: two-column desktop and one-column mobile layouts.
- Produces metadata title SAVEPOINT · 存档点 and the site-specific Chinese description.

- [ ] **Step 1: Replace starter metadata**

Set app/layout.tsx metadata to:

~~~ts
export const metadata: Metadata = {
  title: "SAVEPOINT · 存档点",
  description: "一座把工作、学习与生活收进卡带的个人笔记站。",
};
~~~

Set html lang to zh-CN. Remove the starter preview import, codex-preview marker, and app/_sites-preview. If react-loading-skeleton has no remaining consumer, remove it with npm uninstall react-loading-skeleton.

- [ ] **Step 2: Implement the visual foundations**

Start app/globals.css with:

~~~css
:root {
  --paper: #f3ebdd;
  --panel: #fff9ed;
  --ink: #17130f;
  --red: #c7352a;
  --muted: #756b60;
  --line: #d8c7a9;
  --shadow: 7px 7px 0 var(--ink);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--ink);
  background-color: var(--paper);
  background-image: radial-gradient(circle, rgba(117, 107, 96, .2) 1px, transparent 1px);
  background-size: 18px 18px;
  font-family: Inter, ui-sans-serif, "PingFang SC", "Microsoft YaHei", sans-serif;
}
button, input { font: inherit; }
button { color: inherit; }
:focus-visible { outline: 3px solid #2563eb; outline-offset: 3px; }
~~~

Implement every class used by app/page.tsx. Major surfaces use 3–4px solid var(--ink), var(--panel), and var(--shadow). Selected navigation and cards use var(--red). Controls have a minimum 44px hit area and a pressed state that reduces shadow and translates 2px.

Use this desktop grid:

~~~css
.notes-console {
  display: grid;
  grid-template-columns: minmax(280px, .8fr) minmax(0, 1.4fr);
  gap: 24px;
}
~~~

Keep the site centered at max-width 1480px. Make the reader sticky only on desktop. At max-width 820px stack the notes console, make category navigation horizontally scrollable, and remove sticky reader positioning. At max-width 540px reduce outer padding, stack search controls, and use one-column metrics. Add prefers-reduced-motion rules that disable smooth scrolling and transitions.

- [ ] **Step 3: Verify the finished site**

Run:

~~~bash
npm test
npm run build
~~~

Expected: all 4 tests PASS and the production build exits 0.

- [ ] **Step 4: Commit the finished product**

~~~bash
git add app package.json package-lock.json
git commit -m "feat: style savepoint notes showcase"
~~~

---

### Task 4: Verify and publish privately with Sites

**Files:**
- Modify: .openai/hosting.json with the Sites project_id.
- Create outside the repository: the temporary deployment archive.

**Interfaces:**
- Consumes: successful tests, successful build, and dist/server/index.js.
- Produces: a private deployed Sites URL.

- [ ] **Step 1: Verify the exact source**

Run:

~~~bash
npm test
npm run build
git diff --check
git status --short
~~~

Expected: tests and build pass, git diff --check is silent, and only intentional hosting metadata may remain uncommitted.

- [ ] **Step 2: Create and record the Sites project**

Call create_site once with a slug based on savepoint-notes. Write only project_id plus any existing supported logical bindings to .openai/hosting.json.

- [ ] **Step 3: Commit and push the validated source**

Commit hosting metadata. Push the branch head using the returned short-lived credential in a per-command HTTP authorization header. Keep the credential out of URLs and Git configuration. Use the pushed branch-head SHA as commit_sha.

- [ ] **Step 4: Package and deploy one version**

Run the bundled scripts/package-site.sh helper against the project and a temporary archive path. Save exactly one version with that archive and commit_sha, then call the private deployment operation.

- [ ] **Step 5: Poll and hand off**

Poll deployment status until success or failure. On success, open the exact deployed URL once in Codex, stop the retained development server, and return the private URL.
