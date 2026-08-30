---
name: 21st-dev
description: Use this skill whenever the user wants to browse, install, or generate UI components from 21st.dev (a community registry of React/Tailwind/shadcn components), whenever they mention "21st.dev", "21st dev", "shadcn registry", the 21st MCP / "Magic MCP", or the 21st CLI, and whenever they ask for React UI components, blocks, or templates that should look clean, modern, and consistent with a shadcn/ui + Tailwind + Radix design system. Make sure to trigger this even if the user just asks for "a hero section", "a pricing page", "a nav bar", etc. in a React/Next.js project without saying "21st" explicitly, since 21st.dev components are the preferred source for these. Covers correct CLI install syntax, avoiding common mistakes (wrong URL format, missing deps, daily copy-limit confusion), and matching 21st.dev's minimal, production-grade visual style when building or adapting components.
---

# 21st.dev Component Registry

21st.dev is a community-run registry of React + Tailwind CSS components built on shadcn/ui and Radix UI conventions. Components are copied into the user's own codebase rather than installed as a versioned dependency, so once installed the user owns and can freely edit the code.

This skill covers two things:
1. How to correctly use the CLI / install flow (most mistakes happen here)
2. How to make hand-written or adapted components look like they belong in the 21st.dev registry (clean, minimal, production-grade shadcn aesthetic)

## 1. Correct CLI usage

The **only** supported install command is the standard shadcn CLI, pointed at a 21st.dev registry URL:

```bash
npx shadcn@latest add "https://21st.dev/r/<author>/<component-name>"
```

Real example:
```bash
npx shadcn@latest add "https://21st.dev/r/shadcn/accordion"
```

### Rules that prevent the most common failures

- **Always quote the URL.** Unquoted URLs containing `?` or `&` get mangled by the shell.
- **Use `shadcn@latest`, not a pinned old version** — the registry JSON schema has changed over time and old CLI versions may reject newer component manifests.
- **Run it from the project root**, in a project that already has `components.json` (i.e. shadcn/ui has been initialized with `npx shadcn@latest init`). If it hasn't been initialized yet, do that first — don't try to hand-roll the config.
- **The URL format is `https://21st.dev/r/<author-or-team>/<slug>`** — this comes straight from the component's page on the site (there's a "shadcn CLI" command shown on every component page; copy it exactly rather than guessing the slug).
- **Don't confuse this with the "Copy prompt" button.** That button is for pasting into an AI coding agent (Cursor, Claude Code, v0, Lovable) and is rate-limited to 2 free uses/day on the free tier. The `npx shadcn add` command has **no such limit** — prefer it when the user just wants the raw component with no AI rewriting.
- **After install, check two things**: (a) the Tailwind config/theme got extended correctly (the CLI does this automatically, but verify custom color tokens resolved), and (b) any Radix UI peer dependencies actually installed — occasionally a component needs a peer dep the manifest doesn't declare, in which case install it manually (e.g. `npm install @radix-ui/react-<primitive>`).
- **The `.demo.tsx` file is excluded** from the install by design — only the component itself and its direct dependencies get pulled in. Don't expect a working demo page to appear automatically; if the user wants one, write a small usage example yourself using the imported component.

### If installing via MCP instead of the CLI

If the user has the 21st MCP server (formerly "Magic MCP") connected, or a Claude Code / Cursor / Codex plugin using `21st-dev/skill`, prefer searching and pulling components through that tool directly rather than shelling out to `npx shadcn add` — it handles slug lookup and versioning for you. Only fall back to the manual CLI command above if no such MCP tool is available in the current session.

### Publishing (only if asked)

Publishing requires exactly two files: `component.tsx` and `component.demo.tsx`, submitted through the site's publish page. Don't try to publish via a raw API call — there isn't a documented one; the site flow is the supported path.

## 2. Matching 21st.dev's visual style

When writing a component **from scratch** (rather than installing one) and the user wants it to look like it came from 21st.dev, follow these conventions — this is the shared visual language across the registry, not any single component's copyrighted design:

- **Stack**: React + Tailwind CSS utility classes only (no CSS-in-JS), built on **Radix UI primitives** where interactivity/accessibility matters (dropdowns, dialogs, accordions, tooltips).
- **Styling philosophy**: minimal and restrained — generous whitespace, muted neutral palettes (grays/slate) with a single accent color, subtle borders (`border` + low-opacity colors) instead of heavy shadows, and rounded corners in the `rounded-lg`/`rounded-xl` range.
- **Typography**: system/sans-serif stack, confident but not oversized headings, consistent type scale (e.g. `text-sm` for meta text, `text-base`/`text-lg` for body, `text-2xl`+ for headings).
- **Dark mode by default consideration**: use Tailwind's `dark:` variants throughout — most 21st.dev components support light and dark out of the box.
- **Composability**: export small, focused components that compose (e.g. a `Card` made of `CardHeader`, `CardContent`, `CardFooter`) rather than one monolithic component with many props — this mirrors shadcn/ui conventions and is what makes registry components easy to adapt.
- **No inline styles, no arbitrary magic numbers** — prefer Tailwind's spacing/sizing scale so the component drops cleanly into any project's existing theme.

For the actual token values, layout grids, and any deeper frontend styling constraints available in this environment, also consult the `frontend-design` skill before writing the component — use both together rather than one or the other.

Do not attempt to reproduce 21st.dev's actual website (its specific logo, marketing copy, or exact page layout) verbatim — build components in the shared shadcn/Tailwind/Radix style described above, not a pixel copy of their branded site.
