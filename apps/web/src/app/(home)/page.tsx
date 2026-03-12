import Link from 'next/link';

export default function HomePage() {
  return (
    <section className="flex min-h-[80vh] w-full items-center justify-center py-20">
      <div className="container flex flex-col items-center">
        {/* Badge */}
        <div className="mb-6 flex items-center gap-2 rounded-full border border-dashed px-4 py-1.5 text-sm">
          <span className="inline-block size-2 rounded-full bg-green-500"></span>
          <span className="text-muted-foreground">v2.8.4 Now Available</span>
        </div>

        {/* Hero Title */}
        <div className="relative mb-8 text-center">
          <h1 className="text-5xl font-semibold tracking-tight sm:text-6xl lg:text-7xl">
            A Smarter Way to <br className="hidden sm:block" />
            Fetch Documentation
          </h1>
        </div>

        {/* Description */}
        <p className="mx-auto mb-10 max-w-2xl text-center text-lg text-muted-foreground">
          Fetch documentation from any website, convert to Markdown, and access it
          offline. Perfect for developers who need quick access to docs.
        </p>

        {/* CTA Button */}
        <Link
          href="/docs"
          className="inline-flex h-12 items-center justify-center rounded-lg bg-primary px-8 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90"
        >
          Get Started Now
        </Link>

        {/* Features Grid */}
        <div className="mt-20 grid w-full max-w-4xl grid-cols-1 gap-6 sm:grid-cols-3">
          <div className="flex flex-col items-center text-center">
            <div className="mb-4 flex size-14 items-center justify-center rounded-xl bg-muted">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="28"
                height="28"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-muted-foreground"
              >
                <path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path>
                <path d="M12 2v4"></path>
              </svg>
            </div>
            <h3 className="mb-2 text-lg font-medium">Offline Access</h3>
            <p className="text-sm text-muted-foreground">
              Download entire documentation sites for offline reading
            </p>
          </div>

          <div className="flex flex-col items-center text-center">
            <div className="mb-4 flex size-14 items-center justify-center rounded-xl bg-muted">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="28"
                height="28"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-muted-foreground"
              >
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.3-4.3"></path>
              </svg>
            </div>
            <h3 className="mb-2 text-lg font-medium">Full-Text Search</h3>
            <p className="text-sm text-muted-foreground">
              Find anything instantly across all your documentation
            </p>
          </div>

          <div className="flex flex-col items-center text-center">
            <div className="mb-4 flex size-14 items-center justify-center rounded-xl bg-muted">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="28"
                height="28"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-muted-foreground"
              >
                <path d="m4 4 16 16"></path>
                <path d="m20 4-16 16"></path>
                <path d="M7 8h10"></path>
                <path d="M7 12h10"></path>
                <path d="M7 16h6"></path>
              </svg>
            </div>
            <h3 className="mb-2 text-lg font-medium">Markdown Output</h3>
            <p className="text-sm text-muted-foreground">
              Clean Markdown for use with your favorite tools
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
