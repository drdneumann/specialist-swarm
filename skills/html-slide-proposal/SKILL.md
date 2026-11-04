---
name: html-slide-proposal
description: Turn a finished proposal, deal summary, or report into a single self-contained, animated HTML slide deck that opens in any browser. Every slide fits the screen with no scrolling and no cut-off content. Use when the deliverable should be a presentable HTML file instead of a Word document.
---

# HTML Slide Proposal

Produce ONE file, `outputs/proposal-response.html`. No external assets, no CDN, no frameworks. Plain HTML, CSS, and JS in a single file.

Start from `reference-template.html` (bundled with this skill, invented example data for a fictional customer). Keep its engine and styling; replace the slide content with the real proposal.

## The one rule that matters: nothing may be cut off

- Fixed stage of **1280 x 720 px**, scaled with `transform: scale(min(innerWidth/1280, innerHeight/720))` and centred. Because the whole stage scales, content cannot overflow at any window size.
- One slide = one screen. **No scrolling inside a slide, ever.** If content does not fit, split it across two slides or cut words. Never shrink text below the limits below to make it fit.
- Safe area: 72 px left and right, 48 px top, **72 px bottom** (reserved for the navigation bar). Nothing may extend below y = 648.

## Content budget per slide

| Element | Limit |
|---|---|
| Title | 1 line, max ~50 characters |
| Cards on one slide | max 6 (grid of 3x2 or 2x2) |
| Table rows | max 11, one line each where possible |
| Body text | min 12.5 px, max ~45 words per card |
| Bullets | max 5 |
| Timeline steps | max 7, description under 12 words |

## Slide structure (adapt to the proposal, keep the order)

1. Title: customer, headline price, date, key facts
2. Executive summary: exactly three cards
3. Customer need: 3 headline numbers + prioritised needs
4. Capability fit: table with coverage bars
5. Competitive positioning: one card per named rival
6. Delivery plan: horizontal timeline
7. Pricing: animated bars per year + total + alternative
8. Commercial asks: table of ask vs our position
9. Contract positions: one card per clause, severity tag, summary card
10. Risks: card per risk with mitigation line
11. Next steps: numbered rows
12. Closing: one call to action, contact

Cut slides that have no content in the source. Never pad.

## Interaction and animation (all required)

- Navigation: arrow keys, space, PageUp/PageDown, Home/End, mouse wheel (debounced), swipe, click on dots, prev/next buttons, `F` for fullscreen. Update `location.hash` so a slide is linkable.
- Per-slide entrance: elements with class `a` and `--i` stagger in on activation.
- Number counters run when a slide becomes active (`data-to`, optional `data-pre` / `data-suf`).
- Bars (coverage, pricing) animate from 0 when the slide becomes active and reset when it is left.
- Hover states on cards and table rows. Progress bar at the top, dot indicator and `NN / NN` counter at the bottom.
- Animated particle network on a canvas behind the stage. Respect `prefers-reduced-motion` if adding anything beyond the template.

## Brand rules (Accenture)

- Palette: purple `#A100FF`, dark purple `#7500C0`, light tints `#F5EEFF` `#E6DCFF` `#C2A3FF`, neutrals `#000000` `#818180` `#CFCFCF` `#F1F1EF` `#FFFFFF`. Green is allowed only for "fully met" status.
- **Banned:** navy (`#0E2841`, `#1F4E79`, `#203864`), orange `#E97132`, teal `#0F9ED5`.
- Font: Graphik if available, otherwise **Arial only**. Banned: Barlow, Aptos, Calibri, GT Walsheim.
- Wording: use "Reinvention". Never "Technology Strategy" or "Strategy & Consulting".
- All text at least 10 px on the 1280 x 720 stage; body text at least 12.5 px.

## Content integrity

- Use only facts from the source proposal and specialist inputs. **Never invent** statistics, prices, customer names, references, or certifications.
- Anything missing: write `[PLACEHOLDER: description]` on the slide and say so in the final message.
- If the Critic returned REVISE, apply the revisions before generating. If it returned STOP, do not generate the deck.

## Verify before declaring done

Open the file in a browser (or headless) at 1280 x 720, step through every slide, and confirm for each one that the bottom of the lowest content element is at or above y = 648 and the right edge is at or below x = 1208, and that no content overlaps the title. Snippet for the console:

```js
(async()=>{
  const st=document.getElementById('stage').getBoundingClientRect(), sc=st.width/1280, out=[];
  for(let i=0;i<document.querySelectorAll('.slide').length;i++){
    go(i); await new Promise(r=>setTimeout(r,1500));
    let b=0,r2=0;
    document.querySelectorAll('.slide')[i].querySelectorAll('*').forEach(el=>{
      if(el.closest('.glow')||el.classList.contains('glow')||el.classList.contains('grid'))return;
      const r=el.getBoundingClientRect(); if(!r.width||!r.height)return;
      b=Math.max(b,(r.bottom-st.top)/sc-648); r2=Math.max(r2,(r.right-st.left)/sc-1208);
    });
    out.push((i+1)+': bottom+'+Math.round(b)+' right+'+Math.round(r2));
  }
  return out.join('\n');
})()
```

Every line must read `bottom+0 right+0` (rounding noise of 1 px is fine). Anything larger means that slide loses content: split or trim it, then re-run.

Report what you checked and any `[PLACEHOLDER]` left in the deck.
