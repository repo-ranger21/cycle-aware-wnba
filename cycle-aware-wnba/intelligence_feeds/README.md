# Intelligence Feeds Module

## Purpose

The `intelligence_feeds/` module serves as the ethical data ingestion hub for the cycle-aware WNBA analytics platform. This module ingests and normalizes external data sources to support menstruation-linked performance modeling for WNBA athletes, prioritizing **athlete dignity**, **consent**, and **civic-grade transparency**.

## Ethical Framing

### Core Principles

- **Consent-First**: All data ingestion requires explicit athlete opt-in and can be revoked at any time
- **Privacy-Preserving**: Personal identifiers are anonymized before processing
- **Dignity-Centered**: All modeling serves athlete wellness and performance optimization, never exploitation
- **Transparency**: Data sources, methodologies, and limitations are fully documented
- **Public Good**: Analytics serve civic understanding and athlete empowerment, not commercial exploitation

### Civic Disclaimers

⚠️ **IMPORTANT ETHICAL NOTICE**: This module handles sensitive physiological and performance data. Any use must comply with:
- Athlete consent and data protection laws (GDPR, HIPAA where applicable)
- Non-exploitative research and civic transparency principles
- Privacy-first data handling with anonymization requirements
- Dignity-preserving analysis that empowers rather than exploits athletes

## Module Components

### Data Ingestion Scripts

1. **`ingest_clue_data.py`** - Menstrual Cycle Data
   - Ingests anonymized cycle data via Terra API integration with Clue app
   - Normalizes flow intensity, ovulation indicators, and symptom logs
   - Provides privacy-preserving cycle phase modeling inputs

2. **`ingest_wearable_data.py`** - Biometric Data
   - Connects to Oura, Whoop, and Apple Watch via OAuth
   - Extracts HRV, sleep quality, skin temperature, and breathing patterns
   - Normalizes timestamps for cross-platform compatibility

3. **`ingest_game_stats.py`** - Performance Data  
   - Pulls WNBA player statistics from SportsData.io and NBA.com APIs
   - Synchronizes performance metrics with cycle phase indicators
   - Maintains player privacy through anonymized identifiers

4. **`ingest_weather_sentiment.py`** - Environmental Context
   - Fetches hydration-relevant weather data from OpenWeatherMap API
   - Analyzes public sentiment via Twitter/X NLP (no personal data)
   - Provides mood volatility and environmental context indicators

5. **`data_sources.json`** - Documentation
   - Comprehensive documentation of all external data sources
   - API endpoints, usage terms, and civic compliance notes
   - Data lineage and ethical usage guidelines

## How Each Feed Contributes to Cycle-Aware Modeling

### Physiological Integration
- **Cycle Data** provides hormonal phase context for performance fluctuations
- **Wearable Data** offers objective physiological markers (HRV, sleep, temperature)
- **Combined Analysis** enables evidence-based wellness recommendations

### Performance Context
- **Game Stats** establish baseline performance patterns
- **Environmental Data** accounts for external factors affecting performance
- **Temporal Alignment** ensures all data streams are synchronized

### Ethical Enhancement
- **Transparency** ensures all data sources are documented and auditable
- **Consent Management** maintains athlete control over personal data usage
- **Dignity Preservation** frames analysis in terms of athlete empowerment

## Contributor Onboarding

### Getting Started

1. **Review Ethics Guidelines**: Read `/ETHICS.md` and understand consent requirements
2. **Set Up Environment**: Ensure you have required API keys (see data_sources.json)
3. **Test Data Flows**: Run scripts with sample/test data before using real athlete data
4. **Documentation**: Update this README and data_sources.json for any new integrations

### Development Principles

- **Modularity**: Each script should work independently and be easily testable
- **Reproducibility**: Include clear documentation and example usage
- **Error Handling**: Gracefully handle API failures and missing data
- **Logging**: Log all data access and processing for auditability
- **Testing**: Include unit tests for data normalization functions

### Code Style Guidelines

- Follow Python PEP 8 conventions
- Use clear, descriptive function names
- Include comprehensive docstrings with ethical notes
- Add inline comments explaining privacy-preserving transformations
- Use type hints for better code clarity

### API Key Management

⚠️ **Security Notice**: Never commit API keys or credentials to version control
- Use environment variables for sensitive configuration
- Document required environment variables in each script
- Provide clear setup instructions for contributors

## Data Flow Architecture

```
External APIs → Intelligence Feeds → Normalization → Supabase Storage → Cycle-Aware Modeling
     ↓              ↓                    ↓              ↓                    ↓
Clue/Terra     ingest_clue_data.py   Privacy Layer   Anonymized DB    Ethical Analytics
Wearables      ingest_wearable_data.py   ↓            ↓                    ↓
WNBA APIs      ingest_game_stats.py   Consent Check   Audit Logs       Public Good
Weather/Social ingest_weather_sentiment.py  ↓        ↓                    ↓
                                    Data Validation  Transparency    Athlete Empowerment
```

## Civic Accountability

This module operates under civic-grade transparency principles:
- All data processing is auditable and explainable
- Athlete consent is documented and revocable
- Public benefit takes precedence over commercial interests
- Regular ethical review and bias auditing
- Community oversight and feedback integration

## Support and Contact

For questions about ethical data handling, contributor guidelines, or technical implementation:
- Review the main project `CONTRIBUTING.md` and `ETHICS.md`
- Consult `data_sources.json` for specific API documentation
- Follow civic transparency and athlete dignity principles in all contributions

---

**Remember**: This module exists to empower athletes and advance public understanding of menstrual health in sports. Every line of code should serve these goals with dignity, transparency, and respect.