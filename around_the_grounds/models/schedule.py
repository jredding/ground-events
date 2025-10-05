from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FoodTruckEvent:
    brewery_key: str
    brewery_name: str
    food_truck_name: str
    date: datetime
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    ai_generated_name: bool = False

    def __str__(self) -> str:
        date_str = self.date.strftime("%Y-%m-%d") if self.date else "None"
        time_str = ""
        if self.start_time:
            time_str = f" {self.start_time.strftime('%H:%M')}"
            if self.end_time:
                time_str += f"-{self.end_time.strftime('%H:%M')}"

        return f"{date_str}{time_str}: {self.food_truck_name} @ {self.brewery_name}"


@dataclass
class MusicEvent:
    venue_key: str
    venue_name: str
    artist_name: str
    date: datetime
    doors_time: Optional[datetime] = None
    show_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    min_age: Optional[str] = None
    ticket_url: Optional[str] = None
    price: Optional[str] = None
    ai_generated_name: bool = False

    def __str__(self) -> str:
        date_str = self.date.strftime("%Y-%m-%d") if self.date else "None"
        time_str = ""
        if self.doors_time:
            time_str = f" Doors: {self.doors_time.strftime('%H:%M')}"
            if self.show_time:
                time_str += f" Show: {self.show_time.strftime('%H:%M')}"
        elif self.show_time:
            time_str = f" Show: {self.show_time.strftime('%H:%M')}"

        return f"{date_str}{time_str}: {self.artist_name} @ {self.venue_name}"
