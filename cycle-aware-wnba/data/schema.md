# Q4Trackr Data Schema

## `physio_cycle_sample.csv`

| Column            | Type    | Description                                          |
|-------------------|---------|------------------------------------------------------|
| player_id         | string  | Anonymized player identifier                         |
| game_date         | date    | Date of game                                         |
| cycle_day         | integer | Days since cycle start                               |
| cycle_start       | date    | First day of cycle                                   |
| menstruation_duration | int | Number of days in menstruation period                |
| ovulation_day     | int     | Estimated ovulation day in cycle                     |
| cramps            | int     | Self-reported cramp severity (0-3)                   |
| mood              | int     | Self-reported mood swing (0-3)                       |
| discharge         | int     | Self-reported discharge (0-3)                        |
| bbt               | float   | Basal body temperature                               |
| hr                | int     | Heart rate                                           |
| hrv               | int     | Heart rate variability                               |
| sleep_quality     | float   | 0-1 scale                                            |
| sleep_duration    | float   | Hours slept                                          |
| skin_temp         | float   | Skin temperature                                     |
| breathing_rate    | int     | Breaths per minute                                   |
| flow_intensity    | int     | Self-reported flow scale (1-3)                       |
| lh                | int     | Luteinizing hormone level                            |
| fsh               | int     | Follicle stimulating hormone level                   |
| estrogen          | int     | Estrogen level                                       |
| progesterone      | int     | Progesterone level                                   |
| rest_days         | int     | Days rested before game                              |
| opponent_rating   | float   | Strength of opponent (0-1 scale)                     |
| impact_flag       | int     | Binary outcome for performance impact (1/0)          |

## Civic Reporting Fields

- All columns must be anonymized and consented.
- Cycle-aware features highlighted for explainability-first modeling.

---