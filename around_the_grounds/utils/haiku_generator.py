"""Generate contextual haikus about food truck scenes using Claude AI."""

import asyncio
import logging
import random
from datetime import datetime
from typing import List, Optional

import anthropic

from ..models import FoodTruckEvent


class HaikuGenerator:
    """Generates haikus about food truck events using Claude Sonnet 4.5."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize haiku generator with Anthropic API client."""
        self.client = anthropic.Anthropic(
            api_key=api_key
        )  # Uses ANTHROPIC_API_KEY env var if None
        self.logger = logging.getLogger(__name__)

    async def generate_haiku(
        self, date: datetime, events: List[FoodTruckEvent], max_retries: int = 2
    ) -> Optional[str]:
        """
        Generate a haiku based on today's food truck events.

        Args:
            date: The date for the haiku context
            events: List of food truck events for today
            max_retries: Maximum number of retry attempts

        Returns:
            Haiku string with emojis and 3 lines, or None if generation fails
        """
        if not events:
            self.logger.debug("No events provided for haiku generation")
            return None

        # Retry logic for network issues
        for attempt in range(max_retries + 1):
            try:
                haiku = await self._generate_haiku_internal(date, events)

                if haiku:
                    self.logger.info(f"Generated haiku: {haiku}")
                    return haiku
                else:
                    self.logger.debug("Could not generate haiku")
                    return None

            except anthropic.APITimeoutError:
                if attempt < max_retries:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    continue
                self.logger.warning(
                    f"Haiku generation timed out after {max_retries} retries"
                )
            except anthropic.APIError as e:
                self.logger.error(f"Anthropic API error: {str(e)}")
                break
            except Exception as e:
                if attempt < max_retries:
                    await asyncio.sleep(1)
                    continue
                self.logger.error(f"Error generating haiku: {str(e)}")

        return None

    async def _generate_haiku_internal(
        self, date: datetime, events: List[FoodTruckEvent]
    ) -> Optional[str]:
        """Internal method to generate haiku using Claude API."""
        try:
            # Format date for prompt
            date_str = date.strftime("%B %d, %Y (%A)")

            # Randomly select ONE food truck/brewery combination for diversity
            selected_event = random.choice(events)
            truck_name = selected_event.food_truck_name
            brewery_name = selected_event.brewery_name

            self.logger.debug(
                f"Selected truck for haiku: {truck_name} at {brewery_name}"
            )

            # Build prompt
            prompt = f"""Today's date is: {date_str}

Today's featured food truck: {truck_name} at {brewery_name}

---

Create a haiku (5-7-5 syllable structure) that captures the essence of today's food truck scene in Seattle's Ballard neighborhood. Your haiku should:

1. Reflect the current season and time of year based on today's date
2. Feature the specific food truck ({truck_name}) and brewery ({brewery_name}) mentioned above
3. Evoke the atmosphere of gathering at local breweries and food spots
4. Balance concrete sensory details with seasonal imagery

The haiku should feel authentic to the Pacific Northwest autumn/winter/spring/summer experience and celebrate the diversity of street food culture. Avoid being overly literal - aim for evocative, poetic language that honors the traditional haiku form.

CRITICAL FORMATTING REQUIREMENTS:
- The haiku MUST be exactly 3 lines of text
- Each line must contain actual words, not just emojis
- Add a relevant emoji at the BEGINNING of the first line or at the END of the third line (inline with the text)
- Do NOT put emojis on their own separate lines
- Example format: "🍂 First line text / Second line text / Third line text"

Return only the haiku with inline emoji, nothing else."""

            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=150,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )

            # Extract the response text
            content_block = message.content[0]
            if hasattr(content_block, "text"):
                response_text = content_block.text.strip()  # type: ignore
            else:
                # Handle different content types by converting to string
                response_text = str(content_block).strip()

            if response_text:
                # Clean up the response (remove extra whitespace, ensure 3 lines)
                cleaned_haiku = self._clean_haiku(response_text)
                if cleaned_haiku:
                    return cleaned_haiku
                else:
                    # Incomplete haiku, raise exception to trigger retry
                    raise ValueError("Received incomplete haiku from API")

            return None

        except Exception as e:
            self.logger.error(f"Claude API error generating haiku: {str(e)}")
            raise  # Re-raise to allow retry logic to handle it

    def _clean_haiku(self, haiku: str) -> Optional[str]:
        """Clean up haiku text to ensure proper formatting."""
        # Split by newlines and filter empty lines
        lines = [line.strip() for line in haiku.split("\n") if line.strip()]

        # Filter out lines that are ONLY emojis/symbols (no alphanumeric content)
        text_lines = [line for line in lines if any(c.isalnum() for c in line)]

        # Haiku must have exactly 3 lines with actual text content
        if len(text_lines) < 3:
            self.logger.warning(
                f"Incomplete haiku received ({len(text_lines)} text lines), rejecting"
            )
            return None

        # Take first 3 text lines
        return "\n".join(text_lines[:3])
