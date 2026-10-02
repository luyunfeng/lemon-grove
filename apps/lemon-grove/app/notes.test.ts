import { describe, expect, it } from "vitest";
import { filterNotes } from "./notes";
import { makeSnapshot } from "./test-fixtures";

describe("knowledge note filtering", () => {
  it("combines category and normalized search, including empty results", () => {
    const { notes } = makeSnapshot();
    expect(filterNotes(notes, "all", "")).toEqual(notes);
    expect(filterNotes(notes, "concept", "  VERIFICATION  ").map((n) => n.title)).toEqual(["验证原则"]);
    expect(filterNotes(notes, "roadmap", "verification")).toEqual([]);
    expect(filterNotes(notes, "all", "不存在的内容")).toEqual([]);
    expect(filterNotes([], "all", "")).toEqual([]);
  });
  it.each([
    ["验证原则", ["验证原则"]],
    ["控制输入范围", ["上下文隔离"]],
    ["测试工程", ["验证原则", "上下文隔离", "合成工具", "实践路线"]],
    [" EVIDENCETOKEN ", ["验证原则"]],
    ["tool-interface", ["合成工具"]],
    ["TEST-RUNNER", ["验证原则", "合成工具"]],
  ])("searches title, excerpt, domain, Markdown, tags and entities: %s", (query, titles) => {
    expect(filterNotes(makeSnapshot().notes, "all", query).map((n) => n.title)).toEqual(titles);
  });
  it("preserves input data and ordering", () => {
    const notes = makeSnapshot().notes;
    const before = structuredClone(notes);
    expect(filterNotes(notes, "all", "verification")).toEqual([notes[0], notes[2]]);
    expect(notes).toEqual(before);
  });
});
