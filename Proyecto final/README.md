# League of Legends Data Analysis Project

A data-driven approach to extract insights from high-tier League of Legends matches using machine learning.

## Overview

This project collects, processes, and analyzes match data from the Riot Games API, focusing on high-ranked players (Master, Grandmaster, and Challenger tiers). The goal is to identify patterns and insights that could help understand game mechanics, player behavior, and winning strategies.

## Components

- **Data Collection**: Scrapes match data from Riot's API, handling rate limits and connection issues (`the_collector.py`)
- **Data Processing**: Cleans and transforms raw match data into structured formats for analysis (`data_processor.py`)
- **Data Analysis**: Applies machine learning algorithms to extract patterns and insights (in development)

## Requirements

- Python 3.7+
- Dependencies: requests, pandas, tqdm, numpy, urllib3
- Riot Games API Key (https://developer.riotgames.com/)

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Update the API_KEY in `the_collector.py` with your Riot Games API key
4. Run the collector to gather match data:
   ```
   python the_collector.py
   ```

## How It Works

### Data Collection Process (`the_collector.py`)

The data collection script follows a three-step pipeline:

1. **Player Collection**: 
   - Fetches high-tier players (Master, Grandmaster, Challenger) from Riot's League API
   - Stores player PUUIDs (unique identifiers) in `players_puuids.json`
   - Uses checkpoint system to save progress periodically

2. **Match ID Collection**:
   - For each player, retrieves their recent ranked matches
   - Stores unique match IDs in `latest_games.json`
   - Avoids duplicate matches across different players

3. **Match Data Collection**:
   - For each match ID, retrieves detailed match data
   - Stores complete match information in `matches_timeline.json`
   - Tracks failed requests in `failed_matches.json`

### Key Features

- **Intelligent Rate Limiting**: Respects Riot API's rate limits by analyzing response headers
- **Exponential Backoff**: Implements retry mechanism with increasing wait times for failures
- **Checkpoint System**: Saves progress at regular intervals to prevent data loss
- **Error Handling**: Gracefully handles network issues, timeouts, and server errors
- **Progress Visualization**: Uses tqdm progress bars to track collection status

### Data Processing

After collection, the data is processed to extract relevant features:
- Team compositions and ban information
- Player performance metrics
- Game objective statistics
- Match outcome predictors

## Project Status

- ✅ Data Collection: Implemented with rate limiting and error handling
- 🔄 Data Processing: Basic cleaning and transformation
- 🚧 Machine Learning: In development
- 📊 Visualization: Planned

## Data Files

The collection script generates several data files:
- `players_puuids.json`: Player identifiers (PUUIDs) for high-ranked players
- `latest_games.json`: Match IDs for ranked games played by these players
- `matches_timeline.json`: Detailed match data including team comps, bans, and player stats
- `failed_matches.json`: Tracking of failed API requests for later retry
- `matches_data.json`: Processed match data in JSON format
- `matches_data.parquet`: Compressed match data in Parquet format
- `players_data.parquet`: Processed player data in Parquet format

**Note**: The data files (`matches_data.json`, `matches_data.parquet`, and `players_data.parquet`) are excluded from version control due to their large size. These files will be generated when running the collection and processing scripts.

## Usage Examples

**Basic data collection:**
```python
# Collect data from Korean server high-tier players
python the_collector.py
```

**Processing collected data:**
```python
# Once data is collected, process it into structured formats
# Note: This will be implemented in future updates
```

## Note

This project is for educational purposes. When using the Riot Games API, please respect their [rate limits and terms of service](https://developer.riotgames.com/policies/general). 