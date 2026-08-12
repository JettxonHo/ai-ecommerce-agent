import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import App from "./App";
import { createApiClient } from "./api/client";
import "./styles/global.css";
import { createHttpTaskGateway } from "./tasks/httpGateway";

const queryClient = new QueryClient();
const taskGateway = createHttpTaskGateway(createApiClient());
const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Web root element is missing");
}

createRoot(rootElement).render(
  <StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <App taskGateway={taskGateway} />
      </QueryClientProvider>
    </BrowserRouter>
  </StrictMode>,
);
