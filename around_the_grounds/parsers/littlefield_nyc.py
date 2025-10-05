import json
import re
from datetime import datetime
from typing import Any, List, Optional
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from ..models import MusicEvent, Venue
from ..utils.date_utils import DateUtils
from .base import BaseParser


class LittlefieldNYCParser(BaseParser):
    """
    Parser for Littlefield NYC music venue.
    Extracts concert and event information from their all-shows page.
    """

    def __init__(self, venue: Venue) -> None:
        super().__init__(venue)

    async def parse(self, session: aiohttp.ClientSession) -> List[MusicEvent]:
        try:
            soup = await self.fetch_page(session, self.venue.url)
            events = []

            if not soup:
                raise ValueError("Failed to fetch page content")

            # Try to extract from JSON-LD structured data first
            json_ld_events = self._extract_from_json_ld(soup)
            if json_ld_events:
                events.extend(json_ld_events)
                self.logger.info(f"Extracted {len(json_ld_events)} events from JSON-LD")

            # Fall back to HTML parsing if JSON-LD didn't work or found limited events
            if len(events) < 5:  # Arbitrary threshold - if we got very few events, try HTML parsing too
                html_events = self._extract_from_html(soup)
                # Deduplicate events by combining artist name and date
                existing_event_keys = {self._event_key(event) for event in events}
                for event in html_events:
                    event_key = self._event_key(event)
                    if event_key not in existing_event_keys:
                        events.append(event)
                        existing_event_keys.add(event_key)

                self.logger.info(f"Added {len(html_events)} additional events from HTML parsing")

            # Filter and validate events
            valid_events = self.filter_valid_events(events)
            self.logger.info(
                f"Parsed {len(valid_events)} valid events from {len(events)} total"
            )
            return valid_events

        except Exception as e:
            self.logger.error(f"Error parsing Littlefield NYC: {str(e)}")
            raise ValueError(f"Failed to parse Littlefield NYC website: {str(e)}")

    def _extract_from_json_ld(self, soup: BeautifulSoup) -> List[MusicEvent]:
        """Extract events from JSON-LD structured data."""
        events = []

        try:
            # Find all script tags with JSON-LD data
            json_ld_scripts = soup.find_all('script', type='application/ld+json')

            for script in json_ld_scripts:
                if not script.string:
                    continue

                try:
                    data = json.loads(script.string)

                    # Handle both single events and arrays of events
                    if isinstance(data, list):
                        for item in data:
                            event = self._parse_json_ld_event(item)
                            if event:
                                events.append(event)
                    elif isinstance(data, dict):
                        event = self._parse_json_ld_event(data)
                        if event:
                            events.append(event)

                except json.JSONDecodeError as e:
                    self.logger.debug(f"Failed to parse JSON-LD: {str(e)}")
                    continue

        except Exception as e:
            self.logger.debug(f"Error extracting JSON-LD events: {str(e)}")

        return events

    def _parse_json_ld_event(self, data: dict) -> Optional[MusicEvent]:
        """Parse a single event from JSON-LD data."""
        try:
            # Check if this is an Event type
            event_type = data.get('@type')
            if event_type not in ['Event', 'MusicEvent']:
                return None

            # Extract basic event information
            name = data.get('name', '').strip()
            if not name:
                return None

            # Extract performer/artist name
            artist_name = self._extract_artist_from_json_ld(data)
            if not artist_name:
                artist_name = name  # Fall back to event name

            # Extract date and time
            start_date = self._parse_json_ld_datetime(data.get('startDate'))
            if not start_date:
                return None

            end_date = self._parse_json_ld_datetime(data.get('endDate'))
            doors_time = self._parse_json_ld_datetime(data.get('doorTime'))

            # Extract additional details
            description = data.get('description', '').strip()

            # Extract ticket information
            ticket_url = None
            price = None
            if 'offers' in data:
                offers = data['offers']
                if isinstance(offers, list) and offers:
                    offer = offers[0]
                elif isinstance(offers, dict):
                    offer = offers
                else:
                    offer = {}

                if isinstance(offer, dict):
                    ticket_url = offer.get('url')
                    price = offer.get('price') or offer.get('priceRange')

            # Extract age restrictions
            min_age = self._extract_age_restriction(data.get('typicalAgeRange', ''))

            return MusicEvent(
                venue_key=self.venue.key,
                venue_name=self.venue.name,
                artist_name=artist_name,
                date=start_date,
                doors_time=doors_time,
                show_time=start_date,  # Use start_date as show time
                end_time=end_date,
                description=description,
                min_age=min_age,
                ticket_url=ticket_url,
                price=str(price) if price else None,
                ai_generated_name=False,
            )

        except Exception as e:
            self.logger.debug(f"Error parsing JSON-LD event: {str(e)}")
            return None

    def _extract_artist_from_json_ld(self, data: dict) -> Optional[str]:
        """Extract artist/performer name from JSON-LD event data."""
        # Try performer field first
        if 'performer' in data:
            performers = data['performer']
            if isinstance(performers, list) and performers:
                performer = performers[0]
            elif isinstance(performers, dict):
                performer = performers
            else:
                return None

            if isinstance(performer, dict):
                return performer.get('name', '').strip()
            elif isinstance(performer, str):
                return performer.strip()

        # Fall back to checking if the event name contains artist info
        name = data.get('name', '')
        if name:
            # Remove common venue/event prefixes
            cleaned_name = re.sub(r'^(Live at|Concert at|Show at)\s+', '', name, flags=re.IGNORECASE)
            return cleaned_name.strip()

        return None

    def _extract_from_html(self, soup: BeautifulSoup) -> List[MusicEvent]:
        """Extract events from HTML structure."""
        events = []

        try:
            # Look for common event listing patterns
            event_selectors = [
                '.event-listing',
                '.event-item',
                '.show-listing',
                '.event-card',
                '[class*="event"]',
                'article',
                '.post'
            ]

            event_elements = []
            for selector in event_selectors:
                elements = soup.select(selector)
                if elements:
                    event_elements = elements
                    self.logger.debug(f"Found {len(elements)} events using selector: {selector}")
                    break

            if not event_elements:
                # If no specific event containers found, look for patterns in the page
                event_elements = self._find_event_patterns(soup)

            for element in event_elements:
                event = self._parse_html_event(element)
                if event:
                    events.append(event)

        except Exception as e:
            self.logger.debug(f"Error extracting HTML events: {str(e)}")

        return events

    def _find_event_patterns(self, soup: BeautifulSoup) -> List[Any]:
        """Find event patterns when no obvious containers exist."""
        patterns = []

        # Look for elements containing date patterns
        date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?\b'

        for element in soup.find_all(['div', 'article', 'section']):
            text = element.get_text()
            if re.search(date_pattern, text, re.IGNORECASE):
                # This element contains a date, might be an event
                patterns.append(element)

        return patterns[:20]  # Limit to avoid processing too many elements

    def _parse_html_event(self, element: Any) -> Optional[MusicEvent]:
        """Parse a single event from HTML element."""
        try:
            # Extract text content
            text = element.get_text()

            # Extract event title/artist name
            artist_name = self._extract_artist_from_html(element)
            if not artist_name:
                return None

            # Extract date
            date = self._extract_date_from_html(element, text)
            if not date:
                return None

            # Extract times
            doors_time, show_time = self._extract_times_from_html(element, text, date)

            # Extract additional info
            description = self._extract_description_from_html(element)
            min_age = self._extract_age_from_html(element, text)
            ticket_url = self._extract_ticket_url_from_html(element)

            return MusicEvent(
                venue_key=self.venue.key,
                venue_name=self.venue.name,
                artist_name=artist_name,
                date=date,
                doors_time=doors_time,
                show_time=show_time,
                description=description,
                min_age=min_age,
                ticket_url=ticket_url,
                ai_generated_name=False,
            )

        except Exception as e:
            self.logger.debug(f"Error parsing HTML event: {str(e)}")
            return None

    def _extract_artist_from_html(self, element: Any) -> Optional[str]:
        """Extract artist name from HTML element."""
        # Try common selectors for event titles
        title_selectors = [
            'h1', 'h2', 'h3', 'h4',
            '.event-title', '.title', '.event-name',
            '.artist-name', '.performer', '.headline'
        ]

        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                if title and len(title) > 2:
                    return self._clean_artist_name(title)

        # Fall back to looking for the first non-empty text
        texts = [t.strip() for t in element.stripped_strings]
        for text in texts:
            if len(text) > 2 and not self._is_metadata_text(text):
                return self._clean_artist_name(text)

        return None

    def _clean_artist_name(self, name: str) -> str:
        """Clean up artist name by removing common prefixes/suffixes."""
        # Remove common venue/event prefixes
        name = re.sub(r'^(Live at|Concert at|Show at|Event:)\s+', '', name, flags=re.IGNORECASE)

        # Remove ticket/time suffixes
        name = re.sub(r'\s+(tickets?|get tickets?|buy tickets?).*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+\d+:\d+\s*(pm|am).*$', '', name, flags=re.IGNORECASE)

        return name.strip()

    def _is_metadata_text(self, text: str) -> bool:
        """Check if text is likely metadata rather than an artist name."""
        metadata_patterns = [
            r'^\d+:\d+\s*(pm|am)',  # Time
            r'doors?:',  # Doors time
            r'show:',    # Show time
            r'min\.?\s*age',  # Age restriction
            r'tickets?',  # Ticket info
            r'^\$\d+',   # Price
            r'get tickets',  # Ticket link
        ]

        for pattern in metadata_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _extract_date_from_html(self, element: Any, text: str) -> Optional[datetime]:
        """Extract date from HTML element or text."""
        # Try to find date in the text using various patterns
        date_patterns = [
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s*\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group()
                parsed_date = DateUtils.parse_date_from_text(date_str)
                if parsed_date:
                    return parsed_date

        return None

    def _extract_times_from_html(self, element: Any, text: str, date: datetime) -> tuple:
        """Extract doors and show times from HTML."""
        doors_time = None
        show_time = None

        # Look for doors time
        doors_match = re.search(r'doors?:\s*(\d{1,2}:\d{2}\s*(?:pm|am)?)', text, re.IGNORECASE)
        if doors_match:
            time_str = doors_match.group(1)
            doors_time = self._parse_time_with_date(time_str, date)

        # Look for show time
        show_match = re.search(r'show:\s*(\d{1,2}:\d{2}\s*(?:pm|am)?)', text, re.IGNORECASE)
        if show_match:
            time_str = show_match.group(1)
            show_time = self._parse_time_with_date(time_str, date)

        # If no specific doors/show times, look for any time
        if not doors_time and not show_time:
            time_match = re.search(r'\b(\d{1,2}:\d{2}\s*(?:pm|am))\b', text, re.IGNORECASE)
            if time_match:
                time_str = time_match.group(1)
                show_time = self._parse_time_with_date(time_str, date)

        return doors_time, show_time

    def _extract_description_from_html(self, element: Any) -> Optional[str]:
        """Extract event description."""
        desc_selectors = [
            '.description', '.event-description', '.content',
            '.event-content', '.summary', '.excerpt'
        ]

        for selector in desc_selectors:
            desc_elem = element.select_one(selector)
            if desc_elem:
                desc = desc_elem.get_text().strip()
                if desc and len(desc) > 10:
                    return desc[:500]  # Limit length

        return None

    def _extract_age_from_html(self, element: Any, text: str) -> Optional[str]:
        """Extract age restriction information."""
        age_match = re.search(r'min\.?\s*age:?\s*(\d+\+?|all\s+ages?)', text, re.IGNORECASE)
        if age_match:
            return age_match.group(1)

        # Look for common age restriction patterns
        if re.search(r'\b21\+\b', text):
            return "21+"
        elif re.search(r'\b18\+\b', text):
            return "18+"
        elif re.search(r'\ball\s+ages?\b', text, re.IGNORECASE):
            return "All ages"

        return None

    def _extract_ticket_url_from_html(self, element: Any) -> Optional[str]:
        """Extract ticket purchase URL."""
        # Look for ticket links
        ticket_selectors = [
            'a[href*="ticket"]', 'a[href*="eventbrite"]',
            '.ticket-link', '.buy-tickets', '.get-tickets'
        ]

        for selector in ticket_selectors:
            link = element.select_one(selector)
            if link and link.get('href'):
                href = link.get('href')
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    href = urljoin(self.venue.url, href)
                return href

        return None

    def _parse_json_ld_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime from JSON-LD format."""
        if not date_str:
            return None

        try:
            # Handle ISO format
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Try parsing as date only
                return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return DateUtils.parse_date_from_text(date_str)

    def _parse_time_with_date(self, time_str: str, date: datetime) -> Optional[datetime]:
        """Parse time string and combine with date."""
        try:
            # Clean up time string
            time_str = time_str.strip().lower()

            # Parse 12-hour format
            if 'pm' in time_str or 'am' in time_str:
                time_part = re.sub(r'\s*(pm|am)', '', time_str)
                hour, minute = map(int, time_part.split(':'))

                if 'pm' in time_str and hour != 12:
                    hour += 12
                elif 'am' in time_str and hour == 12:
                    hour = 0
            else:
                # Assume 24-hour format
                hour, minute = map(int, time_str.split(':'))

            return date.replace(hour=hour, minute=minute, second=0, microsecond=0)

        except (ValueError, AttributeError):
            return None

    def _extract_age_restriction(self, age_range: str) -> Optional[str]:
        """Extract age restriction from typicalAgeRange field."""
        if not age_range:
            return None

        # Common patterns in age range fields
        if '21' in age_range:
            return "21+"
        elif '18' in age_range:
            return "18+"
        elif 'all' in age_range.lower():
            return "All ages"

        return age_range

    def _event_key(self, event: MusicEvent) -> str:
        """Generate a unique key for an event to detect duplicates."""
        date_str = event.date.strftime('%Y-%m-%d')
        artist_key = event.artist_name.lower().strip()
        return f"{date_str}|{artist_key}"

    def filter_valid_events(self, events: List[MusicEvent]) -> List[MusicEvent]:
        """Filter out invalid events and apply validation rules."""
        valid_events = []

        for event in events:
            # Skip events without required fields
            if not event.artist_name or not event.date:
                continue

            # Skip events with obviously invalid artist names
            if len(event.artist_name.strip()) < 2:
                continue

            # Skip events too far in the past
            from datetime import date, timedelta
            if event.date.date() < date.today() - timedelta(days=1):
                continue

            valid_events.append(event)

        return valid_events

    @property
    def venue(self) -> Venue:
        """Access venue property (compatibility with base parser that expects brewery)."""
        return self.brewery  # BaseParser uses brewery, but we can treat it as venue