import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import {
  normalizePrimaryInput,
  type TaskCurrentResult,
  type TaskOverview,
  type TaskPrimaryInput,
  type TaskPrimaryInputDraft,
  type TaskPrimaryInputKind,
  type ExportBriefKind,
  type ExportDownload,
} from "../gateway";
import {
  deriveWorkbenchLocation,
  deriveWorkbenchMode,
  panelCatalog,
  stageCatalog,
  type WorkbenchPanel,
  type WorkbenchStage,
} from "./projection";
import styles from "./TaskWorkbench.module.css";

type TaskWorkbenchProps = Readonly<{
  task: TaskOverview;
  primaryInput?: TaskPrimaryInput | null;
  primaryInputLoading?: boolean;
  primaryInputError?: string | null;
  retryPrimaryInput?: () => void;
  savePrimaryInput?: (
    input: TaskPrimaryInputDraft,
  ) => Promise<TaskPrimaryInput>;
  currentResult?: TaskCurrentResult | null;
  currentResultLoading?: boolean;
  currentResultError?: string | null;
  retryCurrentResult?: () => void;
  generateResult?: () => Promise<TaskCurrentResult>;
  confirmCurrentResult?: (
    marketingCoreMessage: string,
    xiaohongshuTitleDirection: string,
  ) => Promise<TaskCurrentResult>;
  exportBrief?: (briefKind: ExportBriefKind) => Promise<ExportDownload>;
}>;

const panelLabels: Readonly<Record<WorkbenchPanel, string>> = {
  intake: "资料输入",
  progress: "进度",
  review: "Review",
  results: "结果",
  evidence: "证据",
};

const neutralPanelMessage: Readonly<Record<WorkbenchPanel, string>> = {
  intake: "在这里粘贴或保存商品资料。",
  progress: "任务正在处理，状态会在本地工作区更新。",
  review: "审核材料会在需要人工判断时出现在这里。",
  results: "结果与导出会在任务完成后出现在这里。",
  evidence: "证据、来源与限制会在上下文栏中保留。",
};

const businessStages: Readonly<
  Readonly<{ stage: WorkbenchStage; label: string }>[]
> = [
  { stage: "product_intake_and_fact_extraction", label: "资料整理" },
  { stage: "customer_insight_analysis", label: "用户洞察" },
  { stage: "product_positioning", label: "商品定位" },
  { stage: "marketing_brief_generation", label: "营销 Brief" },
  { stage: "xiaohongshu_brief_mapping", label: "小红书 Brief" },
];

const internalStageLabels: Readonly<Record<WorkbenchStage, string>> = {
  product_intake_and_fact_extraction: "product_intake_and_fact_extraction",
  customer_insight_analysis: "customer_insight_analysis",
  product_positioning: "product_positioning",
  human_review: "human_review",
  marketing_brief_generation: "marketing_brief_generation",
  xiaohongshu_brief_mapping: "xiaohongshu_brief_mapping",
};

// Display timestamps in UTC so presentation does not infer the operator's local timezone.
const formatTimestamp = (value: string): string => {
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) return value;
  const date = new Date(parsed);
  const pad = (part: number) => String(part).padStart(2, "0");
  return `${date.getUTCFullYear()}年${date.getUTCMonth() + 1}月${date.getUTCDate()}日 ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`;
};

const modeLabels: Readonly<Record<string, string>> = {
  intake: "资料整理",
  running: "处理中",
  needs_input: "待补充资料",
  review: "待审核",
  results: "结果已就绪",
  recovery: "需要恢复",
  unavailable: "暂时不可用",
};

const taskStatusLabels: Readonly<Record<string, string>> = {
  draft: "待开始",
  running: "处理中",
  waiting_for_input: "待补充资料",
  waiting_for_review: "待审核",
  paused: "已暂停",
  completed: "已完成",
  failed: "需要恢复",
  cancelled: "已取消",
};

type StageStatus =
  | "not_started"
  | "ready"
  | "running"
  | "waiting_input"
  | "waiting_review"
  | "valid"
  | "invalid"
  | "failed"
  | "skipped";
type StageStatusPresentation = Readonly<{
  label: string;
  icon: string;
  tone: "upcoming" | "current" | "completed" | "needsInput" | "blocked";
}>;

const neutralStageStatus: StageStatusPresentation = {
  label: "待处理",
  icon: "○",
  tone: "upcoming",
};

const stageStatusPresentation: Readonly<
  Record<StageStatus, StageStatusPresentation>
> = {
  not_started: { label: "待处理", icon: "○", tone: "upcoming" },
  ready: { label: "可开始", icon: "○", tone: "upcoming" },
  running: { label: "处理中", icon: "●", tone: "current" },
  waiting_input: { label: "需补资料", icon: "!", tone: "needsInput" },
  waiting_review: { label: "待审核", icon: "!", tone: "needsInput" },
  valid: { label: "已完成", icon: "✓", tone: "completed" },
  invalid: {
    label: "已失效/需重新处理",
    icon: "!",
    tone: "blocked",
  },
  failed: { label: "失败", icon: "×", tone: "blocked" },
  skipped: { label: "已跳过", icon: "—", tone: "upcoming" },
};

const stageStatusFor = (status: string): StageStatusPresentation =>
  stageStatusPresentation[status as StageStatus] ?? neutralStageStatus;

const visibleStageStatus = (status: string): string =>
  stageStatusFor(status).label;

const userVisibleTaskStatus = (task: TaskOverview): string =>
  taskStatusLabels[task.taskStatus] ?? "等待处理";

const businessStageLabel = (stage: WorkbenchStage): string =>
  businessStages.find((item) => item.stage === stage)?.label ??
  (stage === "human_review" ? "人工审核" : internalStageLabels[stage]);

const stateForStage = (
  task: TaskOverview,
  stage: WorkbenchStage,
): Readonly<{ label: string; icon: string; tone: string }> => {
  const summary = task.stages.find((item) => item.stage === stage);
  const presentation = stageStatusFor(summary?.status ?? "");
  if (task.currentStage !== stage || presentation.label === "处理中") {
    return presentation;
  }
  return {
    ...presentation,
    label: `当前 · ${presentation.label}`,
    icon: "●",
    tone: "current",
  };
};

const linkSearch = (
  search: string,
  panel: WorkbenchPanel,
  stage: WorkbenchStage,
): string => {
  const params = new URLSearchParams(search);
  params.delete("panel");
  params.delete("stage");
  params.set("panel", panel);
  params.set("stage", stage);
  return `?${params.toString()}`;
};

function ReferenceDetails({ task }: Readonly<{ task: TaskOverview }>) {
  const references = [
    task.activeRunId === null ? null : ["Active Run", task.activeRunId],
    task.latestRunId === null ? null : ["Latest Run", task.latestRunId],
    task.needsInputRequest === null
      ? null
      : [
          "Needs Input",
          `${task.needsInputRequest.resourceId} · revision ${task.needsInputRequest.revision}`,
        ],
    task.reviewPackage === null
      ? null
      : [
          "Review Package",
          `${task.reviewPackage.reviewPackageId} · version ${task.reviewPackage.packageVersion}`,
        ],
    task.approvedStrategy === null
      ? null
      : [
          "Approved Strategy",
          `${task.approvedStrategy.resourceKind}: ${task.approvedStrategy.resourceVersionId} · version ${task.approvedStrategy.versionNumber}`,
        ],
    task.marketingBrief === null
      ? null
      : [
          "Marketing Brief",
          `${task.marketingBrief.resourceKind}: ${task.marketingBrief.resourceVersionId} · version ${task.marketingBrief.versionNumber}`,
        ],
    task.xiaohongshuBrief === null
      ? null
      : [
          "Xiaohongshu Brief",
          `${task.xiaohongshuBrief.resourceKind}: ${task.xiaohongshuBrief.resourceVersionId} · version ${task.xiaohongshuBrief.versionNumber}`,
        ],
  ].filter((reference): reference is [string, string] => reference !== null);

  if (references.length === 0) return null;

  return (
    <section className={styles.references}>
      <h2 id="task-references-heading">Current references</h2>
      <dl className={styles.referenceList}>
        {references.map(([label, value]) => (
          <div key={label}>
            <dt>{label}</dt>
            <dd>{value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

function PrimaryInputPanel({
  primaryInput,
  primaryInputLoading = false,
  primaryInputError = null,
  retryPrimaryInput,
  savePrimaryInput,
  generateResult,
}: Readonly<
  Pick<
    TaskWorkbenchProps,
    | "primaryInput"
    | "primaryInputLoading"
    | "primaryInputError"
    | "retryPrimaryInput"
    | "savePrimaryInput"
    | "generateResult"
  >
>) {
  const [kind, setKind] = useState<TaskPrimaryInputKind>("pasted_text");
  const [fileName, setFileName] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [savedPreview, setSavedPreview] = useState<TaskPrimaryInput | null>(
    null,
  );
  const [message, setMessage] = useState<string | null>(null);
  const inputIdentity =
    primaryInput === undefined
      ? "loading"
      : primaryInput === null
        ? "empty"
        : `${primaryInput.inputRevision}:${primaryInput.updatedAt}`;

  useEffect(() => {
    if (primaryInput === undefined) return;
    if (primaryInput === null) {
      setKind("pasted_text");
      setFileName(null);
      setContent("");
      setSavedPreview(null);
      return;
    }
    setKind(primaryInput.inputKind);
    setFileName(primaryInput.fileName);
    setContent(primaryInput.content);
    setSavedPreview(primaryInput);
  }, [inputIdentity, primaryInput]);

  if (
    savePrimaryInput === undefined &&
    !primaryInputLoading &&
    primaryInputError === null
  ) {
    return null;
  }

  const inputBlocked = primaryInputLoading || primaryInput === undefined;

  if (primaryInputError !== null) {
    return (
      <section
        className={styles.primaryInput}
        aria-labelledby="primary-input-heading"
      >
        <h2 id="primary-input-heading">商品资料</h2>
        <p className={styles.inputHint}>
          粘贴商品上下文，或选择一个 UTF-8 .txt/.md
          文件。资料只保存在当前任务中。
        </p>
        <p role="alert" aria-live="polite">
          {primaryInputError}
        </p>
        {retryPrimaryInput !== undefined ? (
          <button type="button" onClick={retryPrimaryInput}>
            重试读取商品资料
          </button>
        ) : null}
      </section>
    );
  }

  const onFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file === undefined) return;
    const displayName = file.name.split(/[\\/]/u).pop() ?? file.name;
    const suffix = displayName
      .slice(displayName.lastIndexOf("."))
      .toLowerCase();
    if (suffix !== ".txt" && suffix !== ".md") {
      setMessage("Choose one .txt or .md file.");
      return;
    }
    try {
      const text = new TextDecoder("utf-8", { fatal: true }).decode(
        await file.arrayBuffer(),
      );
      setKind(suffix === ".md" ? "markdown_file" : "text_file");
      setFileName(displayName);
      setContent(text);
      setMessage(`Loaded ${displayName}. Review it, then save the input.`);
    } catch {
      setMessage("The selected file could not be read as UTF-8 text.");
    }
  };

  const save = async () => {
    setMessage(null);
    let draft: TaskPrimaryInputDraft;
    try {
      draft = normalizePrimaryInput({ inputKind: kind, fileName, content });
    } catch (error) {
      setMessage(
        error instanceof Error ? error.message : "Primary input is invalid.",
      );
      return;
    }
    if (savePrimaryInput === undefined || inputBlocked) return;
    setSaving(true);
    try {
      const saved = await savePrimaryInput(draft);
      setSavedPreview(saved);
      setMessage(`Saved revision ${saved.inputRevision}.`);
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "The primary input could not be saved. Try again.",
      );
    } finally {
      setSaving(false);
    }
  };

  const generate = async () => {
    if (generateResult === undefined || savedPreview === null || generating) {
      return;
    }
    setMessage(null);
    setGenerating(true);
    try {
      const result = await generateResult();
      setMessage(
        result.status === "awaiting_review"
          ? `Generated result revision ${result.resultRevision}.`
          : "The input is insufficient to generate all candidate results.",
      );
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "The result could not be generated. Try again.",
      );
    } finally {
      setGenerating(false);
    }
  };

  return (
    <section
      className={styles.primaryInput}
      aria-labelledby="primary-input-heading"
    >
      <h2 id="primary-input-heading">商品资料</h2>
      <p className={styles.inputHint}>
        粘贴商品上下文，或选择一个 UTF-8 .txt/.md 文件。资料只保存在当前任务中。
      </p>
      {primaryInputLoading ? (
        <p role="status" aria-live="polite">
          Loading saved input…
        </p>
      ) : null}
      <fieldset className={styles.inputChoices}>
        <legend>资料来源</legend>
        <label>
          <input
            type="radio"
            name="primary-input-kind"
            checked={kind === "pasted_text"}
            disabled={inputBlocked || saving}
            onChange={() => {
              setKind("pasted_text");
              setFileName(null);
            }}
          />
          粘贴文本
        </label>
        <label>
          <input
            type="file"
            disabled={inputBlocked || saving}
            accept=".txt,.md,text/plain,text/markdown"
            onChange={onFileChange}
            aria-label="选择文本或 Markdown 文件"
          />
        </label>
      </fieldset>
      <label className={styles.inputField} htmlFor="primary-input-content">
        {fileName === null ? "粘贴文本" : `文件：${fileName}`}
        <textarea
          id="primary-input-content"
          value={content}
          disabled={inputBlocked || saving}
          onChange={(event) => setContent(event.target.value)}
          rows={10}
          required
        />
      </label>
      <button
        type="button"
        onClick={() => void save()}
        disabled={inputBlocked || saving}
      >
        {saving ? "保存中…" : "保存商品资料"}
      </button>
      {generateResult !== undefined && savedPreview !== null ? (
        <button
          type="button"
          onClick={() => void generate()}
          disabled={inputBlocked || saving || generating}
        >
          {generating ? "生成中…" : "生成结果"}
        </button>
      ) : null}
      {message !== null ? (
        <p className={styles.inputStatus} role="status" aria-live="polite">
          {message}
        </p>
      ) : null}
      {savedPreview !== null ? (
        <section
          className={styles.preview}
          aria-labelledby="saved-input-heading"
        >
          <h3 id="saved-input-heading">已保存资料预览</h3>
          <p>
            Revision {savedPreview.inputRevision} · {savedPreview.inputKind} ·{" "}
            {savedPreview.byteCount} bytes
          </p>
          <pre>{savedPreview.content}</pre>
          <time dateTime={savedPreview.updatedAt}>
            更新于 {savedPreview.updatedAt}
          </time>
        </section>
      ) : null}
    </section>
  );
}

const resultCandidates: Readonly<
  Readonly<{
    key: keyof Pick<
      TaskCurrentResult,
      | "productIntake"
      | "customerInsight"
      | "productPositioning"
      | "marketingBrief"
      | "xiaohongshuBrief"
    >;
    label: string;
  }>[]
> = [
  { key: "productIntake", label: "Product Intake" },
  { key: "customerInsight", label: "Customer Insight" },
  { key: "productPositioning", label: "Product Positioning" },
  { key: "marketingBrief", label: "Marketing Brief" },
  { key: "xiaohongshuBrief", label: "Xiaohongshu Brief" },
];

function ResultPanel({
  result,
  loading = false,
  error = null,
  retry,
  exportBrief,
}: Readonly<{
  result?: TaskCurrentResult | null;
  loading?: boolean;
  error?: string | null;
  retry?: () => void;
  exportBrief?: (briefKind: ExportBriefKind) => Promise<ExportDownload>;
}>) {
  const [exporting, setExporting] = useState<ExportBriefKind | null>(null);
  const [exportMessage, setExportMessage] = useState<string | null>(null);
  if (loading || result === undefined) {
    return (
      <p className={styles.neutral} role="status" aria-live="polite">
        Loading current result…
      </p>
    );
  }
  if (error !== null && error !== undefined) {
    return (
      <section className={styles.resultPanel} aria-labelledby="result-heading">
        <h2 id="result-heading">Current result</h2>
        <p role="alert">{error}</p>
        {retry !== undefined ? (
          <button type="button" onClick={retry}>
            Retry current result
          </button>
        ) : null}
      </section>
    );
  }
  if (result === null) {
    return (
      <section className={styles.resultPanel} aria-labelledby="result-heading">
        <h2 id="result-heading">Current result</h2>
        <p>
          No current result yet. Save primary input, then generate a result.
        </p>
      </section>
    );
  }

  const download = async (briefKind: ExportBriefKind) => {
    if (exportBrief === undefined) return;
    setExporting(briefKind);
    setExportMessage(null);
    try {
      const download = await exportBrief(briefKind);
      setExportMessage(
        `Export snapshot ${download.snapshot.exportSnapshotId} is ready.`,
      );
    } catch (value) {
      setExportMessage(
        value instanceof Error ? value.message : "Export failed.",
      );
    } finally {
      setExporting(null);
    }
  };

  return (
    <section className={styles.resultPanel} aria-labelledby="result-heading">
      <h2 id="result-heading">Current result</h2>
      <p>
        Revision {result.resultRevision} · input revision {result.inputRevision}{" "}
        · <strong>{result.status}</strong>
      </p>
      <time dateTime={result.generatedAt}>Generated {result.generatedAt}</time>
      {result.status === "insufficient_input" ? (
        <div className={styles.resultWarning} role="status">
          <h3>More input required</h3>
          <ul>
            {result.missingInformation.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ) : result.status === "confirmed" ? (
        <>
          <div className={styles.resultCandidates}>
            {resultCandidates.map(({ key, label }) => (
              <article key={key}>
                <h3>{label}</h3>
                <pre>{JSON.stringify(result[key], null, 2)}</pre>
              </article>
            ))}
          </div>
          {result.confirmation !== null ? (
            <p>
              Confirmed {result.confirmation.confirmedAt} · Marketing version{" "}
              {result.confirmation.marketingBriefVersion.resourceVersionId} ·
              Xiaohongshu version{" "}
              {result.confirmation.xiaohongshuBriefVersion.resourceVersionId}
            </p>
          ) : null}
          {exportBrief !== undefined ? (
            <div className={styles.downloads}>
              <button
                type="button"
                disabled={exporting !== null}
                onClick={() => void download("marketing")}
              >
                {exporting === "marketing"
                  ? "Preparing…"
                  : "Download Marketing Markdown"}
              </button>
              <button
                type="button"
                disabled={exporting !== null}
                onClick={() => void download("xiaohongshu")}
              >
                {exporting === "xiaohongshu"
                  ? "Preparing…"
                  : "Download Xiaohongshu Markdown"}
              </button>
              {exportMessage !== null ? (
                <p role="status">{exportMessage}</p>
              ) : null}
            </div>
          ) : null}
        </>
      ) : (
        <div className={styles.resultCandidates}>
          {resultCandidates.map(({ key, label }) => {
            const candidate = result[key];
            return (
              <article key={key}>
                <h3>{label}</h3>
                <pre>{JSON.stringify(candidate, null, 2)}</pre>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}

function ReviewPanel({
  result,
  confirmCurrentResult,
}: Readonly<{
  result?: TaskCurrentResult | null;
  confirmCurrentResult?: (
    marketingCoreMessage: string,
    xiaohongshuTitleDirection: string,
  ) => Promise<TaskCurrentResult>;
}>) {
  const record = (value: unknown): Record<string, unknown> | null =>
    typeof value === "object" && value !== null && !Array.isArray(value)
      ? (value as Record<string, unknown>)
      : null;
  const marketing = record(result?.marketingBrief?.brief_candidate);
  const xiaohongshu = record(
    result?.xiaohongshuBrief?.xiaohongshu_brief_candidate,
  );
  const marketingMessageGroup = record(marketing?.message_architecture);
  const xhsStructure = record(xiaohongshu?.creative_structure_directions);
  const constraints = record(marketing?.constraints_and_honesty);
  const platformConstraints = record(
    xiaohongshu?.evidence_and_platform_constraints,
  );
  const strings = (value: unknown): string[] =>
    Array.isArray(value)
      ? value.filter(
          (item): item is string =>
            typeof item === "string" && item.trim() !== "",
        )
      : [];
  const evidenceLimitations = [
    ...strings(constraints?.evidence_limitations),
    ...strings(platformConstraints?.evidence_limitations),
  ];
  const risks = [
    ...strings(constraints?.risk_notes),
    ...strings(platformConstraints?.platform_risk_notes),
  ];
  const titleDirections = Array.isArray(xhsStructure?.title_directions)
    ? xhsStructure.title_directions
    : [];
  const firstTitleDirection = record(titleDirections[0]);
  const marketingMessage =
    typeof marketingMessageGroup?.core_message === "string"
      ? marketingMessageGroup.core_message
      : "";
  const titleDirection =
    typeof firstTitleDirection?.title_direction === "string"
      ? firstTitleDirection.title_direction
      : "";
  const [message, setMessage] = useState(marketingMessage);
  const [title, setTitle] = useState(titleDirection);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  useEffect(() => {
    setMessage(marketingMessage);
    setTitle(titleDirection);
  }, [marketingMessage, titleDirection]);
  if (
    result === undefined ||
    result === null ||
    result.status !== "awaiting_review"
  )
    return null;
  const confirm = async () => {
    if (
      confirmCurrentResult === undefined ||
      message.trim() === "" ||
      title.trim() === ""
    ) {
      setStatus("Enter both bounded corrections before confirming.");
      return;
    }
    setSaving(true);
    setStatus(null);
    try {
      await confirmCurrentResult(message.trim(), title.trim());
      setStatus("Current result confirmed.");
    } catch (value) {
      setStatus(
        value instanceof Error ? value.message : "Confirmation failed.",
      );
    } finally {
      setSaving(false);
    }
  };
  return (
    <section className={styles.reviewPanel} aria-labelledby="review-heading">
      <h2 id="review-heading">Review current result</h2>
      <p>
        Review the bounded positioning, Marketing Brief, and Xiaohongshu Brief
        candidates before confirming.
      </p>
      <div className={styles.reviewCandidates}>
        <article>
          <h3>Positioning candidate</h3>
          <pre>{JSON.stringify(result.productPositioning, null, 2)}</pre>
        </article>
        <article>
          <h3>Marketing Brief candidate</h3>
          <pre>{JSON.stringify(result.marketingBrief, null, 2)}</pre>
        </article>
        <article>
          <h3>Xiaohongshu Brief candidate</h3>
          <pre>{JSON.stringify(result.xiaohongshuBrief, null, 2)}</pre>
        </article>
      </div>
      {evidenceLimitations.length > 0 ? (
        <section>
          <h3>Evidence limitations</h3>
          <ul>
            {evidenceLimitations.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        </section>
      ) : null}
      {risks.length > 0 ? (
        <section>
          <h3>Risks</h3>
          <ul>
            {risks.map((item, index) => (
              <li key={`${item}-${index}`}>{item}</li>
            ))}
          </ul>
        </section>
      ) : null}
      <label className={styles.inputField} htmlFor="review-marketing-message">
        Marketing core message
        <textarea
          id="review-marketing-message"
          maxLength={4096}
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          rows={3}
        />
      </label>
      <label className={styles.inputField} htmlFor="review-xiaohongshu-title">
        Xiaohongshu title direction
        <textarea
          id="review-xiaohongshu-title"
          maxLength={4096}
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          rows={3}
        />
      </label>
      <button
        type="button"
        disabled={saving || confirmCurrentResult === undefined}
        onClick={() => void confirm()}
      >
        {saving ? "Confirming…" : "Confirm current result"}
      </button>
      {status !== null ? <p role="status">{status}</p> : null}
    </section>
  );
}

export function TaskWorkbench({
  task,
  primaryInput,
  primaryInputLoading,
  primaryInputError,
  retryPrimaryInput,
  savePrimaryInput,
  currentResult,
  currentResultLoading,
  currentResultError,
  retryCurrentResult,
  generateResult,
  confirmCurrentResult,
  exportBrief,
}: TaskWorkbenchProps) {
  const routerLocation = useLocation();
  const navigate = useNavigate();
  const [isNarrowContext, setIsNarrowContext] = useState(false);
  const [contextRailOpen, setContextRailOpen] = useState(true);
  const contextRailDetailsRef = useRef<HTMLDetailsElement>(null);
  const mode = deriveWorkbenchMode(task);
  const workbenchLocation = deriveWorkbenchLocation(
    task,
    routerLocation.search,
  );
  const attemptedReplacement = useRef<string | null>(null);

  useEffect(() => {
    if (typeof globalThis.matchMedia !== "function") return;
    const query = globalThis.matchMedia("(max-width: 64rem)");
    const update = () => {
      const narrow = query.matches;
      const open = !narrow;
      setIsNarrowContext(narrow);
      setContextRailOpen(open);
      if (contextRailDetailsRef.current !== null) {
        contextRailDetailsRef.current.open = open;
      }
    };
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  useEffect(() => {
    if (contextRailDetailsRef.current !== null) {
      contextRailDetailsRef.current.open = contextRailOpen;
    }
  }, [contextRailOpen]);

  useEffect(() => {
    const { replaceSearch } = workbenchLocation;
    if (replaceSearch === null) {
      attemptedReplacement.current = null;
      return;
    }

    const attemptKey = `${routerLocation.pathname}\u0000${routerLocation.search}\u0000${replaceSearch}`;
    if (
      routerLocation.search !== replaceSearch &&
      attemptedReplacement.current !== attemptKey
    ) {
      attemptedReplacement.current = attemptKey;
      navigate(
        { pathname: routerLocation.pathname, search: replaceSearch },
        { replace: true },
      );
    }
  }, [
    navigate,
    routerLocation.pathname,
    routerLocation.search,
    workbenchLocation,
  ]);

  const selectedPanel = workbenchLocation.panel;
  const selectedStage = workbenchLocation.stage;
  const selectedSearch = (panel: WorkbenchPanel, stage = selectedStage) =>
    linkSearch(routerLocation.search, panel, stage);
  const generateAndShowResults = async (): Promise<TaskCurrentResult> => {
    if (generateResult === undefined) {
      throw new Error("Result generation is unavailable.");
    }
    const result = await generateResult();
    navigate({
      pathname: routerLocation.pathname,
      search: selectedSearch("results"),
    });
    return result;
  };

  const selectedStageLabel = businessStageLabel(selectedStage);
  const modeLabel = modeLabels[mode] ?? mode;
  const activeAction =
    selectedPanel === "intake" && savePrimaryInput !== undefined
      ? "保存或更新商品资料"
      : neutralPanelMessage[selectedPanel];

  const contextRail = (
    <aside className={styles.contextRail} aria-label="上下文与执行信息">
      <details
        ref={contextRailDetailsRef}
        onToggle={(event) => setContextRailOpen(event.currentTarget.open)}
      >
        <summary>上下文与执行信息</summary>
        <div className={styles.contextRailBody}>
          <section className={styles.contextBlock}>
            <h2>当前任务</h2>
            <dl className={styles.details}>
              <div>
                <dt>状态</dt>
                <dd>{userVisibleTaskStatus(task)}</dd>
              </div>
              <div>
                <dt>阶段</dt>
                <dd>{selectedStageLabel}</dd>
              </div>
              <div>
                <dt>更新时间</dt>
                <dd>
                  <time dateTime={task.updatedAt}>
                    {formatTimestamp(task.updatedAt)}
                  </time>
                </dd>
              </div>
              {task.waitingReason !== null ? (
                <div>
                  <dt>等待原因</dt>
                  <dd>{task.waitingReason}</dd>
                </div>
              ) : null}
            </dl>
          </section>
          <ReferenceDetails task={task} />
          <details className={styles.technicalDetails}>
            <summary>内部阶段深链</summary>
            <nav aria-label="内部阶段深链">
              <div className={styles.linkColumn}>
                {stageCatalog.map((stage) => (
                  <Link
                    key={stage}
                    aria-current={stage === selectedStage ? "step" : undefined}
                    to={{
                      pathname: routerLocation.pathname,
                      search: selectedSearch(selectedPanel, stage),
                    }}
                  >
                    {internalStageLabels[stage]}
                  </Link>
                ))}
              </div>
            </nav>
          </details>
          <section className={styles.contextBlock}>
            <h2>业务阶段摘要</h2>
            <ol className={styles.stages} aria-label="Stage summaries">
              {businessStages.map(({ stage, label }) => {
                const summary = task.stages.find(
                  (item) => item.stage === stage,
                );
                if (summary === undefined) return null;
                return (
                  <li key={stage}>
                    <strong>{label}</strong>
                    <span>{visibleStageStatus(summary.status)}</span>
                    {summary.waitingReason ? (
                      <span>{summary.waitingReason}</span>
                    ) : null}
                    <time dateTime={summary.updatedAt}>
                      {formatTimestamp(summary.updatedAt)}
                    </time>
                  </li>
                );
              })}
            </ol>
          </section>
        </div>
      </details>
    </aside>
  );

  return (
    <section className={styles.page} aria-labelledby="task-workbench-heading">
      <header className={styles.header}>
        <div className={styles.headerTopline}>
          <p className={styles.eyebrow}>任务工作台</p>
          <Link className={styles.backLink} to="/tasks">
            返回最近任务
          </Link>
        </div>
        <div className={styles.headerRow}>
          <div className={styles.headerIdentity}>
            <p className={styles.kicker}>商品上新任务</p>
            <h1 id="task-workbench-heading">{task.taskName}</h1>
            <p className={styles.identity}>{task.productCategory}</p>
          </div>
          <div className={styles.headerStatus}>
            <span
              className={`${styles.statusBadge} ${styles[`status-${mode}`]}`}
            >
              {userVisibleTaskStatus(task)}
            </span>
            <p className={styles.saveTruth}>
              本地工作区 · 更新于{" "}
              <time dateTime={task.updatedAt}>
                {formatTimestamp(task.updatedAt)}
              </time>
            </p>
          </div>
        </div>
        <details className={styles.technicalIdentity}>
          <summary>技术详情</summary>
          <p>{`Task ID: ${task.taskId}`}</p>
          <p>
            内部状态：<code>{task.taskStatus}</code>
          </p>
        </details>
      </header>

      <nav className={styles.stageRail} aria-label="业务阶段">
        <div className={styles.stageRailHeading}>
          <div>
            <p className={styles.sectionLabel}>一条可回看的进度线</p>
            <h2>五个业务阶段</h2>
          </div>
          <p className={styles.stageCurrentLabel}>
            当前：<strong>{selectedStageLabel}</strong>
          </p>
        </div>
        <ol className={styles.stageRailList}>
          {businessStages.map(({ stage, label }) => {
            const state = stateForStage(task, stage);
            return (
              <li
                className={`${styles.stageRailItem} ${styles[`stage-${state.tone}`]}`}
                key={stage}
              >
                <Link
                  aria-current={stage === selectedStage ? "step" : undefined}
                  to={{
                    pathname: routerLocation.pathname,
                    search: selectedSearch(selectedPanel, stage),
                  }}
                >
                  <span className={styles.stageIcon} aria-hidden="true">
                    {state.icon}
                  </span>
                  <span className={styles.stageLabel}>{label}</span>
                  <span className={styles.stageState}>{state.label}</span>
                </Link>
              </li>
            );
          })}
        </ol>
      </nav>

      <div className={styles.workbenchGrid}>
        {isNarrowContext ? contextRail : null}
        <section
          className={styles.workspace}
          aria-labelledby="active-workspace-heading"
        >
          <div className={styles.workspaceHeader}>
            <div>
              <p className={styles.sectionLabel}>当前工作面</p>
              <h2 id="active-workspace-heading">当前工作区</h2>
            </div>
            <span className={styles.modeLabel}>{modeLabel}</span>
          </div>
          <p className={styles.workspaceAction}>
            当前动作：<strong>{activeAction}</strong>
          </p>

          <nav className={styles.navigation} aria-label="工作区面板">
            <h3>工作区</h3>
            <div className={styles.linkRow}>
              {panelCatalog.map((panel) => (
                <Link
                  key={panel}
                  aria-current={panel === selectedPanel ? "page" : undefined}
                  to={{
                    pathname: routerLocation.pathname,
                    search: selectedSearch(panel),
                  }}
                >
                  {panelLabels[panel]}
                </Link>
              ))}
            </div>
          </nav>

          <p className={styles.neutral} role="status" aria-live="polite">
            {selectedPanel === "intake" && savePrimaryInput !== undefined
              ? "资料已准备好，可以保存。"
              : neutralPanelMessage[selectedPanel]}
          </p>

          {selectedPanel === "intake" ? (
            <PrimaryInputPanel
              primaryInput={primaryInput}
              primaryInputLoading={primaryInputLoading}
              primaryInputError={primaryInputError}
              retryPrimaryInput={retryPrimaryInput}
              savePrimaryInput={savePrimaryInput}
              generateResult={
                generateResult === undefined
                  ? undefined
                  : generateAndShowResults
              }
            />
          ) : null}

          {selectedPanel === "results" &&
          (currentResult !== undefined ||
            currentResultLoading !== undefined ||
            currentResultError !== undefined ||
            retryCurrentResult !== undefined) ? (
            <ResultPanel
              result={currentResult}
              loading={currentResultLoading}
              error={currentResultError}
              retry={retryCurrentResult}
              exportBrief={exportBrief}
            />
          ) : null}

          {selectedPanel === "review" ? (
            <ReviewPanel
              result={currentResult}
              confirmCurrentResult={confirmCurrentResult}
            />
          ) : null}
        </section>

        {!isNarrowContext ? contextRail : null}
      </div>
    </section>
  );
}
