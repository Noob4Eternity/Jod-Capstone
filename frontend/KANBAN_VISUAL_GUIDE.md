# Kanban Card Visual Guide

## Before and After Comparison

### BEFORE: Original Card Layout
```
┌─────────────────────────────────────┐
│ Task Title          [⋯ Menu]        │ ← Entire card draggable
│                                     │    Menu button in corner
│ Task description text here...       │
│                                     │
│ [medium] [Overdue]                  │
│                                     │
│ #tag1 #tag2                         │
│                                     │
│ 👤 John  📅 Dec 25  🕐 Dec 20      │
└─────────────────────────────────────┘
         cursor-move (everywhere)
```

### AFTER: Enhanced Card Layout
```
┌─────────────────────────────────────┐
│ Task Title           [⋮ Drag]      │ ← Drag handle only (shows on hover)
│                                     │    Rest of card = click to view
│ Task description text here...       │
│                                     │
│ [medium] [Overdue]                  │
│                                     │
│ #tag1 #tag2                         │
│                                     │
│ 👤 John  📅 Dec 25  🕐 Dec 20      │
└─────────────────────────────────────┘
  cursor-pointer (card body)
  cursor-move (drag handle only)
```

## Interaction States

### 1. Default State (Not Hovering)
```
┌─────────────────────────────────────┐
│ Task Title                          │ ← No drag handle visible
│ Task description text here...       │    Card is clickable
└─────────────────────────────────────┘
```

### 2. Hover State
```
┌─────────────────────────────────────┐
│ Task Title           [⋮ Drag]      │ ← Drag handle appears!
│ Task description text here...       │    Opacity: 0 → 1
│                                     │    Smooth transition
└─────────────────────────────────────┘
     ↑ Hover effect: shadow-md
```

### 3. Dragging State
```
┌─────────────────────────────────────┐
│ Task Title           [⋮ Drag]      │ ← Card appears faded
│ Task description text here...       │    50% opacity
└─────────────────────────────────────┘    Slight rotation (2deg)
```

### 4. Clicked State (Modal Opens)
```
Background Overlay (50% black, blurred)
    ┌───────────────────────────────────────────────┐
    │                                               │
    │          TASK DETAILS MODAL                   │
    │                                               │
    │  [✏️ Edit] [🗑️ Delete] [✕ Close]             │
    │  ─────────────────────────────────────────    │
    │                                               │
    │  🔵 Task Title                                │
    │  Task ID: abc123...                           │
    │                                               │
    │  [MEDIUM Priority] [Overdue]                  │
    │                                               │
    │  DESCRIPTION                                  │
    │  Full task description here...                │
    │                                               │
    │  👤 Assignee: John Doe                        │
    │  📅 Due: December 25, 2024                    │
    │  🕐 Created: December 1, 2024                 │
    │  🕐 Updated: December 20, 2024                │
    │                                               │
    │  🏷️ TAGS                                      │
    │  [#frontend] [#bug] [#urgent]                 │
    │                                               │
    │  ACCEPTANCE CRITERIA                          │
    │  1. Criterion one                             │
    │  2. Criterion two                             │
    │  3. Criterion three                           │
    │                                               │
    │  ⏱️ ESTIMATED HOURS: 8 hours                  │
    │                                               │
    │  [Close] [Edit Task]                          │
    └───────────────────────────────────────────────┘
```

## User Flow Diagrams

### Flow 1: Viewing Task Details
```
User hovers card
       ↓
Drag handle appears (fade in)
       ↓
User clicks card body (not handle)
       ↓
Modal opens with full details
       ↓
User reviews information
       ↓
User clicks Close / Backdrop / ESC
       ↓
Modal closes (fade out)
```

### Flow 2: Moving a Task
```
User hovers card
       ↓
Drag handle appears (fade in)
       ↓
User clicks & holds drag handle
       ↓
Card becomes semi-transparent + rotates
       ↓
User drags to new column
       ↓
Column highlights (drop zone indicator)
       ↓
User releases mouse
       ↓
Card drops in new column
       ↓
Database updates status
       ↓
Card animates to position
```

### Flow 3: Editing from Modal
```
User clicks card
       ↓
Modal opens
       ↓
User clicks "Edit Task" button
       ↓
Modal closes
       ↓
Edit modal/mode opens (future)
       ↓
User makes changes
       ↓
User saves
       ↓
Card updates with new data
```

### Flow 4: Deleting from Modal
```
User clicks card
       ↓
Modal opens
       ↓
User clicks Delete button
       ↓
Confirmation dialog appears
       ↓
User confirms deletion
       ↓
Task deleted from database
       ↓
Modal closes
       ↓
Card disappears with animation
       ↓
Column count updates
```

## Component Communication

```
KanbanBoard (Parent)
    │
    ├── State: isDetailsModalOpen
    ├── State: selectedTask
    │
    ├──→ TaskDetailsModal
    │    │
    │    ├── Props: isOpen, task, onEdit, onDelete, onClose
    │    │
    │    └── Actions:
    │         ├── onEdit → handleTaskEdit → console.log (for now)
    │         ├── onDelete → handleTaskDelete → deleteTask(id)
    │         └── onClose → setIsDetailsModalOpen(false)
    │
    └──→ KanbanColumn
         │
         ├── Props: onTaskClick
         │
         └──→ KanbanCard
              │
              ├── Props: onClick
              │
              └── Events:
                   ├── onClick → handleCardClick → props.onClick(task)
                   └── onDragStart (from handle) → setDragData
```

## CSS Classes Breakdown

### Drag Handle (.drag-handle)
```css
.drag-handle {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  padding: 0.25rem;
  opacity: 0;                    /* Hidden by default */
  cursor: move;                  /* Move cursor on hover */
  transition: opacity 0.2s;      /* Smooth fade in/out */
}

.group:hover .drag-handle {
  opacity: 1;                    /* Visible on card hover */
}
```

### Card States
```css
/* Base Card */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: box-shadow 0.2s;
}

/* Hover State */
.card:hover {
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

/* Dragging State */
.card.dragging {
  opacity: 0.5;
  transform: rotate(2deg);
}

/* Overdue State */
.card.overdue {
  border-color: rgb(252 165 165);  /* red-300 */
  background: rgb(254 242 242);     /* red-50 */
}

/* Dark Mode Overdue */
.dark .card.overdue {
  background: rgb(69 10 10 / 0.2);  /* red-950/20 */
}
```

### Modal Animation
```css
@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-content {
  animation: modalFadeIn 0.2s ease-out;
}
```

## Theme Colors Reference

### Light Theme
- Card Background: `#FFFFFF` (white)
- Card Border: `#E0E6EB` (light gray)
- Text: `#1C2636` (dark gray)
- Muted Text: `#677378` (medium gray)
- Hover Background: `#EEF2F6` (very light gray)

### Dark Theme
- Card Background: `#18181B` (dark gray)
- Card Border: `#303036` (medium dark gray)
- Text: `#EDDEE6` (light pinkish)
- Muted Text: `#BEA7B3` (muted pink)
- Hover Background: `#54454D` (dark muted purple)

## Accessibility Features

### Keyboard Navigation (Current)
- ✅ Modal closes on backdrop click
- ✅ Buttons have focus states
- ⚠️ TODO: ESC key to close modal
- ⚠️ TODO: Tab navigation through modal
- ⚠️ TODO: Enter key to open card details

### Screen Readers
- ✅ Semantic HTML structure
- ✅ Title attributes on interactive elements
- ✅ Alt text on icons (via lucide-react)
- ⚠️ TODO: ARIA labels for drag handle
- ⚠️ TODO: ARIA live region for status updates

### Visual Affordances
- ✅ Clear cursor changes (pointer vs move)
- ✅ Hover effects on all interactive elements
- ✅ Color contrast meets WCAG AA standards
- ✅ Icon + text for important actions
- ✅ Visual feedback during drag

## Responsive Behavior

### Desktop (1024px+)
```
┌────────┬────────┬────────┬────────┐
│  To Do │Progress│ Review │  Done  │
│        │        │        │        │
│ [Card] │ [Card] │ [Card] │ [Card] │
│ [Card] │ [Card] │        │ [Card] │
│        │        │        │        │
└────────┴────────┴────────┴────────┘
```

### Tablet (768px - 1023px)
```
┌────────┬────────┐
│  To Do │Progress│
│ [Card] │ [Card] │
│ [Card] │ [Card] │
├────────┼────────┤
│ Review │  Done  │
│ [Card] │ [Card] │
│        │ [Card] │
└────────┴────────┘
```

### Mobile (<768px)
```
┌──────────┐
│  To Do   │
│  [Card]  │
│  [Card]  │
├──────────┤
│ Progress │
│  [Card]  │
├──────────┤
│  Review  │
│  [Card]  │
├──────────┤
│   Done   │
│  [Card]  │
└──────────┘
```

### Modal Responsive
- Desktop: Max width 768px, centered
- Mobile: Full screen with padding
- Scrollable content area
- Fixed header and footer

## Performance Considerations

1. **Event Delegation**: Click events handled efficiently
2. **Hover Animations**: CSS-only (no JavaScript)
3. **Modal Rendering**: Conditional rendering (not hidden)
4. **Drag Performance**: Native HTML5 drag API
5. **State Updates**: Minimal re-renders with React hooks

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ⚠️ IE 11: Not supported (uses modern CSS)

## Known Issues & Limitations

1. **Mobile Drag-and-Drop**: Touch events may need special handling
2. **Keyboard Drag**: No keyboard-based drag (future enhancement)
3. **Multi-select**: Can't drag multiple cards at once
4. **Undo/Redo**: No undo for drag operations
5. **Offline Mode**: Requires network connection

## Testing Scenarios

### Manual Testing
1. Hover over card → Drag handle should appear
2. Move mouse away → Drag handle should fade out
3. Click card body → Modal should open
4. Click drag handle → Should NOT open modal
5. Drag from handle → Card should move
6. Click backdrop → Modal should close
7. Switch themes → All colors should update
8. Resize window → Layout should adapt

### Automated Testing
```typescript
describe('KanbanCard', () => {
  it('shows drag handle on hover', () => {});
  it('opens modal on card click', () => {});
  it('does not open modal on drag handle click', () => {});
  it('initiates drag from handle', () => {});
  it('displays task details in modal', () => {});
  it('closes modal on backdrop click', () => {});
  it('handles edit action from modal', () => {});
  it('handles delete action from modal', () => {});
});
```
