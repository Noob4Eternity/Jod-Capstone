# Kanban Board Color Scheme

This document describes the color scheme used in the Kanban board components, which is integrated with the global theme system in `globals.css`.

## Theme Integration

All Kanban colors are defined in `app/globals.css` as CSS custom properties (variables) that support both light and dark themes automatically.

## Color Variables (Blue Light / Pink Dark Theme)

### To Do Column

- **Primary Color**: `--kanban-todo`
  - Light: `rgb(14, 165, 233)` - Sky Blue (Sky-500)
  - Dark: `rgb(255, 255, 255)` - White
- **Background**: `--kanban-todo-bg`
  - Light: `rgb(240, 249, 255)` - Very light sky blue
  - Dark: `rgb(45, 34, 43)` - Dark muted purple
- **Border**: `--kanban-todo-border`
  - Light: `rgb(224, 242, 254)` - Light sky blue
  - Dark: `rgb(84, 69, 77)` - Muted dark purple

### In Progress Column

- **Primary Color**: `--kanban-in-progress`
  - Light: `rgb(59, 130, 246)` - Blue (Blue-500)
  - Dark: `rgb(255, 182, 193)` - Light Pink
- **Background**: `--kanban-in-progress-bg`
  - Light: `rgb(239, 246, 255)` - Very light blue
  - Dark: `rgb(43, 34, 45)` - Dark purple tint
- **Border**: `--kanban-in-progress-border`
  - Light: `rgb(219, 234, 254)` - Light blue
  - Dark: `rgb(108, 83, 118)` - Muted purple

### In Review Column

- **Primary Color**: `--kanban-review`
  - Light: `rgb(37, 99, 235)` - Medium Blue (Blue-600)
  - Dark: `rgb(255, 105, 180)` - Hot Pink
- **Background**: `--kanban-review-bg`
  - Light: `rgb(239, 246, 255)` - Very light blue
  - Dark: `rgb(45, 34, 40)` - Dark with red undertone
- **Border**: `--kanban-review-border`
  - Light: `rgb(191, 219, 254)` - Light blue
  - Dark: `rgb(120, 69, 82)` - Muted dark red

### Done Column

- **Primary Color**: `--kanban-done`
  - Light: `rgb(29, 78, 216)` - Royal Blue (Blue-700)
  - Dark: `rgb(255, 20, 147)` - Deep Pink
- **Background**: `--kanban-done-bg`
  - Light: `rgb(239, 246, 255)` - Very light blue
  - Dark: `rgb(40, 34, 43)` - Dark with purple undertone
- **Border**: `--kanban-done-border`
  - Light: `rgb(147, 197, 253)` - Light blue
  - Dark: `rgb(112, 69, 103)` - Muted purple-red

## CSS Classes

The following CSS classes are available for use in components:

### Background Classes

- `.bg-kanban-todo`, `.bg-kanban-in-progress`, `.bg-kanban-review`, `.bg-kanban-done`
- `.bg-kanban-todo-bg`, `.bg-kanban-in-progress-bg`, `.bg-kanban-review-bg`, `.bg-kanban-done-bg`

### Border Classes

- `.border-kanban-todo-border`, `.border-kanban-in-progress-border`
- `.border-kanban-review-border`, `.border-kanban-done-border`

### Text Classes

- `.text-kanban-todo`, `.text-kanban-in-progress`, `.text-kanban-review`, `.text-kanban-done`

## Usage in Components

### KanbanBoard.tsx

Uses theme colors for:

- Background: `bg-background`
- Header: `bg-card`, `border-border`
- Text: `text-foreground`, `text-muted-foreground`
- Inputs: `border-input`, `focus:ring-ring`
- Loading spinner: `border-primary`

### KanbanColumn.tsx

Each column dynamically applies its color scheme:

```typescript
const styles = {
  dotColor: `bg-${column.color}`,
  bgColor: `bg-${column.color}-bg`,
  borderColor: `border-${column.color}-border`,
  textColor: `text-${column.color}`,
  headerBg: `bg-${column.color}-bg`,
};
```

### Theme Consistency

All components use semantic color tokens from the global theme:

- `background`, `foreground`
- `card`, `card-foreground`
- `border`, `input`
- `primary`, `secondary`
- `muted`, `muted-foreground`

This ensures the Kanban board automatically adapts to light/dark mode without additional code.

## Extending Colors

To add a new status column color:

1. Add CSS variables in `globals.css`:

   ```css
   :root {
     --kanban-new-status: rgb(r, g, b);
     --kanban-new-status-bg: rgb(r, g, b);
     --kanban-new-status-border: rgb(r, g, b);
   }

   .dark {
     --kanban-new-status: rgb(r, g, b);
     --kanban-new-status-bg: rgb(r, g, b);
     --kanban-new-status-border: rgb(r, g, b);
   }
   ```

2. Add utility classes:

   ```css
   .bg-kanban-new-status {
     background-color: var(--kanban-new-status);
   }
   /* ... etc */
   ```

3. Update `getStatusColor()` in `KanbanBoard.tsx`:
   ```typescript
   case 'new status': return 'kanban-new-status';
   ```
