# Cycle-Aware WNBA

**Mission Statement: Cycle-aware sports modeling for public-good impact.**

This repository provides a modular, ethical framework for WNBA performance analysis that incorporates menstrual cycle awareness. Built with civic transparency, athlete dignity, and reproducible research principles at its core, this platform empowers data-driven insights while maintaining strict ethical boundaries.

## Mission & Values

- **Public-Good Impact**: All modeling serves civic transparency and athlete empowerment
- **Ethical Sports Modeling**: Athlete-first privacy, consent, and dignity in all analyses  
- **Cycle-Aware Research**: Evidence-based integration of menstrual health in performance modeling
- **Reproducible Science**: Transparent, auditable, and reproducible methodologies
- **Satirical Reflection**: Optional playful overlays to spark critical thought about sports analytics

## Repository Structure

```
cycle-aware-wnba/
├── README.md                  # High-level overview and civic framing
├── ETHICS.md                  # Civic disclaimers and modeling ethics
├── data/
│   ├── raw/                   # Unprocessed game and cycle data
│   └── processed/             # Feature-engineered datasets
├── modeling/
│   ├── model_report.Rmd       # Modeling summary and performance
│   ├── train_model.R          # Training pipeline
│   └── predict_cycle_phase.R  # Cycle-aware prediction logic
├── dashboard/
│   └── app.R                  # Shiny dashboard logic
├── api/
│   └── plumber.R              # REST API setup
└── utils/
    ├── spreadsync.R           # Sync spreads from external sources
    └── parity_check.R         # Reproducibility and audit script
```

## Features

- **Cycle-Aware Modeling**: Evidence-based integration of menstrual cycle data with performance metrics
- **Ensemble Predictions**: Multiple model approaches (Lasso, Random Forest) for robust predictions
- **Ethical Framework**: Built-in consent tracking, privacy protection, and bias monitoring
- **Reproducible Pipeline**: Full audit trails and environment validation
- **External Data Integration**: Betting spreads alignment and health data synchronization
- **Interactive Dashboard**: Shiny-based visualization with ethical toggle modes
- **REST API**: Programmatic access to predictions and cycle insights
- **Satirical UX Modes**: Optional _CrampCast™_, _MoodSwingMeter™_ overlays for critical reflection

## Setup & Installation

### Prerequisites
- R (version 4.0+)
- Git
- Required R packages (installed automatically via setup script)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/repo-ranger21/cycle-aware-wnba.git
   cd cycle-aware-wnba
   ```

2. **Install R dependencies:**
   ```bash
   Rscript install_packages.R
   ```

3. **Run model training pipeline:**
   ```bash
   Rscript modeling/train_model.R
   ```

4. **Generate cycle-aware predictions:**
   ```bash
   Rscript modeling/predict_cycle_phase.R
   ```

5. **Launch interactive dashboard:**
   ```bash
   Rscript dashboard/app.R
   ```

6. **Access via browser:** Navigate to `http://localhost:3838`

### Advanced Setup

For production deployment with external data sources:

1. **Configure spread synchronization:**
   ```R
   # Edit utils/spreadsync.R with your API keys
   source("utils/spreadsync.R")
   sync_betting_spreads(game_data, cycle_data)
   ```

2. **Run reproducibility audit:**
   ```bash
   Rscript utils/parity_check.R
   ```

3. **Start REST API server:**
   ```bash
   Rscript api/plumber.R
   ```

## Contributor Onboarding

We welcome contributors who share our commitment to ethical sports analytics and athlete empowerment.

### Getting Started as a Contributor

1. **Read our ethics guidelines:** Review [ETHICS.md](ETHICS.md) thoroughly
2. **Understand the codebase:** Explore the modular structure and run example workflows
3. **Set up development environment:** Follow the installation guide above
4. **Run parity checks:** Ensure your environment passes reproducibility tests
5. **Start with documentation:** Contribute to docs, comments, or clarifying examples

### Contribution Areas

- **Modeling Improvements**: Enhanced ensemble methods, feature engineering
- **Data Integration**: New health data sources, improved synchronization
- **Ethical Frameworks**: Bias detection, consent tracking, privacy protection  
- **Visualization**: Dashboard enhancements, reporting improvements
- **Documentation**: Onboarding guides, API documentation, ethical guidelines
- **Testing**: Reproducibility tests, model validation, edge case coverage

### Code Standards

- All code must include ethical disclaimers and consent considerations
- Functions should be modular and well-documented
- Include unit tests for new functionality
- Maintain reproducibility through proper random seed management
- Follow R style guidelines (tidyverse conventions)

### Pull Request Process

1. Fork the repository and create a feature branch
2. Implement changes with proper documentation
3. Run parity checks to ensure reproducibility
4. Add tests for new functionality
5. Update relevant documentation
6. Submit PR with clear description of ethical considerations

## Civic Disclaimers & Satirical Notes

### Important Disclaimers

- **This platform is for research and civic transparency purposes only**
- **All predictions are probabilistic and should never drive discriminatory decisions**
- **Athletes maintain complete autonomy over their health data and performance choices**
- **Always consult qualified health professionals for medical advice**
- **No commercial betting or gambling promotion intended**

### Satirical UX Elements

The platform includes optional satirical overlays designed for critical reflection:

- **CrampCast™**: Playful "intensity weather" predictions to highlight absurdity of over-medicalization
- **MoodSwingMeter™**: Satirical mood tracking to provoke thought about reductive stereotypes  
- **Fatigue-o-Tron**: Humorous fatigue metrics to question simplistic performance assumptions

**These modes are toggleable and intended to spark critical thought about:**
- Reductive approaches to women's health in sports
- The risk of over-medicalizing natural biological processes
- The importance of athlete agency and self-advocacy
- Potential biases in sports analytics

*Toggle these modes via dashboard settings or API parameters. See `dashboard/app.R` for implementation.*

## Academic & Research Use

This platform supports academic research with:
- Full reproducibility documentation
- Ethical review guidelines  
- Data anonymization protocols
- Bias monitoring frameworks
- Performance benchmarking tools

For research collaborations or data access inquiries, please review our ethics guidelines and contact maintainers.

---

## Resources

- **[Model Performance Report](modeling/model_report.Rmd)** - Technical modeling documentation
- **[Ethics Guidelines](ETHICS.md)** - Comprehensive ethical framework
- **[Contributor Guide](CONTRIBUTING.md)** - How to contribute ethically
- **[API Documentation](api/plumber.R)** - REST API reference

---

*Built with ❤️ for athlete empowerment and ethical sports analytics*