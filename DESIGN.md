# 🎨 ParkEase — Design System & UI Guide

> **Version:** 1.0.0 | **Last Updated:** April 2026

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Spacing & Layout Grid](#spacing--layout-grid)
5. [Component Library](#component-library)
6. [Page-by-Page Design Spec](#page-by-page-design-spec)
7. [Icons & Imagery](#icons--imagery)
8. [Responsive Design](#responsive-design)
9. [Accessibility Standards](#accessibility-standards)
10. [CSS Architecture](#css-architecture)

---

## Design Philosophy

ParkEase follows **three core design principles**:

1. **Clarity First** — Users should understand slot availability and booking status at a glance. No ambiguity.
2. **Speed of Action** — The path from "I need parking" to "I have a booking" should require as few taps/clicks as possible.
3. **Trust through Professionalism** — Clean, consistent UI that signals reliability. People trust apps that feel polished.

---

## Color Palette

Define all colors as CSS custom properties in `base.css`:

```css
:root {
  /* Primary Brand */
  --color-primary:        #1A3C5E;   /* Deep Navy — authority, trust */
  --color-primary-light:  #2A5F8F;   /* Hover states */
  --color-primary-dark:   #0F2340;   /* Active/pressed */

  /* Accent */
  --color-accent:         #F97316;   /* Vibrant Orange — action, availability */
  --color-accent-light:   #FB923C;
  --color-accent-dark:    #EA6A08;

  /* Status Colors */
  --color-success:        #16A34A;   /* Available slots */
  --color-warning:        #CA8A04;   /* Near-full / expiring soon */
  --color-danger:         #DC2626;   /* Booked / errors */
  --color-info:           #0284C7;   /* Info badges */

  /* Neutrals */
  --color-bg:             #F8FAFC;   /* Page background */
  --color-surface:        #FFFFFF;   /* Cards, modals */
  --color-border:         #E2E8F0;   /* Subtle borders */
  --color-text-primary:   #0F172A;   /* Headings */
  --color-text-secondary: #475569;   /* Body copy */
  --color-text-muted:     #94A3B8;   /* Placeholders, labels */
}
```

### Slot Status Color Mapping

| Status        | Color Variable       | Hex       | Usage                      |
|---------------|----------------------|-----------|----------------------------|
| Available     | `--color-success`    | `#16A34A` | Green slot cards           |
| Booked        | `--color-danger`     | `#DC2626` | Red slot cards             |
| Reserved (you)| `--color-primary`    | `#1A3C5E` | Navy — your own booking    |
| Maintenance   | `--color-text-muted` | `#94A3B8` | Gray — out of service      |

---

## Typography

```css
/* Import in base.css */
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=Inter:wght@400;500&display=swap');

:root {
  --font-display: 'Sora', sans-serif;    /* Headings, nav brand */
  --font-body:    'Inter', sans-serif;   /* Body text, forms */
  --font-mono:    'JetBrains Mono', monospace; /* Slot numbers, codes */

  /* Scale */
  --text-xs:   0.75rem;   /* 12px — labels, badges */
  --text-sm:   0.875rem;  /* 14px — form hints, captions */
  --text-base: 1rem;      /* 16px — body copy */
  --text-lg:   1.125rem;  /* 18px — sub-headings */
  --text-xl:   1.25rem;   /* 20px */
  --text-2xl:  1.5rem;    /* 24px — section headings */
  --text-3xl:  1.875rem;  /* 30px — page titles */
  --text-4xl:  2.25rem;   /* 36px — hero headings */
}
```

### Typography Rules

- **Page Titles** — `Sora`, 700 weight, `--text-3xl`, `--color-text-primary`
- **Section Headings** — `Sora`, 600 weight, `--text-xl`
- **Body Copy** — `Inter`, 400 weight, `--text-base`, line-height: 1.6
- **Slot Numbers** — `JetBrains Mono`, `--text-sm`, uppercase
- **Buttons** — `Sora`, 600 weight, letter-spacing: 0.02em

---

## Spacing & Layout Grid

```css
:root {
  /* Spacing Scale (multiples of 4px) */
  --space-1:  0.25rem;   /* 4px */
  --space-2:  0.5rem;    /* 8px */
  --space-3:  0.75rem;   /* 12px */
  --space-4:  1rem;      /* 16px */
  --space-6:  1.5rem;    /* 24px */
  --space-8:  2rem;      /* 32px */
  --space-12: 3rem;      /* 48px */
  --space-16: 4rem;      /* 64px */

  /* Layout */
  --container-max:  1200px;
  --sidebar-width:  260px;
  --navbar-height:  64px;

  /* Border Radius */
  --radius-sm:  4px;
  --radius-md:  8px;
  --radius-lg:  12px;
  --radius-xl:  16px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm:  0 1px 3px rgba(0,0,0,0.08);
  --shadow-md:  0 4px 12px rgba(0,0,0,0.10);
  --shadow-lg:  0 8px 24px rgba(0,0,0,0.12);
  --shadow-focus: 0 0 0 3px rgba(26,60,94,0.25);
}
```

### Grid System

- **Desktop:** 12-column grid, `--container-max: 1200px`, `gap: 24px`
- **Tablet:** 8-column, 768px–1199px
- **Mobile:** 4-column, <768px, full-width cards

---

## Component Library

### Buttons

```html
<!-- Primary CTA -->
<button class="btn btn-primary">Reserve Slot</button>

<!-- Secondary / Outline -->
<button class="btn btn-outline">View Details</button>

<!-- Danger -->
<button class="btn btn-danger">Cancel Booking</button>

<!-- Sizes -->
<button class="btn btn-primary btn-sm">Small</button>
<button class="btn btn-primary btn-lg">Large</button>
```

```css
.btn {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: var(--text-sm);
  letter-spacing: 0.02em;
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.15s ease;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}
.btn-primary:hover { background: var(--color-primary-light); }
.btn-primary:focus { box-shadow: var(--shadow-focus); }

.btn-outline {
  background: transparent;
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.btn-outline:hover {
  background: var(--color-primary);
  color: white;
}
```

---

### Cards

```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Slot A-04</h3>
    <span class="badge badge-success">Available</span>
  </div>
  <div class="card-body">
    <p>Floor 1 · Standard · $2.50/hr</p>
  </div>
  <div class="card-footer">
    <button class="btn btn-primary btn-sm">Reserve</button>
  </div>
</div>
```

---

### Slot Grid Tile

```css
.slot-tile {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  font-weight: 700;
  cursor: pointer;
  border: 2px solid transparent;
  transition: transform 0.1s ease, box-shadow 0.1s ease;
}

.slot-tile.available  { background: #DCFCE7; color: var(--color-success); border-color: #BBF7D0; }
.slot-tile.booked     { background: #FEE2E2; color: var(--color-danger);  border-color: #FECACA; cursor: not-allowed; }
.slot-tile.mine       { background: #DBEAFE; color: var(--color-primary); border-color: #BFDBFE; }
.slot-tile:hover:not(.booked) { transform: scale(1.05); box-shadow: var(--shadow-md); }
```

---

### Form Inputs

```css
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
}

.form-label {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-input {
  padding: var(--space-3) var(--space-4);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-family: var(--font-body);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  background: var(--color-surface);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: var(--shadow-focus);
}

.form-input.error { border-color: var(--color-danger); }
.form-hint        { font-size: var(--text-xs); color: var(--color-text-muted); }
.form-error       { font-size: var(--text-xs); color: var(--color-danger); }
```

---

### Navigation Bar

```
┌────────────────────────────────────────────────────────────┐
│  🅿  ParkEase          Dashboard  Slots  History     [User ▼]│
└────────────────────────────────────────────────────────────┘
```

- Height: `64px`, background: `--color-primary`, sticky top
- Logo: White `Sora` font + parking icon
- Nav links: White, 500 weight, hover underline with `--color-accent`
- User avatar dropdown: initials in circle

---

### Badges / Status Pills

```html
<span class="badge badge-success">Available</span>
<span class="badge badge-danger">Booked</span>
<span class="badge badge-warning">Expiring Soon</span>
<span class="badge badge-info">Confirmed</span>
```

```css
.badge {
  display: inline-block;
  padding: 2px var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.badge-success { background: #DCFCE7; color: var(--color-success); }
.badge-danger  { background: #FEE2E2; color: var(--color-danger);  }
.badge-warning { background: #FEF9C3; color: var(--color-warning); }
.badge-info    { background: #E0F2FE; color: var(--color-info);    }
```

---

## Page-by-Page Design Spec

### 1. Landing Page (`/`)

**Goal:** Convert visitors to sign-ups. Inspire trust.

| Zone         | Content                                        | Design Notes                          |
|--------------|------------------------------------------------|---------------------------------------|
| Hero         | Headline + CTA buttons                         | Full-width, gradient bg, parking photo|
| Stats Bar    | "500+ Slots · 24/7 Access · 3 Locations"       | 3-column, icon + number + label       |
| How It Works | 3-step visual process                          | Numbered cards with icons             |
| Footer       | Links, copyright                               | Dark bg (`--color-primary-dark`)      |

---

### 2. Register/Login Pages (`/register`, `/login`)

**Goal:** Fast, frictionless entry. No clutter.

- Centered card layout, max-width `420px`
- Form fields: Username, Email, Password
- Clear validation error states below each field
- "Already have an account? Login" toggle link

---

### 3. User Dashboard (`/dashboard`)

**Goal:** One-glance overview of user's parking activity.

**Layout: Sidebar + Main Content**

```
┌────────────────────────────────────────────────────────┐
│ Nav                                                    │
├──────────────┬─────────────────────────────────────────┤
│ Sidebar      │  Stat Cards (row)                       │
│  - Dashboard │  ┌──────┐ ┌──────┐ ┌──────┐           │
│  - My Slots  │  │Active│ │Total │ │Hours │           │
│  - History   │  └──────┘ └──────┘ └──────┘           │
│  - Settings  │                                         │
│              │  Current Booking Card                   │
│              │  ┌──────────────────────────────────┐  │
│              │  │ Slot A-04 · Expires 14:30        │  │
│              │  │ [Extend]   [Cancel]              │  │
│              │  └──────────────────────────────────┘  │
│              │                                         │
│              │  Recent Reservations Table              │
└──────────────┴─────────────────────────────────────────┘
```

---

### 4. Slot Map / Reserve Page (`/slots`)

**Goal:** Let users visually browse and pick a slot.

- Floor selector tabs (Floor 1, 2, 3...)
- Interactive grid of `slot-tile` components
- Sidebar panel: slot details + booking time picker on selection
- Legend: Available / Booked / Your Booking / Maintenance

---

### 5. Admin Dashboard (`/admin`)

**Goal:** Manage slots, view all reservations, handle users.

- Stats row: Total Slots, Active Bookings, Today's Revenue, Users
- Slot Management Table with inline edit/status toggle
- Reservations Table with filters (date, user, status)
- User Management Table

---

## Icons & Imagery

Use **Lucide Icons** (SVG-based, MIT license):

```html
<!-- Include via CDN -->
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>

<!-- Usage -->
<i data-lucide="map-pin"></i>     <!-- Location -->
<i data-lucide="clock"></i>        <!-- Time -->
<i data-lucide="car"></i>          <!-- Parking -->
<i data-lucide="check-circle"></i> <!-- Success -->
<i data-lucide="x-circle"></i>     <!-- Error -->
<i data-lucide="calendar"></i>     <!-- Date picker -->
<i data-lucide="shield"></i>       <!-- Admin/Security -->
```

---

## Responsive Design

### Breakpoints

```css
/* Mobile First */
/* Base:   < 640px  — single column, stacked */
/* sm:    640px+   — 2 columns */
/* md:    768px+   — sidebar appears */
/* lg:   1024px+   — full layout */
/* xl:   1280px+   — max container */
```

### Mobile Adaptations

| Component    | Desktop           | Mobile                        |
|--------------|-------------------|-------------------------------|
| Sidebar      | Fixed left panel  | Hamburger → slide-in drawer   |
| Slot Grid    | 10 cols × n rows  | 5 cols × n rows, smaller tiles|
| Stat Cards   | 4 in a row        | 2×2 grid                      |
| Tables       | Full columns      | Horizontal scroll             |
| Navbar       | Full links        | Logo + hamburger              |

---

## Accessibility Standards

- All interactive elements reachable via **Tab key**
- Focus rings: `box-shadow: var(--shadow-focus)` — never `outline: none` without replacement
- Color contrast: all text meets **WCAG AA** (4.5:1 ratio minimum)
- Slot tiles: `aria-label="Slot A-04 — Available"`, `role="button"`
- Form inputs: always paired with `<label>` via `for`/`id`
- Status badges: include text, never color-only
- Images: always include descriptive `alt` text

---

## CSS Architecture

Follow **BEM naming** with a utility layer:

```
base.css         → CSS variables, resets, body styles
components.css   → .btn, .card, .badge, .form-*, .slot-tile
layout.css       → .navbar, .sidebar, .container, .grid-*
pages/
  dashboard.css  → .stat-card, .booking-banner
  slots.css      → .slot-grid, .slot-panel, .floor-tabs
  auth.css       → .auth-card, .auth-toggle
utilities.css    → .text-center, .mt-4, .hidden, .sr-only
```

**Load order in `base.html`:**

```html
<link rel="stylesheet" href="/static/css/base.css">
<link rel="stylesheet" href="/static/css/layout.css">
<link rel="stylesheet" href="/static/css/components.css">
{% block extra_css %}{% endblock %}  <!-- Page-specific CSS -->
```

---

*ParkEase Design System — Maintained by the Product & Engineering Team*