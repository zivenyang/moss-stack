from app.shared.infrastructure.logging.config import get_logger
from ..domain.events import UserRegistered
# To avoid coupling, handlers could depend on a UoW factory
# from app.shared.infrastructure.uow import IUnitOfWork
# from dependency_injector.providers import Factory

logger = get_logger(__name__)


class IamEventHandlers:
    """Container class for IAM event handlers."""

    async def send_welcome_email(self, event: UserRegistered):
        """Async event handler to send a welcome email."""
        logger.info(
            "ASYNC: Sending welcome email...",
            recipient=event.email,
            user_id=event.user_id,
        )
        # Simulate an async IO operation, like an HTTP call to a mail service
        # await aiosmtplib.send(...)
        # For now, just a sleep to simulate work
        import asyncio

        await asyncio.sleep(2)

        logger.info("ASYNC: Welcome email sent successfully.")
