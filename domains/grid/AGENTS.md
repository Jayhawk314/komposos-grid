# KOMPOSOS Grid Local-Agent Playbook

This folder exposes a local agent API for the grid map. The browser chat calls
Python running beside the repository, and that server calls grounded JSON tools
instead of inventing numbers.

## Start

From the repository root:

```bash
python -m domains.grid.agent_server --port 8000
```

Then open:

```text
http://127.0.0.1:8000/network_map.html
```

For terminal-agent or debugging use:

```bash
python -m domains.grid.agent_tools prompt
python -m domains.grid.agent_tools manifest
```

The map's `AI` tab talks to `/api/grid/chat`. The prompt/manifest commands are
still useful if a separate terminal coding agent wants to inspect the same tool
contract.

## Grounding Contract

- Use tool JSON for quantitative or structural grid claims.
- Include the returned `summary` and `provenance` in the answer.
- Keep measured data, proxy evidence, and screening lenses separate.
- Say when a requested claim is outside the available tools.
- Do not invent balancing-authority facts, flows, costs, topology, years, or
  evidence.

## Tools

All commands run from the repository root. `--year YEAR` is optional and must
appear before the subcommand, for example:

```bash
python -m domains.grid.agent_tools --year 2025 ba PJM
```

Useful calls:

```bash
python -m domains.grid.agent_tools ba PJM
python -m domains.grid.agent_tools tie PJM NYIS
python -m domains.grid.agent_tools path CISO PJM --k 3
python -m domains.grid.agent_tools similar PJM --top 5
python -m domains.grid.agent_tools bottlenecks --top 10
python -m domains.grid.agent_tools seam
python -m domains.grid.agent_tools whatif --cut PJM-NYIS,MISO-SWPP
python -m domains.grid.agent_tools gaps --top 5
```

Every normal tool returns JSON with:

- `summary`: short human-readable result.
- `provenance`: where the computation comes from and what it is not.
- `result`: structured values for deeper explanation.

## Map Chat Integration

`docs/network_map.html` remains a static GitHub Pages artifact when published,
so it cannot run Python by itself there. Locally, run `agent_server.py`; the same
page then becomes a connected app and the `AI` tab sends chat messages to
`/api/grid/chat`.

If the API is not running, the panel shows a fallback telling the user to start
the local bridge.
