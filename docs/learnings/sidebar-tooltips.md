# Sidebar Tooltip Pattern in Fresh

## Overview

The Fresh web app uses a collapsible sidebar component built on shadcn/ui. When the sidebar is collapsed to icon mode, tooltips are displayed to provide context for each icon-only menu item.

## How It Works

### SidebarMenuButton Tooltip Support

The `SidebarMenuButton` component from shadcn/ui natively supports a `tooltip` prop:

```tsx
<SidebarMenuButton
  asChild
  isActive={pathname === item.href}
  tooltip={item.tooltip}
>
  <Link href={item.href}>
    <item.icon />
    <span>{item.title}</span>
  </Link>
</SidebarMenuButton>
```

### Automatic Visibility Control

The tooltip is **automatically shown/hidden** based on sidebar state:

| Sidebar State | Tooltip Visible |
|---------------|-----------------|
| Expanded | No (hidden) |
| Collapsed (icon mode) | Yes |
| Mobile | No |

This behavior is built into `SidebarMenuButton` via the `useSidebar` hook:

```tsx
// From sidebar.tsx
const { isMobile, state } = useSidebar()

// Tooltip is hidden when sidebar is NOT collapsed or on mobile
hidden={state !== "collapsed" || isMobile}
```

### Tooltip Positioning

When visible, tooltips appear:
- **Side**: `right`
- **Alignment**: `center`

## Implementation Pattern

### 1. Define Menu Items with Tooltips

```tsx
const featureItems = [
  {
    title: "Search",
    href: "/home/search",
    icon: SearchIcon,
    tooltip: "Search",  // Shown when collapsed
  },
  {
    title: "Fetch",
    href: "/home/fetch",
    icon: GlobeIcon,
    tooltip: "Fetch",  // Shown when collapsed
  },
]
```

### 2. Apply Tooltip to SidebarMenuButton

```tsx
{featureItems.map((item) => (
  <SidebarMenuItem key={item.href}>
    <SidebarMenuButton
      asChild
      isActive={pathname === item.href}
      tooltip={item.tooltip}  // Pass tooltip prop
    >
      <Link href={item.href}>
        <item.icon />
        <span>{item.title}</span>
      </Link>
    </SidebarMenuButton>
  </SidebarMenuItem>
))}
```

## Sidebar Structure in Fresh

The Fresh sidebar uses collapsible icon mode with grouped navigation:

```
┌──────────────────────┐
│ Fresh (logo)         │
├──────────────────────┤
│ Features             │
│  🔍 Search          │
│  🌐 Fetch           │
├──────────────────────┤
│ Management           │
│  📊 Usage           │
│  💳 Billing         │
│  🔑 API Keys        │
├──────────────────────┤
│ Learning            │
│  📖 Documentation   │
├──────────────────────┤
│ ? Support           │
├──────────────────────┤
│ ◀ (collapse toggle) │
└──────────────────────┘
```

When collapsed:
```
┌────┐
│ F  │
├────┤
│ 🔍 │
│ 🌐 │
├────┤
│ 📊 │
│ 💳 │
│ 🔑 │
├────┤
│ 📖 │
├────┤
│ ?  │
├────┤
│ ◀  │
└────┘
     ↑
   Tooltips appear on hover
```

## Key Components

| Component | Purpose |
|-----------|---------|
| `SidebarProvider` | Provides sidebar context |
| `Sidebar` | Main sidebar container with `collapsible="icon"` |
| `SidebarGroup` | Groups related menu items with label |
| `SidebarGroupLabel` | Label text for a group |
| `SidebarMenu` | Wraps menu items |
| `SidebarMenuItem` | Individual menu item wrapper |
| `SidebarMenuButton` | Clickable button with tooltip support |
| `SidebarRail` | Visual rail element |
| `SidebarTrigger` | Toggle button to collapse/expand |

## Collapse Behavior

The sidebar uses `collapsible="icon"` which means:

1. **Expanded**: Shows icon + text for each item
2. **Collapsed**: Shows only icons, with tooltips on hover
3. **Toggle**: The `SidebarTrigger` button cycles between states

### Manual Collapse Control

To programmatically collapse the sidebar from child pages:

```tsx
// In layout
const { setOpen } = useSidebar()

const closeSidebar = () => setOpen(false)

// Provide via context
<SidebarControlContext.Provider value={{ closeSidebar }}>
  {/* children */}
</SidebarControlContext.Provider>

// In page
const sidebarControl = useSidebarControl()
const closeSidebar = sidebarControl?.closeSidebar
closeSidebar?.()
```

## Notes

- Tooltips only appear when sidebar is in "collapsed" state
- On mobile devices, tooltips are hidden regardless of state
- The tooltip uses shadcn's `Tooltip` component internally
- Tooltip content can be customized via the `tooltip` prop (accepts string or `TooltipContent` props)
