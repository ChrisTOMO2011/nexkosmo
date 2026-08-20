import { type FormEvent, useEffect, useState } from "react";
import { api, type Project } from "../../api/client";
import type { AuthSession } from "../../auth/session";
import { signOut } from "../../auth/session";
import { CanonicalLogo } from "../../components/brand/CanonicalLogo";
import { Button, Panel } from "../../components/ui";

export function ProjectDirectory({ session }: { session: AuthSession }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [status, setStatus] = useState("Loading Projects…");

  const reload = async () => {
    try {
      const result = await api.listProjects(session);
      setProjects(result);
      setStatus(result.length ? "" : "No Projects are available to this account.");
    } catch (reason) {
      setStatus((reason as Error).message);
    }
  };

  useEffect(() => {
    let active = true;
    void api
      .listProjects(session)
      .then((result) => {
        if (!active) return;
        setProjects(result);
        setStatus(result.length ? "" : "No Projects are available to this account.");
      })
      .catch((reason: Error) => {
        if (active) setStatus(reason.message);
      });
    return () => {
      active = false;
    };
  }, [session]);

  const create = async (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim()) return;
    try {
      await api.createProject(session, name.trim());
      setName("");
      await reload();
    } catch (reason) {
      setStatus((reason as Error).message);
    }
  };

  return (
    <div className="project-directory">
      <header>
        <CanonicalLogo />
        <Button
          variant="outlined"
          onClick={() => {
            signOut();
            window.location.reload();
          }}
        >
          Sign out
        </Button>
      </header>
      <main>
        <Panel className="project-directory__panel">
          <h1>Your Projects</h1>
          <p>Only Projects with an active Project membership are listed.</p>
          <form onSubmit={(event) => void create(event)}>
            <label htmlFor="project-name">New Project name</label>
            <input
              id="project-name"
              value={name}
              maxLength={200}
              onChange={(event) => setName(event.target.value)}
            />
            <Button type="submit" variant="outlined">
              Create Project
            </Button>
          </form>
          {status && <p role="status">{status}</p>}
          <ul className="project-list">
            {projects.map((project) => (
              <li key={project.project_id}>
                <a href={`/studio/projects/${project.project_id}/build`}>
                  <strong>{project.name}</strong>
                  <span>{project.lifecycle}</span>
                </a>
              </li>
            ))}
          </ul>
        </Panel>
      </main>
    </div>
  );
}
