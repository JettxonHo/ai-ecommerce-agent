import { describe, expect, it } from "vitest";
import type { TaskOverview } from "../gateway";
import {
  deriveWorkbenchLocation,
  deriveWorkbenchMode,
  WORKBENCH_PANELS,
  WORKBENCH_STAGES,
} from "./projection";

const factStage = WORKBENCH_STAGES[0];
const insightStage = WORKBENCH_STAGES[1];
const task = (overrides: Partial<TaskOverview> = {}): TaskOverview =>
  ({
    taskId: "task-1",
    taskName: "Launch",
    productCategory: "Backpack",
    taskStatus: "draft",
    currentStage: null,
    waitingReason: null,
    updatedAt: "2026-08-12T00:00:00Z",
    revision: 0,
    primaryAction: { kind: "none" },
    capabilities: [],
    stages: [],
    activeRunId: null,
    latestRunId: null,
    needsInputRequest: null,
    reviewPackage: null,
    approvedStrategy: null,
    marketingBrief: null,
    xiaohongshuBrief: null,
    ...overrides,
  }) as TaskOverview;

const location = (overrides: Partial<TaskOverview> = {}, search = "") =>
  deriveWorkbenchLocation(task(overrides), search);

describe("private Workbench projection", () => {
  it("publishes the exact ordered panel and stage catalogs", () => {
    expect(WORKBENCH_PANELS).toEqual([
      "intake",
      "progress",
      "review",
      "results",
      "evidence",
    ]);
    expect(WORKBENCH_STAGES).toEqual([
      "product_intake_and_fact_extraction",
      "customer_insight_analysis",
      "product_positioning",
      "human_review",
      "marketing_brief_generation",
      "xiaohongshu_brief_mapping",
    ]);
    expect(Object.isFrozen(WORKBENCH_PANELS)).toBe(true);
    expect(Object.isFrozen(WORKBENCH_STAGES)).toBe(true);
  });

  it.each([
    [
      "needs input",
      { needsInputRequest: { resourceId: "input-1", revision: 2 } },
      "needs_input",
    ],
    [
      "review",
      { reviewPackage: { reviewPackageId: "review-1", packageVersion: 3 } },
      "review",
    ],
    ["active run", { activeRunId: "run-1" }, "running"],
    [
      "marketing result",
      {
        marketingBrief: {
          resourceKind: "brief",
          resourceVersionId: "brief-1",
          versionNumber: 1,
        },
      },
      "results",
    ],
    [
      "xiaohongshu result",
      {
        xiaohongshuBrief: {
          resourceKind: "xhs",
          resourceVersionId: "xhs-1",
          versionNumber: 1,
        },
      },
      "results",
    ],
    ["failed recovery", { taskStatus: "failed" }, "recovery"],
    ["paused recovery", { taskStatus: "paused" }, "recovery"],
    [
      "primary recovery",
      { primaryAction: { kind: "navigate", target: "recovery" } },
      "recovery",
    ],
    ["otherwise intake", {}, "intake"],
  ] as const)("derives %s mode", (_name, overrides, expected) => {
    expect(deriveWorkbenchMode(task(overrides))).toBe(expected);
  });

  it("applies mode precedence without letting lower-priority signals win", () => {
    expect(
      deriveWorkbenchMode(
        task({
          needsInputRequest: { resourceId: "input-1", revision: 2 },
          reviewPackage: { reviewPackageId: "review-1", packageVersion: 3 },
          activeRunId: "run-1",
          marketingBrief: {
            resourceKind: "brief",
            resourceVersionId: "brief-1",
            versionNumber: 1,
          },
          taskStatus: "failed",
        }),
      ),
    ).toBe("needs_input");
  });

  it("ignores latest run, approved strategy, waiting text, current stage and unknown action for mode", () => {
    expect(
      deriveWorkbenchMode(
        task({
          latestRunId: "run-latest",
          approvedStrategy: {
            resourceKind: "strategy",
            resourceVersionId: "strategy-1",
            versionNumber: 1,
          },
          waitingReason: "still waiting",
          currentStage: insightStage,
          primaryAction: { kind: "unavailable" },
        }),
      ),
    ).toBe("intake");
  });

  it.each([
    ["intake", {}, "intake"],
    [
      "needs input",
      { needsInputRequest: { resourceId: "input-1", revision: 1 } },
      "intake",
    ],
    ["running", { activeRunId: "run-1" }, "progress"],
    ["recovery", { taskStatus: "failed" }, "progress"],
    [
      "review",
      { reviewPackage: { reviewPackageId: "review-1", packageVersion: 1 } },
      "review",
    ],
    [
      "results",
      {
        marketingBrief: {
          resourceKind: "brief",
          resourceVersionId: "brief-1",
          versionNumber: 1,
        },
      },
      "results",
    ],
  ] as const)("uses the %s default panel", (_name, overrides, expected) => {
    expect(location(overrides).panel).toBe(expected);
  });

  it("defaults stage to valid currentStage, then first valid summary, then fact stage", () => {
    expect(location({ currentStage: "product_positioning" }).stage).toBe(
      "product_positioning",
    );
    expect(
      location({
        currentStage: "not-a-stage",
        stages: [
          {
            stage: insightStage,
            status: "ready",
            waitingReason: null,
            updatedAt: "now",
          },
        ],
      }).stage,
    ).toBe(insightStage);
    expect(
      location({
        currentStage: "not-a-stage",
        stages: [
          {
            stage: "not-a-stage",
            status: "ready",
            waitingReason: null,
            updatedAt: "now",
          },
        ],
      }).stage,
    ).toBe(factStage);
  });

  it("preserves one valid selection and leaves search untouched", () => {
    const result = location(
      { currentStage: insightStage },
      "?panel=review&stage=customer_insight_analysis&filter=mine",
    );
    expect(result).toEqual({
      panel: "review",
      stage: insightStage,
      replaceSearch: null,
    });
  });

  it.each([
    ["?panel=", "intake"],
    ["?panel=unknown&stage=customer_insight_analysis", "intake"],
    ["?panel=review&panel=intake&stage=customer_insight_analysis", "intake"],
    ["?panel=review&stage=unknown", "review"],
    [
      "?panel=review&stage=customer_insight_analysis&stage=human_review",
      "review",
    ],
  ] as const)("canonicalizes invalid selection %s", (search, expectedPanel) => {
    const result = location(
      {
        currentStage: insightStage,
        stages: [
          {
            stage: insightStage,
            status: "ready",
            waitingReason: null,
            updatedAt: "now",
          },
        ],
      },
      search,
    );
    expect(result.panel).toBe(expectedPanel);
    expect(result.stage).toBe(insightStage);
    expect(result.replaceSearch).toBe(
      `?panel=${expectedPanel}&stage=customer_insight_analysis`,
    );
  });

  it("canonicalizes an inapplicable supplied stage and preserves unrelated params", () => {
    const result = location(
      {
        stages: [
          {
            stage: insightStage,
            status: "ready",
            waitingReason: null,
            updatedAt: "now",
          },
        ],
      },
      "?filter=mine&panel=review&stage=human_review&sort=updated",
    );
    expect(result).toEqual({
      panel: "review",
      stage: insightStage,
      replaceSearch:
        "?filter=mine&sort=updated&panel=review&stage=customer_insight_analysis",
    });
  });

  it("allows any catalog stage when no stage summaries are supplied", () => {
    expect(
      location({}, "?panel=evidence&stage=xiaohongshu_brief_mapping"),
    ).toEqual({
      panel: "evidence",
      stage: "xiaohongshu_brief_mapping",
      replaceSearch: null,
    });
  });

  it("does not replace search when panel or stage is absent", () => {
    expect(location({}, "?filter=mine").replaceSearch).toBeNull();
    expect(location({}, "?panel=review").replaceSearch).toBeNull();
    expect(location({}, "?stage=human_review").replaceSearch).toBeNull();
  });

  it("is pure, repeatable and detached", () => {
    const input = task({
      stages: [
        {
          stage: insightStage,
          status: "ready",
          waitingReason: null,
          updatedAt: "now",
        },
      ],
    });
    const first = deriveWorkbenchLocation(
      input,
      "?panel=review&stage=human_review",
    );
    const second = deriveWorkbenchLocation(
      input,
      "?panel=review&stage=human_review",
    );
    expect(first).toEqual(second);
    expect(Object.isFrozen(first)).toBe(true);
    expect(input.stages).toHaveLength(1);
    expect(input.currentStage).toBeNull();
  });
});
