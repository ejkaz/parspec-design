#!/usr/bin/env python3
"""
parspec-review — design jury dispatcher

Invokes 4 vision-capable jurors per slide in parallel, then runs an aggregator
to produce review/visual-r1.yaml.

Two backends, selectable via --mode:
  api          — Anthropic SDK + asyncio. Needs ANTHROPIC_API_KEY (env or
                 macOS Keychain entry `claude-anthropic-claude-api`). Faster,
                 cheaper for one-off runs once a key is onboarded.
  subscription — Claude Code CLI subprocesses (`claude -p`). Uses the user's
                 existing Claude Code subscription auth — no new credential
                 needed. Slightly slower per call (subprocess overhead).
                 Default; works out of the box if `claude` CLI is on PATH.

Usage:
    python3 run-design-jury.py /path/to/deck-dir [--mode subscription|api]
                                                 [--juror-model sonnet|opus]
                                                 [--aggregator-model sonnet|opus]
                                                 [--concurrency 10]
                                                 [--slides 01,13,22]

Required deck-dir layout:
    deck-dir/
    ├── plan.yaml
    ├── slides/slide-NN.html (+ slide-NN.manifest.yaml, .v2/.v3 variants OK)
    └── render/slide-NN.png  (1920×1080)

Outputs:
    deck-dir/review/jury/<juror>/slide-NN.yaml   (raw juror outputs)
    deck-dir/review/visual-r1.yaml               (aggregated verdict, parspec-slides
                                                  Round 5b/5c compatible)
"""

import argparse
import asyncio
import base64
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
REF_DIR = SKILL_DIR / "references"

JURORS = ["composition", "dataviz", "brand-fidelity", "anti-slop"]


# ─── Prompt construction (shared across backends) ──────────────────

def load_juror_prompts() -> dict[str, str]:
    return {j: (REF_DIR / f"juror-{j}.md").read_text() for j in JURORS}


def load_aggregator_prompt() -> str:
    return (REF_DIR / "aggregator-prompt.md").read_text()


def latest_manifest(slides_dir: Path, nn: str) -> str | None:
    for v in ("v3", "v2", ""):
        suffix = f".{v}" if v else ""
        p = slides_dir / f"slide-{nn}{suffix}.manifest.yaml"
        if p.exists():
            return p.read_text()
    return None


def load_design_model(repo_root: Path) -> str:
    p = repo_root / "plugins/parspec-design/skills/parspec-design/design-model.yaml"
    return p.read_text() if p.exists() else "# design-model.yaml not found"


def extract_plan_slide(plan_yaml: str, nn: str) -> str:
    lines = plan_yaml.splitlines()
    out: list[str] = []
    in_slide = False
    target = f"position: {int(nn)}"
    for line in lines:
        if target in line and "- position:" in line:
            in_slide = True
            out.append(line)
            continue
        if in_slide:
            if line.startswith("  - position:") or line.startswith("slides:"):
                break
            out.append(line)
    return "\n".join(out) if out else f"# no plan entry for slide {nn}"


def build_user_text(juror: str, slide_id: str, manifest: str | None,
                    plan_excerpt: str, design_model: str) -> str:
    """Build the user-content text for a juror call (image attached separately)."""
    if juror == "anti-slop":
        return (
            f"Review this slide (slide_id={slide_id}). Apply the Anti-AI-Slop "
            "Critic rubric from your system prompt. Output ONLY the YAML block, "
            "no prose."
        )
    if juror == "brand-fidelity":
        return (
            f"Review slide_id={slide_id}.\n\n"
            f"Manifest:\n```yaml\n{manifest or '# none'}\n```\n\n"
            f"design-model.yaml excerpt:\n```yaml\n{design_model[:8000]}\n```\n\n"
            "Apply the Brand Fidelity Critic rubric from your system prompt. "
            "Output ONLY the YAML block."
        )
    # composition, dataviz
    return (
        f"Review slide_id={slide_id}.\n\n"
        f"Manifest:\n```yaml\n{manifest or '# none'}\n```\n\n"
        f"plan.yaml excerpt:\n```yaml\n{plan_excerpt}\n```\n\n"
        "Apply your juror rubric from the system prompt. Output ONLY the YAML block."
    )


# ─── Backends ──────────────────────────────────────────────────────

class ApiBackend:
    """Anthropic SDK backend. Requires API key."""

    def __init__(self, model: str):
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            sys.exit("ERROR: --mode api requires `pip install anthropic`")

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            try:
                sys.path.insert(0, str(Path.home() / ".claude/skills/_shared"))
                from claude_secrets import keychain_get  # type: ignore
                api_key = keychain_get("claude-anthropic-claude-api")
            except Exception:
                sys.exit(
                    "ERROR: --mode api needs ANTHROPIC_API_KEY (env) or Keychain "
                    "entry `claude-anthropic-claude-api`. Onboard via add-api-key skill."
                )

        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def call_juror(self, juror: str, juror_prompt: str, png_path: Path,
                         user_text: str, sem: asyncio.Semaphore) -> str:
        async with sem:
            png_b64 = base64.b64encode(png_path.read_bytes()).decode()
            content = [
                {"type": "image", "source": {
                    "type": "base64", "media_type": "image/png", "data": png_b64,
                }},
                {"type": "text", "text": user_text},
            ]
            for attempt in range(3):
                try:
                    resp = await self.client.messages.create(
                        model=self.model,
                        max_tokens=2500,
                        system=juror_prompt,
                        messages=[{"role": "user", "content": content}],
                    )
                    return resp.content[0].text
                except Exception as e:
                    if attempt == 2:
                        return _error_yaml(juror, str(e))
                    await asyncio.sleep(2 ** attempt)
            return _error_yaml(juror, "exhausted retries")

    async def call_aggregator(self, prompt: str, body: str) -> str:
        resp = await self.client.messages.create(
            model=self.model,
            max_tokens=16000,
            system=prompt,
            messages=[{"role": "user", "content": body}],
        )
        return resp.content[0].text


class SubscriptionBackend:
    """Claude Code CLI subprocess backend. Uses subscription auth."""

    def __init__(self, model: str):
        if shutil.which("claude") is None:
            sys.exit("ERROR: --mode subscription needs `claude` CLI on PATH.")
        self.model = model  # accepts "sonnet"/"opus" aliases or full IDs

    async def _run_claude(self, system_prompt: str, user_text: str,
                          png_path: Path | None, max_tokens_hint: int = 2500) -> str:
        """Invoke `claude -p` in a subprocess. Image is passed via @path reference
        in the user prompt — Claude Code resolves @-paths to file attachments."""
        # Stage the system prompt to a temp file (simpler than embedding)
        with tempfile.TemporaryDirectory() as td:
            sys_path = Path(td) / "system.md"
            sys_path.write_text(system_prompt)

            if png_path:
                user_with_image = f"{user_text}\n\n[Attached image] @{png_path.absolute()}"
            else:
                user_with_image = user_text

            cmd = [
                "claude", "-p", user_with_image,
                "--model", self.model,
                "--system-prompt-file", str(sys_path),
                "--output-format", "text",
                "--no-session-persistence",
            ]
            for attempt in range(3):
                try:
                    proc = await asyncio.to_thread(
                        subprocess.run, cmd,
                        capture_output=True, text=True, timeout=180,
                    )
                    if proc.returncode == 0 and proc.stdout.strip():
                        return proc.stdout
                    err = (proc.stderr or proc.stdout or "non-zero exit").strip()[:200]
                    if attempt == 2:
                        return f"# ERROR (subscription): {err}"
                    await asyncio.sleep(2 ** attempt)
                except subprocess.TimeoutExpired:
                    if attempt == 2:
                        return "# ERROR: subprocess timeout 180s"
                    await asyncio.sleep(2 ** attempt)
                except Exception as e:
                    if attempt == 2:
                        return f"# ERROR: {e}"
                    await asyncio.sleep(2 ** attempt)
            return "# ERROR: exhausted retries"

    async def call_juror(self, juror: str, juror_prompt: str, png_path: Path,
                         user_text: str, sem: asyncio.Semaphore) -> str:
        async with sem:
            return await self._run_claude(juror_prompt, user_text, png_path)

    async def call_aggregator(self, prompt: str, body: str) -> str:
        return await self._run_claude(prompt, body, png_path=None,
                                      max_tokens_hint=16000)


def _error_yaml(juror: str, msg: str) -> str:
    return (
        f"# ERROR: {msg}\n"
        f"juror: {juror}\nverdict: PASS\nfindings: []\n"
        f"notes: 'juror call failed after retries'\n"
    )


# ─── Orchestration ─────────────────────────────────────────────────

async def main() -> None:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=__doc__)
    parser.add_argument("deck_dir", type=Path)
    parser.add_argument("--mode", choices=["api", "subscription"], default="subscription",
                        help="Backend to use (default: subscription = Claude Code CLI auth)")
    parser.add_argument("--juror-model", default="sonnet",
                        help="Model for jurors. 'sonnet'/'opus' aliases or full ID. "
                             "(default: sonnet)")
    parser.add_argument("--aggregator-model", default="sonnet",
                        help="Model for aggregator. (default: sonnet)")
    parser.add_argument("--concurrency", type=int, default=8,
                        help="Max in-flight calls (subscription default lower — subprocess overhead)")
    parser.add_argument("--slides", type=str, default="",
                        help="Comma-separated slide IDs (default: all rendered slides)")
    args = parser.parse_args()

    deck_dir: Path = args.deck_dir.resolve()
    render_dir = deck_dir / "render"
    slides_dir = deck_dir / "slides"
    review_dir = deck_dir / "review"
    jury_dir = review_dir / "jury"
    review_dir.mkdir(exist_ok=True)
    jury_dir.mkdir(exist_ok=True)

    plan_yaml = (deck_dir / "plan.yaml").read_text()

    # design-model.yaml — walk up to find .claude-plugin marker
    repo_root = SCRIPT_DIR
    while repo_root.parent != repo_root and not (repo_root / ".claude-plugin").exists():
        repo_root = repo_root.parent
    design_model = load_design_model(repo_root) if (repo_root / ".claude-plugin").exists() \
        else "# design-model.yaml not found"

    juror_prompts = load_juror_prompts()
    aggregator_prompt = load_aggregator_prompt()

    if args.mode == "api":
        backend: ApiBackend | SubscriptionBackend = ApiBackend(args.juror_model)
    else:
        backend = SubscriptionBackend(args.juror_model)

    if args.slides:
        slide_ids = [s.strip().zfill(2) for s in args.slides.split(",") if s.strip()]
    else:
        slide_ids = [f"{n:02d}" for n in range(1, 56)
                     if (render_dir / f"slide-{n:02d}.png").exists()]

    n_calls = len(slide_ids) * len(JURORS)
    print(f"Mode:         {args.mode}")
    print(f"Juror model:  {args.juror_model}")
    print(f"Aggregator:   {args.aggregator_model}")
    print(f"Slides:       {len(slide_ids)}")
    print(f"Total juror calls: {n_calls}")
    print(f"Concurrency:  {args.concurrency}")
    print()

    sem = asyncio.Semaphore(args.concurrency)
    tasks = []
    for nn in slide_ids:
        png_path = render_dir / f"slide-{nn}.png"
        manifest = latest_manifest(slides_dir, nn)
        plan_excerpt = extract_plan_slide(plan_yaml, nn)
        for juror in JURORS:
            user_text = build_user_text(juror, nn, manifest, plan_excerpt, design_model)
            tasks.append((nn, juror, backend.call_juror(
                juror, juror_prompts[juror], png_path, user_text, sem,
            )))

    print(f"Dispatching {len(tasks)} juror calls...")
    completed = 0
    juror_outputs: dict[str, dict[str, str]] = {}

    # gather coroutines while preserving (slide_id, juror) tagging
    async def tagged(slide_id: str, juror: str, coro):
        nonlocal completed
        result = await coro
        completed += 1
        if completed % 10 == 0 or completed == len(tasks):
            print(f"  {completed}/{len(tasks)} jurors complete")
        return slide_id, juror, result

    results = await asyncio.gather(*[tagged(s, j, c) for s, j, c in tasks])

    for slide_id, juror, output in results:
        out_dir = jury_dir / juror
        out_dir.mkdir(exist_ok=True)
        # Strip markdown fences the model often wraps YAML in
        cleaned = output.strip()
        if cleaned.startswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[1:])
        if cleaned.endswith("```"):
            cleaned = "\n".join(cleaned.split("\n")[:-1])
        cleaned = cleaned.rstrip() + "\n"
        (out_dir / f"slide-{slide_id}.yaml").write_text(cleaned)
        juror_outputs.setdefault(slide_id, {})[juror] = cleaned

    print(f"\nAll juror outputs persisted to {jury_dir}/<juror>/slide-NN.yaml")

    # Aggregator
    print("Running aggregator...")
    body_blocks = []
    for slide_id in sorted(juror_outputs.keys()):
        body_blocks.append(f"=== Slide {slide_id} ===")
        for juror in JURORS:
            body_blocks.append(f"--- juror: {juror} ---")
            body_blocks.append(juror_outputs[slide_id].get(juror, "# missing"))
    body = "\n".join(body_blocks)

    if args.aggregator_model != args.juror_model:
        if args.mode == "api":
            backend = ApiBackend(args.aggregator_model)
        else:
            backend = SubscriptionBackend(args.aggregator_model)

    verdict = await backend.call_aggregator(aggregator_prompt, (
        "Aggregate these per-slide juror outputs into a single visual-r1.yaml verdict. "
        "Apply the clustering and severity-times-agreement scoring from your system prompt. "
        "Output ONLY valid YAML conforming to verdict-schema.yaml — NO markdown fences, "
        "NO prose preamble, just raw YAML starting with `visual_review_round:`.\n\n" + body
    ))
    # Strip any markdown fences the model added anyway
    verdict = verdict.strip()
    if verdict.startswith("```"):
        verdict = "\n".join(verdict.split("\n")[1:])
    if verdict.endswith("```"):
        verdict = "\n".join(verdict.split("\n")[:-1])
    out = review_dir / "visual-r1.yaml"
    out.write_text(verdict.rstrip() + "\n")
    print(f"Verdict: {out}")


if __name__ == "__main__":
    asyncio.run(main())
