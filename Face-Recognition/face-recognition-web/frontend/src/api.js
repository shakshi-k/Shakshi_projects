const BASE = "/api";

async function handle(res) {
  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      msg = typeof body.detail === "string" ? body.detail : msg;
    } catch {}
    throw new Error(msg);
  }
  return res.json();
}

export const getPeople = () => fetch(`${BASE}/people`).then(handle);

export const registerPerson = (name, files) => {
  const form = new FormData();
  form.append("name", name);
  files.forEach((f) => form.append("files", f));
  return fetch(`${BASE}/people`, { method: "POST", body: form }).then(handle);
};

export const deletePerson = (name) =>
  fetch(`${BASE}/people/${encodeURIComponent(name)}`, { method: "DELETE" }).then(handle);

export const recognize = (file, threshold) => {
  const form = new FormData();
  form.append("file", file);
  form.append("threshold", threshold);
  return fetch(`${BASE}/recognize`, { method: "POST", body: form }).then(handle);
};
