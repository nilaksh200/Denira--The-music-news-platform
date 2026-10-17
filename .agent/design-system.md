# Denira Desktop — Design System Specification

## 1. Design Philosophy
**Denira Desktop** is an ultra-focused, immersive music news deck engineered exclusively for high-resolution desktop viewports. It borrows the rapid editorial consumption pattern of Inshorts and translates it into a premium, cinematic desktop interface with fluid vertical deck transitions and balanced 50/50 horizontal split cards.

---

## 2. Global Viewport & Canvas Architecture
- **Root Dimensions**: Strictly locked to `100vw` by `100vh` (with fallback `100dvh`).
- **Scroll Behavior**: `overflow: hidden` on `html`, `body`, and container root. No native browser scrollbar is permitted.
- **Backdrop Canvas**: Rich dark aesthetic with subtle radial vignettes (`radial-gradient(ellipse at center, #171717 0%, #0a0a0a 100%)`).
- **Centering**: The active card is perfectly centered both vertically and horizontally in the viewport (`display: flex; align-items: center; justify-content: center;`).

---

## 3. Design Tokens & Color Palette

| Token Role | Tailwind Class | Hex / RGBA Value | Usage Context |
| :--- | :--- | :--- | :--- |
| **App Canvas Background** | `bg-neutral-950` | `#0a0a0a` | Global viewport background |
| **Card Surface** | `bg-neutral-900` | `#171717` | Card body container and right editorial pane |
| **Elevated Surface** | `bg-neutral-800` | `#262626` | Badges, pills, metadata chips, tooltip surfaces |
| **Primary Borders** | `border-neutral-800` | `#262626` | Card outer boundary, subtle split separators |
| **Muted Borders** | `border-neutral-800/90` | `rgba(38, 38, 38, 0.9)` | Outer card edge definition with depth |
| **Primary Text** | `text-neutral-50` | `#fafafa` | Card headlines, primary values |
| **Editorial Body Text** | `text-neutral-300` | `#d4d4d4` | 50–60 word summary paragraphs |
| **Muted Metadata** | `text-neutral-500` | `#737373` | Timestamps, secondary labels, shortcuts |
| **Brand Accent (Primary)** | `text-rose-500` | `#f43f5e` | Active genre highlights, cursor indicators |
| **Brand Accent (Surface)** | `bg-rose-600/20` | `rgba(225, 29, 72, 0.2)` | Active genre pill backgrounds, subtle glows |
| **Accent Hover** | `bg-rose-500` / `hover:bg-rose-600` | `#e11d48` | Primary CTA buttons, link arrows |

---

## 4. Card Geometry & Anatomy

### 4.1 Outer Card Enclosure
- **Fixed Dimensions**: `width: 900px` (`w-[900px]`), `height: 520px` (`h-[520px]`).
- **Corner Curvature**: `rounded-2xl` (`border-radius: 1rem` / `16px`).
- **Border Treatment**: `border border-neutral-800/90`.
- **Elevation / Shadow**: `shadow-2xl` (augmented with subtle ambient drop glow `0 25px 50px -12px rgba(0, 0, 0, 0.7)`).
- **Clipping**: `overflow-hidden` to maintain strict boundary radius on media and editorial panes.

```
+---------------------------------------------------------------------------------------+
|  [ Card Container: 900px x 520px | rounded-2xl | border-neutral-800/90 | shadow-2xl ]  |
|                                                                                       |
|  +-----------------------------------+  +------------------------------------------+  |
|  | LEFT: Media Visual (50% | 450px)  |  | RIGHT: Editorial Panel (50% | 450px)      |  |
|  |                                   |  |                                          |  |
|  | - Full bleed cover photography    |  | - Top Meta: [GENRE PILL] [TIME] [SOURCE]  |  |
|  | - Dark gradient overlay           |  | - Headline: < 12 words (text-xl font-bold)|  |
|  |   (to-t from-neutral-950/80)      |  | - Summary: 50-60 words (leading-relaxed)  |  |
|  | - Subtle bottom caption/artist    |  | - Bottom Bar: [Read Full Story ->]       |  |
|  |                                   |  |               [Source Domain Pill]       |  |
|  +-----------------------------------+  +------------------------------------------+  |
+---------------------------------------------------------------------------------------+
```

### 4.2 Left Media Visual Container (50% / 450px width)
- **Dimensions**: `w-1/2 h-full relative overflow-hidden bg-neutral-950`.
- **Image Behavior**: `object-cover w-full h-full transform transition-transform duration-700 hover:scale-105`.
- **Atmospheric Overlay**: Multi-stop gradient overlay (`bg-gradient-to-t from-neutral-950/90 via-neutral-950/30 to-transparent`) to ensure contrast against any background lighting and preserve deep black card framing.
- **Fallback Imagery**: High-contrast geometric music visualizer or waveform gradient in case of missing or broken remote imagery.

### 4.3 Right Editorial Container (50% / 450px width)
- **Dimensions**: `w-1/2 h-full flex flex-col justify-between p-8 bg-neutral-900`.
- **Layout Stacking**:
  1. **Header Metadata Row**:
     - **Genre Pill**: `text-xs font-semibold px-2.5 py-1 rounded-full text-rose-500 bg-rose-600/20 border border-rose-500/30 tracking-wide uppercase`.
     - **Timestamp**: `text-xs text-neutral-500 font-mono` (e.g., `2h ago`).
     - **Source Chip**: `text-xs text-neutral-400 bg-neutral-800/80 px-2 py-0.5 rounded border border-neutral-700/50`.
  2. **Editorial Core**:
     - **Headline**: Semantic `<h2>`, strictly `< 12 words`, `text-xl lg:text-2xl font-bold tracking-tight text-neutral-50 leading-snug`.
     - **Summary**: Strictly **50–60 words**, `text-sm text-neutral-300 leading-relaxed font-normal antialiased`.
  3. **Footer Action Row**:
     - **Outbound Source Link**: Interactive button or link badge directing to original publication:
       - Style: `inline-flex items-center gap-2 text-xs font-medium text-neutral-300 hover:text-white bg-neutral-800 hover:bg-neutral-700 px-4 py-2 rounded-lg transition-colors border border-neutral-700/60`.
       - Attributes: `target="_blank" rel="noopener noreferrer"`.
     - **Keyboard Indicator**: Subtle muted chip showing navigation key hints (e.g., `[↓ / Spc] Next`).

---

## 5. Interaction Handlers & Navigation Directives

### 5.1 Vertical Deck Transition Model
The interface behaves as a single stacked deck of cards with smooth snap physics:
- **Card Transition Animation**: 300ms–400ms cubic-bezier ease (`cubic-bezier(0.16, 1, 0.3, 1)`).
- **Deck Offset**: Cards smoothly translate on the Y-axis (`translate-y-[calc(-100%*index)]` or dedicated Virtual Deck stack).

### 5.2 Input Modalities & Event Handlers
1. **Mouse Wheel / Trackpad**:
   - Debounced vertical delta listener (`wheel` event with ~350ms throttle).
   - Downward scroll threshold (`deltaY > 30`) triggers `nextCard()`.
   - Upward scroll threshold (`deltaY < -30`) triggers `prevCard()`.
2. **Keyboard Navigation (`keydown`)**:
   - `ArrowDown` or `Spacebar` or `j` -> Advance to next card.
   - `ArrowUp` or `k` -> Return to previous card.
   - `Home` -> Jump to deck top (card 0).
3. **On-Screen Navigation Controls**:
   - Floating discrete pagination indicators on the right margin (dots / card counter e.g., `14 / 120`).
   - Minimalist vertical arrow chevron controls (`Next` / `Previous`) for explicit mouse clicks.
