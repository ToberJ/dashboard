# Visualization Hub

Research project dashboards — data, training campaigns, and policy rollout clips.

Live: https://toberj.github.io/dashboard/

Built from `~/Desktop/x2_sonic_dashboard/` (sources + build.py); this repo holds the generated static site only.

## Dexterous Guitar workspace

The Guitar page is generated separately from `tools/guitar/build.py` and
`tools/guitar/page.template.html`; its CSS and JavaScript are in `assets/guitar/`.
It adds one card to the hub without changing other projects.

From the local dex-project root, rebuild with its existing Python environment:

```bash
source env.sh
.pixi/envs/default/bin/python website/dashboard/tools/guitar/build.py --project-root .
```

The builder needs the saved retarget manifest, audit reports, and robot-only
simulation renders in that project. It does not run simulation or publish.
`assets/guitar/project.json` contains the reviewed plan/status and SHA-256
references to source reports; `evidence.json` contains the compact clip evidence.
These are dated snapshots, not live process status. Updating the plan requires
editing the source and rebuilding; task filters do not change completion state.
Raw MoCap files are not redistributed.
