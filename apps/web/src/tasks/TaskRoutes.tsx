import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";
import {
  Link,
  Navigate,
  useLocation,
  useNavigate,
  useParams,
} from "react-router";
import styles from "./TaskRoutes.module.css";
import { TaskWorkbench } from "./workbench/TaskWorkbench";
import {
  mapNeedsInputResolution,
  NeedsInputGatewayError,
  resolutionIdentity,
  type NeedsInputActionRequest,
  type NeedsInputGateway,
  type NeedsInputResolution,
  type NeedsInputResolutionResult,
} from "../needsInput/gateway";
import {
  TaskGatewayError,
  type TaskGateway,
  type TaskPrimaryInputDraft,
  type TaskPrimaryAction,
  type TaskCurrentResult,
  type TaskOverview,
  type TaskSummary,
  type ExportBriefKind,
  type ExportDownload,
} from "./gateway";

type TaskRoutesProps = Readonly<{
  taskGateway: TaskGateway;
  needsInputGateway?: NeedsInputGateway;
}>;

const recentTasksKey = ["tasks", "recent"] as const;
const overviewKey = (taskId: string) => ["tasks", "overview", taskId] as const;
const primaryInputKey = (taskId: string) =>
  ["tasks", "primary-input", taskId] as const;
const currentResultKey = (taskId: string) =>
  ["tasks", "current-result", taskId] as const;
const needsInputKey = (
  taskId: string,
  actionRequestId: string,
  revision: number,
) => ["tasks", "needs-input", taskId, actionRequestId, revision] as const;

const needsInputAuthorityMatches = (
  task: TaskOverview,
  request: NeedsInputActionRequest | undefined,
): request is NeedsInputActionRequest =>
  request !== undefined &&
  task.needsInputRequest !== null &&
  task.needsInputRequest.resourceId === request.actionRequestId &&
  task.needsInputRequest.revision === request.revision &&
  request.taskId === task.taskId &&
  request.status === "open" &&
  request.supersededBy === null;

const needsInputErrorMessage = (error: unknown): string => {
  if (error instanceof NeedsInputGatewayError) {
    if (error.kind === "missing") return "该补充请求已不存在，请刷新任务事实。";
    if (error.kind === "stale")
      return "补充请求已变化，请刷新任务事实后再提交。";
    if (error.kind === "invalid")
      return "当前补充动作无法提交，请检查允许动作。";
  }
  return "补充请求暂时不可用，请手动重试。";
};

const makeRetryKey = (taskId: string, inputRevision: number): string => {
  const random =
    typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  return `result:${taskId}:${inputRevision}:${random}`;
};
const makeOpaqueNeedsInputKey = (): string => {
  const random =
    typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  return `needs-input:${random}`.slice(0, 200);
};
const makeConfirmationKey = (taskId: string, revision: number) => {
  const random =
    typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
      ? crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  return `confirm:${taskId}:${revision}:${random}`;
};
const makeExportKey = (basis: {
  taskId: string;
  taskRevision: number;
  briefKind: string;
  briefVersion: { resourceVersionId: string };
}) =>
  `export:${basis.taskId}:${basis.taskRevision}:${basis.briefKind}:${basis.briefVersion.resourceVersionId}`;

// Display timestamps in UTC so presentation does not infer the operator's local timezone.
const formatTimestamp = (value: string): string => {
  const parsed = Date.parse(value);
  if (Number.isNaN(parsed)) return value;
  const date = new Date(parsed);
  const pad = (part: number) => String(part).padStart(2, "0");
  return `${date.getUTCFullYear()}年${date.getUTCMonth() + 1}月${date.getUTCDate()}日 ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`;
};

const stageLabels: Readonly<Record<string, string>> = {
  product_intake_and_fact_extraction: "资料整理",
  customer_insight_analysis: "用户洞察",
  product_positioning: "商品定位",
  human_review: "人工审核",
  marketing_brief_generation: "营销 Brief",
  xiaohongshu_brief_mapping: "小红书 Brief",
};

const taskStateLabels: Readonly<Record<string, string>> = {
  draft: "待开始",
  running: "处理中",
  waiting_for_input: "待补充资料",
  waiting_for_review: "待审核",
  paused: "已暂停",
  completed: "已完成",
  failed: "需要恢复",
  cancelled: "已取消",
};

const taskStateLabel = (task: TaskSummary): string =>
  taskStateLabels[task.taskStatus] ??
  (task.currentStage === null
    ? "等待处理"
    : (stageLabels[task.currentStage] ?? "等待处理"));

const actionDescription = (action: TaskPrimaryAction): string => {
  if (action.kind === "navigate") {
    const labels: Readonly<Record<string, string>> = {
      intake: "继续整理资料",
      needs_input: "补充资料",
      review: "查看审核",
      results: "查看结果",
      recovery: "恢复任务",
    };
    return labels[action.target] ?? "继续处理";
  }
  if (action.kind === "command") {
    return action.command === "start" ? "开始处理" : "继续处理";
  }
  if (action.kind === "none") return "等待下一步";
  return "下一步暂不可用";
};

const resumePriority = (task: TaskSummary): number => {
  if (
    task.taskStatus === "waiting_for_input" ||
    (task.primaryAction.kind === "navigate" &&
      task.primaryAction.target === "needs_input")
  ) {
    return 0;
  }
  if (
    task.taskStatus === "waiting_for_review" ||
    task.currentStage === "human_review" ||
    (task.primaryAction.kind === "navigate" &&
      task.primaryAction.target === "review")
  ) {
    return 1;
  }
  if (
    task.taskStatus === "failed" ||
    task.taskStatus === "paused" ||
    (task.primaryAction.kind === "navigate" &&
      task.primaryAction.target === "recovery")
  ) {
    return 2;
  }
  return 3;
};

const chooseResumeTask = (
  tasks: readonly TaskSummary[],
): TaskSummary | null => {
  let selected: TaskSummary | null = null;
  let selectedPriority = Number.POSITIVE_INFINITY;
  for (const task of tasks) {
    const priority = resumePriority(task);
    if (selected === null || priority < selectedPriority) {
      selected = task;
      selectedPriority = priority;
    }
  }
  return selected;
};

const ReadState = ({ children }: Readonly<{ children: string }>) => (
  <p className={styles.state} role="status" aria-live="polite">
    {children}
  </p>
);

function RecentTasks({ taskGateway }: TaskRoutesProps) {
  const query = useQuery({
    queryKey: recentTasksKey,
    queryFn: () => taskGateway.listTasks(),
    retry: false,
  });

  const resumeTask = query.isSuccess ? chooseResumeTask(query.data) : null;

  return (
    <section className={styles.page} aria-labelledby="recent-tasks-heading">
      <header className={styles.homeHeader}>
        <p className={styles.eyebrow}>运营编辑部 / 策略桌</p>
        <p className={styles.kicker}>商品上新行动工作台</p>
        <h1 id="recent-tasks-heading">行动首页</h1>
        <p className={styles.intro}>
          从一个明确动作开始，回到最近的商品上新任务。
        </p>
        <Link className={styles.primaryAction} to="/tasks/new">
          新建商品上新任务
        </Link>
      </header>
      <p className={styles.intro}>
        固定本地工作区 · 单用户 · 当前事实由任务本身保留
      </p>
      {query.isPending ? <ReadState>正在读取最近任务…</ReadState> : null}
      {query.isError ? (
        <div className={styles.state} role="alert">
          <p>最近任务暂时无法读取，请稍后重试。</p>
          <button type="button" onClick={() => void query.refetch()}>
            重试读取任务
          </button>
        </div>
      ) : null}
      {query.isSuccess && query.data.length === 0 ? (
        <p className={styles.state}>还没有商品上新任务。</p>
      ) : null}
      {resumeTask !== null ? (
        <section className={styles.resume} aria-labelledby="resume-heading">
          <div className={styles.sectionHeading}>
            <p className={styles.sectionLabel}>优先动作</p>
            <h2 id="resume-heading">继续处理</h2>
          </div>
          <article className={styles.resumeCard}>
            <div>
              <p className={styles.resumeState}>
                {taskStateLabel(resumeTask)} · {resumeTask.productCategory}
              </p>
              <h3>
                <Link to={`/tasks/${encodeURIComponent(resumeTask.taskId)}`}>
                  {resumeTask.taskName}
                </Link>
              </h3>
              <p>
                {resumeTask.waitingReason ??
                  actionDescription(resumeTask.primaryAction)}
              </p>
            </div>
            <time dateTime={resumeTask.updatedAt}>
              {formatTimestamp(resumeTask.updatedAt)}
            </time>
          </article>
        </section>
      ) : null}
      {query.isSuccess && query.data.length > 0 ? (
        <section aria-labelledby="recent-heading" className={styles.recent}>
          <div className={styles.sectionHeading}>
            <p className={styles.sectionLabel}>保持可回到</p>
            <h2 id="recent-heading">最近任务</h2>
          </div>
          <div className={styles.taskList}>
            {query.data.map((task) => (
              <article className={styles.taskCard} key={task.taskId}>
                <div className={styles.taskCardHeading}>
                  <div>
                    <p className={styles.taskMeta}>{task.productCategory}</p>
                    <h3>
                      <Link to={`/tasks/${encodeURIComponent(task.taskId)}`}>
                        {task.taskName}
                      </Link>
                    </h3>
                  </div>
                  <span className={styles.taskState}>
                    {taskStateLabel(task)}
                  </span>
                </div>
                <p className={styles.taskNextAction}>
                  {actionDescription(task.primaryAction)}
                </p>
                {task.waitingReason !== null ? (
                  <p>{task.waitingReason}</p>
                ) : null}
                <time dateTime={task.updatedAt}>
                  {formatTimestamp(task.updatedAt)}
                </time>
              </article>
            ))}
          </div>
        </section>
      ) : null}
    </section>
  );
}

function TaskOverviewRoute({
  taskGateway,
  taskId,
  needsInputGateway,
}: TaskRoutesProps & Readonly<{ taskId: string }>) {
  const queryClient = useQueryClient();
  const location = useLocation();
  const navigate = useNavigate();
  const [needsInputCompletion, setNeedsInputCompletion] = useState(false);
  const [needsInputRefreshError, setNeedsInputRefreshError] = useState<
    string | null
  >(null);
  const query = useQuery({
    queryKey: overviewKey(taskId),
    queryFn: () => taskGateway.getTaskOverview(taskId),
    retry: false,
  });
  const primaryInputQuery = useQuery({
    queryKey: primaryInputKey(taskId),
    queryFn: async () => {
      try {
        return await taskGateway.getPrimaryInput(taskId);
      } catch (error) {
        if (error instanceof TaskGatewayError && error.kind === "missing") {
          return null;
        }
        throw error;
      }
    },
    retry: false,
  });
  const currentResultQuery = useQuery({
    queryKey: currentResultKey(taskId),
    queryFn: async () => (await taskGateway.getCurrentResult(taskId)) ?? null,
    retry: false,
  });
  const authoritativeRequestReference = query.data?.needsInputRequest ?? null;
  const needsInputReadEnabled =
    needsInputGateway !== undefined && authoritativeRequestReference !== null;
  const needsInputQuery = useQuery({
    queryKey:
      authoritativeRequestReference === null
        ? (["tasks", "needs-input", taskId, "none", 0] as const)
        : needsInputKey(
            taskId,
            authoritativeRequestReference.resourceId,
            authoritativeRequestReference.revision,
          ),
    enabled: needsInputReadEnabled,
    queryFn: async () => {
      if (
        needsInputGateway === undefined ||
        authoritativeRequestReference === null
      ) {
        throw new NeedsInputGatewayError("invalid", "补充请求读取不可用。");
      }
      return needsInputGateway.getNeedsInputActionRequest(
        authoritativeRequestReference.resourceId,
      );
    },
    retry: false,
  });
  const resultRetryKey = useRef<{ inputRevision: number; key: string } | null>(
    null,
  );
  const confirmationRetryKey = useRef<{
    key: string;
    resultRevision: number;
    message: string;
    title: string;
  } | null>(null);
  const exportRetryKeys = useRef(new Map<string, string>());
  const needsInputRetryKey = useRef<{
    requestKey: string;
    resolutionKey: string;
    key: string;
  } | null>(null);
  const needsInputCommandResolved = useRef(false);

  const needsInputRequest = needsInputQuery.data;
  const needsInputAuthorityMatch = needsInputAuthorityMatches(
    query.data ?? ({} as TaskOverview),
    needsInputRequest,
  );

  const refreshTask = async (): Promise<boolean> => {
    try {
      const refreshedTask = await taskGateway.getTaskOverview(taskId);
      queryClient.setQueryData(overviewKey(taskId), refreshedTask);
      const refreshedReference = refreshedTask.needsInputRequest ?? null;
      const sameAuthoritativeReference =
        needsInputReadEnabled &&
        authoritativeRequestReference !== null &&
        refreshedReference !== null &&
        refreshedReference.resourceId ===
          authoritativeRequestReference.resourceId &&
        refreshedReference.revision === authoritativeRequestReference.revision;
      if (sameAuthoritativeReference) {
        await needsInputQuery.refetch();
      }
      setNeedsInputRefreshError(null);
      if (needsInputCommandResolved.current) {
        setNeedsInputCompletion(true);
      }
      return true;
    } catch {
      setNeedsInputCompletion(false);
      setNeedsInputRefreshError("任务事实暂时无法刷新，请手动重试。");
      return false;
    }
  };

  const resolveNeedsInput = async (
    resolution: NeedsInputResolution,
  ): Promise<NeedsInputResolutionResult> => {
    if (
      needsInputGateway === undefined ||
      authoritativeRequestReference === null ||
      needsInputRequest === undefined ||
      !needsInputAuthorityMatch
    ) {
      throw new NeedsInputGatewayError(
        "stale",
        "当前补充请求已变化，请先刷新任务事实。",
      );
    }
    const normalized = mapNeedsInputResolution(resolution);
    const normalizedKey = resolutionIdentity(normalized);
    const requestKey = `${taskId}:${needsInputRequest.actionRequestId}:${needsInputRequest.revision}`;
    const previous = needsInputRetryKey.current;
    const key =
      previous !== null &&
      previous.requestKey === requestKey &&
      previous.resolutionKey === normalizedKey
        ? previous.key
        : makeOpaqueNeedsInputKey();
    needsInputRetryKey.current = {
      requestKey,
      resolutionKey: normalizedKey,
      key,
    };
    const resolved = await needsInputGateway.resolveNeedsInput(
      needsInputRequest.actionRequestId,
      needsInputRequest.revision,
      normalized,
      key,
    );
    needsInputCommandResolved.current = true;
    queryClient.setQueryData(
      needsInputKey(
        taskId,
        needsInputRequest.actionRequestId,
        needsInputRequest.revision,
      ),
      resolved.actionRequest,
    );
    await refreshTask();
    await queryClient.invalidateQueries({ queryKey: recentTasksKey });
    return resolved;
  };
  const savePrimaryInput = async (input: TaskPrimaryInputDraft) => {
    const saved = await taskGateway.savePrimaryInput(taskId, input);
    await queryClient.invalidateQueries({ queryKey: primaryInputKey(taskId) });
    if (
      resultRetryKey.current !== null &&
      resultRetryKey.current.inputRevision !== saved.inputRevision
    ) {
      resultRetryKey.current = null;
    }
    return saved;
  };
  const generateResult = async (): Promise<TaskCurrentResult> => {
    const input = primaryInputQuery.data;
    if (input === undefined || input === null) {
      throw new TaskGatewayError(
        "invalid",
        "Save primary input before generating a result.",
      );
    }
    const existingKey = resultRetryKey.current;
    const retryKey =
      existingKey?.inputRevision === input.inputRevision
        ? existingKey.key
        : makeRetryKey(taskId, input.inputRevision);
    resultRetryKey.current = {
      inputRevision: input.inputRevision,
      key: retryKey,
    };
    try {
      const result = await taskGateway.generateResult(
        taskId,
        retryKey,
        input.inputRevision,
      );
      queryClient.setQueryData(currentResultKey(taskId), result);
      await queryClient.invalidateQueries({ queryKey: overviewKey(taskId) });
      return result;
    } catch (error) {
      throw error;
    }
  };
  const confirmCurrentResult = async (
    message: string,
    title: string,
  ): Promise<TaskCurrentResult> => {
    const result = currentResultQuery.data;
    if (
      !result ||
      result.status !== "awaiting_review" ||
      taskGateway.confirmCurrentResult === undefined
    ) {
      throw new TaskGatewayError(
        "invalid",
        "Current result confirmation is unavailable.",
      );
    }
    const previous = confirmationRetryKey.current;
    const retryKey =
      previous !== null &&
      previous.resultRevision === result.resultRevision &&
      previous.message === message &&
      previous.title === title
        ? previous.key
        : makeConfirmationKey(taskId, result.resultRevision);
    confirmationRetryKey.current = {
      key: retryKey,
      resultRevision: result.resultRevision,
      message,
      title,
    };
    const confirmed = await taskGateway.confirmCurrentResult(
      taskId,
      retryKey,
      result.resultRevision,
      { marketingCoreMessage: message, xiaohongshuTitleDirection: title },
    );
    confirmationRetryKey.current = null;
    queryClient.setQueryData(currentResultKey(taskId), confirmed);
    await queryClient.invalidateQueries({ queryKey: overviewKey(taskId) });
    const searchParams = new URLSearchParams(location.search);
    searchParams.set("panel", "results");
    navigate({
      pathname: location.pathname,
      search: `?${searchParams.toString()}`,
    });
    return confirmed;
  };
  const exportBrief = async (
    briefKind: ExportBriefKind,
  ): Promise<ExportDownload> => {
    if (
      taskGateway.previewExport === undefined ||
      taskGateway.createExportSnapshot === undefined
    ) {
      throw new TaskGatewayError("invalid", "Export is unavailable.");
    }
    const preview = await taskGateway.previewExport(taskId, briefKind);
    const key =
      exportRetryKeys.current.get(makeExportKey(preview.basis)) ??
      `export:${taskId}:${preview.basis.taskRevision}:${briefKind}:${preview.basis.briefVersion.resourceVersionId}`;
    exportRetryKeys.current.set(makeExportKey(preview.basis), key);
    const snapshot = await taskGateway.createExportSnapshot(key, preview.basis);
    const download =
      taskGateway.downloadExportContent === undefined
        ? { snapshot, content: "" }
        : await taskGateway.downloadExportContent(snapshot);
    if (download.content !== "" && typeof document !== "undefined") {
      const url = URL.createObjectURL(
        new Blob([download.content], { type: download.snapshot.mediaType }),
      );
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = download.snapshot.fileName;
      anchor.click();
      URL.revokeObjectURL(url);
    }
    return download;
  };

  if (query.isPending) {
    return <ReadState>Loading task overview…</ReadState>;
  }
  if (query.isError) {
    const missing =
      query.error instanceof TaskGatewayError && query.error.kind === "missing";
    return (
      <section className={styles.page} aria-labelledby="task-error-heading">
        <p className={styles.eyebrow}>Task overview</p>
        <h1 id="task-error-heading">
          {missing ? "Task not found" : "Task overview unavailable"}
        </h1>
        <p className={styles.state} role="alert">
          {missing
            ? "This task is not available in the fixed workspace."
            : "The task overview is temporarily unavailable."}
        </p>
        {!missing ? (
          <button type="button" onClick={() => void query.refetch()}>
            Retry
          </button>
        ) : null}
        <p>
          <Link to="/tasks">Back to recent tasks</Link>
        </p>
      </section>
    );
  }

  return (
    <TaskWorkbench
      task={query.data}
      primaryInput={primaryInputQuery.data}
      primaryInputLoading={primaryInputQuery.isPending}
      primaryInputError={
        primaryInputQuery.isError
          ? "Saved input is unavailable. Retry to continue."
          : null
      }
      retryPrimaryInput={
        primaryInputQuery.isError
          ? () => void primaryInputQuery.refetch()
          : undefined
      }
      savePrimaryInput={
        primaryInputQuery.isSuccess ? savePrimaryInput : undefined
      }
      currentResult={
        currentResultQuery.isSuccess ? currentResultQuery.data : undefined
      }
      currentResultLoading={currentResultQuery.isPending}
      currentResultError={
        currentResultQuery.isError
          ? "The current result is temporarily unavailable. Retry to reload it."
          : null
      }
      retryCurrentResult={
        currentResultQuery.isError
          ? () => void currentResultQuery.refetch()
          : undefined
      }
      generateResult={generateResult}
      confirmCurrentResult={
        taskGateway.confirmCurrentResult === undefined
          ? undefined
          : confirmCurrentResult
      }
      exportBrief={
        taskGateway.previewExport === undefined ||
        taskGateway.createExportSnapshot === undefined
          ? undefined
          : exportBrief
      }
      needsInputRequest={needsInputRequest}
      needsInputLoading={needsInputReadEnabled && needsInputQuery.isPending}
      needsInputError={
        needsInputQuery.isError
          ? needsInputErrorMessage(needsInputQuery.error)
          : null
      }
      needsInputAuthorityMatch={needsInputAuthorityMatch}
      retryNeedsInput={
        needsInputReadEnabled ? () => void needsInputQuery.refetch() : undefined
      }
      resolveNeedsInput={needsInputReadEnabled ? resolveNeedsInput : undefined}
      refreshTask={() => void refreshTask()}
      needsInputRefreshError={needsInputRefreshError}
      hasCurrentResult={
        query.data.marketingBrief !== null ||
        query.data.xiaohongshuBrief !== null
      }
      needsInputCompletion={needsInputCompletion}
    />
  );
}

export function TaskRoutes({
  taskGateway,
  needsInputGateway,
}: TaskRoutesProps) {
  const { taskId } = useParams();
  if (taskId === "new") return <Navigate replace to="/tasks" />;
  return taskId ? (
    <TaskOverviewRoute
      taskGateway={taskGateway}
      needsInputGateway={needsInputGateway}
      taskId={taskId}
    />
  ) : (
    <RecentTasks taskGateway={taskGateway} />
  );
}
