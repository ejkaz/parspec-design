# Anti-AI-Slop Rules — Parspec Edition

Universal rules that distinguish "designed by a Parspec brand-aware human" from "default LLM output." These rules apply regardless of which brand version is active. Palette-specific forbidden colors / fonts live in `design-model.yaml`'s `avoid:` block — read those at runtime.

> Adapted from `nexu-io/open-design/craft/anti-ai-slop.md` (which adapts `referodesign/refero_skill`), tightened for Parspec's Construction Materials Distributor ICP.

## Cardinal sins (severity: error)

These are the patterns parspec-craft blocks at P0 (must-fix):

1. **Consumer-purple as accent** — `#6366F1`, `#4F46E5`, `#4338CA`, `#3730A3`, `#8B5CF6`, `#7C3AED`, `#A855F7`, and the entire `#6270F2` Tailwind-indigo / Linear / Notion register. This is the textbook AI tell. Parspec primary CTA is Brand Orange `#FFA72B` — non-negotiable. 0 of 27 ICP brands surveyed use this color family.

2. **Trust gradient** — purple → blue, blue → cyan, indigo → pink, mesh-gradient hero backgrounds. A flat surface plus intentional type beats this every time. Parspec's hero motif is single-color orange line illustrations on dark, not gradient atmospherics.

3. **Emoji as feature icon** — `✨`, `🚀`, `🎯`, `⚡`, `🔥`, `💡`, etc. inside `<h*>`, `<button>`, `<li>`, or `class*="icon"`. Use 1.6–2px-stroke monoline SVG with `currentColor`. Parspec icon system: Lucide-style outline icons in Brand Orange on dark surfaces.

4. **Non-Montserrat display font** — `h1`, `h2`, `h3`, hero copy must use Montserrat. No `Inter`, `Roboto`, `Arial`, `system-ui`, `Helvetica`, `SF Pro` in display rules. Body and mono are also Montserrat (single-family discipline). The locked `--font-family` is Montserrat — use it.

5. **Rounded card with colored left-border accent** — the canonical "AI dashboard tile" shape. Drop either the radius or the left border. (Square-cornered callouts with a left border are fine — that's a different pattern.)

6. **Invented metrics** — "10× faster", "99.9% uptime", "3× more productive" without a real source. Parspec has real metrics: $22.5B quoted, 300+ distributor customers, 52% faster bid cycle. Use those.

7. **Filler copy** — `lorem ipsum`, `feature one / two / three`, `placeholder text`, `sample content`. An empty section is a design problem to solve with composition, not by inventing words.

8. **Pastels in any structural role** — `#FFEDD4` Peach, `#E2E2FF` Lavender, `#C7C7FF` Soft Violet, `#C6E1DA` Soft Green, `#FFE4E7` Rose. 0 of 27 ICP brands surveyed use these. They read as wedding stationery / café menu / wellness app, not industrial software.

9. **Colored customer logos in social-proof rows** — Sonepar, Graybar, Rexel, Wesco, etc. must be rendered as grayscale logos in social-proof / partner / customer strips. Reduces visual noise; lets the eye land on the Brand Orange CTA.

10. **CTA color other than Brand Orange `#FFA72B`** — primary CTA monopoly is non-negotiable. Secondary buttons can be ghost / outline in any approved secondary, but the primary action color is locked.

## Soft tells (severity: warning)

- **Standard "Hero → Features → Pricing → FAQ → CTA" sequence with no variation** — the AI-template skeleton. Introduce at least one unconventional move (full-bleed customer-quote section, comparison-against-status-quo pricing, inline mini-product-demo).

- **External placeholder image CDNs** (`unsplash.com`, `placehold.co`, `picsum.photos`) — fragile and obvious. Use grayscale named placeholders or honest "[image]" text blocks.

- **More than ~12 raw hex values outside `:root` / CSS variables** — tokens were not honoured. Move to `var(--...)` referencing design-model.yaml semantics.

- **`var(--accent)` (Brand Orange) used 6+ times in the rendered body** — cap at 2 visible uses per screen so the action signal stays a signal.

- **Decorative blob / wave / mesh-gradient SVG backgrounds** — meaningless geometry. Parspec backgrounds are flat dark with deliberate motifs (corner brackets, quarter circles, orange line illustrations).

- **Perfect symmetric layout with no visual tension** — alternating density (one tight section, one breathing section) reads as intentional.

## Polish tells (severity: info)

- Sections without semantic landmark roles (`<section>`, `<header>`, `<main>`).
- Charts where 5 secondaries appear adjacent without dividers and 2+ are dark — boundary visibility suffers.
- CSS that hardcodes rgba alpha values instead of using a tint from `design-model.yaml`'s tints palette.

## How to add soul without breaking the rules

Aim for **~80% Parspec brand discipline + ~20% distinctive choice**. The 20% should live in:

- One bold visual move per surface — a Brand Orange treatment, a corner-bracket placement, a single quarter-circle anchor.
- Voice — a button that says "Quote it" beats one that says "Get started." Parspec speaks the trade's vocabulary.
- One micro-detail that proves a Parspec employee touched it — an MEP industry-aware label, a real customer name in a tooltip, a kbd shortcut hint.

If a Sonepar VP screenshots the artifact and recognizes it as "from the Parspec people" — soul is present. If they think it could be from any vertical-AI startup — it's a template.
