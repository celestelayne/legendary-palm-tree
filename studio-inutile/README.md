## Gallery Host Overview

[`gallery-host.html`](./gallery-host.html) is a static gallery and interaction harness for student-made applets. It displays each applet in a sandboxed iframe, provides a conversational control panel, and coordinates communication between the host and embedded applets with browser `postMessage()` events.

When the page loads, it scans `./submissions/`, reads each folder's `applet.manifest.json`, and creates a gallery card for the configured entrypoint. Each applet can receive an `applet:action` message such as:

```js
{
  type: "applet:action",
  action: "disturb_air",
  params: { impulse: 0.25, temperature: "cool" }
}
```

Applets can report their current state back to the host with an `applet:state` message. The host uses that state to update each card's status dot, agitation level, angle, and idle timer.

The chat panel translates message length and punctuation into air-current parameters. Question marks reverse the impulse, exclamation marks increase it and select a warmer response, and long messages select a humid response. Presets provide a few fixed examples.

The **Spawn Reference Applet** button creates a self-contained canvas applet directly in the page, so the gallery can be tested even when `./submissions/` is empty.

### How to Use the Gallery Host During Studio Pin-Ups

1. **Automatic Discovery:** Start a local static server in your studio folder (`python3 -m http.server 8000`) and open `http://localhost:8000/gallery-host.html`. The harness parses the local directory index of `./submissions/` and mounts every student’s folder automatically.
2. **Live Critique Coupling:** As you type critique notes or prompts into the **Conversational Host Simulator** on the right, the host converts message length, question marks, and exclamation points into directional `disturb_air` `postMessage` payloads—letting you watch the entire class’s sculptures react simultaneously to the discussion.
3. **Passive Equilibrium Readout:** Each plinth displays a live status dot (`still`, `drifting`, `turbulent`) and idle timer driven by the student applet’s outbound `applet:state` messages.

### Validation Script

The Python CLI validator (`validate_submissions.py`) audits every student folder in `./submissions/` before pin-up or MCP registration.

It uses Python’s standard library (`json`, `re`, `pathlib`, `sys`) so you can run it immediately without installing packages, while also checking for the zero-explicit-UI studio constraint and `postMessage` bridge hooks.

---

# Gallery Host

This is a static “gallery host” for displaying and interacting with small student-made applets.

## Overall layout
[gallery-host.html](./gallery-host.html) has two areas:
- **Left:** a gallery wall containing embedded applets.
- **Right:** a simulated conversational host that sends prompts to those applets.

Each applet is loaded into a sandboxed `<iframe>`.

### What happens on load

At the bottom, `scanSubmissionsDirectory()` runs automatically.

It:
1. Fetches `./submissions/.`
2. Reads the directory listing produced by a local web server.
3. Finds student folders.
4. Loads each folder’s `applet.manifest.json`.
5. Creates a gallery card using `createPlinth()`.
6. Loads the applet’s configured `index.html` into an iframe.

A manifest might provide:

```json
{
  "applet": {
    "name": "Example Applet",
    "author": "alice",
    "description": "A small kinetic sculpture.",
    "entrypoint": "index.html"
  }
}
```

It needs to be run through a local server, such as:

```bash
python3 -m http.server 8000
```

Then open: `http://localhost:8000/studio-inutile/gallery-host.html`

Opening the file directly usually will not work because browsers block the directory `fetch()` calls.

### How applets communicate

The host and applets communicate with browser `postMessage()` events.

The host sends messages through `sendDraft()`:

```json
{
  type: "applet:action",
  action: "disturb_air",
  params: {
    impulse: 0.25,
    temperature: "cool"
  }
}
```

An applet can listen for that message and react visually.

The applet can send state back to the host:

```json
{
  type: "applet:state",
  state: {
    agitationLevel: "drifting",
    idleSeconds: 3,
    angleRadians: 0.42
  }
}
```

The host listens for those events near `window.addEventListener('message', ...)` and updates each card’s status dot and telemetry text.

### How the chat controls work

When you type a message:

- A question mark makes the impulse negative.
- An exclamation mark increases its strength and selects "warm".
- Long messages select "humid".
- Message length affects the impulse magnitude.

That converted data is passed to `sendDraft()`, either to one selected applet or to all applets.
