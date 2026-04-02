const DEFAULT_AGENTS = [
  { name: "product", purpose: "Define visión, roadmap y backlog" },
  { name: "legal", purpose: "Gestiona cumplimiento y privacidad" },
  { name: "marketing", purpose: "Posicionamiento y GTM" },
  { name: "design", purpose: "UX/UI y flujos" },
  { name: "development", purpose: "Arquitectura e implementación" },
  { name: "qa", purpose: "Pruebas y control de calidad" },
];

const projects = new Map();
const tasks = new Map();

function nowIso() {
  return new Date().toISOString();
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

function ensureDefaultProject() {
  if (projects.size > 0) return;
  const id = crypto.randomUUID();
  const createdAt = nowIso();
  projects.set(id, {
    id,
    name: "Proyecto General",
    description: "Proyecto base para iniciar Mission Control",
    created_at: createdAt,
    updated_at: createdAt,
  });
}

function getTaskProgress(task) {
  const total = task.work_items.length;
  const completed = task.work_items.filter((item) => item.status === "completed").length;
  const percent = total === 0 ? 0 : Math.round((completed / total) * 100);
  return { total, completed, percent };
}

function taskSummary(task) {
  return {
    ...task,
    progress: getTaskProgress(task),
  };
}

function projectSummary(project) {
  const projectTasks = Array.from(tasks.values()).filter((task) => task.project_id === project.id);
  const completedTasks = projectTasks.filter((task) => task.status === "completed").length;
  const avgProgress =
    projectTasks.length === 0
      ? 0
      : Math.round(projectTasks.reduce((acc, task) => acc + getTaskProgress(task).percent, 0) / projectTasks.length);

  return {
    ...project,
    task_count: projectTasks.length,
    completed_task_count: completedTasks,
    avg_progress: avgProgress,
  };
}

function createProject(body) {
  const id = crypto.randomUUID();
  const timestamp = nowIso();
  const project = {
    id,
    name: body.name,
    description: body.description || "",
    created_at: timestamp,
    updated_at: timestamp,
  };
  projects.set(id, project);
  return projectSummary(project);
}

function createTask(body, projectId) {
  const project = projects.get(projectId);
  if (!project) {
    return null;
  }

  const id = crypto.randomUUID();
  const createdAt = nowIso();
  const workItems = DEFAULT_AGENTS.map((agent) => ({
    id: crypto.randomUUID(),
    agent: agent.name,
    objective: `Entregable inicial (${agent.name}) para ${body.idea}`,
    status: "planned",
    output: "",
    updated_at: createdAt,
  }));

  const scopeLower = (body.scope || "").toLowerCase();
  if (scopeLower.includes("ollama") || scopeLower.includes("cloud")) {
    workItems.push({
      id: crypto.randomUUID(),
      agent: "development",
      objective: "Automatización con Ollama en cloud privado con controles anti-fuga",
      status: "planned",
      output: "",
      updated_at: createdAt,
    });
  }

  const task = {
    id,
    project_id: projectId,
    idea: body.idea,
    scope: body.scope,
    status: "planned",
    created_at: createdAt,
    updated_at: createdAt,
    work_items: workItems,
  };

  tasks.set(id, task);
  project.updated_at = nowIso();
  return taskSummary(task);
}

function executeTaskStep(task) {
  const nextItem = task.work_items.find((item) => item.status !== "completed");
  if (!nextItem) {
    task.status = "completed";
    task.updated_at = nowIso();
    return taskSummary(task);
  }

  task.status = "in_progress";
  task.updated_at = nowIso();
  nextItem.status = "completed";
  nextItem.output = `[${nextItem.agent}] ${nextItem.objective} completado`;
  nextItem.updated_at = nowIso();

  const hasPending = task.work_items.some((item) => item.status !== "completed");
  if (!hasPending) {
    task.status = "completed";
  }
  task.updated_at = nowIso();
  return taskSummary(task);
}

function htmlPage() {
  return new Response(
    `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Mission Control</title>
<style>
:root{font-family:Inter,Arial,sans-serif;color:#101828;background:#f6f8fb}
body{margin:0}
.container{max-width:1100px;margin:0 auto;padding:20px}
.grid{display:grid;grid-template-columns:320px 1fr;gap:16px}
.card{background:#fff;border:1px solid #e4e7ec;border-radius:12px;padding:14px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
h1{margin:0 0 12px} h2{margin:0 0 10px;font-size:18px}
input,textarea,select,button{width:100%;box-sizing:border-box;border-radius:10px;border:1px solid #d0d5dd;padding:10px;margin:6px 0}
button{background:#2563eb;color:#fff;border:none;font-weight:600;cursor:pointer}
button.secondary{background:#0f766e}
button.ghost{background:#f2f4f7;color:#101828}
.list{display:flex;flex-direction:column;gap:8px;max-height:270px;overflow:auto}
.item{padding:10px;border:1px solid #e4e7ec;border-radius:10px;background:#fff;cursor:pointer}
.item.active{border-color:#2563eb;background:#eef4ff}
.row{display:flex;justify-content:space-between;gap:8px;align-items:center}
.badge{font-size:12px;padding:3px 8px;border-radius:99px;background:#eef4ff;color:#1d4ed8}
.progress{height:8px;border-radius:999px;background:#eef2f6;overflow:hidden;margin:6px 0}
.progress > div{height:100%;background:#16a34a}
.task{border:1px solid #e4e7ec;border-radius:10px;padding:10px;margin-bottom:10px;background:#fff}
small{color:#667085}
@media (max-width: 900px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
  <div class="container">
    <h1>Mission Control · Proyectos</h1>
    <div class="grid">
      <section class="card">
        <h2>Nuevo proyecto</h2>
        <input id="project-name" placeholder="Nombre del proyecto" />
        <textarea id="project-description" rows="2" placeholder="Descripción"></textarea>
        <button id="create-project">Crear proyecto</button>
        <h2 style="margin-top:14px">Proyectos</h2>
        <div id="projects" class="list"></div>
      </section>

      <section class="card">
        <h2 id="selected-title">Tareas por proyecto</h2>
        <input id="task-idea" placeholder="Idea/tarea" />
        <textarea id="task-scope" rows="2" placeholder="Scope"></textarea>
        <button id="create-task" class="secondary">Crear tarea</button>
        <div style="margin:10px 0">
          <button id="refresh" class="ghost">Actualizar</button>
        </div>
        <div id="tasks"></div>
      </section>
    </div>
  </div>

<script>
let selectedProjectId = null;

async function api(path, options = {}) {
  const response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function projectCard(project) {
  const div = document.createElement("div");
  div.className = "item" + (project.id === selectedProjectId ? " active" : "");
  div.innerHTML =
    '<div class="row"><b>' +
    project.name +
    '</b><span class="badge">' +
    project.avg_progress +
    '%</span></div><small>' +
    project.task_count +
    ' tareas · ' +
    project.completed_task_count +
    " completadas</small>";
  div.onclick = async () => {
    selectedProjectId = project.id;
    await loadProjects();
    await loadTasks();
  };
  return div;
}

function taskCard(task) {
  const div = document.createElement("div");
  div.className = "task";
  const status = task.status;
  div.innerHTML =
    '<div class="row"><b>' +
    task.idea +
    '</b><span class="badge">' +
    status +
    '</span></div><small>' +
    task.scope +
    '</small><div class="progress"><div style="width:' +
    task.progress.percent +
    '%"></div></div><small>' +
    task.progress.completed +
    "/" +
    task.progress.total +
    ' work-items completados</small><div style="margin-top:8px"><button data-id="' +
    task.id +
    '">Avanzar paso</button></div>';
  div.querySelector("button").onclick = async () => {
    await api("/api/tasks/" + task.id + "/execute", { method: "POST" });
    await loadTasks();
    await loadProjects();
  };
  return div;
}

async function loadProjects() {
  const data = await api("/api/projects");
  const list = document.getElementById("projects");
  list.innerHTML = "";
  if (!selectedProjectId && data.length > 0) selectedProjectId = data[0].id;
  data.forEach((project) => list.appendChild(projectCard(project)));
  const selected = data.find((p) => p.id === selectedProjectId);
  document.getElementById("selected-title").innerText = selected ? "Tareas · " + selected.name : "Tareas por proyecto";
}

async function loadTasks() {
  const panel = document.getElementById("tasks");
  panel.innerHTML = "";
  if (!selectedProjectId) return;
  const data = await api("/api/projects/" + selectedProjectId + "/tasks");
  data.forEach((task) => panel.appendChild(taskCard(task)));
  if (data.length === 0) panel.innerHTML = "<small>Sin tareas en este proyecto.</small>";
}

document.getElementById("create-project").onclick = async () => {
  const name = document.getElementById("project-name").value.trim();
  const description = document.getElementById("project-description").value.trim();
  if (!name) return;
  await api("/api/projects", { method: "POST", body: JSON.stringify({ name, description }) });
  document.getElementById("project-name").value = "";
  document.getElementById("project-description").value = "";
  await loadProjects();
};

document.getElementById("create-task").onclick = async () => {
  if (!selectedProjectId) return;
  const idea = document.getElementById("task-idea").value.trim();
  const scope = document.getElementById("task-scope").value.trim();
  if (!idea || !scope) return;
  await api("/api/projects/" + selectedProjectId + "/tasks", { method: "POST", body: JSON.stringify({ idea, scope }) });
  document.getElementById("task-idea").value = "";
  document.getElementById("task-scope").value = "";
  await loadTasks();
  await loadProjects();
};

document.getElementById("refresh").onclick = async () => {
  await loadProjects();
  await loadTasks();
};

(async function init() {
  try {
    await loadProjects();
    await loadTasks();
  } catch (error) {
    document.getElementById("tasks").innerHTML = "<small>Error cargando panel: " + error.message + "</small>";
  }
})();
</script>
</body>
</html>`,
    { headers: { "content-type": "text/html; charset=utf-8" } },
  );
}

export default {
  async fetch(request) {
    ensureDefaultProject();
    const url = new URL(request.url);

    if (url.pathname === "/") return htmlPage();
    if (url.pathname === "/api/health") return json({ status: "ok", platform: "cloudflare-workers" });
    if (url.pathname === "/api/agents") return json(DEFAULT_AGENTS);

    if (url.pathname === "/api/projects" && request.method === "GET") {
      return json(Array.from(projects.values()).map(projectSummary));
    }

    if (url.pathname === "/api/projects" && request.method === "POST") {
      const body = await request.json();
      if (!body?.name) return json({ error: "name es obligatorio" }, 400);
      return json(createProject(body), 201);
    }

    const projectTasksMatch = url.pathname.match(/^\/api\/projects\/([^/]+)\/tasks$/);
    if (projectTasksMatch && request.method === "GET") {
      const projectId = projectTasksMatch[1];
      if (!projects.has(projectId)) return json({ error: "project no encontrado" }, 404);
      return json(Array.from(tasks.values()).filter((task) => task.project_id === projectId).map(taskSummary));
    }

    if (projectTasksMatch && request.method === "POST") {
      const projectId = projectTasksMatch[1];
      const body = await request.json();
      if (!body?.idea || !body?.scope) return json({ error: "idea y scope son obligatorios" }, 400);
      const task = createTask(body, projectId);
      if (!task) return json({ error: "project no encontrado" }, 404);
      return json(task, 201);
    }

    const taskMatch = url.pathname.match(/^\/api\/tasks\/([^/]+)$/);
    if (taskMatch && request.method === "GET") {
      const task = tasks.get(taskMatch[1]);
      if (!task) return json({ error: "task no encontrada" }, 404);
      return json(taskSummary(task));
    }

    const executeMatch = url.pathname.match(/^\/api\/tasks\/([^/]+)\/execute$/);
    if (executeMatch && request.method === "POST") {
      const task = tasks.get(executeMatch[1]);
      if (!task) return json({ error: "task no encontrada" }, 404);
      return json(executeTaskStep(task));
    }

    return json({ error: "not found" }, 404);
  },
};
