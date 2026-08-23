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
import { projectResult, renderMarkdownProjection } from "./resultProjection";
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
  const [showTechnical, setShowTechnical] = useState(false);
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
      <h2 id="task-references-heading">当前引用</h2>
      <p className={styles.referenceSummary}>
        来源与版本信息已保留在当前任务中。
      </p>
      <details
        className={styles.technicalDetails}
        onToggle={(event) => setShowTechnical(event.currentTarget.open)}
      >
        <summary>技术详情</summary>
        {showTechnical ? (
          <dl className={styles.referenceList}>
            {references.map(([label, value]) => (
              <div key={label}>
                <dt>{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        ) : null}
      </details>
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

function RunningPanel({
  task,
  selectedStage,
}: Readonly<{ task: TaskOverview; selectedStage: WorkbenchStage }>) {
  const [showTechnical, setShowTechnical] = useState(false);
  const stage = task.stages.find((item) => item.stage === selectedStage);
  return (
    <section className={styles.runningPanel} aria-labelledby="running-heading">
      <div className={styles.stateLead}>
        <div>
          <p className={styles.sectionLabel}>执行中</p>
          <h2 id="running-heading">正在处理</h2>
        </div>
        <span className={styles.stateMarker}>当前阶段</span>
      </div>
      <p className={styles.stateIntro}>
        系统正在处理这项商品上新任务。完成后会回到这里显示下一步，不展示虚构的百分比或完成时间。
      </p>
      <div className={styles.runningGrid}>
        <section
          className={styles.semanticGroup}
          aria-labelledby="running-stage-heading"
        >
          <p className={styles.groupLabel}>当前阶段</p>
          <h3 id="running-stage-heading">
            {businessStageLabel(selectedStage)}
          </h3>
          <p>{stage?.waitingReason ?? "正在整理已提供的资料和上下文。"}</p>
        </section>
        <section
          className={styles.semanticGroup}
          aria-labelledby="running-context-heading"
        >
          <p className={styles.groupLabel}>已知上下文</p>
          <h3 id="running-context-heading">{task.productCategory}</h3>
          <p>任务：{task.taskName}</p>
        </section>
      </div>
      <section
        className={styles.nextAction}
        aria-labelledby="running-next-heading"
      >
        <h3 id="running-next-heading">下一步</h3>
        <p className={styles.nextActionTitle}>等待当前阶段完成</p>
        <p>状态更新后继续查看结果或审核材料。</p>
      </section>
      <details
        className={styles.technicalDetails}
        onToggle={(event) => setShowTechnical(event.currentTarget.open)}
      >
        <summary>技术详情</summary>
        {showTechnical ? (
          <>
            {task.activeRunId !== null ? (
              <p>Active Run：{task.activeRunId}</p>
            ) : null}
            <p>任务版本：{task.revision}</p>
          </>
        ) : null}
      </details>
    </section>
  );
}

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
  const [activeBrief, setActiveBrief] = useState<ExportBriefKind>("marketing");
  const [showPreview, setShowPreview] = useState(false);
  const [showTechnical, setShowTechnical] = useState(false);
  const resultHeadingRef = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    resultHeadingRef.current?.focus();
  }, [error, loading, result]);
  if (loading || result === undefined) {
    return (
      <p className={styles.neutral} role="status" aria-live="polite">
        正在读取当前结果…
      </p>
    );
  }
  if (error !== null && error !== undefined) {
    return (
      <section className={styles.resultPanel} aria-labelledby="result-heading">
        <h2 id="result-heading" ref={resultHeadingRef} tabIndex={-1}>
          结果暂时不可用
        </h2>
        <p role="alert">{error}</p>
        {retry !== undefined ? (
          <button type="button" onClick={retry}>
            重试读取结果
          </button>
        ) : null}
      </section>
    );
  }
  if (result === null) {
    return (
      <section className={styles.resultPanel} aria-labelledby="result-heading">
        <h2 id="result-heading" ref={resultHeadingRef} tabIndex={-1}>
          还没有当前结果
        </h2>
        <p>先保存商品资料，再生成结果。</p>
      </section>
    );
  }

  const download = async (briefKind: ExportBriefKind) => {
    if (exportBrief === undefined) return;
    setExporting(briefKind);
    setExportMessage(null);
    try {
      const download = await exportBrief(briefKind);
      if (download.content.trim() === "") {
        setExportMessage("导出快照已记录，但没有可下载内容，未生成文件。");
      } else {
        setExportMessage(
          `${briefKind === "marketing" ? "营销" : "小红书"} Markdown 已生成并下载。`,
        );
      }
    } catch (value) {
      setExportMessage(
        value instanceof Error ? value.message : "导出失败，请稍后重试。",
      );
    } finally {
      setExporting(null);
    }
  };

  if (result.status === "insufficient_input") {
    return (
      <section className={styles.resultPanel} aria-labelledby="result-heading">
        <h2 id="result-heading" ref={resultHeadingRef} tabIndex={-1}>
          需要补充资料
        </h2>
        <p>当前资料不足以形成可审核的 Brief。下面列出真实缺口。</p>
        <ul className={styles.resultList}>
          {result.missingInformation.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
    );
  }

  const projection = projectResult(result);
  const markdown = renderMarkdownProjection(result, activeBrief);
  const briefKinds: readonly ExportBriefKind[] = ["marketing", "xiaohongshu"];
  const selectBrief = (briefKind: ExportBriefKind) => {
    setActiveBrief(briefKind);
    setShowPreview(false);
  };
  const renderBriefPanel = (kind: ExportBriefKind) => {
    const selected = activeBrief === kind;
    const title = kind === "marketing" ? "营销 Brief" : "小红书 Brief";
    const content =
      kind === "marketing"
        ? projection.marketing.coreMessage
        : projection.xiaohongshu.titleDirection;
    const primaryMessage =
      kind === "marketing" ? projection.marketing.primaryMessage : null;
    const secondaryBenefits =
      kind === "marketing"
        ? projection.marketing.secondaryBenefits
        : projection.xiaohongshu.messagePriority;
    return (
      <section
        key={kind}
        id={`${kind}-brief-panel`}
        role="tabpanel"
        aria-labelledby={`${kind}-brief-tab`}
        aria-hidden={!selected}
        hidden={!selected}
        className={styles.briefPanel}
      >
        <div className={styles.briefPanelHeading}>
          <h3>{title}</h3>
          {content !== null ? (
            <p>{content}</p>
          ) : (
            <p>当前结果没有该 Brief 的核心信息。</p>
          )}
        </div>
        {primaryMessage !== null ? <p>{primaryMessage}</p> : null}
        {secondaryBenefits.length > 0 ? (
          <ul>
            {secondaryBenefits.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        ) : null}
      </section>
    );
  };

  return (
    <section className={styles.resultPanel} aria-labelledby="result-heading">
      <div className={styles.stateLead}>
        <div>
          <p className={styles.sectionLabel}>结果工作区</p>
          <h2 id="result-heading" ref={resultHeadingRef} tabIndex={-1}>
            结果已就绪
          </h2>
        </div>
        <span className={styles.stateMarker}>
          {result.status === "confirmed" ? "已确认" : "待审核"}
        </span>
      </div>
      <p className={styles.resultIntro}>
        先看定位、受众、证据与限制，再选择要使用的 Brief。
      </p>
      <div className={styles.resultSummary}>
        <section
          className={styles.summaryGroup}
          aria-labelledby="result-positioning-heading"
        >
          <h3 id="result-positioning-heading">定位摘要</h3>
          <p className={styles.summaryValue}>
            {projection.positioningTitle ?? "定位仍待确认"}
          </p>
          {projection.positioningSummary !== null ? (
            <p>{projection.positioningSummary}</p>
          ) : null}
        </section>
        <section
          className={styles.summaryGroup}
          aria-labelledby="result-audience-heading"
        >
          <h3 id="result-audience-heading">目标用户</h3>
          <p className={styles.summaryValue}>
            {projection.audience ?? "资料未提供"}
          </p>
          {projection.audienceContext.length > 0 ? (
            <ul>
              {projection.audienceContext.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : null}
        </section>
        <section
          className={styles.summaryGroup}
          aria-labelledby="result-proof-heading"
        >
          <h3 id="result-proof-heading">Proof Points / 证据</h3>
          <p className={styles.summaryValue}>资料中实际支持的要点</p>
          {projection.proofPoints.length > 0 ? (
            <ul>
              {projection.proofPoints.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p>当前结果没有可展示的证据要点。</p>
          )}
        </section>
        <section
          className={styles.summaryGroup}
          aria-labelledby="result-risks-heading"
        >
          <h3 id="result-risks-heading">风险与限制</h3>
          <p className={styles.summaryValue}>保持事实边界</p>
          {projection.evidenceLimitations.length > 0 ||
          projection.risks.length > 0 ? (
            <ul>
              {[...projection.evidenceLimitations, ...projection.risks].map(
                (item) => (
                  <li key={item}>{item}</li>
                ),
              )}
            </ul>
          ) : (
            <p>当前结果没有额外限制说明。</p>
          )}
        </section>
        <section
          className={styles.summaryGroup}
          aria-labelledby="result-next-heading"
        >
          <h3 id="result-next-heading">下一步</h3>
          <p className={styles.summaryValue}>
            {result.status === "confirmed"
              ? "使用当前确认版本"
              : "完成人工审核"}
          </p>
          {projection.nextSteps.length > 0 ? (
            <ul>
              {projection.nextSteps.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p>确认后可分别导出两个 Brief。</p>
          )}
        </section>
      </div>

      <div className={styles.resultBriefArea}>
        <div className={styles.tabsHeader}>
          <p className={styles.groupLabel}>Brief 视图</p>
          <div
            className={styles.resultTabs}
            role="tablist"
            aria-label="结果视图"
          >
            {briefKinds.map((kind) => {
              const label =
                kind === "marketing" ? "营销 Brief" : "小红书 Brief";
              const selected = activeBrief === kind;
              return (
                <button
                  key={kind}
                  type="button"
                  role="tab"
                  id={`${kind}-brief-tab`}
                  aria-selected={selected}
                  aria-controls={`${kind}-brief-panel`}
                  tabIndex={selected ? 0 : -1}
                  className={selected ? styles.tabActive : styles.tab}
                  onClick={() => {
                    selectBrief(kind);
                  }}
                  onKeyDown={(event) => {
                    const direction =
                      event.key === "ArrowRight" || event.key === "ArrowDown"
                        ? 1
                        : event.key === "ArrowLeft" || event.key === "ArrowUp"
                          ? -1
                          : event.key === "Home"
                            ? -Infinity
                            : event.key === "End"
                              ? Infinity
                              : 0;
                    if (direction === 0) return;
                    event.preventDefault();
                    const currentIndex = briefKinds.indexOf(kind);
                    const nextIndex =
                      direction === Infinity
                        ? briefKinds.length - 1
                        : direction === -Infinity
                          ? 0
                          : (currentIndex + direction + briefKinds.length) %
                            briefKinds.length;
                    const nextBrief = briefKinds[nextIndex] ?? "marketing";
                    selectBrief(nextBrief);
                    event.currentTarget.parentElement
                      ?.querySelectorAll<HTMLButtonElement>('[role="tab"]')
                      .item(nextIndex)
                      ?.focus();
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>
        {briefKinds.map(renderBriefPanel)}
        <div className={styles.resultActions}>
          <button type="button" onClick={() => setShowPreview((open) => !open)}>
            {showPreview ? "收起 Markdown 预览" : "预览 Markdown"}
          </button>
          {exportBrief !== undefined && result.status === "confirmed" ? (
            <>
              <button
                type="button"
                disabled={exporting !== null}
                onClick={() => void download("marketing")}
              >
                {exporting === "marketing" ? "导出中…" : "导出营销 Markdown"}
              </button>
              <button
                type="button"
                disabled={exporting !== null}
                onClick={() => void download("xiaohongshu")}
              >
                {exporting === "xiaohongshu"
                  ? "导出中…"
                  : "导出小红书 Markdown"}
              </button>
            </>
          ) : null}
        </div>
        {showPreview ? (
          <section
            className={styles.markdownPreview}
            aria-label="Markdown 预览"
          >
            <h3>Markdown 预览</h3>
            <pre>{markdown}</pre>
          </section>
        ) : null}
        {exportMessage !== null ? (
          <p className={styles.exportMessage} role="status">
            {exportMessage}
          </p>
        ) : null}
      </div>
      <details
        className={styles.technicalDetails}
        onToggle={(event) => setShowTechnical(event.currentTarget.open)}
      >
        <summary>技术细节</summary>
        {showTechnical ? (
          <>
            <p>
              结果版本：{result.resultRevision} · 输入版本：
              {result.inputRevision}
            </p>
            <time dateTime={result.generatedAt}>
              生成于 {formatTimestamp(result.generatedAt)}
            </time>
            <pre>
              {JSON.stringify(
                {
                  productIntake: result.productIntake,
                  customerInsight: result.customerInsight,
                  productPositioning: result.productPositioning,
                  marketingBrief: result.marketingBrief,
                  xiaohongshuBrief: result.xiaohongshuBrief,
                },
                null,
                2,
              )}
            </pre>
          </>
        ) : null}
      </details>
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
  const projection =
    result === undefined || result === null ? null : projectResult(result);
  const marketingMessage = projection?.marketing.coreMessage ?? "";
  const titleDirection = projection?.xiaohongshu.titleDirection ?? "";
  const [message, setMessage] = useState(marketingMessage);
  const [title, setTitle] = useState(titleDirection);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [showTechnical, setShowTechnical] = useState(false);
  useEffect(() => {
    setMessage(marketingMessage);
    setTitle(titleDirection);
  }, [marketingMessage, titleDirection]);
  if (
    result === undefined ||
    result === null ||
    result.status !== "awaiting_review" ||
    projection === null
  )
    return null;
  const confirm = async () => {
    if (
      confirmCurrentResult === undefined ||
      message.trim() === "" ||
      title.trim() === ""
    ) {
      setStatus("请填写两项限定修改后再确认。");
      return;
    }
    setSaving(true);
    setStatus(null);
    try {
      await confirmCurrentResult(message.trim(), title.trim());
      setStatus("结果已确认，可以查看并导出两个 Brief。");
    } catch {
      setStatus("确认失败，请重试。");
    } finally {
      setSaving(false);
    }
  };
  return (
    <section className={styles.reviewPanel} aria-labelledby="review-heading">
      <div className={styles.stateLead}>
        <div>
          <p className={styles.sectionLabel}>人工审核</p>
          <h2 id="review-heading">审核候选结果</h2>
        </div>
        <span className={styles.stateMarker}>待确认</span>
      </div>
      <p className={styles.reviewIntro}>
        按商品定位、营销 Brief、小红书 Brief 三组信息判断是否可以继续。
      </p>
      <div className={styles.reviewCandidates}>
        <section
          className={styles.semanticGroup}
          aria-labelledby="review-positioning-heading"
        >
          <h3 id="review-positioning-heading">商品定位</h3>
          <p className={styles.summaryValue}>
            {projection.positioningTitle ?? "当前没有定位标题"}
          </p>
          {projection.positioningSummary !== null ? (
            <p>{projection.positioningSummary}</p>
          ) : null}
          {projection.proofPoints.length > 0 ? (
            <ul>
              {projection.proofPoints.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : null}
        </section>
        <section
          className={styles.semanticGroup}
          aria-labelledby="review-marketing-heading"
        >
          <h3 id="review-marketing-heading">营销 Brief</h3>
          <p className={styles.summaryValue}>
            {marketingMessage || "当前没有核心信息"}
          </p>
          {projection.audience !== null ? (
            <p>目标用户：{projection.audience}</p>
          ) : null}
          {projection.marketing.primaryMessage !== null ? (
            <p>{projection.marketing.primaryMessage}</p>
          ) : null}
        </section>
        <section
          className={styles.semanticGroup}
          aria-labelledby="review-xhs-heading"
        >
          <h3 id="review-xhs-heading">小红书 Brief</h3>
          <p className={styles.summaryValue}>
            {titleDirection || "当前没有标题方向"}
          </p>
          {projection.xiaohongshu.contentAngle !== null ? (
            <p>{projection.xiaohongshu.contentAngle}</p>
          ) : null}
        </section>
      </div>
      {projection.evidenceLimitations.length > 0 ? (
        <section
          className={styles.reviewNotes}
          aria-labelledby="review-limitations-heading"
        >
          <h3 id="review-limitations-heading">证据与限制</h3>
          <ul>
            {projection.evidenceLimitations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      ) : null}
      {projection.risks.length > 0 ? (
        <section
          className={styles.reviewNotes}
          aria-labelledby="review-risks-heading"
        >
          <h3 id="review-risks-heading">风险</h3>
          <ul>
            {projection.risks.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>
      ) : null}
      <div className={styles.reviewFields}>
        <label className={styles.inputField} htmlFor="review-marketing-message">
          营销核心信息
          <textarea
            id="review-marketing-message"
            maxLength={4096}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            rows={3}
          />
        </label>
        <label className={styles.inputField} htmlFor="review-xiaohongshu-title">
          小红书标题方向
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
          {saving ? "确认中…" : "确认并生成结果"}
        </button>
      </div>
      {status !== null ? <p role="status">{status}</p> : null}
      <details
        className={styles.technicalDetails}
        onToggle={(event) => setShowTechnical(event.currentTarget.open)}
      >
        <summary>技术细节</summary>
        {showTechnical ? (
          <pre>
            {JSON.stringify(
              {
                productPositioning: result.productPositioning,
                marketingBrief: result.marketingBrief,
                xiaohongshuBrief: result.xiaohongshuBrief,
              },
              null,
              2,
            )}
          </pre>
        ) : null}
      </details>
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

          {selectedPanel === "progress" && mode === "running" ? (
            <RunningPanel task={task} selectedStage={selectedStage} />
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
