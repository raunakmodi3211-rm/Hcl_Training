"""
Project 4: Air Quality Insights
Analysis using only NumPy and Pandas.

Expected project structure:
    project/
        data/04_air_quality.csv
        src/analysis.py

Run from the project root:
    python src/analysis.py

The categories describe the PM2.5 concentration band only. They are not
a calculation of the complete National Air Quality Index (AQI).
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# 1. File paths
# ---------------------------------------------------------------------
# Run this script from the project root.
DATA_PATH = "data/04_air_quality.csv"

# Also support keeping the CSV in the current working directory.
try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    DATA_PATH = "04_air_quality.csv"
    df = pd.read_csv(DATA_PATH)


# ---------------------------------------------------------------------
# 2. Load and validate the dataset
# ---------------------------------------------------------------------
required_columns = [
    "Date", "City", "PM25", "PM10", "NO2", "Temperature_C"
]
missing_columns = [column for column in required_columns
                   if column not in df.columns]

if missing_columns:
    raise ValueError(
        "The dataset is missing required columns: "
        + ", ".join(missing_columns)
    )

if df.empty:
    raise ValueError("The dataset contains no records.")

print("Dataset:", DATA_PATH)
print("Original shape:", df.shape)
print("\nFirst five rows:\n", df.head())
print("\nData types:\n", df.dtypes)
print("\nMissing values:\n", df.isna().sum())
print("\nDuplicate rows:", int(df.duplicated().sum()))


# ---------------------------------------------------------------------
# 3. Clean data
# ---------------------------------------------------------------------
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# Convert analysis columns to numeric values safely.
numeric_columns = ["PM25", "PM10", "NO2", "Temperature_C"]
for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

missing_pm25_before = int(df["PM25"].isna().sum())

# Fill missing PM2.5 values using the median for the same city.
city_medians = df.groupby("City")["PM25"].transform("median")
df["PM25"] = df["PM25"].fillna(city_medians)

# Fallback for a city whose PM2.5 values are all missing.
overall_pm25_median = df["PM25"].median()
if pd.isna(overall_pm25_median):
    raise ValueError(
        "PM25 has no valid numeric values, so missing values cannot "
        "be filled and the analysis cannot continue."
    )

df["PM25"] = df["PM25"].fillna(overall_pm25_median)

# Rows without a valid date cannot be included in time-based analysis.
invalid_date_count = int(df["Date"].isna().sum())
df["Month"] = df["Date"].dt.month
df["Year_Month"] = df["Date"].dt.to_period("M").astype("string")


# ---------------------------------------------------------------------
# 4. Descriptive statistics
# ---------------------------------------------------------------------
pm25_values = df["PM25"].to_numpy(dtype=float)

pm25_mean = float(np.mean(pm25_values))
pm25_median = float(np.median(pm25_values))
pm25_min = float(np.min(pm25_values))
pm25_max = float(np.max(pm25_values))
pm25_std = float(np.std(pm25_values, ddof=1)) if len(pm25_values) > 1 else 0.0

percentiles = np.percentile(pm25_values, [25, 50, 75, 90, 95])

summary = pd.DataFrame({
    "Metric": [
        "Count", "Mean", "Median", "Minimum", "Maximum",
        "Standard deviation", "25th percentile", "50th percentile",
        "75th percentile", "90th percentile", "95th percentile"
    ],
    "PM2.5 (ug/m3)": [
        len(pm25_values), pm25_mean, pm25_median, pm25_min, pm25_max,
        pm25_std, *percentiles
    ]
})
summary.to_csv("pm25_overall_summary.csv", index=False)


# ---------------------------------------------------------------------
# 5. Rank cities by average PM2.5
# ---------------------------------------------------------------------
city_summary = (
    df.groupby("City", as_index=False)
      .agg(
          Average_PM25=("PM25", "mean"),
          Median_PM25=("PM25", "median"),
          Maximum_PM25=("PM25", "max"),
          Observations=("PM25", "count")
      )
      .sort_values("Average_PM25", ascending=False)
)
city_summary.to_csv("city_ranking.csv", index=False)


# ---------------------------------------------------------------------
# 6. Highest PM2.5 observations
# ---------------------------------------------------------------------
highest_readings = (
    df.nlargest(10, "PM25")[["Date", "City", "PM25", "PM10", "NO2"]]
)
highest_readings.to_csv(
    "top_10_pm25_readings.csv", index=False
)


# ---------------------------------------------------------------------
# 7. Compare PM10 and PM2.5 city-wise
# ---------------------------------------------------------------------
pollutant_comparison = (
    df.groupby("City", as_index=False)
      .agg(
          Average_PM25=("PM25", "mean"),
          Average_PM10=("PM10", "mean")
      )
)
pollutant_comparison.to_csv(
    "pm10_pm25_city_comparison.csv", index=False
)


# ---------------------------------------------------------------------
# 8. PM2.5 concentration categories
# ---------------------------------------------------------------------
# India National AQI PM2.5 concentration bands, in ug/m3.
bins = [-np.inf, 30, 60, 90, 120, 250, np.inf]
labels = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]

df["PM25_Category"] = pd.cut(
    df["PM25"],
    bins=bins,
    labels=labels,
    right=True,
    include_lowest=True
)

category_counts = (
    df["PM25_Category"].value_counts()
      .reindex(labels, fill_value=0)
      .rename_axis("PM25_Category")
      .reset_index(name="Records")
)
category_counts.to_csv(
    "pm25_category_distribution.csv", index=False
)


# ---------------------------------------------------------------------
# 9. Monthly average PM2.5
# ---------------------------------------------------------------------
valid_dates = df.dropna(subset=["Date"])

monthly_city = (
    valid_dates.groupby(["City", "Year_Month"], as_index=False)
               .agg(Average_PM25=("PM25", "mean"))
)
monthly_city.to_csv(
    "monthly_average_pm25_by_city.csv", index=False
)

monthly_overall = (
    valid_dates.groupby("Year_Month", as_index=False)
               .agg(Average_PM25=("PM25", "mean"))
)
monthly_overall.to_csv(
    "monthly_overall_pm25.csv", index=False
)


# ---------------------------------------------------------------------
# 10. IQR outlier detection using NumPy
# ---------------------------------------------------------------------
q1, q3 = np.percentile(pm25_values, [25, 75])
iqr = q3 - q1
lower_bound = q1 - 1.5 * iqr
upper_bound = q3 + 1.5 * iqr

outliers = df[
    (df["PM25"] < lower_bound) | (df["PM25"] > upper_bound)
]
outliers[["Date", "City", "PM25", "PM10", "NO2"]].to_csv(
    "pm25_iqr_outliers.csv", index=False
)


# ---------------------------------------------------------------------
# 11. Correlation between temperature and PM2.5
# ---------------------------------------------------------------------
correlation_data = df[["Temperature_C", "PM25"]].dropna()

if (
    len(correlation_data) >= 2
    and correlation_data["Temperature_C"].nunique() > 1
    and correlation_data["PM25"].nunique() > 1
):
    correlation = float(np.corrcoef(
        correlation_data["Temperature_C"].to_numpy(dtype=float),
        correlation_data["PM25"].to_numpy(dtype=float)
    )[0, 1])
else:
    correlation = np.nan

correlation_result = pd.DataFrame({
    "Variable_1": ["Temperature_C"],
    "Variable_2": ["PM25"],
    "Pearson_Correlation": [correlation],
    "Valid_Records": [len(correlation_data)]
})
correlation_result.to_csv(
    "temperature_pm25_correlation.csv", index=False
)


# ---------------------------------------------------------------------
# 12. Records above the selected PM2.5 threshold
# ---------------------------------------------------------------------
threshold = 60.0
above_count = int((df["PM25"] > threshold).sum())
total_records = len(df)
above_percent = (above_count / total_records) * 100

threshold_summary = pd.DataFrame({
    "Threshold_PM25_ug_m3": [threshold],
    "Records_Above_Threshold": [above_count],
    "Total_Records": [total_records],
    "Percentage_Above_Threshold": [above_percent]
})
threshold_summary.to_csv(
    "above_threshold_summary.csv", index=False
)


# ---------------------------------------------------------------------
# 13. Save cleaned dataset and chart-ready data tables in the current working directory
# ---------------------------------------------------------------------
df.to_csv("cleaned_air_quality.csv", index=False)

# These CSV files can be used to create charts in another tool.
# No plotting library is used in this project.


# ---------------------------------------------------------------------
# 14. Print key findings
# ---------------------------------------------------------------------
print("\n========== KEY RESULTS ==========")
print(summary.to_string(index=False))

if not city_summary.empty:
    worst_city = city_summary.iloc[0]
    print(
        "\nCity with highest average PM2.5:",
        worst_city["City"],
        f"({worst_city['Average_PM25']:.2f} ug/m3)"
    )

max_row = df.loc[df["PM25"].idxmax()]
print(
    "Highest individual reading:",
    f"{max_row['PM25']:.2f} ug/m3",
    "on",
    max_row["Date"].date() if pd.notna(max_row["Date"]) else "unknown date",
    "in",
    max_row["City"]
)

if not monthly_overall.empty:
    best_month_row = monthly_overall.loc[
        monthly_overall["Average_PM25"].idxmax()
    ]
    print(
        "Month with highest overall average PM2.5:",
        best_month_row["Year_Month"]
    )
else:
    print("Month with highest overall average PM2.5: unavailable")

if np.isnan(correlation):
    print("Temperature-PM2.5 correlation: unavailable")
else:
    print(f"Temperature-PM2.5 correlation: {correlation:.3f}")

print(
    f"Records above {threshold:g} ug/m3: "
    f"{above_count}/{total_records} ({above_percent:.1f}%)"
)
print("IQR outlier count:", len(outliers))
print("Missing PM2.5 values filled:", missing_pm25_before)
print("Rows with invalid dates:", invalid_date_count)
print("\nAnalysis completed successfully.")
print("CSV reports are saved in the current working directory.")
