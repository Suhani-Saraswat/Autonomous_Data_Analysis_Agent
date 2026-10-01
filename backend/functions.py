from typing import Any
import pandas as pd
import numpy as np


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    columns = []
    for col in df.columns:
        s = df[col]
        missing = int(s.isna().sum())
        unique = int(s.nunique(dropna=True))
        if pd.api.types.is_numeric_dtype(s):
            clean = pd.to_numeric(s, errors="coerce")
            distribution = {
                "mean": round(float(clean.mean()), 2) if clean.notna().any() else None,
                "min": round(float(clean.min()), 2) if clean.notna().any() else None,
                "max": round(float(clean.max()), 2) if clean.notna().any() else None,
            }
        else:
            counts = s.astype("string").value_counts(dropna=True).head(3)
            distribution = {str(k): int(v) for k, v in counts.items()}
        columns.append({
            "name": str(col), "type": str(s.dtype), "missing": missing,
            "missing_pct": round(missing / max(len(df), 1) * 100, 2), "unique": unique,
            "distribution": distribution, "samples": [str(x) for x in s.dropna().head(3).tolist()],
        })
    return {
        "rows": int(len(df)), "columns": int(len(df.columns)),
        "duplicate_rows": int(df.duplicated().sum()), "column_profiles": columns,
    }


def infer_plan(query: str, df: pd.DataFrame) -> list[str]:
    q = query.lower()
    plan = ["Inspect schema and identify relevant measures and dimensions"]
    if "region" in q: plan.append("Group sales and profit by region")
    if "profit" in q or "margin" in q: plan.append("Calculate profit totals and profit margin")
    if "discount" in q: plan.append("Measure discount relationship with sales and profit")
    if "segment" in q: plan.append("Aggregate metrics by customer segment")
    if "category" in q: plan.append("Aggregate metrics by product category")
    if "product" in q and "category" not in q: plan.append("Identify product-level sales and profit patterns")
    if "trend" in q or "month" in q or "time" in q: plan.append("Parse dates and calculate monthly trend")
    if "outlier" in q or "unusual" in q: plan.append("Detect numerical outliers using IQR")
    if "top" in q or "highest" in q or "lowest" in q: plan.append("Rank the relevant groups and identify the requested top or bottom items")
    if len(plan) == 1: plan.extend(["Compute descriptive statistics", "Generate an evidence-backed summary"])
    return plan


def _numeric(df, col):
    return pd.to_numeric(df[col], errors="coerce") if col in df.columns else pd.Series(dtype=float)


def _clean_group_name(value):
    if pd.isna(value): return "Unknown"
    text = str(value).strip()
    return text if text else "Unknown"


def _bar_chart(title, series):
    series = series.dropna()
    return {
        "type": "bar", "title": title,
        "labels": [_clean_group_name(x) for x in series.index],
        "values": [round(float(x), 2) for x in series.values],
    }


def execute_plan(df: pd.DataFrame, query: str) -> tuple[dict, dict, list[str]]:
    q = query.lower()
    metrics: dict[str, Any] = {}
    chart = {"type": "bar", "title": "Analysis Result", "labels": [], "values": []}
    insights: list[str] = []

    sales = _numeric(df, "Sales")
    profit = _numeric(df, "Profit")
    quantity = _numeric(df, "Quantity")
    discount = _numeric(df, "Discount")

    if "region" in q and "Region" in df.columns:
        temp = df.assign(_sales=sales, _profit=profit).groupby("Region", dropna=False)[["_sales", "_profit"]].sum()
        temp.index = [_clean_group_name(x) for x in temp.index]
        temp = temp.sort_values("_sales", ascending=False)
        metrics["by_region"] = {str(idx): {"sales": round(float(row["_sales"]), 2), "profit": round(float(row["_profit"]), 2)} for idx, row in temp.iterrows()}
        chart = _bar_chart("Sales by Region", temp["_sales"])
        if len(temp):
            top = temp.index[0]
            insights.append(f"{top} has the highest total sales at {temp.iloc[0]['_sales']:,.2f}.")
            margin = temp["_profit"] / temp["_sales"].replace(0, np.nan) * 100
            best_margin = margin.dropna().idxmax() if not margin.dropna().empty else None
            if best_margin is not None:
                insights.append(f"{best_margin} has the highest calculated profit margin at {margin[best_margin]:.2f}%.")
            total_sales = float(temp["_sales"].sum())
            total_profit = float(temp["_profit"].sum())
            metrics["total_sales"] = round(total_sales, 2)
            metrics["total_profit"] = round(total_profit, 2)
            metrics["overall_profit_margin_pct"] = round(total_profit / total_sales * 100, 2) if total_sales else None

    if "category" in q and "Category" in df.columns:
        temp = df.assign(_sales=sales, _profit=profit).groupby("Category")[["_sales", "_profit"]].sum().sort_values("_sales", ascending=False)
        metrics["by_category"] = {str(i): {"sales": round(float(r["_sales"]), 2), "profit": round(float(r["_profit"]), 2)} for i, r in temp.iterrows()}
        chart = _bar_chart("Sales by Category", temp["_sales"])
        if len(temp): insights.append(f"{temp.index[0]} generates the highest sales among the available categories.")

    if "segment" in q and "Segment" in df.columns:
        temp = df.assign(_profit=profit).groupby("Segment")['_profit'].sum().sort_values(ascending=False)
        metrics["by_segment"] = {str(i): round(float(v), 2) for i, v in temp.items()}
        chart = _bar_chart("Profit by Customer Segment", temp)
        if len(temp): insights.append(f"{temp.index[0]} has the highest total profit.")

    if "discount" in q:
        corr = discount.corr(sales)
        metrics["discount_sales_correlation"] = None if pd.isna(corr) else round(float(corr), 4)
        if not pd.isna(corr):
            direction = "positive" if corr > 0 else "negative" if corr < 0 else "near-zero"
            insights.append(f"The Pearson correlation between discount and sales is {corr:.3f}, indicating a {direction} linear relationship in this dataset.")
        valid = pd.DataFrame({"discount": discount, "sales": sales}).dropna()
        chart = {
            "type": "scatter", "title": "Discount vs Sales",
            "x_labels": [round(float(x), 4) for x in valid["discount"].head(250).tolist()],
            "y_values": [round(float(x), 2) for x in valid["sales"].head(250).tolist()],
        }

    if ("trend" in q or "month" in q or "time" in q) and "Order_Date" in df.columns:
        dates = pd.to_datetime(df["Order_Date"], errors="coerce")
        temp = pd.DataFrame({"date": dates, "sales": sales}).dropna()
        monthly = temp.assign(month=temp["date"].dt.to_period("M").astype(str)).groupby("month")["sales"].sum()
        metrics["monthly_sales"] = {str(i): round(float(v), 2) for i, v in monthly.items()}
        chart = {"type": "line", "title": "Monthly Sales Trend", "labels": list(monthly.index), "values": [round(float(v), 2) for v in monthly.values]}
        if len(monthly) >= 2:
            change = (monthly.iloc[-1] - monthly.iloc[0]) / max(abs(monthly.iloc[0]), 1) * 100
            insights.append(f"Sales changed by {change:.1f}% from the first to the last observed month.")

    if "outlier" in q or "unusual" in q:
        values = sales.dropna()
        q_values = quantity.dropna()
        if len(values):
            q1, q3 = values.quantile([.25, .75]); iqr = q3 - q1
            low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            count = int(((values < low) | (values > high)).sum())
            metrics["sales_outliers"] = {"count": count, "lower_bound": round(float(low), 2), "upper_bound": round(float(high), 2)}
            insights.append(f"IQR analysis identifies {count:,} sales values outside the calculated bounds.")
        if len(q_values):
            q1, q3 = q_values.quantile([.25, .75]); iqr = q3 - q1
            low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            count = int(((q_values < low) | (q_values > high)).sum())
            metrics["quantity_outliers"] = {"count": count, "lower_bound": round(float(low), 2), "upper_bound": round(float(high), 2)}
            insights.append(f"IQR analysis identifies {count:,} quantity values outside the calculated bounds.")
        counts = []
        if "sales_outliers" in metrics: counts.append(("Sales", metrics["sales_outliers"]["count"]))
        if "quantity_outliers" in metrics: counts.append(("Quantity", metrics["quantity_outliers"]["count"]))
        if counts:
            chart = {"type": "bar", "title": "Detected Outlier Counts", "labels": [x[0] for x in counts], "values": [x[1] for x in counts]}

    if not insights:
        metrics["total_sales"] = round(float(sales.sum()), 2) if sales.notna().any() else None
        metrics["total_profit"] = round(float(profit.sum()), 2) if profit.notna().any() else None
        metrics["average_order_value"] = round(float(sales.mean()), 2) if sales.notna().any() else None
        chart = {"type": "bar", "title": "Dataset Overview", "labels": ["Sales", "Profit", "Avg Sales"], "values": [metrics["total_sales"] or 0, metrics["total_profit"] or 0, metrics["average_order_value"] or 0]}
        insights.append(f"The dataset contains {len(df):,} rows and {len(df.columns):,} columns.")
        if metrics["total_sales"] is not None and metrics["total_profit"] is not None:
            insights.append(f"Total sales are {metrics['total_sales']:,.2f} and total profit is {metrics['total_profit']:,.2f}.")

    return metrics, chart, insights


def validate_results(metrics: dict) -> list[str]:
    errors = []
    def check(v, key):
        if isinstance(v, (int, float)) and not np.isfinite(v): errors.append(f"Non-finite metric detected: {key}")
        elif isinstance(v, dict):
            for k, child in v.items(): check(child, f"{key}.{k}")
    for key, value in metrics.items(): check(value, key)
    return errors
