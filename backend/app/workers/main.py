import asyncio
import signal
from app.di import AppContainer
from app.shared.infrastructure.logging.config import setup_logging, get_logger


async def main():
    """
    Main entry point for the Kafka worker process.
    """
    setup_logging()
    logger = get_logger("kafka_worker")

    # Create the container, which holds our configured event bus and handlers
    container = AppContainer()
    container.wire_event_handlers()  # Ensure handlers are subscribed

    event_bus = container.event_bus()

    # Create a shutdown event that can be triggered by signals
    shutdown_event = asyncio.Event()

    def handle_signal(sig, frame):
        logger.warning(f"Received signal {sig}, initiating graceful shutdown...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info("Starting Kafka worker process...")

    # The run_consumer method is a long-running task
    await event_bus.run_consumer(shutdown_event)

    logger.info("Kafka worker process has shut down.")


if __name__ == "__main__":
    asyncio.run(main())
