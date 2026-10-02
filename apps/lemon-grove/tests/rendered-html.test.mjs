import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

const developmentPreviewMeta =
  /<meta(?=[^>]*\bname=["']codex-preview["'])(?=[^>]*\bcontent=["']development["'])[^>]*>/i;
const templateRoot = new URL("../", import.meta.url);

const previewUrl = process.env.SAVEPOINT_TEST_URL ?? "http://localhost:3000";
const publication = JSON.parse(await readFile(new URL("../app/knowledge-publication.json", import.meta.url), "utf8"));
async function render() { return fetch(previewUrl, { headers: { accept: "text/html" } }); }

test("server-renders the Lemon Grove console", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<html lang="zh-CN">/);
  assert.match(html, /<title>柠檬林 · Lemon Grove<\/title>/);
  assert.match(
    html,
    /<meta name="description" content="从 GitHub 知识库读取概念、工具与学习路线的个人知识存档站。"\/>/,
  );
  assert.match(html, /<h1 id="intro-title">把理解存进这里<\/h1>/);
  assert.match(html, /aria-label="笔记分类"/);
  assert.match(html, /aria-label="知识库数据源"/);
  assert.match(html, /luyunfeng\/lemon-grove/);
  assert.match(html, /GitHub 已同步/);
  assert.equal((html.match(/class="note-card"/g) ?? []).length, publication.notes.length);
  assert.match(html, /class="reader-panel"/);
  assert.doesNotMatch(html, /等待知识库连接/);
  assert.doesNotMatch(html, /DEMO · READ ONLY|项目启动清单|周末咖啡清单/);
});

test("serves a bounded knowledge response without a shared HTTP cache", async () => {
  const response = await fetch(new URL("/api/knowledge", previewUrl));
  assert.equal(response.headers.get("cache-control"), "private, no-store");
  assert.equal(response.headers.get("x-content-type-options"), "nosniff");
  const data = await response.json();
  assert.equal(data.source.repository, "luyunfeng/lemon-grove");
  assert.equal(data.source.branch, "main");
  assert.equal(data.status, "ready");
  assert.equal(data.source.delivery, "published");
  assert.equal(data.source.revision, publication.source.revision);
  assert.equal(data.notes.length, publication.notes.length);
  assert.ok(["ready", "empty", "setup_required", "access_denied", "unavailable", "rate_limited", "stale"].includes(data.status));
  assert.ok(data.notes.every((note) => /^wiki\/(?:overview$|(?:concepts|entities|roadmaps|syntheses)\/)/.test(note.id)));
  assert.equal(Object.hasOwn(data, "token"), false);
  assert.equal(Object.hasOwn(data.source, "token"), false);
});

test("does not ship the starter preview", async () => {
  const [response, packageJson] = await Promise.all([
    render(),
    readFile(new URL("../package.json", import.meta.url), "utf8"),
  ]);
  const html = await response.text();

  assert.doesNotMatch(html, developmentPreviewMeta);
  assert.doesNotMatch(html, /Your site is taking shape|Codex is working/i);
  assert.doesNotMatch(html, /react-loading-skeleton/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);

  await assert.rejects(
    access(new URL("app/_sites-preview", templateRoot)),
  );
});
