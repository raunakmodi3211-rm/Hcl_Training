# Air Quality Insights Dashboard (Python)

## Overview
An individual data-analysis project for the Environment / Smart Cities domain. It analyses the supplied `04_air_quality.csv` dataset and provides an interactive Streamlit dashboard.

## Dataset
- 600 observations
- 4 cities: Delhi, Jaipur, Chandigarh and Lucknow
- Columns: Date, City, PM25, PM10, NO2, Temperature_C, Humidity_Percent
- PM25 has 15 missing values; other columns have no missing values in the supplied file.

## Setup
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

## Run dashboard
```bash
streamlit run app.py
```

## Run analysis without dashboard
```bash
python app.py --analyze
```
This creates CSV outputs in the `outputs/` directory.

## Methodology and assumptions
- Missing PM25 values are filled using the dataset median (82.1). Median imputation is less sensitive to extreme values than mean imputation.
- Date is parsed as datetime; Month is extracted as YYYY-MM.
- City ranking uses mean PM25 after imputation.
- IQR outliers use Q1 - 1.5*IQR and Q3 + 1.5*IQR.
- Task 62 uses a chosen threshold of 60 µg/m³. This is an analyst-selected project threshold, not an official standard.
- The assignment says to use instructor-supplied category thresholds, but none were visible in the provided brief. The code therefore uses clearly labelled provisional project bands (30, 60, 90, 120 µg/m³). Replace these cut-offs if your instructor shares exact values.
- Correlation describes association only; it does not establish causation.

## GitHub submission
Create a new public repository on GitHub, upload all files in this folder, and paste the repository URL into the LMS submission field. Do not upload private credentials.
