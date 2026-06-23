"use client";

export default function CTA() {
  return (
    <div className="mt-8 mb-8 text-center">
      <div className="flex flex-wrap justify-center gap-4">
        <button className="rounded-lg bg-black px-6 py-3 font-medium text-white transition hover:-translate-y-0.5 hover:opacity-90">
          Start Tracking Metrics
        </button>

        <button className="rounded-lg border px-6 py-3 font-medium transition hover:bg-gray-50">
          View Demo
        </button>
      </div>

      <p className="mt-4 text-sm text-gray-500">
        Connect your marketing data and get actionable insights in minutes.
      </p>
    </div>
  );
}
