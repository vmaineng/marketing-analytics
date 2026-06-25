const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type OverviewTotals = {
  impressions: number;
  reach: number;
  clicks: number;
  conversions: number;
  spend: number;
};

export type OverviewResponse = {
  date_range: { start: string; end: string };
  totals: OverviewTotals;
};

export type TrendDay = {
  date: string;
  impressions: number;
  reach: number;
  clicks: number;
  conversions: number;
  spend: number;
};

export type TrendResponse = {
  date_range: { start: string; end: string };
  trend: TrendDay[];
};

export async function fetchOverview(days = 7): Promise<OverviewResponse> {
  const res = await fetch(`${API_URL}/api/overview?days=${days}`, {
    next: { revalidate: 3600 }, // cache for 1 hour
  });
  if (!res.ok) throw new Error("Failed to fetch overview");
  return res.json();
}

export async function fetchTrend(days = 7): Promise<TrendResponse> {
  const res = await fetch(`${API_URL}/api/overview/trend?days=${days}`, {
    next: { revalidate: 3600 },
  });
  if (!res.ok) throw new Error("Failed to fetch trend");
  return res.json();
}
