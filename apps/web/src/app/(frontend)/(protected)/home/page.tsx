import { redirect } from "next/navigation";
import { headers } from "next/headers";
import Link from "next/link";
import { deesseAuth } from "@/lib/deesse";
import { SearchIcon, GlobeIcon, ArrowRightIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default async function HomePage() {
  const session = await deesseAuth.api.getSession({
    headers: await headers(),
  });

  if (!session) {
    redirect("/login?redirectTo=/home");
  }

  const userName = session.user?.name || session.user?.email || "there";

  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">Welcome back, {userName}</h1>
        <p className="text-muted-foreground">What would you like to do today?</p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <Card className="hover:bg-muted/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <SearchIcon className="h-5 w-5" />
              Web Search
            </CardTitle>
            <CardDescription>
              Search the web using AI-powered search with advanced filters, categories, and date ranges.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/home/search">
                Go to Search
                <ArrowRightIcon className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>

        <Card className="hover:bg-muted/50 transition-colors">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <GlobeIcon className="h-5 w-5" />
              Fetch Content
            </CardTitle>
            <CardDescription>
              Extract and summarize content from web pages, articles, and documents.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <Link href="/home/fetch">
                Go to Fetch
                <ArrowRightIcon className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>

      <div className="rounded-lg border bg-muted/50 p-6">
        <h2 className="font-semibold mb-2">Quick Tips</h2>
        <ul className="text-sm text-muted-foreground space-y-1">
          <li>• Use <strong>Search</strong> to find web pages, news articles, research papers, and more</li>
          <li>• Use <strong>Fetch</strong> to extract full content from specific URLs</li>
          <li>• You can access Fresh from your terminal using <code className="text-xs bg-muted px-1 py-0.5 rounded">npm install -g @nesalia/fresh</code></li>
        </ul>
      </div>
    </div>
  );
}
