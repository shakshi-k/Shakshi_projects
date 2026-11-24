import { deletePerson } from "../api.js";

export default function People({ people, onChange }) {
  const remove = async (name) => {
    if (!window.confirm(`Delete ${name}?`)) return;
    await deletePerson(name);
    onChange();
  };

  return (
    <div className="card">
      <h3>Registered people ({people.length})</h3>
      {people.length === 0 && <p className="muted">No one registered yet.</p>}
      <ul className="list">
        {people.map((p) => (
          <li key={p.name}>
            <span><b>{p.name}</b> <span className="muted">({p.photos} photos)</span></span>
            <button className="danger" onClick={() => remove(p.name)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
