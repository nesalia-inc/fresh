"use client"

import { useState } from "react"
import { Loader2, GlobeIcon, PlusIcon, TrashIcon, ExternalLinkIcon, CalendarIcon, UserIcon } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ResizablePanel, ResizableHandle, ResizablePanelGroup } from "@/components/ui/resizable"
import { FetchResponse, FetchResult } from "@/core/types"
import { useSidebarControl } from "../layout"

const VERBOSITY_OPTIONS = [
  { value: "", label: "Standard" },
  { value: "compact", label: "Compact" },
  { value: "full", label: "Full" },
]

interface FetchState {
  isLoading: boolean
  results: FetchResult[] | null
  error: string | null
  totalCost: number | null
  statuses: Array<{ url: string; code: string }> | null
}

export default function FetchPage() {
  const sidebarControl = useSidebarControl()
  const closeSidebar = sidebarControl?.closeSidebar
  const [urls, setUrls] = useState<string[]>([""])
  const [verbosity, setVerbosity] = useState("")
  const [maxCharacters, setMaxCharacters] = useState<string>("")
  const [highlightsPerUrl, setHighlightsPerUrl] = useState<string>("")

  const [fetchState, setFetchState] = useState<FetchState>({
    isLoading: false,
    results: null,
    error: null,
    totalCost: null,
    statuses: null,
  })

  function addUrl() {
    if (urls.length < 10) {
      setUrls([...urls, ""])
    } else {
      toast.warning("Maximum 10 URLs allowed")
    }
  }

  function removeUrl(index: number) {
    if (urls.length > 1) {
      setUrls(urls.filter((_, i) => i !== index))
    }
  }

  function updateUrl(index: number, value: string) {
    const newUrls = [...urls]
    newUrls[index] = value
    setUrls(newUrls)
  }

  async function handleFetch(e: React.FormEvent) {
    e.preventDefault()

    const validUrls = urls.filter((url) => url.trim() !== "")

    if (validUrls.length === 0) {
      toast.error("Please enter at least one URL")
      return
    }

    // Validate URLs
    for (const url of validUrls) {
      try {
        new URL(url)
      } catch {
        toast.error(`Invalid URL: ${url}`)
        return
      }
    }

    // Close sidebar when fetching
    closeSidebar?.()

    setFetchState({ isLoading: true, results: null, error: null, totalCost: null, statuses: null })

    try {
      const body: Record<string, unknown> = {
        urls: validUrls.length === 1 ? validUrls[0] : validUrls,
      }

      if (verbosity) {
        body.text = { verbosity: verbosity as "compact" | "standard" | "full" }
      }
      if (maxCharacters) {
        const num = parseInt(maxCharacters)
        if (!isNaN(num)) {
          body.text = { ...(body.text as object || {}), maxCharacters: num }
        }
      }
      if (highlightsPerUrl) {
        const num = parseInt(highlightsPerUrl)
        if (!isNaN(num)) {
          body.highlights = { highlightsPerUrl: num }
        }
      }

      const response = await fetch("/api/fetch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || "Fetch failed")
      }

      const fetchResponse = data as FetchResponse

      setFetchState({
        isLoading: false,
        results: fetchResponse.results,
        error: null,
        totalCost: fetchResponse.costDollars?.totalCost ?? null,
        statuses: fetchResponse.statuses ?? null,
      })

      const successCount = fetchResponse.results.length
      const failCount = (fetchResponse.statuses ?? []).filter((s) => s.code !== "success").length

      if (successCount === 0) {
        toast.error("Could not fetch any URLs")
      } else if (failCount > 0) {
        toast.warning(`Fetched ${successCount} URL(s), ${failCount} failed`)
      } else {
        toast.success(`Successfully fetched ${successCount} URL(s)`)
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error"
      setFetchState({ isLoading: false, results: null, error: message, totalCost: null, statuses: null })
      toast.error(message)
    }
  }

  function handleClear() {
    setUrls([""])
    setVerbosity("")
    setMaxCharacters("")
    setHighlightsPerUrl("")
    setFetchState({ isLoading: false, results: null, error: null, totalCost: null, statuses: null })
  }

  function getStatusBadge(code: string) {
    switch (code) {
      case "success":
        return <span className="text-xs bg-green-500/10 text-green-600 px-2 py-1 rounded">Success</span>
      case "error":
        return <span className="text-xs bg-destructive/10 text-destructive px-2 py-1 rounded">Error</span>
      case "notFound":
        return <span className="text-xs bg-yellow-500/10 text-yellow-600 px-2 py-1 rounded">Not Found</span>
      case "unavailable":
        return <span className="text-xs bg-muted text-muted-foreground px-2 py-1 rounded">Unavailable</span>
      default:
        return <span className="text-xs bg-muted px-2 py-1 rounded">{code}</span>
    }
  }

  const hasResults = fetchState.results && fetchState.results.length > 0

  return (
    <ResizablePanelGroup direction="horizontal" className="flex-1">
      {/* LEFT: Fetch Form */}
      <ResizablePanel defaultSize={hasResults ? 35 : 100} minSize={hasResults ? 25 : 50}>
        <div className="h-full overflow-auto p-6">
          <div className="max-w-xl space-y-6">
            <div className="space-y-2">
              <h1 className="text-2xl font-semibold tracking-tight flex items-center gap-2">
                <GlobeIcon className="h-6 w-6" />
                Fetch Content
              </h1>
              <p className="text-sm text-muted-foreground">
                Extract and summarize content from web pages
              </p>
            </div>

            <Card>
              <CardContent className="pt-6 space-y-4">
                <form onSubmit={handleFetch} className="space-y-4">
                  <div className="space-y-3">
                    {urls.map((url, index) => (
                      <div key={index} className="flex gap-2">
                        <Input
                          placeholder="https://example.com/article"
                          value={url}
                          onChange={(e) => updateUrl(index, e.target.value)}
                          disabled={fetchState.isLoading}
                          className="flex-1"
                        />
                        {urls.length > 1 && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            onClick={() => removeUrl(index)}
                            disabled={fetchState.isLoading}
                          >
                            <TrashIcon className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>

                  {urls.length < 10 && (
                    <Button type="button" variant="outline" size="sm" onClick={addUrl} disabled={fetchState.isLoading}>
                      <PlusIcon className="mr-2 h-4 w-4" />
                      Add URL
                    </Button>
                  )}

                  <div className="grid gap-4 sm:grid-cols-3">
                    <div className="space-y-2">
                      <Label htmlFor="verbosity">Verbosity</Label>
                      <Select
                        id="verbosity"
                        options={VERBOSITY_OPTIONS}
                        value={verbosity}
                        onChange={(e) => setVerbosity(e.target.value)}
                        disabled={fetchState.isLoading}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="maxCharacters">Max Characters</Label>
                      <Input
                        id="maxCharacters"
                        type="number"
                        placeholder="5000"
                        min={100}
                        max={50000}
                        value={maxCharacters}
                        onChange={(e) => setMaxCharacters(e.target.value)}
                        disabled={fetchState.isLoading}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="highlightsPerUrl">Highlights per URL</Label>
                      <Input
                        id="highlightsPerUrl"
                        type="number"
                        placeholder="5"
                        min={1}
                        max={20}
                        value={highlightsPerUrl}
                        onChange={(e) => setHighlightsPerUrl(e.target.value)}
                        disabled={fetchState.isLoading}
                      />
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button type="submit" disabled={fetchState.isLoading}>
                      {fetchState.isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Fetching...
                        </>
                      ) : (
                        <>
                          <GlobeIcon className="mr-2 h-4 w-4" />
                          Fetch Content
                        </>
                      )}
                    </Button>
                    <Button type="button" variant="outline" onClick={handleClear} disabled={fetchState.isLoading}>
                      Clear
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </ResizablePanel>

      {/* RIGHT: Results */}
      {hasResults && (
        <>
          <ResizableHandle withHandle />
          <ResizablePanel defaultSize={65} minSize={40}>
            <div className="h-full overflow-auto p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold">
                  {fetchState.results!.length} Result{fetchState.results!.length !== 1 ? "s" : ""}
                  {fetchState.totalCost !== null && (
                    <span className="ml-2 text-sm font-normal text-muted-foreground">
                      (~${fetchState.totalCost.toFixed(4)})
                    </span>
                  )}
                </h2>
              </div>

              {fetchState.statuses && (
                <Card>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">Fetch Status</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {fetchState.statuses.map((status, index) => (
                        <div key={index} className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground truncate max-w-md">{status.url}</span>
                          {getStatusBadge(status.code)}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {fetchState.isLoading && (
                <div className="space-y-4">
                  {[1, 2].map((i) => (
                    <Card key={i}>
                      <CardContent className="pt-6">
                        <Skeleton className="h-6 w-3/4 mb-2" />
                        <Skeleton className="h-4 w-1/2 mb-4" />
                        <Skeleton className="h-4 w-full mb-1" />
                        <Skeleton className="h-4 w-full mb-1" />
                        <Skeleton className="h-4 w-2/3" />
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}

              {fetchState.error && (
                <Card className="border-destructive">
                  <CardContent className="pt-6">
                    <p className="text-sm text-destructive">{fetchState.error}</p>
                  </CardContent>
                </Card>
              )}

              {fetchState.results!.map((result, index) => (
                <Card key={result.id || index}>
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <CardTitle className="text-base line-clamp-2">
                        {result.title || "Untitled"}
                      </CardTitle>
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="shrink-0"
                      >
                        <Button variant="ghost" size="icon">
                          <ExternalLinkIcon className="h-4 w-4" />
                        </Button>
                      </a>
                    </div>
                    <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="truncate max-w-md hover:text-foreground"
                      >
                        {result.url}
                      </a>
                    </div>
                    {(result.author || result.publishedDate) && (
                      <div className="flex flex-wrap gap-4 text-xs text-muted-foreground pt-1">
                        {result.author && (
                          <span className="flex items-center gap-1">
                            <UserIcon className="h-3 w-3" />
                            {result.author}
                          </span>
                        )}
                        {result.publishedDate && (
                          <span className="flex items-center gap-1">
                            <CalendarIcon className="h-3 w-3" />
                            {new Date(result.publishedDate).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    )}
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {result.highlights && result.highlights.length > 0 && (
                      <div className="space-y-2">
                        <h3 className="text-sm font-medium">Highlights</h3>
                        {result.highlights.map((highlight, i) => (
                          <p key={i} className="text-sm bg-muted p-3 rounded-lg">
                            {highlight.length > 500 ? `${highlight.substring(0, 500)}...` : highlight}
                          </p>
                        ))}
                      </div>
                    )}

                    {result.text && (
                      <div className="space-y-2">
                        <h3 className="text-sm font-medium">Content</h3>
                        <Textarea
                          value={result.text}
                          readOnly
                          className="min-h-[200px] font-mono text-sm"
                        />
                      </div>
                    )}

                    {!result.text && !result.highlights && (
                      <p className="text-sm text-muted-foreground">No content available</p>
                    )}
                  </CardContent>
                </Card>
              ))}

              {fetchState.results!.length === 0 && !fetchState.isLoading && (
                <Card>
                  <CardContent className="pt-6 text-center">
                    <p className="text-muted-foreground">No content could be fetched from the provided URLs.</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </ResizablePanel>
        </>
      )}
    </ResizablePanelGroup>
  )
}
