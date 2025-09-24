import abc
import json
import asyncio
from typing import List, Dict, Type, Callable, Awaitable
from confluent_kafka import Producer, Consumer, KafkaException, Message
from app.config import settings
from app.shared.domain.event import DomainEvent
from app.shared.infrastructure.logging.config import get_logger

# --- Type Definitions ---
EventHandler = Callable[[DomainEvent], Awaitable[None]]
logger = get_logger(__name__)

# --- Interface Definition ---
class IEventBus(abc.ABC):
    @abc.abstractmethod
    def publish(self, events: List[DomainEvent]) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    async def run_consumer(self, shutdown_event: asyncio.Event):
        raise NotImplementedError

# --- Kafka Implementation ---
class KafkaEventBus(IEventBus):
    def __init__(self):
        self._producer_config = {'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS}
        self._producer = Producer(self._producer_config)
        
        self._consumer_config = {
            'bootstrap.servers': settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': settings.KAFKA_CONSUMER_GROUP_ID,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,  # Manual commit for at-least-once processing
        }
        self._consumer: Consumer | None = None
        
        # Internal registries for subscriptions
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._topic_to_event_class: Dict[str, Type[DomainEvent]] = {}

    def publish(self, events: List[DomainEvent]) -> None:
        try:
            for event in events:
                topic = event.__class__.__name__
                message = event.model_dump_json()

                self._producer.produce(
                    topic,
                    value=message.encode('utf-8'),
                    callback=self._delivery_report
                )
            
            remaining = self._producer.flush(timeout=5)
            if remaining > 0:
                logger.warning(f"{remaining} messages failed to flush from Kafka producer queue.")
        except BufferError:
            logger.error("Kafka producer's local queue is full.")
        except Exception as e:
            logger.exception(f"An unexpected error occurred while publishing to Kafka: {e}")

    @staticmethod
    def _delivery_report(err, msg: Message):
        if err is not None:
            logger.error(f"Message delivery failed for topic '{msg.topic()}': {err}")
        else:
            logger.info(f"Message delivered to '{msg.topic()}' [partition {msg.partition()}]")

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """
        Registers a handler for a specific event type in memory.
        The actual Kafka consumer subscription happens when `run_consumer` is called.
        """
        topic = event_type.__name__
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        
        self._subscribers[topic].append(handler)
        self._topic_to_event_class[topic] = event_type
        
        logger.info(f"Handler for topic '{topic}' has been registered in memory.")

    async def run_consumer(self, shutdown_event: asyncio.Event):
        """
        A long-running consumer loop. It creates, subscribes, and runs the consumer.
        """
        # --- [核心修改] ---
        # 1. Check if there are any subscriptions before starting.
        topics_to_subscribe = list(self._subscribers.keys())
        if not topics_to_subscribe:
            logger.warning("No topics to subscribe to. Consumer will not start.")
            return

        # 2. Create the consumer instance right before the loop starts.
        self._consumer = Consumer(self._consumer_config)

        # 3. Subscribe to ALL registered topics at once.
        self._consumer.subscribe(topics_to_subscribe)
        logger.info(f"Kafka consumer subscribed to topics: {topics_to_subscribe}")

        # --- The rest of the loop remains the same ---
        try:
            while not shutdown_event.is_set():
                msg = await asyncio.to_thread(self._consumer.poll, 1.0)

                if msg is None:
                    await asyncio.sleep(0.1)
                    continue
                if msg.error():
                    if msg.error().code() != KafkaException._PARTITION_EOF:
                        logger.error(f"Kafka consumer error: {msg.error()}")
                    continue

                topic = msg.topic()
                
                try:
                    event_class = self._topic_to_event_class.get(topic)
                    if not event_class:
                        logger.warning(f"No event class registered for topic: {topic}")
                        self._consumer.commit(msg, asynchronous=False)
                        continue

                    message_data = json.loads(msg.value().decode('utf-8'))
                    event = event_class.model_validate(message_data)
                    
                    logger.info(f"Consumed event from topic '{topic}'", event_id=event.event_id)
                    
                    if topic in self._subscribers:
                        await asyncio.gather(
                            *(handler(event) for handler in self._subscribers[topic])
                        )
                    
                    self._consumer.commit(msg, asynchronous=False)

                except Exception as e:
                    logger.exception(
                        f"Error processing message from topic '{topic}'",
                        error=e,
                        raw_message=msg.value().decode('utf-8', errors='ignore')
                    )
        finally:
            logger.info("Closing Kafka consumer...")
            if self._consumer:
                self._consumer.close()

    def _get_event_class_from_topic(self, topic: str) -> Type[DomainEvent]:
        # This is a helper method, let's add it for completeness
        # A more robust solution might use a central registry.
        event_class = self._topic_to_event_class.get(topic)
        if not event_class:
            raise ValueError(f"No event class found for topic: {topic}")
        return event_class