"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { SearchIcon, GlobeIcon, CreditCardIcon, KeyIcon, BarChartIcon, HelpCircleIcon } from "lucide-react"
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
} from "@/components/ui/sidebar"
import { Header } from '@/components/header'

const featureItems = [
  {
    title: "Search",
    href: "/home/search",
    icon: SearchIcon,
  },
  {
    title: "Fetch",
    href: "/home/fetch",
    icon: GlobeIcon,
  },
]

const managementItems = [
  {
    title: "Usage",
    href: "/home/usage",
    icon: BarChartIcon,
  },
  {
    title: "Billing",
    href: "/home/billing",
    icon: CreditCardIcon,
  },
  {
    title: "API Keys",
    href: "/home/api-keys",
    icon: KeyIcon,
  },
]

// Context to allow child pages to control the sidebar
const SidebarControlContext = React.createContext<{
  closeSidebar: () => void
} | null>(null)

export function useSidebarControl() {
  return React.useContext(SidebarControlContext)
}

function HomeSidebar() {
  const pathname = usePathname()

  return (
    <Sidebar collapsible="icon">
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
      </SidebarContent>

      <SidebarFooter className="mt-auto border-t">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <button type="button" className="w-full">
                <HelpCircleIcon />
                <span>Support</span>
              </button>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarTrigger />
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}

// Wrapper component that provides the sidebar control context
function SidebarController({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = React.useState(true)

  const closeSidebar = React.useCallback(() => {
    setSidebarOpen(false)
  }, [])

  return (
    <SidebarControlContext.Provider value={{ closeSidebar }}>
      <Sidebar open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <HomeSidebar />
      </Sidebar>
      <SidebarInset>
        <Header />
        <main className="flex flex-1 flex-col">
          {children}
        </main>
      </SidebarInset>
    </SidebarControlContext.Provider>
  )
}

export default function HomeLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <SidebarProvider>
      <SidebarController>
        {children}
      </SidebarController>
    </SidebarProvider>
  )
}
