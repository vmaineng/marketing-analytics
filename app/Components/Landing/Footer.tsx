"use client";

export default function Footer() {
  return (
    <footer className="relative overflow-hidden border-t border-(--card-border) bg-background px-4 sm:px-6 py-10 sm:py-12 transition-colors duration-300">
      <div className="mx-auto max-w-7xl">
        <div className="space-y-3">
          //Marketing Analytics Platform
          <p className="max-w-md text-xs leading-relaxed text-(--text-secondary) transition-colors duration-300">
            Software engineer building thoughtful interfaces, AI-powered tools,
            and open source contributions.
          </p>
        </div>
        <div className="text-xs tracking-wide text-(--text-muted) sm:text-right transition-colors duration-300">
          © {new Date().getFullYear()} Maizee. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
