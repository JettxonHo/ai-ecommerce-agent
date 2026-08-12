import { useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router";
import type { TaskOverview } from "../gateway";
import {
  deriveWorkbenchLocation,
  deriveWorkbenchMode,
  panelCatalog,
  stageCatalog,
  type WorkbenchPanel,
  type WorkbenchStage,
} from "./projection";
import styles from "./TaskWorkbench.module.css";

type TaskWorkbenchProps = Readonly<{ task: TaskOverview }>;

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

export function TaskWorkbench({ task }: TaskWorkbenchProps) {
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
        {neutralPanelMessage[selectedPanel]}
      </p>

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
