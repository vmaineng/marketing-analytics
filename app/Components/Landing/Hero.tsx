"use client";

export default function Hero() {
  return (
    <section className="mx-auto max-w-7xl px-6 py-24">
      <div className="grid gap-12 lg:grid-cols-2 lg:items-center">
        <div>
          <span className="rounded-full border px-3 py-1 text-sm">
            Marketing Analytics Platform
          </span>

          <h1 className="mt-6 text-5xl font-bold tracking-tight">
            Know What&apos;s Working.
            <br />
            Fix What&apos;s Not.
          </h1>

          <p className="mt-6 max-w-xl text-lg text-gray-600">
            Track conversions, campaign performance, acquisition costs, and ROI
            from one dashboard. Stop digging through spreadsheets and start
            making data-driven decisions faster.
          </p>

          <div className="mt-8 flex gap-4">
            <button className="rounded-lg bg-black px-6 py-3 text-white">
              Get Started
            </button>

            <button className="rounded-lg border px-6 py-3">View Demo</button>
          </div>

          <div className="mt-10 flex gap-8 text-sm">
            <div>
              <p className="text-2xl font-bold">30%</p>
              <p className="text-gray-500">Higher ROI Visibility</p>
            </div>

            <div>
              <p className="text-2xl font-bold">15+</p>
              <p className="text-gray-500">Data Sources</p>
            </div>

            <div>
              <p className="text-2xl font-bold">Real-Time</p>
              <p className="text-gray-500">Campaign Insights</p>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border bg-white p-6 shadow-lg">
          <h3 className="mb-6 text-lg font-semibold">Performance Overview</h3>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border p-4">
              <p className="text-sm text-gray-500">Revenue</p>
              <p className="mt-2 text-3xl font-bold">$84,231</p>
              <p className="text-green-600">↑ 12%</p>
            </div>

            <div className="rounded-xl border p-4">
              <p className="text-sm text-gray-500">Conversions</p>
              <p className="mt-2 text-3xl font-bold">1,284</p>
              <p className="text-green-600">↑ 8%</p>
            </div>

            <div className="rounded-xl border p-4">
              <p className="text-sm text-gray-500">ROAS</p>
              <p className="mt-2 text-3xl font-bold">4.8x</p>
              <p className="text-green-600">↑ 15%</p>
            </div>

            <div className="rounded-xl border p-4">
              <p className="text-sm text-gray-500">CTR</p>
              <p className="mt-2 text-3xl font-bold">3.4%</p>
              <p className="text-green-600">↑ 2%</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
