import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import ArchiveBrowser from "./archive-browser";
import { CATEGORY_LABELS } from "./notes";
import { makeNote, makeSnapshot } from "./test-fixtures";

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });

describe("Lemon Grove ArchiveBrowser", () => {
  it("combines category and search, handles no matches, and resets selection", async () => {
    const user = userEvent.setup();
    const snapshot = makeSnapshot();
    render(<ArchiveBrowser initialSnapshot={snapshot} />);
    expect(screen.getByText("显示 4 个存档")).toBeVisible();
    for (const note of snapshot.notes) {
      expect(within(screen.getByRole("button", { name: `打开：${note.title}` }))
        .getByText(CATEGORY_LABELS[note.category])).toBeVisible();
    }
    await user.click(screen.getByRole("button", { name: "概念" }));
    expect(screen.getByText("显示 2 个存档")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "打开：上下文隔离" }));
    const search = screen.getByRole("searchbox", { name: "搜索存档" });
    await user.type(search, "上下文");
    expect(screen.getByText("显示 1 个存档")).toBeVisible();
    await user.clear(search);
    await user.type(search, "合成工具");
    expect(screen.getByRole("heading", { name: "没有找到这个存档" })).toBeVisible();
    await user.click(within(screen.getByRole("region", { name: "没有找到这个存档" }))
      .getByRole("button", { name: "清除筛选" }));
    expect(search).toHaveValue("");
    expect(screen.getByRole("button", { name: "全部" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("显示 4 个存档")).toBeVisible();
    expect(screen.getByRole("button", { name: "打开：验证原则" })).toHaveAttribute("aria-pressed", "true");
  });

  it("selects cards for reading and applies reader tags across categories", async () => {
    const user = userEvent.setup();
    render(<ArchiveBrowser initialSnapshot={makeSnapshot()} />);
    await user.click(screen.getByRole("button", { name: "打开：合成工具" }));
    expect(screen.getByRole("button", { name: "打开：验证原则" })).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByRole("button", { name: "打开：合成工具" })).toHaveAttribute("aria-pressed", "true");
    const reader = screen.getByRole("article", { name: "合成工具" });
    expect(within(reader).getByText("工具正文：可以运行检查。")).toBeVisible();
    expect(within(reader).getByRole("link", { name: "在 GitHub 阅读" }))
      .toHaveAttribute("href", makeSnapshot().notes[2].sourceUrl);
    expect(within(within(reader).getByRole("list", { name: "标签" })).getAllByRole("listitem")).toHaveLength(2);
    await user.click(screen.getByRole("button", { name: "工具与项目" }));
    await user.click(within(reader).getByRole("button", { name: "按 verification 筛选" }));
    expect(screen.getByRole("searchbox")).toHaveValue("verification");
    expect(screen.getByRole("button", { name: "全部" })).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByText("显示 2 个存档")).toBeVisible();
    expect(screen.queryByRole("button", { name: "打开：上下文隔离" })).not.toBeInTheDocument();
  });

  it("renders Markdown tables and literal code while stripping executable HTML and URLs", () => {
    const markdown = [
      "| 项目 | 结果 |", "| --- | --- |", "| 表格校验 | 通过 |", "",
      "```js", 'const example = "<script>literal</script>";', "```", "",
      '<script>globalThis.__savepointUnsafe = true</script>', "",
      '<img src="invalid" onerror="globalThis.__savepointUnsafe = true">', "",
      "[危险链接](javascript:alert%281%29)", "",
      "[普通链接](https://example.com/docs)",
    ].join("\n");
    const { container } = render(<ArchiveBrowser initialSnapshot={makeSnapshot({ notes: [makeNote({ markdown })] })} />);
    const reader = screen.getByRole("article", { name: "验证原则" });
    expect(within(reader).getByRole("table")).toBeVisible();
    expect(within(reader).getByRole("cell", { name: "表格校验" })).toBeVisible();
    expect(reader.querySelector("pre code")).toHaveTextContent('const example = "<script>literal</script>";');
    expect(container.querySelector("script, img, [onerror]")).toBeNull();
    expect((globalThis as typeof globalThis & { __savepointUnsafe?: boolean }).__savepointUnsafe).toBeUndefined();
    expect(within(reader).getByText("危险链接").closest("a")).not.toHaveAttribute("href", expect.stringMatching(/^javascript:/i));
    expect(within(reader).getByRole("link", { name: "普通链接" })).toHaveAttribute("href", "https://example.com/docs");
  });

  it.each([
    ["empty", "等待第一份知识存档", "等待知识页", "知识库还没有知识页。"],
    ["setup_required", "等待知识库连接", "等待连接", "请先连接数据源。"],
  ] as const)("shows %s without sample cards", (status, heading, state, message) => {
    render(<ArchiveBrowser initialSnapshot={makeSnapshot({ status, notes: [], message })} />);
    expect(screen.getByRole("heading", { name: heading })).toBeVisible();
    expect(screen.getByRole("status")).toHaveTextContent(state);
    expect(screen.getByText(message)).toBeVisible();
    expect(screen.queryByRole("article")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^打开：/ })).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: "打开 GitHub 知识库" })).toHaveAttribute("href", makeSnapshot().source.url);
  });

  it("reloads from the same-origin API and replaces the displayed snapshot", async () => {
    const user = userEvent.setup();
    const updated = makeSnapshot({ notes: [makeNote({ id: "concepts/test-updated", title: "更新后的知识", markdown: "更新后的正文。" })] });
    let finish!: (response: Response) => void;
    const fetchMock = vi.fn(() => new Promise<Response>((resolve) => { finish = resolve; }));
    vi.stubGlobal("fetch", fetchMock);
    render(<ArchiveBrowser initialSnapshot={makeSnapshot()} />);
    await user.click(screen.getByRole("button", { name: "重新加载" }));
    expect(fetchMock).toHaveBeenCalledOnce();
    expect(fetchMock).toHaveBeenCalledWith("/api/knowledge", { cache: "no-store", signal: expect.any(AbortSignal) });
    expect(screen.getByRole("button", { name: "读取中" })).toBeDisabled();
    expect(screen.getByRole("status")).toHaveTextContent("正在读取…");
    finish(new Response(JSON.stringify(updated), { status: 200 }));
    const reader = await screen.findByRole("article", { name: "更新后的知识" });
    expect(within(reader).getByText("更新后的正文。")).toBeVisible();
    expect(screen.queryByRole("button", { name: "打开：验证原则" })).not.toBeInTheDocument();
    expect(screen.getByText("显示 1 个存档")).toBeVisible();
    expect(screen.getByRole("status")).toHaveTextContent("已读取");
    expect(screen.getByRole("button", { name: "重新加载" })).toBeEnabled();
  });

  it.each(["access_denied", "setup_required"] as const)("clears displayed private content after %s", async (status) => {
    const user = userEvent.setup();
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify(makeSnapshot({ status, notes: [], message: "读取连接已失效。" })), { status: status === "access_denied" ? 403 : 503 })));
    render(<ArchiveBrowser initialSnapshot={makeSnapshot()} />);
    await user.click(screen.getByRole("button", { name: "重新加载" }));
    await waitFor(() => expect(screen.queryByRole("article")).not.toBeInTheDocument());
    expect(screen.queryByRole("button", { name: /^打开：/ })).not.toBeInTheDocument();
    expect(screen.getByText("读取连接已失效。")).toBeVisible();
    expect(screen.queryByText("显示上次内容")).not.toBeInTheDocument();
  });

  it.each(["network", "invalid-response", "unavailable", "rate_limited"])("retains selected content and marks it stale after %s failure", async (failure) => {
    const user = userEvent.setup();
    vi.stubGlobal("fetch", failure === "network"
      ? vi.fn().mockRejectedValue(new Error("offline"))
      : vi.fn().mockResolvedValue(new Response(JSON.stringify(
        failure === "invalid-response" ? { notes: [] }
          : makeSnapshot({ status: failure as "unavailable" | "rate_limited", notes: [], message: "读取失败。", retryAfterSeconds: failure === "rate_limited" ? 60 : undefined }),
      ), { status: failure === "unavailable" ? 503 : failure === "rate_limited" ? 429 : 200 })));
    render(<ArchiveBrowser initialSnapshot={makeSnapshot()} />);
    await user.click(screen.getByRole("button", { name: "打开：合成工具" }));
    await user.click(screen.getByRole("button", { name: "重新加载" }));
    await waitFor(() => expect(screen.getByRole("button", { name: "重新加载" })).toBeEnabled());
    expect(screen.getByText("显示上次内容")).toBeVisible();
    expect(screen.getByText(/保留上次成功读取的内容/)).toBeVisible();
    expect(screen.getByText("显示 4 个存档")).toBeVisible();
    expect(within(screen.getByRole("article", { name: "合成工具" })).getByText("工具正文：可以运行检查。")).toBeVisible();
    expect(screen.getByRole("button", { name: "打开：合成工具" })).toHaveAttribute("aria-pressed", "true");
  });
});
