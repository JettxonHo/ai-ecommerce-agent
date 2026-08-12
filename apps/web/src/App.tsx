import styles from "./App.module.css";
import { Navigate, Route, Routes } from "react-router";
import { NewTaskRoute } from "./tasks/NewTaskRoute";
import { TaskRoutes } from "./tasks/TaskRoutes";
import type { TaskGateway } from "./tasks/gateway";

type AppProps = Readonly<{ taskGateway: TaskGateway }>;

export function App({ taskGateway }: AppProps) {
  return (
    <main className={styles.shell}>
      <Routes>
        <Route path="/" element={<Navigate replace to="/tasks" />} />
        <Route
          path="/tasks"
          element={<TaskRoutes taskGateway={taskGateway} />}
        />
        <Route
          path="/tasks/new"
          element={<NewTaskRoute taskGateway={taskGateway} />}
        />
        <Route
          path="/tasks/:taskId"
          element={<TaskRoutes taskGateway={taskGateway} />}
        />
        <Route path="*" element={<Navigate replace to="/tasks" />} />
      </Routes>
    </main>
  );
}

export default App;
