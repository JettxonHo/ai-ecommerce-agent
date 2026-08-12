import { useQuery } from "@tanstack/react-query";
import { Link, Navigate, useParams } from "react-router";
import styles from "./TaskRoutes.module.css";
import {
  TaskGatewayError,
  type TaskGateway,
  type TaskOverview,
  type TaskPrimaryAction,
  type TaskSummary,
} from "./gateway";

type TaskRoutesProps = Readonly<{ taskGateway: TaskGateway }>;

const recentTasksKey = ["tasks", "recent"] as const;
const overviewKey = (taskId: string) => ["tasks", "overview", taskId] as const;

const taskStatus = (task: TaskSummary): string =>
  task.currentStage ?? task.waitingReason ?? task.taskStatus;

const actionDescription = (action: TaskPrimaryAction): string => {
  if (action.kind === "navigate") return `Continue in ${action.target}`;
  if (action.kind === "command") return `Next action: ${action.command}`;
  if (action.kind === "none") return "No next action";
  return "Next action unavailable";
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

  return (
    <section className={styles.page} aria-labelledby="recent-tasks-heading">
      <p className={styles.eyebrow}>Task index</p>
      <h1 id="recent-tasks-heading">Recent tasks</h1>
      <p className={styles.intro}>
        Return to a saved task from the fixed workspace.
      </p>
      {query.isPending ? <ReadState>Loading recent tasks…</ReadState> : null}
      {query.isError ? (
        <div className={styles.state} role="alert">
          <p>Recent tasks are temporarily unavailable.</p>
          <button type="button" onClick={() => void query.refetch()}>
            Retry
          </button>
        </div>
      ) : null}
      {query.isSuccess && query.data.length === 0 ? (
        <p className={styles.state}>No tasks yet.</p>
      ) : null}
      {query.isSuccess && query.data.length > 0 ? (
        <div className={styles.taskList}>
          {query.data.map((task) => (
            <article className={styles.taskCard} key={task.taskId}>
              <h2>
                <Link to={`/tasks/${encodeURIComponent(task.taskId)}`}>
                  {task.taskName}
                </Link>
              </h2>
              <p>{task.productCategory}</p>
              <p>{taskStatus(task)}</p>
              <time dateTime={task.updatedAt}>{task.updatedAt}</time>
              <p>{actionDescription(task.primaryAction)}</p>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function TaskOverviewRoute({
  taskGateway,
  taskId,
}: TaskRoutesProps & Readonly<{ taskId: string }>) {
  const query = useQuery({
    queryKey: overviewKey(taskId),
    queryFn: () => taskGateway.getTaskOverview(taskId),
    retry: false,
  });

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

  return <OverviewContent task={query.data} />;
}

function OverviewContent({ task }: Readonly<{ task: TaskOverview }>) {
  return (
    <section className={styles.page} aria-labelledby="task-overview-heading">
      <p className={styles.eyebrow}>Task overview</p>
      <p className={styles.backLink}>
        <Link to="/tasks">Back to recent tasks</Link>
      </p>
      <h1 id="task-overview-heading">{task.taskName}</h1>
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
          <dt>Current stage</dt>
          <dd>{task.currentStage ?? task.waitingReason ?? "Not started"}</dd>
        </div>
        <div>
          <dt>Updated</dt>
          <dd>
            <time dateTime={task.updatedAt}>{task.updatedAt}</time>
          </dd>
        </div>
      </dl>
      <h2>Stage summaries</h2>
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
  );
}

export function TaskRoutes({ taskGateway }: TaskRoutesProps) {
  const { taskId } = useParams();
  if (taskId === "new") return <Navigate replace to="/tasks" />;
  return taskId ? (
    <TaskOverviewRoute taskGateway={taskGateway} taskId={taskId} />
  ) : (
    <RecentTasks taskGateway={taskGateway} />
  );
}
