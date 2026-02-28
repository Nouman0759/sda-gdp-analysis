from typing import List, Dict, Any, Tuple
from functools import reduce
from itertools import chain, pairwise
from core.contracts import DataSink, PipelineService


class TransformationEngine(PipelineService):
    def __init__(self, sink: DataSink):
        self.sink = sink
        self.results: Dict[str, List[Dict]] = {}
        self.config = None  # temporary - set from main

    def execute(self, raw_data: List[Dict]) -> None:
        if self.config is None:
            raise ValueError("Config not set in engine")

        start = self.config["analysis"].get("start_year", 2015)
        end = self.config["analysis"].get("end_year", 2022)
        continent = self.config["analysis"].get("continent", "Asia")
        year = str(self.config["analysis"].get("year", 2020))
        decline_years = self.config["analysis"].get("decline_years", 5)

        self.results = {
            "top_10": self._top_bottom(raw_data, continent, year, top=True),
            "bottom_10": self._top_bottom(raw_data, continent, year, top=False),
            "global_trend": self._global_trend(raw_data, start, end),
            "average_continent": self._average_by_continent(raw_data, start, end),
            "growth_rates": self._growth_rates(raw_data, continent, start, end),
            "fastest_continent": self._fastest_growing_continent(raw_data, start, end),
            "consistent_decline": self._consistent_decline(raw_data, continent, decline_years, end),
            "continent_contribution": self._continent_contribution(raw_data, start, end),
        }
        print("Computed results keys and lengths:")
        for key, val in self.results.items():
            print(f"  {key}: {len(val)} items")

        self.sink.write(self.results)

    # ────────────────────────────────────────────────
    # Helpers (pure)
    # ────────────────────────────────────────────────
    def _get_gdp_value(self, row: Dict, year: str) -> float | None:
        val = row.get(year)
        if val in ("", None, "..", "NA", "#N/A"):
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    def _is_real_country(self, row: Dict) -> bool:
        name = row.get("Country Name", "").lower()
        skip = ["world", "income", "excluding", "ibrd", "ida", "aggregate", "&", "pacific", "europe", "asia", "africa", "america", "arab world", "high income", "low income", "middle income", "small states"]
        return not any(kw in name for kw in skip)

    # ────────────────────────────────────────────────
    # Existing 1–2: Top / Bottom 10
    # ────────────────────────────────────────────────
    def _top_bottom(self, data: List[Dict], continent: str, year: str, top: bool = True) -> List[Dict]:
        country_key = next((k for k in data[0] if "country" in k.lower() and "code" not in k.lower()), "Country Name")

        filtered = filter(
            lambda r: self._is_real_country(r) and r.get("Continent") == continent and self._get_gdp_value(r, year) is not None,
            data
        )

        mapped = map(lambda r: (r[country_key], self._get_gdp_value(r, year), year), filtered)
        sorted_data = sorted(mapped, key=lambda x: x[1], reverse=top)
        return [{"Country": c, "GDP": g, "Year": y} for c, g, y in sorted_data[:10]]

    # ────────────────────────────────────────────────
    # Existing 4–5: Average Continent + Global Trend
    # ────────────────────────────────────────────────
    def _global_trend(self, data: List[Dict], start: int, end: int) -> List[Dict]:
        years = range(start, end + 1)
        def year_total(y: int) -> Tuple[int, float]:
            ys = str(y)
            total = sum(v for r in data if self._is_real_country(r) and (v := self._get_gdp_value(r, ys)) is not None)
            return (y, total)
        return [{"Year": y, "Total GDP": t} for y, t in map(year_total, years)]

    def _average_by_continent(self, data: List[Dict], start: int, end: int) -> List[Dict]:
        from collections import defaultdict

        sums = defaultdict(float)
        counts = defaultdict(int)

        for row in data:
            if not self._is_real_country(row):
                continue
            c = row.get("Continent")
            if not c:
                continue
            for y in range(start, end + 1):
                val = self._get_gdp_value(row, str(y))
                if val is not None:
                    sums[c] += val
                    counts[c] += 1

        return [
            {"Continent": c, "Average GDP": sums[c] / counts[c]}
            for c in sums if counts[c] > 0
        ]

    # ────────────────────────────────────────────────
    # 3. Growth Rates (per country in continent)
    # ────────────────────────────────────────────────
    def _growth_rates(self, data: List[Dict], continent: str, start: int, end: int) -> List[Dict]:
        country_key = next((k for k in data[0] if "country" in k.lower() and "code" not in k.lower()), "Country Name")

        def country_growths(row: Dict) -> Dict | None:
            if not self._is_real_country(row) or row.get("Continent") != continent:
                return None
            name = row[country_key]
            years = [str(y) for y in range(start, end + 1)]
            gdps = [self._get_gdp_value(row, y) for y in years]

            # Build list of valid consecutive pairs only
            growths = []
            for i in range(len(gdps) - 1):
                prev = gdps[i]
                curr = gdps[i+1]
                if prev is not None and curr is not None and prev != 0:
                    growth_pct = ((curr - prev) / prev) * 100
                    growths.append({"Year": int(years[i+1]), "Growth %": growth_pct})

            if len(growths) < 1:  # need at least one valid growth
                return None

            avg_growth = sum(g["Growth %"] for g in growths) / len(growths)
            return {"Country": name, "Average Growth": avg_growth, "Growths": growths}

        all_growths = [g for g in map(country_growths, data) if g is not None]
        sorted_growths = sorted(all_growths, key=lambda x: x["Average Growth"], reverse=True)
        return sorted_growths[:8]  # top 8 by average growth

    # ────────────────────────────────────────────────
    # 6. Fastest Growing Continent
    # ────────────────────────────────────────────────
    def _fastest_growing_continent(self, data: List[Dict], start: int, end: int) -> List[Dict]:
        def continent_growths() -> Dict[str, List[float]]:
            cont_growth = {}
            for row in data:
                if not self._is_real_country(row):
                    continue
                c = row.get("Continent")
                if not c:
                    continue
                gdps = [self._get_gdp_value(row, str(y)) for y in range(start + 1, end + 1)]
                prev = self._get_gdp_value(row, str(start))
                if prev is None or None in gdps:
                    continue
                growths = [(g - prev) / prev * 100 if prev != 0 else 0 for g in gdps]
                cont_growth[c] = cont_growth.get(c, []) + growths
                prev = gdps[-1]
            return cont_growth

        growths_per_cont = continent_growths()
        avg_growth = {c: sum(g)/len(g) for c, g in growths_per_cont.items() if g}
        return [{"Continent": c, "Avg Annual Growth %": avg_growth[c]} for c in sorted(avg_growth, key=avg_growth.get, reverse=True)]

    # ────────────────────────────────────────────────
    # 7. Consistent Decline
    # ────────────────────────────────────────────────
    def _consistent_decline(self, data: List[Dict], continent: str, num_years: int, end_year: int) -> List[Dict]:
        def has_decline(row: Dict) -> Dict | None:
            if not self._is_real_country(row) or row.get("Continent") != continent:
                return None
            name = row.get("Country Name", "")
            years = [str(y) for y in range(end_year - num_years + 1, end_year + 1)]
            gdps = [self._get_gdp_value(row, y) for y in years]
            if None in gdps or len(gdps) < 2:
                return None
            growths = [(gdps[i+1] - gdps[i]) / gdps[i] for i in range(len(gdps)-1) if gdps[i] != 0]
            if not growths:
                return None
            if all(g < 0 for g in growths):
                avg_decline = sum(growths) / len(growths) * 100
                return {"Country": name, "Years": num_years, "Avg Decline %": avg_decline}
            return None

        # Convert filter to list immediately
        decliners = list(filter(None, map(has_decline, data)))

        # Debug print
        print("Consistent Decline countries found:", len(decliners))
        if decliners:
            print("First few:", [d["Country"] for d in decliners[:3]])

        # Sort by most negative (smallest number) first
        return sorted(decliners, key=lambda x: x["Avg Decline %"])[:10]

    # ────────────────────────────────────────────────
    # 8. Continent Contribution to Global
    # ────────────────────────────────────────────────
    def _continent_contribution(self, data: List[Dict], start: int, end: int) -> List[Dict]:
        yearly_data = []
        for y in range(start, end + 1):
            ys = str(y)
            global_total = sum(
                v for r in data if self._is_real_country(r) and (v := self._get_gdp_value(r, ys)) is not None
            )
            if global_total == 0:
                continue
            cont_totals = reduce(
                lambda acc, r: {**acc, r["Continent"]: acc.get(r["Continent"], 0.0) + (self._get_gdp_value(r, ys) or 0.0)}
                if self._is_real_country(r) else acc,
                data,
                {}
            )
            contrib = {c: (t / global_total * 100) for c, t in cont_totals.items() if t > 0}
            yearly_data.append({"Year": y, "Contributions": contrib, "Global Total": global_total})
        return yearly_data