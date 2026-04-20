import type { Artifact } from "../types";
import { StatusBadge } from "./StatusBadge";

interface ArtifactViewerProps {
  artifact: Artifact | null;
  content: string;
  onExport?: () => void;
}

export function ArtifactViewer({ artifact, content, onExport }: ArtifactViewerProps) {
  return (
    <section className="card artifact-viewer">
      <div className="card-heading card-heading--split">
        <div>
          <h2>内容预览</h2>
          <p>文档查看与流程查看分离，后续接入真实文件读取。</p>
        </div>
        {onExport ? (
          <button className="button button-primary" type="button" onClick={onExport}>
            导出交付包
          </button>
        ) : null}
      </div>
      {artifact ? (
        <div className="artifact-meta">
          <StatusBadge label={artifact.artifact_type} tone="info" compact />
          <span>{artifact.artifact_name}</span>
          <span>v{artifact.version}</span>
          <span>{artifact.generated_by}</span>
        </div>
      ) : null}
      <pre className="artifact-body">{content}</pre>
    </section>
  );
}
