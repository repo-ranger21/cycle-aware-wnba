# Intelligence Feeds Module

## Purpose

The `intelligence_feeds/` module provides ethical, privacy-first data ingestion capabilities for menstruation-linked performance modeling in WNBA analytics. This module normalizes and harmonizes external data sources to support civic-grade, transparent sports analytics while maintaining athlete dignity and consent.

## Ethical Framing

🛡️ **Civic-Grade Analytics**: All data ingestion follows privacy-first principles with explicit athlete consent and anonymization.

🛡️ **Dignity & Respect**: This module treats menstrual health data with the highest level of respect and clinical sensitivity.

🛡️ **Transparency**: All data sources, processing methods, and limitations are documented for public accountability.

🛡️ **Non-Exploitative**: Data is used exclusively for health-supportive research and public good, never for discriminatory or commercial exploitation.

## Module Components

### Data Ingestion Scripts

1. **`ingest_clue_data.py`** - Anonymized menstrual cycle data via Terra API
   - Normalizes flow intensity, ovulation flags, symptom logs
   - Formats for Supabase/local storage integration
   - Includes civic disclaimers and ethical processing notes

2. **`ingest_wearable_data.py`** - Biometric data from consumer devices
   - OAuth integration for Oura, Whoop, Apple Watch
   - Extracts HRV, sleep, skin temperature, breathing rate
   - Timestamp normalization and ethical data handling

3. **`ingest_game_stats.py`** - Official WNBA performance metrics
   - Integration with SportsData.io or NBA.com APIs
   - Synchronizes performance data with cycle phase indicators
   - Player anonymization and reproducible processing

4. **`ingest_weather_sentiment.py`** - Environmental and social context data
   - OpenWeatherMap API for hydration-relevant weather
   - Ethical sentiment analysis from public social media
   - Mood volatility indicators with timestamp alignment

### Documentation

5. **`data_sources.json`** - Comprehensive data source registry
   - API endpoints, authentication methods, rate limits
   - Civic-grade usage guidelines and ethical constraints
   - Data quality metrics and known limitations

## Civic Disclaimers

⚠️ **Medical Disclaimer**: This module is for research purposes only and does not provide medical advice. All predictions are probabilistic and should never replace professional medical consultation.

⚠️ **Privacy Notice**: All athlete data must be explicitly consented to and processed in accordance with applicable privacy laws (GDPR, CCPA, HIPAA where relevant).

⚠️ **Bias Awareness**: Menstrual cycle modeling contains inherent uncertainties and potential biases. All outputs include uncertainty estimates and bias commentary.

⚠️ **Non-Discrimination**: This data must never be used for athlete selection, exclusion, or any form of discrimination based on menstrual cycle status.

## Contributor Onboarding

### Getting Started

1. **Ethics First**: Review `ETHICS.md` and `CONTRIBUTING.md` before making any changes
2. **Consent Required**: Ensure all data sources have proper consent mechanisms
3. **Privacy by Design**: Implement anonymization and data protection from day one
4. **Transparent Processing**: Document all data transformations and assumptions

### Development Guidelines

- **Modular Design**: Each ingestion script should be independently testable
- **Error Handling**: Include robust error handling with ethical fail-safes
- **Documentation**: Every function includes docstrings with ethical considerations
- **Reproducibility**: All scripts should produce consistent, auditable outputs

### Testing & Validation

- Use synthetic/mock data for development and testing
- Include data quality checks and validation metrics
- Test edge cases and error conditions
- Document known limitations and uncertainties

## Data Flow Architecture

```
External APIs → Intelligence Feeds → Normalization → Supabase/Storage
    ↓                ↓                    ↓              ↓
  OAuth/Keys    Ethical Filters    Anonymization    Audit Logs
```

## Contributing

We welcome contributions that advance:
- **Ethical data practices** in sports analytics
- **Privacy-preserving** data processing methods  
- **Transparent modeling** with bias documentation
- **Civic accountability** in algorithmic systems

## Support

For questions about ethical data handling, privacy compliance, or civic-grade analytics, please open an issue with the `ethics` or `privacy` label.

---

*Built by contributors. Audited by ethics. Powered by dignity.*