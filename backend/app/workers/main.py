import asyncio
from app.container import AppContainer
from app.shared.infrastructure.logging.config import get_logger

# --- [新增] ---
# 将核心消费逻辑封装在一个可被调用的函数中
async def run_kafka_consumer_in_background(container: AppContainer):
    """
    Runs the Kafka consumer loop. This function is designed to be called
    and run as a background task.
    """
    logger = get_logger("kafka_worker")
    
    # The container already has handlers subscribed from di.py
    event_bus = container.event_bus()
    
    shutdown_event = asyncio.Event()

    # In a background task, we can't easily catch SIGINT/SIGTERM.
    # Graceful shutdown will be handled by the main app's lifespan.
    logger.info("Starting Kafka consumer in background...")
    
    try:
        await event_bus.run_consumer(shutdown_event)
    except asyncio.CancelledError:
        logger.info("Kafka consumer background task was cancelled.")
    finally:
        logger.info("Kafka consumer background task has stopped.")

async def main_standalone():
    """Main entry point for running the worker as a standalone process."""
    from app.di import initialize_dependencies_for_worker
    
    container = initialize_dependencies_for_worker() # A new DI setup for worker
    await run_kafka_consumer_in_background(container)

if __name__ == "__main__":
    asyncio.run(main_standalone())