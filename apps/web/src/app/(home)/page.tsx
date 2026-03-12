import Link from 'next/link';

export default function HomePage() {
  return (
    <section className="h-full overflow-hidden py-32 w-full">
      <div className="container border-t border-b border-dashed">
        <div className="relative flex w-full max-w-5xl flex-col justify-start border border-t-0 border-dashed px-5 py-12 md:items-center md:justify-center lg:mx-auto">
          <p className="flex items-center gap-2 gap-3 text-sm text-muted-foreground">
            <span className="inline-block size-2 rounded bg-green-500"></span>
            v2.8.4 Now Available
          </p>
          <div className="mt-3 mb-7 w-full max-w-xl text-5xl font-medium font-semibold tracking-tighter md:mb-10 md:text-center md:text-6xl lg:mb-0 lg:text-left lg:text-7xl">
            <h1 className="relative z-10 inline md:mr-3">
              A Smarter Way to <br className="block md:hidden" /> Fetch
              <br className="block md:hidden" /> Documentation
            </h1>
            <div
              className="inline-block rounded-lg pt-2 pb-3 text-center text-black dark:text-white absolute text-4xl font-semibold tracking-tighter md:bottom-4 md:left-1/2 md:-translate-x-1/2 md:text-5xl lg:bottom-4 lg:left-auto lg:translate-x-0 lg:text-7xl"
              style={{
                transform: 'none',
                transformOrigin: '50% 50% 0px',
                width: '200px',
                background: 'linear-gradient(to_bottom,#f3f4f6,#e5e7eb)',
                boxShadow: 'inset 0 -1px #d1d5db,inset 0 0 0 1px #d1d5db, 0 4px 8px #d1d5db',
              }}
            >
              <div className="inline-block" style={{ transform: 'none', transformOrigin: '50% 50% 0px' }}>
                <span style={{ opacity: 1, filter: 'blur(0px)' }}>F</span>
                <span style={{ opacity: 1, filter: 'blur(0px)' }}>r</span>
                <span style={{ opacity: 1, filter: 'blur(0px)' }}>e</span>
                <span style={{ opacity: 1, filter: 'blur(0px)' }}>s</span>
                <span style={{ opacity: 1, filter: 'blur(0px)' }}>h</span>
              </div>
            </div>
          </div>
        </div>
        <div className="mx-auto flex w-full max-w-5xl flex-col items-center justify-center border border-t-0 border-b-0 border-dashed py-20">
          <div className="w-full max-w-2xl space-y-5 md:text-center">
            <p className="px-5 text-muted-foreground lg:text-lg">
              Fetch documentation from any website, convert to Markdown, and access it offline. Perfect for developers who need quick access to docs.
            </p>
            <Link
              href="/docs"
              className="inline-flex items-center justify-center whitespace-nowrap transition-all disabled:pointer-events-none disabled:opacity-50 shrink-0 outline-none group/button select-none bg-primary text-primary-foreground hover:bg-primary/80 gap-1.5 px-2.5 h-12 rounded-lg text-sm font-medium"
            >
              Get Started Now
            </Link>
          </div>
        </div>
        <ul className="mx-auto grid h-44 w-full max-w-5xl grid-cols-1 border border-b-0 border-dashed md:h-34 md:grid-cols-2 lg:h-24 lg:grid-cols-3">
          <li className="flex h-full items-center justify-between gap-10 px-5 md:gap-3 lg:justify-center">
            <div className="flex size-12 items-center justify-center rounded-lg bg-muted">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="lucide lucide-zap size-6 text-muted-foreground"
                aria-hidden="true"
              >
                <path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path>
              </svg>
            </div>
            <p className="text-lg text-muted-foreground">Offline Access</p>
          </li>
          <li className="flex h-full items-center justify-between gap-10 border-t border-l border-dashed px-5 md:gap-3 lg:justify-center lg:border-t-0">
            <div className="flex size-12 items-center justify-center rounded-lg bg-muted">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="lucide lucide-search size-6 text-muted-foreground"
                aria-hidden="true"
              >
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.3-4.3"></path>
              </svg>
            </div>
            <p className="text-lg text-muted-foreground">Full-Text Search</p>
          </li>
          <li className="col-span-1 flex h-full items-center justify-between gap-10 border-t border-l border-dashed px-5 md:col-span-2 md:justify-center md:gap-3 lg:col-span-1 lg:border-t-0">
            <div className="flex size-12 items-center justify-center rounded-lg bg-muted">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="lucide lucide-markdown size-6 text-muted-foreground"
                aria-hidden="true"
              >
                <path d="m4 4 16 16"></path>
                <path d="m20 4-16 16"></path>
                <path d="M7 8h10"></path>
                <path d="M7 12h10"></path>
                <path d="M7 16h6"></path>
              </svg>
            </div>
            <p className="text-lg text-muted-foreground">Markdown Output</p>
          </li>
        </ul>
      </div>
    </section>
  );
}
