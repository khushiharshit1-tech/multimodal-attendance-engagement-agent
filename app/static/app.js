
let currentSession = null;

const $ = (id) => document.getElementById(id);

const esc = (s) =>
  String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  }[c]));

async function api(url, options = {}) {
  const res = await fetch(url, options);

  if (!res.ok) {
    const data = await res.json().catch(() => ({
      detail: "Request failed"
    }));
    throw new Error(data.detail || "Request failed");
  }

  return res;
}

async function refresh() {
  const [studentsRes, sessionsRes] = await Promise.all([
    api("/api/students"),
    api("/api/sessions")
  ]);

  const students = await studentsRes.json();
  const sessions = await sessionsRes.json();

  $("studentCount").textContent = students.length;
  $("sessionCount").textContent = sessions.length;

  renderStudents(students);
  renderHistory(sessions);

  if (sessions.length) {
    const latest = sessions[0];
    $("trackCount").textContent = latest.tracks.length;
    $("activityLabel").textContent =
      latest.visual_activity?.label || "—";
  } else {
    $("trackCount").textContent = "0";
    $("activityLabel").textContent = "—";
  }
}

function renderStudents(students) {
  $("studentList").innerHTML = students.length
    ? students.map((s) => `
      <div class="student-item">
        <span>
          <b>${esc(s.name)}</b>
          <small>${esc(s.roll_number)}</small>
        </span>
        <button class="delete" data-delete="${esc(s.id)}">
          Remove
        </button>
      </div>
    `).join("")
    : '<p class="muted">Add students before assigning detected tracks.</p>';

  document.querySelectorAll("[data-delete]").forEach((b) => {
    b.onclick = async () => {
      try {
        await api(`/api/students/${b.dataset.delete}`, {
          method: "DELETE"
        });
        await refresh();
      } catch (err) {
        alert(err.message);
      }
    };
  });
}

function renderHistory(sessions) {
  $("historyList").innerHTML = sessions.length
    ? sessions.map((s) => `
      <div class="history-item">
        <span>
          <b>${esc(s.filename)}</b><br>
          <small>
            ${esc(s.created_at)} ·
            ${s.tracks.length} sustained track(s)
          </small>
        </span>
        <button data-open="${esc(s.id)}">
          View session →
        </button>
      </div>
    `).join("")
    : '<p class="muted">No sessions processed yet.</p>';

  document.querySelectorAll("[data-open]").forEach((b) => {
    b.onclick = () => loadSession(b.dataset.open);
  });
}

$("studentForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  try {
    await api("/api/students", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: $("studentName").value,
        roll_number: $("rollNumber").value
      })
    });

    $("studentName").value = "";
    $("rollNumber").value = "";

    await refresh();
  } catch (err) {
    alert(err.message);
  }
});

$("uploadForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = $("videoFile").files[0];

  if (!file) {
    alert("Please select a video first.");
    return;
  }

  $("error").classList.add("hidden");
  $("progress").classList.remove("hidden");
  $("processBtn").disabled = true;

  const form = new FormData();
  form.append("video", file);
  form.append("min_presence_seconds", $("presence").value);

  try {
    const res = await api("/api/sessions/process", {
      method: "POST",
      body: form
    });

    currentSession = await res.json();

    await renderSession(currentSession);
    await refresh();

    $("results").scrollIntoView({
      behavior: "smooth"
    });
  } catch (err) {
    $("error").textContent = err.message;
    $("error").classList.remove("hidden");
  } finally {
    $("progress").classList.add("hidden");
    $("processBtn").disabled = false;
  }
});

async function loadSession(id) {
  const res = await api(`/api/sessions/${id}`);
  currentSession = await res.json();

  await renderSession(currentSession);

  $("results").scrollIntoView({
    behavior: "smooth"
  });
}

async function renderSession(session) {
  const students = await (await api("/api/students")).json();

  $("results").classList.remove("hidden");

  $("resultMeta").textContent =
    `${session.filename} · ${session.duration_seconds}s video · ` +
    `${session.sampled_frames} sampled frames · ` +
    `${session.tracks.length} sustained track(s)`;

  $("trackRows").innerHTML = session.tracks.length
    ? session.tracks.map((t) => {
        const assigned =
          session.assignments?.[String(t.track_id)] || "";

        const opts = students.map((s) => `
          <option value="${esc(s.id)}"
            ${assigned === s.id ? "selected" : ""}>
            ${esc(s.name)}
            ${s.roll_number ? " · " + esc(s.roll_number) : ""}
          </option>
        `).join("");

        return `
          <tr>
            <td><b>#${t.track_id}</b></td>
            <td>${t.first_seen}s</td>
            <td>${t.last_seen}s</td>
            <td>${t.observed_seconds}s</td>
            <td>
              <select data-track="${t.track_id}">
                <option value="">Choose student…</option>
                ${opts}
              </select>
            </td>
            <td class="${assigned ? "status" : "pending"}">
              ${assigned ? "Present" : "Needs identification"}
            </td>
          </tr>
        `;
      }).join("")
    : `
      <tr>
        <td colspan="6">
          No sustained person tracks found.
          Try a clearer, wider classroom video.
        </td>
      </tr>
    `;

  document.querySelectorAll("[data-track]").forEach((sel) => {
    sel.onchange = async () => {
      if (!sel.value) return;

      try {
        await api("/api/sessions/assign", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            session_id: session.id,
            track_id: Number(sel.dataset.track),
            student_id: sel.value
          })
        });

        await loadSession(session.id);
        await refresh();
      } catch (err) {
        alert(err.message);
      }
    };
  });

  $("insight").innerHTML = `
    <b>Visual activity estimate:</b>
    ${esc(session.visual_activity?.label || "Not available")}
    <br>
    <span>${esc(session.visual_activity?.note || "")}</span>
  `;

  $("csvBtn").onclick = () => {
    window.location.href =
      `/api/sessions/${session.id}/attendance.csv`;
  };
}

refresh().catch((err) => {
  console.error("Dashboard loading error:", err);
});
