(function () {
  const React = window.React;
  const ReactDOM = window.ReactDOM;
  const { useEffect, useMemo, useState } = React;
  const h = React.createElement;
  const API_BASE = window.API_BASE || 'http://127.0.0.1:8000';

  function api(path, options) {
    return fetch(API_BASE + path, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    }).then(async (response) => {
      const data = await response.json();
      if (!response.ok || data.success === false) {
        const error = new Error(data.message || '请求失败');
        error.payload = data;
        throw error;
      }
      return data.data;
    });
  }

  function parseRoute() {
    const url = new URL(window.location.href);
    const path = url.pathname === '/' ? '/input' : url.pathname;
    return { path, search: url.searchParams };
  }

  function navigate(path) {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  }

  function statusBadge(status) {
    const cls = ['status-badge', status];
    return h('span', { className: cls.join(' ') }, statusLabel(status));
  }

  function statusLabel(status) {
    const map = {
      created: '已创建', clarifying: '需求澄清中', prd_generating: 'PRD 生成中', waiting_prd_approval: '待 PRD 审批',
      designing: '技术方案中', waiting_design_approval: '待技术方案审批', developing: '开发中', testing: '测试中',
      reviewing: '评审中', delivering: '交付中', done: '已完成', failed: '失败', paused: '已暂停',
      pending: '待处理', processing: '进行中', completed: '已完成', approved: '已通过', rejected: '已驳回'
    };
    return map[status] || status;
  }

  function Layout(props) {
    const route = parseRoute();
    const links = [
      ['/input', '需求输入页'],
      ['/dashboard', '流程看板页'],
      ['/approvals', '审批页'],
      ['/artifacts', '产物页'],
    ];
    return h('div', { className: 'app-shell' },
      h('header', { className: 'topbar' },
        h('div', null,
          h('div', { className: 'brand-title' }, 'AI 驱动的需求交付流程引擎'),
          h('div', { className: 'brand-subtitle' }, '比赛版 MVP · 固定 Pipeline Demo')
        ),
        h('nav', { className: 'nav-links' },
          ...links.map(([path, label]) => h('a', {
            key: path,
            href: path,
            className: route.path.startsWith(path) ? 'active' : '',
            onClick: function (event) { event.preventDefault(); navigate(path + (props.projectId ? ('?project_id=' + props.projectId) : '')); }
          }, label))
        )
      ),
      h('main', { className: 'page' }, props.children)
    );
  }

  function InputPage() {
    const [name, setName] = useState('Todo Web App');
    const [description, setDescription] = useState('比赛版演示项目');
    const [rawRequirement, setRawRequirement] = useState('开发一个简单的 Todo Web App，要求支持用户登录、待办事项新增、删除、修改以及完成/未完成状态切换。');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    function fillDemo() {
      setName('Todo Web App');
      setDescription('比赛版演示项目');
      setRawRequirement('开发一个简单的 Todo Web App，要求支持用户登录、待办事项新增、删除、修改以及完成/未完成状态切换。');
    }

    async function submit() {
      setLoading(true);
      setError('');
      try {
        const result = await api('/api/projects', {
          method: 'POST',
          body: JSON.stringify({ name, description, raw_requirement: rawRequirement })
        });
        localStorage.setItem('lastProjectId', result.project_id);
        navigate('/dashboard?project_id=' + result.project_id);
      } catch (err) {
        setError(err.message || '创建项目失败');
      } finally {
        setLoading(false);
      }
    }

    return h(Layout, null,
      h('h1', null, '需求输入页'),
      h('p', { className: 'lead' }, '输入项目名、描述和原始需求，系统会自动推进到结构化需求与 PRD 阶段。'),
      error ? h('div', { className: 'error' }, error) : null,
      h('div', { className: 'grid two' },
        h('section', { className: 'card' },
          h('div', { className: 'field' }, h('label', null, '项目名称'), h('input', { value: name, onChange: (e) => setName(e.target.value) })),
          h('div', { className: 'field' }, h('label', null, '项目描述'), h('input', { value: description, onChange: (e) => setDescription(e.target.value) })),
          h('div', { className: 'field' }, h('label', null, '原始需求'), h('textarea', { value: rawRequirement, onChange: (e) => setRawRequirement(e.target.value) })),
          h('div', { className: 'row' },
            h('button', { className: 'btn primary', onClick: submit, disabled: loading }, loading ? '启动中...' : '启动流程'),
            h('button', { className: 'btn', onClick: fillDemo }, '填充示例需求')
          )
        ),
        h('section', { className: 'card' },
          h('h2', null, '固定演示路径'),
          h('ol', null,
            h('li', null, '创建项目后自动生成结构化需求与 PRD'),
            h('li', null, '在审批页完成 PRD 与技术方案审批'),
            h('li', null, '系统自动创建 login / todo 的开发与测试任务'),
            h('li', null, 'login 首轮测试失败，触发返修与重测'),
            h('li', null, '完成最终评审并在产物页导出 zip')
          ),
          h('div', { className: 'notice' }, '系统会优先展示固定 Pipeline 的可视化、审批门禁与失败回流。')
        )
      )
    );
  }

  function DashboardPage(props) {
    const [overview, setOverview] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    async function load() {
      if (!props.projectId) return;
      try {
        const [ov, taskList, eventList] = await Promise.all([
          api('/api/projects/' + props.projectId + '/overview'),
          api('/api/projects/' + props.projectId + '/tasks'),
          api('/api/projects/' + props.projectId + '/events?limit=12')
        ]);
        setOverview(ov);
        setTasks(taskList);
        setEvents(eventList);
        setError('');
      } catch (err) {
        setError(err.message || '读取看板失败');
      } finally {
        setLoading(false);
      }
    }

    useEffect(() => {
      setLoading(true);
      load();
      const timer = setInterval(load, 4000);
      return () => clearInterval(timer);
    }, [props.projectId]);

    if (!props.projectId) {
      return h(Layout, null,
        h('h1', null, '流程看板页'),
        h('p', { className: 'lead' }, '请先从输入页创建项目。'),
        h('button', { className: 'btn primary', onClick: () => navigate('/input') }, '去创建项目')
      );
    }

    const project = overview && overview.project;
    return h(Layout, { projectId: props.projectId },
      h('div', { className: 'header-row' },
        h('div', null,
          h('h1', null, '流程看板页'),
          h('p', { className: 'lead' }, '展示当前项目状态、主流程时间线、任务列表、Agent 状态和最近事件。')
        ),
        h('div', { className: 'quick-actions' },
          h('button', { className: 'btn', onClick: () => navigate('/approvals?project_id=' + props.projectId) }, '去审批'),
          h('button', { className: 'btn', onClick: () => navigate('/artifacts?project_id=' + props.projectId) }, '看产物')
        )
      ),
      error ? h('div', { className: 'error' }, error) : null,
      loading && !overview ? h('div', { className: 'notice' }, '看板加载中...') : null,
      overview ? h(React.Fragment, null,
        h('div', { className: 'card' },
          h('div', { className: 'header-row' },
            h('div', null,
              h('h2', null, project.name),
              h('div', { className: 'small' }, '项目编号：' + project.project_id),
              h('p', { className: 'lead' }, project.description || '无描述')
            ),
            h('div', { className: 'row' },
              statusBadge(project.status),
              h('span', { className: 'status-badge processing' }, project.current_stage),
              h('span', { className: 'status-badge pending' }, '版本 v' + project.current_version)
            )
          ),
          h('div', { className: 'notice' }, overview.current_focus)
        ),
        h('div', { className: 'grid three' },
          metricCard('任务总数', overview.stats.task_total),
          metricCard('已完成任务', overview.stats.task_done),
          metricCard('待审批数', overview.stats.pending_approvals),
          metricCard('返修相关任务', overview.stats.repair_related)
        ),
        h('section', { className: 'card' },
          h('h2', null, '主流程时间线'),
          h('div', { className: 'timeline' }, ...(overview.timeline || []).map((item) => h('div', { className: 'timeline-item', key: item.name }, h('div', { className: 'timeline-name' }, item.name), statusBadge(item.status))))
        ),
        h('div', { className: 'grid two' },
          h('section', { className: 'card' },
            h('h2', null, '任务列表'),
            taskTable(tasks)
          ),
          h('section', { className: 'card' },
            h('h2', null, '最近事件流'),
            eventList(events)
          )
        ),
        h('section', { className: 'card' },
          h('h2', null, 'Agent 状态'),
          h('div', { className: 'grid three' }, ...(overview.agent_statuses || []).map((agent) => h('div', { className: 'list-item', key: agent.agent_id }, h('div', { className: 'row' }, h('strong', null, agent.agent_name), statusBadge(agent.status)), h('div', { className: 'small' }, agent.summary || '待命中'))))
        )
      ) : null
    );
  }

  function metricCard(label, value) {
    return h('div', { className: 'card' }, h('div', { className: 'metric-value' }, String(value)), h('div', { className: 'metric-label' }, label));
  }

  function taskTable(tasks) {
    if (!tasks || tasks.length === 0) return h('div', { className: 'empty' }, '暂无任务。');
    return h('table', { className: 'table' },
      h('thead', null, h('tr', null, h('th', null, '任务'), h('th', null, '模块'), h('th', null, 'Agent'), h('th', null, '状态'), h('th', null, '摘要'))),
      h('tbody', null, ...tasks.map((task) => h('tr', { key: task.task_id }, h('td', null, h('div', null, task.task_name), h('div', { className: 'small' }, task.task_type)), h('td', null, task.module_name || '-'), h('td', null, task.assigned_agent), h('td', null, statusBadge(task.status === 'done' ? 'completed' : task.status === 'failed' ? 'failed' : 'processing')), h('td', null, task.summary || '-'))))
    );
  }

  function eventList(events) {
    if (!events || events.length === 0) return h('div', { className: 'empty' }, '暂无事件。');
    return h('ul', { className: 'list' }, ...events.map((item) => h('li', { className: 'list-item', key: item.event_id }, h('div', { className: 'row' }, statusBadge(item.event_type.includes('failed') ? 'failed' : 'completed'), h('strong', null, item.message)), h('div', { className: 'small' }, item.created_at), item.related_ref ? h('div', { className: 'small' }, item.related_ref) : null)));
  }

  function ApprovalsPage(props) {
    const [approvals, setApprovals] = useState([]);
    const [selected, setSelected] = useState(null);
    const [artifact, setArtifact] = useState(null);
    const [comment, setComment] = useState('');
    const [error, setError] = useState('');
    const [busy, setBusy] = useState(false);

    async function loadApprovals() {
      if (!props.projectId) return;
      try {
        const list = await api('/api/projects/' + props.projectId + '/approvals');
        setApprovals(list);
        const pending = list.find((item) => item.status === 'pending');
        const target = selected ? list.find((item) => item.approval_id === selected.approval_id) : (pending || list[0]);
        setSelected(target || null);
        setError('');
      } catch (err) {
        setError(err.message || '审批列表读取失败');
      }
    }

    useEffect(() => {
      loadApprovals();
    }, [props.projectId]);

    useEffect(() => {
      if (!selected || !selected.artifact_id || !props.projectId) {
        setArtifact(null);
        return;
      }
      api('/api/projects/' + props.projectId + '/artifacts/' + selected.artifact_id)
        .then((data) => setArtifact(data))
        .catch((err) => setError(err.message || '审批文档读取失败'));
    }, [selected && selected.approval_id, props.projectId]);

    async function submit(action) {
      if (!selected) return;
      setBusy(true);
      setError('');
      try {
        await api('/api/approvals/' + selected.approval_id + '/submit', {
          method: 'POST',
          body: JSON.stringify({ action, reviewer: 'human_reviewer', comment })
        });
        setComment('');
        await loadApprovals();
      } catch (err) {
        setError(err.message || '审批提交失败');
      } finally {
        setBusy(false);
      }
    }

    function renderApprovalList() {
      if (approvals.length === 0) {
        return h('div', { className: 'empty' }, '暂无审批记录。');
      }
      return h(
        'ul',
        { className: 'list' },
        ...approvals.map((item) => h(
          'li',
          {
            key: item.approval_id,
            className: 'list-item' + ((selected && selected.approval_id === item.approval_id) ? ' active' : '')
          },
          h(
            'button',
            {
              className: 'btn',
              style: { width: '100%', textAlign: 'left' },
              onClick: () => setSelected(item)
            },
            h('div', { className: 'row' }, h('strong', null, item.approval_type), statusBadge(item.status)),
            h('div', { className: 'small' }, item.stage),
            h('div', { className: 'small' }, item.created_at)
          )
        ))
      );
    }

    function renderApprovalDetail() {
      if (!selected) {
        return h('div', { className: 'empty' }, '请选择一条审批记录。');
      }
      return h(
        React.Fragment,
        null,
        h('div', { className: 'header-row' },
          h('div', null,
            h('h2', null, selected.approval_type),
            h('div', { className: 'small' }, selected.stage)
          ),
          statusBadge(selected.status)
        ),
        h('div', { className: 'small' }, '目标文件：' + selected.target_ref),
        h('div', { className: 'field' },
          h('label', null, '审批意见'),
          h('textarea', {
            value: comment,
            onChange: (e) => setComment(e.target.value),
            placeholder: '填写审批意见或驳回原因'
          })
        ),
        h('div', { className: 'row' },
          h('button', {
            className: 'btn success',
            onClick: () => submit('approved'),
            disabled: busy || selected.status !== 'pending'
          }, busy ? '提交中...' : '通过'),
          h('button', {
            className: 'btn danger',
            onClick: () => submit('rejected'),
            disabled: busy || selected.status !== 'pending'
          }, '驳回')
        ),
        h('h3', null, '文档预览'),
        artifact ? h('div', { className: 'preview' }, artifact.content) : h('div', { className: 'empty' }, '暂无文档内容。')
      );
    }

    if (!props.projectId) {
      return h(Layout, null,
        h('h1', null, '审批页'),
        h('p', { className: 'lead' }, '请先创建项目后再进行审批。')
      );
    }

    return h(Layout, { projectId: props.projectId },
      h('h1', null, '审批页'),
      h('p', { className: 'lead' }, '处理 PRD、技术方案和最终评审的人工审批门禁。'),
      error ? h('div', { className: 'error' }, error) : null,
      h('div', { className: 'split' },
        h('section', { className: 'card' },
          h('h2', null, '审批列表'),
          renderApprovalList()
        ),
        h('section', { className: 'card' }, renderApprovalDetail())
      )
    );
  }

  function ArtifactsPage(props) {
    const [artifacts, setArtifacts] = useState([]);
    const [selectedId, setSelectedId] = useState(null);
    const [artifactDetail, setArtifactDetail] = useState(null);
    const [error, setError] = useState('');
    const [exportInfo, setExportInfo] = useState(null);
    const [exporting, setExporting] = useState(false);

    async function loadArtifacts() {
      if (!props.projectId) return;
      try {
        const list = await api('/api/projects/' + props.projectId + '/artifacts');
        setArtifacts(list);
        const targetId = selectedId || (list[0] && list[0].artifact_id);
        setSelectedId(targetId || null);
        setError('');
      } catch (err) {
        setError(err.message || '产物列表读取失败');
      }
    }

    useEffect(() => {
      loadArtifacts();
    }, [props.projectId]);

    useEffect(() => {
      if (!selectedId || !props.projectId) {
        setArtifactDetail(null);
        return;
      }
      api('/api/projects/' + props.projectId + '/artifacts/' + selectedId)
        .then((data) => setArtifactDetail(data))
        .catch((err) => setError(err.message || '产物读取失败'));
    }, [selectedId, props.projectId]);

    async function doExport() {
      setExporting(true);
      setError('');
      try {
        const result = await api('/api/projects/' + props.projectId + '/export', {
          method: 'POST',
          body: JSON.stringify({ export_type: 'delivery_bundle' })
        });
        setExportInfo(result);
        await loadArtifacts();
      } catch (err) {
        setError(err.message || '导出失败');
      } finally {
        setExporting(false);
      }
    }

    function renderArtifactList() {
      if (artifacts.length === 0) {
        return h('div', { className: 'empty' }, '暂无产物。');
      }
      return h(
        'ul',
        { className: 'list' },
        ...artifacts.map((item) => h(
          'li',
          {
            key: item.artifact_id,
            className: 'list-item' + (selectedId === item.artifact_id ? ' active' : '')
          },
          h(
            'button',
            {
              className: 'btn',
              style: { width: '100%', textAlign: 'left' },
              onClick: () => setSelectedId(item.artifact_id)
            },
            h('div', { className: 'row' }, h('strong', null, item.artifact_name), statusBadge('completed')),
            h('div', { className: 'small' }, item.artifact_type + ' · v' + item.version)
          )
        ))
      );
    }

    function renderArtifactDetail() {
      if (!artifactDetail) {
        return h('div', { className: 'empty' }, '请选择一个产物查看正文。');
      }
      return h(
        React.Fragment,
        null,
        h('div', { className: 'header-row' },
          h('div', null,
            h('h2', null, artifactDetail.artifact.artifact_name),
            h('div', { className: 'small' }, artifactDetail.artifact.uri)
          ),
          h('div', { className: 'row' }, statusBadge('completed'), h('span', { className: 'status-badge pending' }, artifactDetail.content_type))
        ),
        h('div', { className: 'preview' }, artifactDetail.content)
      );
    }

    if (!props.projectId) {
      return h(Layout, null,
        h('h1', null, '产物页'),
        h('p', { className: 'lead' }, '请先创建并推进项目。')
      );
    }

    return h(Layout, { projectId: props.projectId },
      h('div', { className: 'header-row' },
        h('div', null,
          h('h1', null, '产物页'),
          h('p', { className: 'lead' }, '查看全过程文档产物，并导出交付 zip 包。')
        ),
        h('button', { className: 'btn primary', onClick: doExport, disabled: exporting }, exporting ? '导出中...' : '导出交付包')
      ),
      exportInfo ? h('div', { className: 'notice' }, '导出成功：' + exportInfo.export_path) : null,
      error ? h('div', { className: 'error' }, error) : null,
      h('div', { className: 'split' },
        h('section', { className: 'card' },
          h('h2', null, '产物列表'),
          renderArtifactList()
        ),
        h('section', { className: 'card' }, renderArtifactDetail())
      )
    );
  }

  function App() {
    const [route, setRoute] = useState(parseRoute());
    useEffect(() => {
      const handler = () => setRoute(parseRoute());
      window.addEventListener('popstate', handler);
      return () => window.removeEventListener('popstate', handler);
    }, []);
    const projectId = route.search.get('project_id') || localStorage.getItem('lastProjectId') || '';
    const path = route.path;
    if (path.startsWith('/dashboard')) return h(DashboardPage, { projectId });
    if (path.startsWith('/approvals')) return h(ApprovalsPage, { projectId });
    if (path.startsWith('/artifacts')) return h(ArtifactsPage, { projectId });
    return h(InputPage, null);
  }

  const rootNode = document.getElementById('root');
  if (ReactDOM.createRoot) {
    ReactDOM.createRoot(rootNode).render(h(App));
  } else {
    ReactDOM.render(h(App), rootNode);
  }
})();
