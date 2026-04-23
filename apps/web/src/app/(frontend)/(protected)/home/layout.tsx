"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { SearchIcon, GlobeIcon, CreditCardIcon, KeyIcon, BarChartIcon, HelpCircleIcon, BookOpenIcon } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarRail,
  SidebarTrigger,
  SidebarInset,
  useSidebar,
} from "@/components/ui/sidebar"
import { TooltipProvider } from "@/components/ui/tooltip"
import { Header } from '@/components/header'

const featureItems = [
  {
    title: "Search",
    href: "/home/search",
    icon: SearchIcon,
    tooltip: "Search",
  },
  {
    title: "Fetch",
    href: "/home/fetch",
    icon: GlobeIcon,
    tooltip: "Fetch",
  },
]

const managementItems = [
  {
    title: "Usage",
    href: "/home/usage",
    icon: BarChartIcon,
    tooltip: "Usage",
  },
  {
    title: "Billing",
    href: "/home/billing",
    icon: CreditCardIcon,
    tooltip: "Billing",
  },
  {
    title: "API Keys",
    href: "/home/api-keys",
    icon: KeyIcon,
    tooltip: "API Keys",
  },
]

const learningItems = [
  {
    title: "Documentation",
    href: "/docs",
    icon: BookOpenIcon,
    tooltip: "Documentation",
  },
]

const bottomItems = [
  {
    title: "Support",
    href: "#",
    icon: HelpCircleIcon,
    tooltip: "Support",
  },
]

// Context to allow child pages to control the sidebar
const SidebarControlContext = React.createContext<{
  closeSidebar: () => void
} | null>(null)

export function useSidebarControl() {
  return React.useContext(SidebarControlContext)
}

function SidebarContent_() {
  const pathname = usePathname()

  return (
    <>
      <SidebarHeader className="h-14 border-border border-b">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Link href="/home">
                <span className="text-lg font-semibold">Fresh</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Features</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {featureItems.map((item) => (
                <SidebarMenuItem key={item.href}>
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
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Management</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {managementItems.map((item) => (
                <SidebarMenuItem key={item.href}>
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
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>Learning</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {learningItems.map((item) => (
                <SidebarMenuItem key={item.href}>
                  <SidebarMenuButton
                    asChild
                    isActive={pathname === item.href}
                    tooltip={item.tooltip}
                  >
                    <Link href={item.href} target="_blank">
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {bottomItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild tooltip={item.tooltip}>
                    <Link href={item.href}>
                      <item.icon />
                      <span>{item.title}</span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarTrigger />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </>
  )
}

function SidebarWithContext() {
  const { setOpen } = useSidebar()

  const closeSidebar = React.useCallback(() => {
    setOpen(false)
  }, [setOpen])

  return (
    <SidebarControlContext.Provider value={{ closeSidebar }}>
      <TooltipProvider>
        <Sidebar collapsible="icon">
          <SidebarContent_ />
        </Sidebar>
      </TooltipProvider>
    </SidebarControlContext.Provider>
  )
}

export default function HomeLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <SidebarProvider defaultOpen={true}>
      <SidebarWithContext />
      <SidebarInset>
        <Header />
        <main className="flex flex-1 flex-col">
          {children}
        </main>
      </SidebarInset>
    </SidebarProvider>
  )
}
