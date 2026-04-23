"use client"

import { useState } from "react"
import { Loader2, SearchIcon, ExternalLinkIcon, CalendarIcon, HashIcon } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Separator } from "@/components/ui/separator"
import { SearchResponse, SearchResult } from "@/core/types"

const SEARCH_TYPES = [
  { value: "auto", label: "Auto (Balanced)" },
  { value: "fast", label: "Fast (Quick)" },
  { value: "deep-lite", label: "Deep Lite (Moderate)" },
  { value: "deep", label: "Deep (Thorough)" },
  { value: "deep-reasoning", label: "Deep Reasoning (AI)" },
  { value: "instant", label: "Instant (Fastest)" },
]

const CATEGORIES = [
  { value: "", label: "All Categories" },
  { value: "company", label: "Company" },
  { value: "research paper", label: "Research Paper" },
  { value: "news", label: "News" },
  { value: "pdf", label: "PDF" },
  { value: "personal site", label: "Personal Site" },
  { value: "financial report", label: "Financial Report" },
  { value: "people", label: "People" },
]

interface SearchState {
  isLoading: boolean
  results: SearchResult[] | null
  error: string | null
  totalCost: number | null
}

export default function SearchPage() {
  const [query, setQuery] = useState("")
  const [searchType, setSearchType] = useState("auto")
  const [category, setCategory] = useState("")
  const [numResults, setNumResults] = useState(10)
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [includeDomains, setIncludeDomains] = useState("")
  const [excludeDomains, setExcludeDomains] = useState("")

  const [searchState, setSearchState] = useState<SearchState>({
    isLoading: false,
    results: null,
    error: null,
    totalCost: null,
  })

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault()

    if (!query.trim()) {
      toast.error("Please enter a search query")
      return
    }

    setSearchState({ isLoading: true, results: null, error: null, totalCost: null })

    try {
      const body: Record<string, unknown> = {
        query: query.trim(),
        type: searchType,
        numResults,
      }

      if (category) body.category = category
      if (startDate) body.startPublishedDate = startDate
      if (endDate) body.endPublishedDate = endDate
      if (includeDomains.trim()) {
        body.includeDomains = includeDomains.split(",").map((d) => d.trim()).filter(Boolean)
      }
      if (excludeDomains.trim()) {
        body.excludeDomains = excludeDomains.split(",").map((d) => d.trim()).filter(Boolean)
      }

      const response = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message || "Search failed")
      }

      const searchResponse = data as SearchResponse

      setSearchState({
        isLoading: false,
        results: searchResponse.results,
        error: null,
        totalCost: searchResponse.costDollars?.totalCost ?? null,
      })

      if (searchResponse.results.length === 0) {
        toast.info("No results found")
      } else {
        toast.success(`Found ${searchResponse.results.length} results`)
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error"
      setSearchState({ isLoading: false, results: null, error: message, totalCost: null })
      toast.error(message)
    }
  }

  function handleClear() {
    setQuery("")
    setSearchType("auto")
    setCategory("")
    setNumResults(10)
    setStartDate("")
    setEndDate("")
    setIncludeDomains("")
    setExcludeDomains("")
    setSearchState({ isLoading: false, results: null, error: null, totalCost: null })
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">Web Search</h1>
        <p className="text-sm text-muted-foreground">
          Search the web using AI-powered search with advanced filters
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SearchIcon className="h-5 w-5" />
            Search Query
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="query">Search Query *</Label>
              <Textarea
                id="query"
                placeholder="What are you looking for?"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                rows={2}
                disabled={searchState.isLoading}
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="space-y-2">
                <Label htmlFor="type">Search Type</Label>
                <Select
                  id="type"
                  options={SEARCH_TYPES}
                  value={searchType}
                  onChange={(e) => setSearchType(e.target.value)}
                  disabled={searchState.isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  id="category"
                  options={CATEGORIES}
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  disabled={searchState.isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="numResults">Number of Results</Label>
                <Input
                  id="numResults"
                  type="number"
                  min={1}
                  max={100}
                  value={numResults}
                  onChange={(e) => setNumResults(parseInt(e.target.value) || 10)}
                  disabled={searchState.isLoading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="startDate">Start Date</Label>
                <Input
                  id="startDate"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  disabled={searchState.isLoading}
                />
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="includeDomains">Include Domains</Label>
                <Input
                  id="includeDomains"
                  placeholder="example.com, another.com"
                  value={includeDomains}
                  onChange={(e) => setIncludeDomains(e.target.value)}
                  disabled={searchState.isLoading}
                />
                <p className="text-xs text-muted-foreground">Comma-separated domains</p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="excludeDomains">Exclude Domains</Label>
                <Input
                  id="excludeDomains"
                  placeholder="spam.com, ads.com"
                  value={excludeDomains}
                  onChange={(e) => setExcludeDomains(e.target.value)}
                  disabled={searchState.isLoading}
                />
                <p className="text-xs text-muted-foreground">Comma-separated domains</p>
              </div>
            </div>

            <div className="flex gap-2">
              <Button type="submit" disabled={searchState.isLoading}>
                {searchState.isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <SearchIcon className="mr-2 h-4 w-4" />
                    Search
                  </>
                )}
              </Button>
              <Button type="button" variant="outline" onClick={handleClear} disabled={searchState.isLoading}>
                Clear
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {searchState.isLoading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-6 w-3/4 mb-2" />
                <Skeleton className="h-4 w-1/2 mb-4" />
                <Skeleton className="h-4 w-full mb-1" />
                <Skeleton className="h-4 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {searchState.error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-sm text-destructive">{searchState.error}</p>
          </CardContent>
        </Card>
      )}

      {searchState.results && searchState.results.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              {searchState.results.length} Results
              {searchState.totalCost !== null && (
                <span className="ml-2 text-sm font-normal text-muted-foreground">
                  (~${searchState.totalCost.toFixed(4)})
                </span>
              )}
            </h2>
          </div>

          {searchState.results.map((result, index) => (
            <Card key={result.id || index} className="hover:bg-muted/50 transition-colors">
              <CardContent className="pt-6">
                <div className="flex flex-col gap-2">
                  <div className="flex items-start justify-between gap-4">
                    <a
                      href={result.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="font-semibold text-primary hover:underline flex items-center gap-2"
                    >
                      {result.title}
                      <ExternalLinkIcon className="h-3 w-3" />
                    </a>
                    {result.score !== undefined && (
                      <span className="text-xs bg-muted px-2 py-1 rounded flex items-center gap-1 shrink-0">
                        <HashIcon className="h-3 w-3" />
                        {(result.score * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-muted-foreground break-all">{result.url}</p>

                  {result.publishedDate && (
                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                      <CalendarIcon className="h-3 w-3" />
                      {new Date(result.publishedDate).toLocaleDateString()}
                    </p>
                  )}

                  {result.highlights && result.highlights.length > 0 && (
                    <div className="mt-2 space-y-2">
                      {result.highlights.slice(0, 2).map((highlight, i) => (
                        <p key={i} className="text-sm bg-muted p-3 rounded-lg">
                          {highlight.length > 300 ? `${highlight.substring(0, 300)}...` : highlight}
                        </p>
                      ))}
                    </div>
                  )}

                  {result.text && !result.highlights && (
                    <p className="text-sm text-muted-foreground">
                      {result.text.length > 200 ? `${result.text.substring(0, 200)}...` : result.text}
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {searchState.results && searchState.results.length === 0 && !searchState.isLoading && (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">No results found. Try different keywords or filters.</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
