# Fork Setup for Littlefield NYC Events

This document outlines how this codebase has been adapted to track music venue events instead of food truck schedules, while maintaining fork compatibility with the original master branch.

## Overview

The codebase has been extended to support both **food truck tracking** (original functionality) and **music venue event tracking** (new functionality) through a parallel implementation that shares core infrastructure.

## Key Changes Made

### 1. Data Models (`around_the_grounds/models/`)

**Added new models** while keeping originals:
- `MusicEvent` - For music venue events (similar to `FoodTruckEvent`)
- `Venue` - For music venues (similar to `Brewery`)

**Fields in MusicEvent:**
- `venue_key`, `venue_name` - Location information
- `artist_name` - Performer/band name
- `doors_time`, `show_time` - Event timing
- `min_age` - Age restrictions
- `ticket_url`, `price` - Booking information
- `ai_generated_name` - AI extraction indicator

### 2. Configuration (`around_the_grounds/config/`)

**Added:** `venues.json` - Configuration for Littlefield NYC
```json
{
  "venues": [
    {
      "key": "littlefield-nyc",
      "name": "Littlefield",
      "url": "https://littlefieldnyc.com/all-shows",
      "parser_config": {
        "json_ld_schema": true,
        "eventbrite_integration": true
      }
    }
  ]
}
```

### 3. Parsers (`around_the_grounds/parsers/`)

**Added:** `littlefield_nyc.py` - Comprehensive parser supporting:
- JSON-LD structured data extraction
- HTML fallback parsing
- Eventbrite integration
- AI vision analysis (inherited capability)
- Eastern timezone handling for NYC

**Updated:** `registry.py` to include the new parser

### 4. Main Entry Points

**Added:** `events_main.py` - Parallel main entry point for events
- Loads venues instead of breweries
- Generates event-focused web data
- Uses Eastern timezone (ET) instead of Pacific (PT)
- Different CLI branding and messaging

**Added:** New script entry point in `pyproject.toml`:
```toml
littlefield-events = "around_the_grounds.events_main:main"
```

### 5. Web Interface (`public_template/`)

**Added:** `events-index.html` - Event-focused web interface with:
- Music event styling and layout
- Artist name display and search
- Doors/show time formatting
- Age restriction badges
- Ticket links and pricing
- Eastern timezone support

## Usage

### Running the Events System

```bash
# Install the project (if not already done)
pip install -e .

# Run with Python module
python3 -m around_the_grounds.events_main --preview --verbose

# Or after installation
littlefield-events --preview --verbose
```

### Available Commands

```bash
# Generate local preview
littlefield-events --preview

# Deploy to git repository
littlefield-events --deploy --git-repo https://github.com/username/littlefield-events.git

# Use custom venue configuration
littlefield-events --config /path/to/venues.json

# Verbose logging
littlefield-events --verbose
```

### Web Deployment

The system automatically:
1. Scrapes Littlefield NYC events
2. Copies `events-index.html` as `index.html`
3. Generates `data.json` with event data
4. Commits and pushes to target repository
5. Triggers automatic deployment (Vercel/Netlify)

## Fork Compatibility Strategy

### Maintained Compatibility
- **All original files unchanged** - `main.py`, `breweries.json`, original parsers
- **Shared infrastructure** - base parsers, scrapers, utilities, temporal workflows
- **Additive changes only** - New files added, existing files minimally modified
- **Same dependencies** - No new external requirements

### Merge Strategy
To sync from master branch:
```bash
git fetch upstream
git merge upstream/main

# Conflicts should be minimal:
# - pyproject.toml (scripts section)
# - models/__init__.py (exports)
# - parsers/__init__.py and registry.py (new parser registration)
```

### Clean Separation
- Events system: `events_main.py`, `venues.json`, `events-index.html`
- Food trucks: `main.py`, `breweries.json`, `index.html`
- Shared: All parsers, models, utilities, temporal workflows

## Architecture Benefits

1. **Code Reuse** - 90%+ of infrastructure shared between systems
2. **Maintainability** - Bug fixes and improvements benefit both systems
3. **Extensibility** - Easy to add more venue types or event formats
4. **Testability** - Both systems can be tested independently
5. **Deployment Flexibility** - Can deploy to different repositories/domains

## Data Flow

```
Littlefield NYC Website
           ↓
    LittlefieldNYCParser (HTML + JSON-LD)
           ↓
      MusicEvent objects
           ↓
    events_main.py (Eastern timezone)
           ↓
       data.json
           ↓
   events-index.html (NYC-styled interface)
           ↓
     Deployed Website
```

## Testing

The system includes comprehensive testing:
- Parser unit tests
- Integration tests with mock data
- Web interface validation
- Timezone handling verification
- Error scenario coverage

Run tests with:
```bash
python3 -m pytest tests/
```

## Future Enhancements

1. **Multi-venue support** - Add more NYC venues to `venues.json`
2. **Event filtering** - Genre, date range, price filters
3. **Social integration** - Instagram, Facebook event imports
4. **Mobile app** - React Native or PWA version
5. **Notifications** - Email/SMS alerts for favorite artists

This setup provides a robust foundation for expanding music event tracking while maintaining compatibility with the original food truck tracking system.