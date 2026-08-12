import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, Navigate, useParams } from "react-router";
import styles from "./TaskRoutes.module.css";
import { TaskWorkbench } from "./workbench/TaskWorkbench";
import {
  TaskGatewayError,
  type TaskGateway,
  type TaskPrimaryInputDraft,
  type TaskPrimaryAction,
  type TaskSummary,
} from "./gateway";

type TaskRoutesProps = Readonly<{ taskGateway: TaskGateway }>;

const recentTasksKey = ["tasks", "recent"] as const;
const overviewKey = (taskId: string) => ["tasks", "overview", taskId] as const;
const primaryInputKey = (taskId: string) =>
  ["tasks", "primary-input", taskId] as const;

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

  // The Workbench remains the sole projection consumer (formerly: return <TaskWorkbench task={query.data} />;).
  return (
    <section className={styles.page} aria-labelledby="recent-tasks-heading">
      <p className={styles.eyebrow}>Task index</p>
      <h1 id="recent-tasks-heading">Recent tasks</h1>
      <p className={styles.intro}>
        Return to a saved task from the fixed workspace.
      </p>
      <p className={styles.createLink}>
        <Link to="/tasks/new">Create a task</Link>
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
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: overviewKey(taskId),
    queryFn: () => taskGateway.getTaskOverview(taskId),
    retry: false,
  });
  const primaryInputQuery = useQuery({
    queryKey: primaryInputKey(taskId),
    queryFn: () =>
      taskGateway.getPrimaryInput === undefined
        ? Promise.resolve(null)
        : taskGateway.getPrimaryInput(taskId),
    retry: false,
  });
  const savePrimaryInput = async (input: TaskPrimaryInputDraft) => {
    if (taskGateway.savePrimaryInput === undefined) {
      throw new TaskGatewayError("temporary", "Primary input is unavailable.");
    }
    const saved = await taskGateway.savePrimaryInput(taskId, input);
    await queryClient.invalidateQueries({ queryKey: primaryInputKey(taskId) });
    return saved;
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
      savePrimaryInput={savePrimaryInput}
    />
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
