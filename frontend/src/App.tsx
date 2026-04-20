import { useEffect, useState } from "react";
import { AppShell, type AppPath } from "./components/AppShell";
import { RequirementInputPage } from "./pages/RequirementInputPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ApprovalsPage } from "./pages/ApprovalsPage";
import { ArtifactsPage } from "./pages/ArtifactsPage";

const ROUTES = {
  "/input": { title: "需求输入", element: <RequirementInputPage /> },
  "/dashboard": { title: "流程看板", element: <DashboardPage /> },
  "/approvals": { title: "审批页", element: <ApprovalsPage /> },
  "/artifacts": { title: "产物页", element: <ArtifactsPage /> },
} as const;

function normalizePath(pathname: string): AppPath {
  if (pathname === "/dashboard" || pathname === "/approvals" || pathname === "/artifacts") {
    return pathname;
  }

  return "/input";
}

export default function App() {
  const [path, setPath] = useState<AppPath>(() => normalizePath(window.location.pathname));

  useEffect(() => {
    const handlePopState = () => {
      setPath(normalizePath(window.location.pathname));
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  useEffect(() => {
    if (window.location.pathname !== path) {
      window.history.replaceState({}, "", path);
    }

    document.title = `${ROUTES[path].title} | 需求交付流程引擎`;
  }, [path]);

  const activePage = ROUTES[path].element;

  return (
    <AppShell
      activePath={path}
      onNavigate={(nextPath) => {
        if (nextPath === path) {
          return;
        }

        window.history.pushState({}, "", nextPath);
        setPath(nextPath);
      }}
    >
      {activePage}
    </AppShell>
  );
}
