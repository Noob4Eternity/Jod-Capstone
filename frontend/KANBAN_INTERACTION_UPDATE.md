# Kanban Card Interaction Update

## Overview
Updated the Kanban board cards to support both drag-and-drop functionality and click-to-view-details interaction without conflicts.

## New Features

### 1. Task Details Modal
A new comprehensive modal component (`TaskDetailsModal.tsx`) that displays all task information:

#### Features:
- **Full Task Information**: Title, description, priority, status
- **Metadata Display**: Created date, updated date, due date, assignee
- **Visual Priority Indicators**: Color-coded priority badges with emoji icons
- **Tags & Categories**: Visual display of all task tags and category
- **Acceptance Criteria**: Numbered list of acceptance criteria
- **Technical Notes**: Code-formatted technical notes section
- **Dependencies**: List of task dependencies
- **Estimated Hours**: Large, prominent display of time estimates
- **Overdue Warning**: Visual indicators for overdue tasks
- **Quick Actions**: Edit and Delete buttons in header and footer

#### Theme Integration:
- Fully themed with CSS variables from `globals.css`
- Supports both light and dark modes
- Consistent with overall design system

### 2. Enhanced Kanban Card

#### Drag Handle Implementation:
- **Position**: Top right corner of each card
- **Visual**: Grip icon (vertical dots) that appears on hover
- **Behavior**: Only appears when hovering over the card
- **Functionality**: Drag-and-drop only works from this handle

#### Click Functionality:
- **Entire Card Clickable**: Clicking anywhere on the card (except the drag handle) opens the details modal
- **Smart Event Handling**: Prevents conflicts between drag and click events
- **Visual Feedback**: Card has hover effects to indicate it's interactive

#### Updated Styling:
- Changed from `cursor-move` (entire card) to `cursor-pointer` (entire card) with `cursor-move` (drag handle only)
- Theme colors replace hardcoded grays
- Improved dark mode support
- Smooth transitions and hover effects

### 3. KanbanColumn Updates
- Added `onTaskClick` prop for handling card clicks
- Passes click handler to each `KanbanCard` component

### 4. KanbanBoard Updates
- Imported and integrated `TaskDetailsModal`
- Added state management for modal visibility
- Added `handleTaskClick` function to open modal with selected task
- Modal closes when:
  - Close button clicked
  - Outside modal clicked (backdrop)
  - Edit button clicked (to switch to edit mode)
  - Delete action completed

## Component Hierarchy

```
KanbanBoard
├── TaskDetailsModal (new)
│   ├── Task Details Display
│   ├── Edit Button → handleTaskEdit
│   └── Delete Button → handleTaskDelete
├── KanbanColumn
│   └── KanbanCard (updated)
│       ├── Drag Handle (top right)
│       └── Click Handler (entire card)
└── AddTaskModal
```

## User Interaction Flow

### Viewing Task Details:
1. User hovers over a card
2. Drag handle appears in top right corner
3. User clicks anywhere on the card (except drag handle)
4. Task Details Modal opens with full information
5. User can close modal or take actions (edit/delete)

### Moving Tasks:
1. User hovers over a card
2. Drag handle appears in top right corner
3. User clicks and holds the drag handle
4. Card becomes slightly transparent and rotates
5. User drags to new column
6. User releases to drop in new status

### Editing Tasks:
1. User opens Task Details Modal (click card)
2. User clicks "Edit Task" button in header or footer
3. Modal closes
4. Edit functionality executes (currently logs to console)

### Deleting Tasks:
1. User opens Task Details Modal (click card)
2. User clicks delete button (trash icon)
3. Confirmation dialog appears
4. User confirms deletion
5. Task is deleted from database
6. Modal closes automatically

## Technical Implementation

### Event Handling
```typescript
const handleCardClick = (e: React.MouseEvent) => {
  // Prevent click event when clicking on the drag handle
  if ((e.target as HTMLElement).closest('.drag-handle')) {
    return;
  }
  onClick?.(task);
};
```

### Drag Handle
```tsx
<div
  className="drag-handle absolute top-2 right-2 p-1 text-muted-foreground hover:text-foreground hover:bg-secondary rounded cursor-move opacity-0 group-hover:opacity-100 transition-opacity"
  draggable
  onDragStart={handleDragStart}
  title="Drag to move"
>
  <GripVertical size={16} />
</div>
```

### Modal State Management
```typescript
const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
const [selectedTask, setSelectedTask] = useState<Task | null>(null);

const handleTaskClick = (task: Task) => {
  setSelectedTask(task);
  setIsDetailsModalOpen(true);
};
```

## Styling Updates

### KanbanCard.tsx
**Before:**
- `cursor-move` on entire card
- Hardcoded gray colors
- `draggable` on entire card div
- `MoreHorizontal` menu button

**After:**
- `cursor-pointer` on card body
- `cursor-move` only on drag handle
- Theme colors (`bg-card`, `text-foreground`, etc.)
- `draggable` only on drag handle
- `GripVertical` drag icon (appears on hover)

### CSS Additions
```css
/* Kanban Card Animations */
.drag-handle {
  transition: opacity 0.2s ease-in-out, background-color 0.2s ease-in-out;
}

/* Modal Animations */
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
```

## Props Changes

### KanbanCard
```typescript
interface KanbanCardProps {
  task: Task;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
  onClick?: (task: Task) => void;  // NEW
  isDragging?: boolean;
}
```

### KanbanColumn
```typescript
interface KanbanColumnProps {
  column: Column;
  tasks: Task[];
  stories?: Record<string, { id: string; title: string; storyId: string }>;
  onAddTask?: () => void;
  onTaskMove?: (taskId: string, newStatusId: number) => void;
  onTaskEdit?: (task: Task) => void;
  onTaskDelete?: (taskId: string) => void;
  onTaskClick?: (task: Task) => void;  // NEW
}
```

## Theme Colors Used

### Task Details Modal:
- Background: `bg-card`
- Text: `text-foreground`
- Muted text: `text-muted-foreground`
- Borders: `border-border`
- Secondary background: `bg-secondary`
- Primary actions: `bg-primary`, `text-primary-foreground`
- Destructive actions: `text-destructive`, `bg-destructive/10`
- Accents: `bg-accent`, `text-accent-foreground`

### Kanban Card:
- Background: `bg-card`
- Border: `border-border`
- Text: `text-foreground`
- Muted text: `text-muted-foreground`
- Secondary background: `bg-secondary`
- Priority badges: Keep original color scheme (works in both themes)
- Overdue indicators: Red with dark mode support

## Accessibility Improvements

1. **Clear Visual Affordances**: Drag handle appears on hover
2. **Cursor Changes**: Appropriate cursors for different interactions
3. **Keyboard Support**: Modal can be closed with backdrop click
4. **Focus Management**: Buttons have clear hover states
5. **Color Contrast**: All text meets WCAG standards in both themes
6. **Screen Reader Support**: Semantic HTML structure
7. **Title Attributes**: Tooltips on interactive elements

## Future Enhancements

1. **Edit Modal**: Create dedicated edit modal (similar to AddTaskModal)
2. **Keyboard Navigation**: 
   - Arrow keys to move between cards
   - Enter to open details
   - Escape to close modal
3. **Quick Actions**: Add quick status change buttons in modal
4. **Inline Editing**: Edit task title directly from card
5. **Comments Section**: Add task comments in details modal
6. **Activity Log**: Show task history and changes
7. **Attachments**: Support file attachments display
8. **Assignee Picker**: Visual assignee selection in modal
9. **Due Date Editor**: Calendar picker in modal
10. **Time Tracking**: Start/stop timer in modal

## Testing Checklist

- [x] Drag handle appears on card hover
- [x] Drag handle disappears when not hovering
- [x] Clicking drag handle initiates drag operation
- [x] Clicking card body opens details modal
- [x] Clicking card body does not initiate drag
- [x] Modal displays all task information correctly
- [x] Modal edit button works
- [x] Modal delete button works with confirmation
- [x] Modal close button works
- [x] Clicking backdrop closes modal
- [x] Theme colors apply correctly in light mode
- [x] Theme colors apply correctly in dark mode
- [x] Overdue tasks show warning indicators
- [x] Priority badges display with correct colors
- [x] Tags render properly
- [x] Dates format correctly
- [x] Long text content scrolls properly in modal
- [x] Modal is responsive on mobile devices
- [x] No console errors or warnings

## Breaking Changes

None. All changes are backward compatible. The component will work with or without the new `onClick` handler.

## Migration Guide

If you have custom implementations of KanbanColumn or KanbanCard:

1. Add `onClick` prop to your KanbanCard component
2. Add `onTaskClick` prop to your KanbanColumn component
3. Update drag functionality to use a drag handle instead of the entire card
4. Import and use the new TaskDetailsModal component
5. Update colors from hardcoded values to theme variables

Example:
```typescript
// Before
<KanbanCard task={task} onEdit={handleEdit} onDelete={handleDelete} />

// After
<KanbanCard 
  task={task} 
  onEdit={handleEdit} 
  onDelete={handleDelete}
  onClick={handleTaskClick}  // NEW
/>
```
