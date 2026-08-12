import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRef } from "react";
import { useForm, type SubmitHandler } from "react-hook-form";
import { Link, useNavigate } from "react-router";
import styles from "./TaskRoutes.module.css";
import {
  normalizeTaskInput,
  TaskGatewayError,
  type TaskGateway,
  type TaskInput,
} from "./gateway";

type NewTaskRouteProps = Readonly<{ taskGateway: TaskGateway }>;
type TaskFormValues = TaskInput;
type Attempt = Readonly<{ input: TaskInput; key: string }>;
type MutationVariables = Readonly<{ input: TaskInput; key: string }>;

const sameInput = (left: TaskInput, right: TaskInput): boolean =>
  left.taskName === right.taskName &&
  left.productCategory === right.productCategory &&
  left.promotionGoal === right.promotionGoal;

const required = (label: string) => (value: string) =>
  value.trim() !== "" || `${label} is required.`;

const createIdempotencyKey = (): string => globalThis.crypto.randomUUID();

const failureMessage = (error: unknown): string =>
  error instanceof TaskGatewayError && error.kind === "invalid"
    ? "The task request could not be completed. Check the entries and try again."
    : "Task creation is temporarily unavailable. Your entries are preserved. Try again.";

export function NewTaskRoute({ taskGateway }: NewTaskRouteProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const attemptRef = useRef<Attempt | null>(null);
  const retryableRef = useRef(false);
  const { register, handleSubmit, setError, formState } =
    useForm<TaskFormValues>({ mode: "onSubmit" });

  const mutation = useMutation({
    mutationFn: ({ input, key }: MutationVariables) =>
      taskGateway.createTask(input, key),
    retry: false,
    onError: (error) => {
      retryableRef.current =
        error instanceof TaskGatewayError && error.kind === "temporary";
      if (!retryableRef.current) attemptRef.current = null;
    },
    onSuccess: async (task) => {
      retryableRef.current = false;
      attemptRef.current = null;
      await queryClient.invalidateQueries({ queryKey: ["tasks"] });
      await navigate(`/tasks/${encodeURIComponent(task.taskId)}`);
    },
  });

  const submit: SubmitHandler<TaskFormValues> = (values) => {
    let input: TaskInput;
    try {
      input = normalizeTaskInput(values);
    } catch {
      setError("root", {
        type: "validation",
        message: "Enter a task name, product category, and promotion goal.",
      });
      return;
    }

    const previous = attemptRef.current;
    const key =
      retryableRef.current && previous && sameInput(previous.input, input)
        ? previous.key
        : createIdempotencyKey();
    attemptRef.current = { input, key };
    retryableRef.current = false;
    mutation.mutate({ input, key });
  };

  const formError = formState.errors.root?.message;
  const gatewayError = mutation.isError ? failureMessage(mutation.error) : null;

  return (
    <section className={styles.page} aria-labelledby="create-task-heading">
      <p className={styles.eyebrow}>Task intake</p>
      <p className={styles.backLink}>
        <Link to="/tasks">Back to recent tasks</Link>
      </p>
      <h1 id="create-task-heading">Create a task</h1>
      <p className={styles.intro}>
        Start a task with the three planning inputs. Workflow execution is a
        separate action after creation.
      </p>
      {formError || gatewayError ? (
        <p className={styles.alert} role="alert" aria-live="assertive">
          {formError ?? gatewayError}
        </p>
      ) : null}
      <form className={styles.form} onSubmit={handleSubmit(submit)} noValidate>
        <div className={styles.field}>
          <label htmlFor="task-name">Task name</label>
          <input
            id="task-name"
            {...register("taskName", { validate: required("Task name") })}
            required
            aria-invalid={formState.errors.taskName ? "true" : "false"}
            aria-describedby={
              formState.errors.taskName ? "task-name-error" : undefined
            }
          />
          {formState.errors.taskName ? (
            <span className={styles.fieldError} id="task-name-error">
              {formState.errors.taskName.message}
            </span>
          ) : null}
        </div>
        <div className={styles.field}>
          <label htmlFor="product-category">Product category</label>
          <input
            id="product-category"
            {...register("productCategory", {
              validate: required("Product category"),
            })}
            required
            aria-invalid={formState.errors.productCategory ? "true" : "false"}
            aria-describedby={
              formState.errors.productCategory
                ? "product-category-error"
                : undefined
            }
          />
          {formState.errors.productCategory ? (
            <span className={styles.fieldError} id="product-category-error">
              {formState.errors.productCategory.message}
            </span>
          ) : null}
        </div>
        <div className={styles.field}>
          <label htmlFor="promotion-goal">Promotion goal</label>
          <input
            id="promotion-goal"
            {...register("promotionGoal", {
              validate: required("Promotion goal"),
            })}
            required
            aria-invalid={formState.errors.promotionGoal ? "true" : "false"}
            aria-describedby={
              formState.errors.promotionGoal
                ? "promotion-goal-error"
                : undefined
            }
          />
          {formState.errors.promotionGoal ? (
            <span className={styles.fieldError} id="promotion-goal-error">
              {formState.errors.promotionGoal.message}
            </span>
          ) : null}
        </div>
        <div className={styles.formActions}>
          <button type="submit" disabled={mutation.isPending}>
            {mutation.isPending
              ? "Creating…"
              : mutation.isError
                ? "Retry create"
                : "Create task"}
          </button>
        </div>
      </form>
    </section>
  );
}
