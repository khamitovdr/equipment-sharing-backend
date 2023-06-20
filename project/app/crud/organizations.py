from app.models.organizations import Organization, Activity


async def create_activities(okveds: dict):
    """Creates activities in DB."""
    activities = [Activity(code=code, description=description) for code, description in okveds.items()]
    await Activity.bulk_create(activities)