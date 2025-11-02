import logging
import re
from datetime import datetime
from typing import List, Optional

import aiohttp

from ..models import FoodTruckEvent
from ..utils.date_utils import DateUtils
from ..utils.timezone_utils import now_in_pacific_naive
from .base import BaseParser


class RouletteParser(BaseParser):
    """Parser for Roulette calendar page."""

    async def parse(self, session: aiohttp.ClientSession) -> List[FoodTruckEvent]:
        """
        Parse events from Roulette calendar.

        Args:
            session: aiohttp session for making HTTP requests

        Returns:
            List of valid FoodTruckEvent objects

        Raises:
            ValueError: If parsing fails
        """
        try:
            soup = await self.fetch_page(session, self.brewery.url)
            events = []

            # Find all event containers
            event_containers = soup.select('div.event')
            self.logger.debug(f"Found {len(event_containers)} event containers")

            for event_elem in event_containers:
                try:
                    # Extract event title
                    title_elem = event_elem.select_one('h2.event-title a')
                    if not title_elem:
                        self.logger.debug("Skipping event: no title found")
                        continue

                    event_name = title_elem.get_text(strip=True)

                    # Extract event time
                    time_elem = event_elem.select_one('div.event-time')
                    if not time_elem:
                        self.logger.debug(f"Skipping event: no time found for {event_name}")
                        continue

                    time_text = time_elem.get_text(strip=True)
                    # Format: "Tuesday, November 4, 2025. 7:00 pm"

                    # Parse date and time
                    date_obj, start_time, end_time = self._parse_datetime(time_text)

                    if not date_obj:
                        self.logger.debug(f"Skipping event: could not parse date from '{time_text}'")
                        continue

                    # Extract description (optional)
                    desc_elem = event_elem.select_one('div.event-desc')
                    description = desc_elem.get_text(strip=True) if desc_elem else None

                    event = FoodTruckEvent(
                        brewery_key=self.brewery.key,
                        brewery_name=self.brewery.name,
                        food_truck_name=event_name,
                        date=date_obj,
                        start_time=start_time,
                        end_time=end_time,
                        description=description,
                    )
                    events.append(event)
                    self.logger.debug(f"Parsed event: {event_name} on {date_obj}")

                except Exception as e:
                    self.logger.warning(f"Error parsing individual event: {e}")
                    continue

            # Filter and validate all events before returning
            valid_events = self.filter_valid_events(events)
            self.logger.info(f"Parsed {len(valid_events)} valid events from {self.brewery.name}")
            return valid_events

        except Exception as e:
            self.logger.error(f"Error parsing {self.brewery.name}: {str(e)}")
            raise ValueError(f"Failed to parse brewery website: {str(e)}")

    def _parse_datetime(self, time_text: str) -> tuple[Optional[datetime], Optional[datetime], Optional[datetime]]:
        """
        Parse date and time from text like "Tuesday, November 4, 2025. 7:00 pm".

        Args:
            time_text: Text containing date and time

        Returns:
            Tuple of (date_obj, start_time, end_time)
        """
        try:
            # Split on period to separate date from time
            parts = time_text.split('.')
            if len(parts) < 2:
                self.logger.debug(f"Could not split date/time: {time_text}")
                return None, None, None

            date_part = parts[0].strip()
            time_part = parts[1].strip()

            # Parse date - format: "Tuesday, November 4, 2025"
            # Remove day of week
            date_without_dow = re.sub(r'^[A-Za-z]+,\s*', '', date_part)

            # Parse date using datetime.strptime for full month name format
            try:
                date_obj = datetime.strptime(date_without_dow, "%B %d, %Y")
            except ValueError:
                self.logger.debug(f"Could not parse date: {date_without_dow}")
                return None, None, None

            # Parse time - format: "7:00 pm" or "8:00 pm"
            time_match = re.search(r'(\d{1,2}):(\d{2})\s*(am|pm)', time_part, re.IGNORECASE)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2))
                am_pm = time_match.group(3).lower()

                # Convert to 24-hour format
                if am_pm == 'pm' and hour != 12:
                    hour += 12
                elif am_pm == 'am' and hour == 12:
                    hour = 0

                start_time = datetime(
                    year=date_obj.year,
                    month=date_obj.month,
                    day=date_obj.day,
                    hour=hour,
                    minute=minute
                )

                # No end time specified for Roulette events
                return date_obj, start_time, None

            # If no time found, just return date
            return date_obj, None, None

        except Exception as e:
            self.logger.warning(f"Error parsing datetime '{time_text}': {e}")
            return None, None, None
