### Temporal Schedule Management

The system includes comprehensive schedule management for automated workflow execution:

#### Creating and Managing Schedules
```bash
# Create a schedule that runs every 30 minutes
uv run python -m around_the_grounds.temporal.schedule_manager create --schedule-id daily-scrape --interval 30

# Create a schedule with custom config and start paused
uv run python -m around_the_grounds.temporal.schedule_manager create --schedule-id custom-scrape --interval 60 --config /path/to/config.json --paused

# List all schedules
uv run python -m around_the_grounds.temporal.schedule_manager list

# Describe a specific schedule
uv run python -m around_the_grounds.temporal.schedule_manager describe --schedule-id daily-scrape

# Pause/unpause schedules
uv run python -m around_the_grounds.temporal.schedule_manager pause --schedule-id daily-scrape --note "Maintenance window"
uv run python -m around_the_grounds.temporal.schedule_manager unpause --schedule-id daily-scrape

# Trigger immediate execution
uv run python -m around_the_grounds.temporal.schedule_manager trigger --schedule-id daily-scrape

# Update schedule interval
uv run python -m around_the_grounds.temporal.schedule_manager update --schedule-id daily-scrape --interval 45

# Delete a schedule
uv run python -m around_the_grounds.temporal.schedule_manager delete --schedule-id daily-scrape
```