import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import {
  normalizePrimaryInput,
  type TaskCurrentResult,
  type TaskOverview,
  type TaskPrimaryInput,
  type TaskPrimaryInputDraft,
  type TaskPrimaryInputKind,
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
}>;

const panelLabels: Readonly<Record<WorkbenchPanel, string>> = {
  intake: "Intake",
  progress: "Progress",
  review: "Review",
  results: "Results",
  evidence: "Evidence",
};

const neutralPanelMessage: Readonly<Record<WorkbenchPanel, string>> = {
  intake: "Intake resources and actions are not implemented in this slice.",
  progress:
    "Progress and recovery resources and actions are not implemented in this slice.",
  review: "Review resources and actions are not implemented in this slice.",
  results:
    "Results and export resources and actions are not implemented in this slice.",
  evidence:
    "Evidence and context resources and actions are not implemented in this slice.",
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
        <h2 id="primary-input-heading">Primary input</h2>
        <p className={styles.inputHint}>
          Paste product context or choose one UTF-8 .txt/.md file. The saved
          input is scoped to this Task.
        </p>
        <p role="alert" aria-live="polite">
          {primaryInputError}
        </p>
        {retryPrimaryInput !== undefined ? (
          <button type="button" onClick={retryPrimaryInput}>
            Retry primary input
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
      <h2 id="primary-input-heading">Primary input</h2>
      <p className={styles.inputHint}>
        Paste product context or choose one UTF-8 .txt/.md file. The saved input
        is scoped to this Task.
      </p>
      {primaryInputLoading ? (
        <p role="status" aria-live="polite">
          Loading saved input…
        </p>
      ) : null}
      <fieldset className={styles.inputChoices}>
        <legend>Input source</legend>
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
          Paste text
        </label>
        <label>
          <input
            type="file"
            disabled={inputBlocked || saving}
            accept=".txt,.md,text/plain,text/markdown"
            onChange={onFileChange}
            aria-label="Choose a text or markdown file"
          />
        </label>
      </fieldset>
      <label className={styles.inputField} htmlFor="primary-input-content">
        {fileName === null ? "Pasted text" : `File: ${fileName}`}
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
        {saving ? "Saving…" : "Save primary input"}
      </button>
      {generateResult !== undefined && savedPreview !== null ? (
        <button
          type="button"
          onClick={() => void generate()}
          disabled={inputBlocked || saving || generating}
        >
          {generating ? "Generating…" : "Generate result"}
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
          <h3 id="saved-input-heading">Saved input preview</h3>
          <p>
            Revision {savedPreview.inputRevision} · {savedPreview.inputKind} ·{" "}
            {savedPreview.byteCount} bytes
          </p>
          <pre>{savedPreview.content}</pre>
          <time dateTime={savedPreview.updatedAt}>
            Updated {savedPreview.updatedAt}
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
}: Readonly<{
  result?: TaskCurrentResult | null;
  loading?: boolean;
  error?: string | null;
  retry?: () => void;
}>) {
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
}: TaskWorkbenchProps) {
  const routerLocation = useLocation();
  const navigate = useNavigate();
  const mode = deriveWorkbenchMode(task);
  const workbenchLocation = deriveWorkbenchLocation(
    task,
    routerLocation.search,
  );
  const attemptedReplacement = useRef<string | null>(null);

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

  return (
    <section className={styles.page} aria-labelledby="task-workbench-heading">
      <p className={styles.eyebrow}>Task workbench</p>
      <p className={styles.backLink}>
        <Link to="/tasks">Back to recent tasks</Link>
      </p>
      <h1 id="task-workbench-heading">{task.taskName}</h1>
      <p className={styles.identity}>Task ID: {task.taskId}</p>

      <dl className={styles.details}>
        <div>
          <dt>Category</dt>
          <dd>{task.productCategory}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{task.taskStatus}</dd>
        </div>
        <div>
          <dt>Current stage or waiting reason</dt>
          <dd>{task.currentStage ?? task.waitingReason ?? "Not started"}</dd>
        </div>
        <div>
          <dt>Updated</dt>
          <dd>
            <time dateTime={task.updatedAt}>{task.updatedAt}</time>
          </dd>
        </div>
      </dl>

      <section className={styles.workspace}>
        <h2 id="workspace-heading">Current workspace: {mode}</h2>
        <p>
          Current panel: <strong>{selectedPanel}</strong>
        </p>
        <p>
          Current stage: <strong>{selectedStage}</strong>
        </p>
      </section>

      <nav className={styles.navigation} aria-label="Task panels">
        <h2>Panels</h2>
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

      <nav className={styles.navigation} aria-label="Task stages">
        <h2>Stages</h2>
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
              {stage}
            </Link>
          ))}
        </div>
      </nav>

      <p className={styles.neutral} role="status" aria-live="polite">
        {selectedPanel === "intake" && savePrimaryInput !== undefined
          ? "Intake input is ready to save."
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
            generateResult === undefined ? undefined : generateAndShowResults
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
        />
      ) : null}

      <section>
        <h2 id="stage-summaries-heading">Stage summaries</h2>
        <ol className={styles.stages} aria-label="Stage summaries">
          {task.stages.map((stage) => (
            <li key={stage.stage}>
              <strong>{stage.stage}</strong>
              <span>{stage.status}</span>
              {stage.waitingReason ? <span>{stage.waitingReason}</span> : null}
              <time dateTime={stage.updatedAt}>{stage.updatedAt}</time>
            </li>
          ))}
        </ol>
      </section>

      <ReferenceDetails task={task} />
    </section>
  );
}
