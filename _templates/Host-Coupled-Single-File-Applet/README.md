# Host-Coupled Single-File Applet

Paste this boilerplate directly into their editor or feed it to an LLM coding agent as their structural scaffold. It includes built-in hooks for window geometry, cursor velocity, and optional ambient mic volume, plus a clean requestAnimationFrame physics loop, and a lightweight `postMessage` bridge so it works seamlessly inside an MCP UI host or Web Applet runtime.

## Manifest

The schema registers the applet with an MCP server or Web Applet host. The **Actions** are framed as environmental disturbances ("gusts") that the model can trigger, while **State** exposes the mobile's passive equilibrium.

Why are Actions and States relevant in traditional applications?

## Minimal MCP Server Wrapper

If students submit both `index.html` and `applet.manifest.json` to the **shared studio folder**, a lightweight Python MCP server can expose every student's useless applet as both a **UI Resource** (`ui://...`) and an ambient tool for any MCP-compatible chat host: