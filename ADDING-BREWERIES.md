# ADDING NEW BREWERIES
To add a new brewery with proper error handling:

1. **Create Parser Class** in `parsers/` inheriting from `BaseParser`:
```python
from .base import BaseParser
from ..models import FoodTruckEvent
from typing import List
import aiohttp

class NewBreweryParser(BaseParser):
    async def parse(self, session: aiohttp.ClientSession) -> List[FoodTruckEvent]:
        try:
            soup = await self.fetch_page(session, self.brewery.url)
            events = []
            
            # Extract events from HTML with error handling
            # Use self.logger for debugging
            # Use self.validate_event() for data validation
            
            # Filter and validate all events before returning
            valid_events = self.filter_valid_events(events)
            self.logger.info(f"Parsed {len(valid_events)} valid events")
            return valid_events
            
        except Exception as e:
            self.logger.error(f"Error parsing {self.brewery.name}: {str(e)}")
            raise ValueError(f"Failed to parse brewery website: {str(e)}")
```

2. **Register Parser** in `parsers/registry.py`:
```python
from .new_brewery import NewBreweryParser

class ParserRegistry:
    _parsers: Dict[str, Type[BaseParser]] = {
        'new-brewery-key': NewBreweryParser,
        # ... existing parsers
    }
```

3. **Add Configuration** to `config/breweries.json`:
```json
{
  "key": "new-brewery-key",
  "name": "New Brewery Name", 
  "url": "https://newbrewery.com/food-trucks",
  "parser_config": {
    "selectors": {
      "container": ".food-truck-container",
      "date": ".date-element",
      "time": ".time-element"
    }
  }
}
```

4. **Write Tests** in `tests/parsers/test_new_brewery.py`:
- Test successful parsing with mock HTML
- Test error scenarios (network, parsing, validation)
- Test with real HTML fixtures if available
- Mock vision analysis if your parser uses it