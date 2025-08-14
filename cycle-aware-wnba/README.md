# Q4Trackr

**Q4Trackr** is a modular, cycle-aware prediction platform for WNBA performance with a mission to empower civic transparency, athlete dignity, and playful engagement. Built for reproducible research, Q4Trackr combines ethical modeling, explainability-first reporting, and satirical UX overlays (toggleable for fun and reflection).

## Mission

- Ethical, cycle-aware sports modeling
- Civic reporting with transparency
- Athlete-first privacy and consent
- Satirical overlays to spark critical reflection

## Features

- Cycle-aware predictions for WNBA players
- Modular R code for feature engineering and modeling
- Toggle satirical UX modes: _CrampCast™_, _MoodSwingMeter™_ and more
- Shiny dashboard and REST API (optional)
- Full civic reporting and explainability

## Setup

1. Clone the repo:
   ```
   git clone https://github.com/repo-ranger21/Q4Trackr.git
   cd Q4Trackr
   ```
2. Install R packages:
   ```
   Rscript install_packages.R
   ```
3. Run sample predictions:
   ```
   Rscript scripts/run_predictions.R
   ```
4. View outputs in `output/predictions.csv`
5. For dashboard, run:
   ```
   Rscript dashboard/app.R
   ```

## Satirical UX Toggle

Enable playful overlays in the dashboard or API:
- **CrampCast™**: Predicts "intensity weather" for cramps
- **MoodSwingMeter™**: Visualizes mood phase swings
- **Fatigue-o-Tron**: Fatigue index with satirical warnings

_Toggle these modes via dashboard or API parameter. See `dashboard/app.R` and `api/plumber.R`._

---

- [Model Report](model_report.Rmd)
- [Ethics Guidelines](ETHICS.md)

---