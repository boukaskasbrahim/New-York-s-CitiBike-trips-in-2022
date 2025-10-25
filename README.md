# New York CitiBike Trips in 2022

## Overview
This project was completed as part of CareerFoundry’s Data Analytics Program, Achievement 2, Exercise 2.2.  
The goal was to collect, clean, and combine CitiBike’s 2022 trip data with daily weather data from NOAA to explore how weather conditions might affect bike usage in New York City.

The exercise covered project planning, API sourcing, and data integration while following best practices in environment setup, data management, and version control.

---

## Project Steps
1. Planned the project and defined the goal of combining CitiBike data with weather data.
2. Collected CitiBike 2022 trip data from the official public S3 source.
3. Cleaned and merged all twelve monthly datasets using Python.
4. Retrieved daily average temperature data from the NOAA API (station: LaGuardia Airport, New York).
5. Merged both datasets by date to create one combined dataset for analysis.
6. Pushed all relevant files to GitHub, excluding large data files as instructed in the course.

---

## Repository Structure
```bash

New-York-s-CitiBike-trips-in-2022/
├── notebooks/
│ └── 2.2_citibike_weather_merge.ipynb
├── requirements.txt
├── README.md
└── .gitignore

```

---

## Data Sources
- **CitiBike NYC 2022 Data:** https://s3.amazonaws.com/tripdata/index.html  
- **Weather Data (NOAA API):** https://www.ncdc.noaa.gov/cdo-web/  
  - Dataset ID: GHCND  
  - Station ID: USW00014739 (LaGuardia Airport)  
  - Parameter: TAVG (average daily temperature in °C)

> Note: The raw CitiBike data and merged CSV files were not uploaded to GitHub because they exceed 25 MB.  
> The notebook can be used to reproduce all data and analysis steps locally.

---

## Tools Used
- Python (pandas, requests, dotenv)  
- Jupyter Notebook  
- NOAA API  
- Conda environment  
- Git and GitHub

---

## Author
**Brahim Boukaskas**  
CareerFoundry Data Analytics Program  
GitHub: [boukaskasbrahim](https://github.com/boukaskasbrahim)

