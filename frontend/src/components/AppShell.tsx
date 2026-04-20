import type { ReactNode } from "react";
import { StatusBadge } from "./StatusBadge";

export type AppPath = "/input" | "/dashboard" | "/approvals" | "/artifacts";

interface NavItem {
  path: AppPath;
  label: string;
}

const NAV_ITEMS: NavItem[] = [
  { path: "/input", label: "需求输入" },
  { path: "/dashboard", label: "流程看板" },
  { path: "/approvals", label: "审批页" },
  { path: "/artifacts", label: "产物页" },
];

interface AppShellProps {
  activePath: AppPath;
  onNavigate: (path: AppPath) => void;
  children: ReactNode;
}

export function AppShell({ activePath, onNavigate, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="shell-header">
        <div className="brand">
          <div className="brand-mark">AI</div>
          <div>
            <h1>需求交付流程引擎</h1>
            <p>React + Vite 前端骨架</p>
          </div>
        </div>
        <nav className="shell-nav" aria-label="主导航">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.path}
              type="button"
              className={`nav-button ${activePath === item.path ? "is-active" : ""}`}
              onClick={() => onNavigate(item.path)}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="shell-status">
          <StatusBadge label="Scaffold" tone="info" />
          <StatusBadge label="API pending" tone="warning" />
        </div>
      </header>
      <main className="app-main">{children}</main>
    </div>
  );
}
