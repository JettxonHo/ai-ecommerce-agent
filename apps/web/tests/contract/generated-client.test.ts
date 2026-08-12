import type {
  components,
  operations,
  paths,
} from "../../src/api/generated/schema";
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

type Assert<T extends true> = T;
type HasKey<T, K extends PropertyKey> = [T] extends [never]
  ? false
  : K extends keyof T
    ? true
    : false;
type TaskQuery = NonNullable<operations["listTasks"]["parameters"]["query"]>;
type TaskCreateBody =
  operations["createTask"]["requestBody"]["content"]["application/json"];
type RunReadBody =
  operations["getRun"]["responses"][200]["content"]["application/json"];
type RunRecoveryBody =
  operations["resumeRun"]["requestBody"]["content"]["application/json"];
type RunRecoveryResponse =
  operations["resumeRun"]["responses"][202]["content"]["application/json"];
type ReviewSubmitBody =
  operations["submitReview"]["requestBody"]["content"]["application/json"];
type ReviewSubmitResponse =
  operations["submitReview"]["responses"][201]["content"]["application/json"];
type BriefReadBody =
  operations["getMarketingBrief"]["responses"][200]["content"]["application/json"];
type ExportReadBody =
  operations["getExportSnapshot"]["responses"][200]["content"]["application/json"];
type ProblemBody = components["schemas"]["ProblemDetails"];
type ProblemResponseBody =
  components["responses"]["Problem409"]["content"]["application/problem+json"];

type HasTaskCollection = "/api/v1/tasks" extends keyof paths ? true : false;
type HasTaskQuery = HasKey<TaskQuery, "limit">;
type HasTaskCreate = HasKey<TaskCreateBody, "taskName">;
type HasRun = "/api/v1/runs/{runId}" extends keyof paths ? true : false;
type HasRunRead = HasKey<RunReadBody, "failureSummary">;
type HasRunRecovery = HasKey<RunRecoveryBody, "expectedRevision">;
type HasRunRecoveryReceipt = HasKey<RunRecoveryResponse, "monitor">;
type HasReviewSubmit = HasKey<ReviewSubmitBody, "reviewId">;
type HasReviewSubmitRevision = HasKey<
  ReviewSubmitBody,
  "expectedDraftRevision"
>;
type HasReviewSubmitResult = HasKey<ReviewSubmitResponse, "reviewDecision">;
type HasBrief = HasKey<BriefReadBody, "briefKind">;
type HasExport = HasKey<ExportReadBody, "contentLocation">;
type HasProblem = HasKey<ProblemBody, "type">;
type HasProblemAction = HasKey<ProblemBody, "action">;
type HasProblemResponse = HasKey<ProblemResponseBody, "status">;

const representativePaths = [
  "/api/v1/tasks",
  "/api/v1/runs/{runId}",
  "/api/v1/review-packages/{reviewPackageId}/commands/submit",
  "/api/v1/marketing-briefs/{marketingBriefVersionId}",
  "/api/v1/export-snapshots/{exportSnapshotId}",
] as const satisfies readonly (keyof paths)[];
const generatedCoverage: readonly [
  Assert<HasTaskCollection>,
  Assert<HasTaskQuery>,
  Assert<HasTaskCreate>,
  Assert<HasRun>,
  Assert<HasRunRead>,
  Assert<HasRunRecovery>,
  Assert<HasRunRecoveryReceipt>,
  Assert<HasReviewSubmit>,
  Assert<HasReviewSubmitRevision>,
  Assert<HasReviewSubmitResult>,
  Assert<HasBrief>,
  Assert<HasExport>,
  Assert<HasProblem>,
  Assert<HasProblemAction>,
  Assert<HasProblemResponse>,
] = [
  true,
  true,
  true,
  true,
  true,
  true,
  true,
  true,
  true,
  true,
  true,
  true,
  true,
  true,
  true,
];

const generatedSource = readFileSync("src/api/generated/schema.d.ts", "utf8");
const clientSource = readFileSync("src/api/client.ts", "utf8");

describe("generated OpenAPI client contract", () => {
  it("commits representative authored paths and schemas to generated types", () => {
    expect(representativePaths).toEqual([
      "/api/v1/tasks",
      "/api/v1/runs/{runId}",
      "/api/v1/review-packages/{reviewPackageId}/commands/submit",
      "/api/v1/marketing-briefs/{marketingBriefVersionId}",
      "/api/v1/export-snapshots/{exportSnapshotId}",
    ]);
    expect(generatedCoverage).toEqual(new Array(15).fill(true));
  });

  it("keeps generated output type-only and the client consumer direction narrow", () => {
    const importLines = clientSource
      .split("\n")
      .filter((line) => line.startsWith("import "));
    expect(generatedSource).toContain("export interface paths");
    expect(generatedSource).not.toContain("fetch(");
    expect(importLines).toEqual([
      'import createClient, { type Client } from "openapi-fetch";',
      'import type { paths } from "./generated/schema";',
    ]);
    expect(clientSource).not.toContain("new Client");
    expect(clientSource).not.toContain("globalThis.fetch(");
  });
});
