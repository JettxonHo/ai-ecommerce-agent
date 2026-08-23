import { describe, expect, it } from "vitest";
import type { TaskCurrentResult } from "../gateway";
import { projectResult } from "./resultProjection";

describe("projectResult", () => {
  it("keeps proof and next-step projections within their authoritative meanings", () => {
    const result: TaskCurrentResult = {
      taskId: "task-7",
      resultRevision: 2,
      inputRevision: 1,
      status: "awaiting_review",
      generatedAt: "2026-08-12T00:00:00Z",
      missingInformation: [],
      productIntake: null,
      customerInsight: null,
      productPositioning: {
        positioning_candidates: [
          {
            candidate_title: "城市通勤的清晰收纳方案",
            proof_points: [{ statement: "可放入 14 英寸级别设备" }],
          },
        ],
      },
      marketingBrief: {
        brief_candidate: {
          message_architecture: {
            message_hierarchy: {
              supporting_features: ["独立证据不足的功能描述"],
            },
          },
          execution_direction: {
            call_to_action_objective: "CTA 目标不是运营下一步",
          },
          constraints_and_honesty: {
            hypotheses_to_test: ["验证晚高峰取用是否更顺手"],
            mandatory_messages: ["必须保留资料限制说明"],
          },
        },
      },
      xiaohongshuBrief: {
        xiaohongshu_brief_candidate: {
          discovery_and_action_directions: {
            cta_mapping: {
              cta_direction: "小红书 CTA 方向不是运营下一步",
            },
          },
        },
      },
      confirmation: null,
    };

    const projection = projectResult(result);

    expect(projection.proofPoints).toEqual(["可放入 14 英寸级别设备"]);
    expect(projection.proofPoints).not.toContain("独立证据不足的功能描述");
    expect(projection.nextSteps).toEqual(["验证晚高峰取用是否更顺手"]);
    expect(projection.nextSteps).not.toContain("CTA 目标不是运营下一步");
    expect(projection.nextSteps).not.toContain("小红书 CTA 方向不是运营下一步");
    expect(projection.nextSteps).not.toContain("必须保留资料限制说明");
  });
});
