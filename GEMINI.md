# GEMINI.md - HALSEN | Soluciones Industriales y Arquitectónicas

This document serves as the foundational instruction manual and context guide for any AI assistant or developer working on the **Halsen Website**. Always adhere to the architecture, style guidelines, and conventions outlined below.

---

## 1. Project Overview

HALSEN is a professional static website for an industrial wood and panel processing workshop specializing in **Precision CNC Maquila** (nesting, cutting) and **Premium Edgebanding (Enchapado de Cantos)**. The business serves designers, architects, and furniture manufacturers in Puebla, Cholula, Tlaxcalancingo, and Chipilo, Mexico.

### Core Stack
- **Static Site Generator:** [Hugo](https://gohugo.io/) (Extended Version v0.148.1+)
- **Templating:** Go HTML Templates (`layouts/`)
- **Styling:** Custom Vanilla CSS with native CSS variables (`assets/css/styles.css`). **Avoid Tailwind CSS** or custom CSS preprocessors unless explicitly requested.
- **Interactivity:** Vanilla JavaScript embedded directly in layouts (e.g., responsive menu, calculator logic).

### Key Architecture & Directory Structure
- `hugo.toml`: The global configuration file holding page metadata, site menus, and key contact params (email, phone, address).
- `content/`: Holds index content. The frontmatter of `content/_index.md` configures page-level parameters, but the homepage design is located in `layouts/index.html`.
- `layouts/`: Holds all layout templates.
  - `index.html`: Main landing page layout. Divided into Hero (with CNC simulation animation), Services, How it Works, and the interactive **Estimador de Lista de Corte (Cutlist Estimator)**.
  - `_default/baseof.html`: Standard base template loading fonts, rendering page headers, injecting partials, and linking minified/fingerprinted stylesheets.
  - `partials/`: Reusable components such as `header.html` and `footer.html`.
- `assets/css/styles.css`: The central stylesheet containing theme design variables, resets, responsive helpers, and components.
- `static/`: Contains static media files (e.g., `images/logo.svg`) and reference files like `templates/Halsen_Template_Cutlist.csv` which are copied directly to the built site root.
- `input/`: Design references and source content assets (e.g., `servicios.md` pricing sheet, logos, references).

---

## 2. Building and Running

### Prerequisites
- Go Hugo CLI (Extended version recommended).

### Commands

- **Start Local Development Server:**
  ```bash
  hugo server
  ```
  Runs a hot-reloading development server locally. Typically available at `http://localhost:1313/`.

- **Build Production Site:**
  ```bash
  hugo
  ```
  Generates the fully optimized static files into the `public/` directory.

- **Clean and Rebuild:**
  ```bash
  rm -rf public/ resources/ && hugo
  ```

---

## 3. Design System & Style Conventions

### Color Palette & CSS Variables
The aesthetic is curated to be **Natural & Premium** (Burgundy, Charcoal, Warm Gray, and Sage Green).
All colors are defined inside the `:root` pseudo-class in `assets/css/styles.css`:

| Variable Name | Hex Color | Description |
| :--- | :--- | :--- |
| `--color-wood` | `#8a1c2c` | Primary Accent: Halsen Burgundy |
| `--color-wood-dark` | `#6b121f` | Dark Burgundy: Hover state |
| `--color-wood-light` | `#f5e6e8` | Light Burgundy: Highlight |
| `--color-espresso` | `#1a1a1a` | Text Dark: Clean Charcoal |
| `--color-charcoal` | `#333333` | Text Body: Soft Charcoal |
| `--color-bg-warm` | `#fafafa` | Page Background: Off-White |
| `--color-sand` | `#f4f4f4` | Section BG: Soft Light Gray |
| `--color-border` | `#e0e0e0` | UI Borders: Muted Gray |
| `--color-sage` | `#2e7d32` | Accent/Success: Eco Green |
| `--color-sage-light`| `#e8f5e9` | Light Green: Success background |

### Typography
- **Primary / UI Font:** `Plus Jakarta Sans` via Google Fonts.
- Set `--font-sans` and `--font-serif` to `'Plus Jakarta Sans', system-ui, -apple-system, sans-serif`.

### Layout & Spacing
Always use the relative spacing scale in layouts:
- `--space-xs`: `0.5rem`
- `--space-sm`: `1rem`
- `--space-md`: `1.5rem`
- `--space-lg`: `3rem`
- `--space-xl`: `5rem`

Use modern flexbox or grid layouts. Ensure container usage utilizes `.container` (`width: 90%; max-width: 1200px; margin: 0 auto;`).

---

## 4. Development Conventions & Guidelines

### 1. Maintain Content & Layout Separation
- When creating new content sections, keep structured text elements within standard markdown files in `content/` if possible.
- If a section relies heavily on complex, highly stylized custom HTML layouts (e.g., the interactive CNC simulation or Cutlist table), implement it cleanly in `layouts/index.html` or as a new partial under `layouts/partials/` and refer to site parameters configured in `hugo.toml`.

### 2. Follow Existing UI/UX Patterns
- **No Tailwind CSS:** Style elements using semantic classes defined in `assets/css/styles.css`.
- **Responsive design:** Keep styles responsive down to mobile sizes (320px). Use mobile-first media queries if modifying structure.
- **Button styling:** Use standard `.btn .btn-primary` or `.btn .btn-outline` classes.
- **Smooth scroll:** Page navigates via anchor links (`/#services`, `/#how-it-works`, `/#quote`) to section IDs. Ensure any new sections preserve this routing approach.

### 3. Dynamic Interactive Estimator
- The landing page contains a **Cutlist Estimator (Estimador de Lista de Corte)** inside the section `#quote` of `layouts/index.html`.
- It allows inputs for panel dimension, edgebanding configurations (L1, L2, A1, A2 markers), material, and edgeband type.
- The interactive calculator is currently a simulation/prototype. If implementing the live calculation logic:
  - Keep calculations in plain Vanilla JS.
  - Read input dimensions (`Largo`, `Ancho`, `Cantidad`) and edge flags.
  - Follow pricing structure defined in `input/servicios.md`:
    - **Nesting optimization cost:** $75.00 MXN per 3 boards.
    - **Corte CNC maquila:** $10.00 MXN per minute of active cut (estimated ~100-120 MXN per board).
    - **Edgebanding (Enchapado):** From $11.50 MXN per linear meter.
- Ensure any downloadable CSV template follows the structure of `static/templates/Halsen_Template_Cutlist.csv`.

### 4. Updating Global Site Information
- Global contact parameters such as phone, email, and address should be edited strictly in `hugo.toml`. Avoid hardcoding these directly in layouts.
- Example usage in layouts: `{{ .Site.Params.contact_email }}`.
