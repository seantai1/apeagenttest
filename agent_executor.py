"""APE Agent Executor - Handles A2A protocol interactions."""

import base64
import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import FilePart, TextPart, Part, TaskState
from a2a.utils import new_agent_text_message, new_task

from agent import APEAgent

logger = logging.getLogger(__name__)


class APEAgentExecutor(AgentExecutor):
    """Agent executor for the APE agent."""

    def __init__(self):
        """Initialize the APE agent executor."""
        self.agent = APEAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute the agent logic for incoming requests.
        
        Args:
            context: The request context containing user message
            event_queue: Queue to send events back to the client
        """
        # try:
            # Extract text and image data from message
        text_prompt = ""
        image_data = None
        
        if context.message and context.message.parts:
            for part in context.message.parts:
                if isinstance(part.root, TextPart):
                    text_prompt += part.root.text + " "
                elif isinstance(part.root, FilePart):
                    # Check if it's an image
                    file_info = part.root.file
                    mime_type = getattr(file_info, 'mime_type', None) or getattr(file_info, 'mimeType', None)
                    
                    if mime_type and mime_type.startswith('image/'):
                        # Extract image data
                        if hasattr(file_info, 'bytes') and file_info.bytes:
                            if isinstance(file_info.bytes, str):
                                # Already base64
                                image_data = {
                                    'mimeType': mime_type,
                                    'data': file_info.bytes
                                }
                            else:
                                # Convert bytes to base64
                                image_data = {
                                    'mimeType': mime_type,
                                    'data': base64.b64encode(file_info.bytes).decode('utf-8')
                                }
                        elif hasattr(file_info, 'data'):
                            image_data = {
                                'mimeType': mime_type,
                                'data': file_info.data
                            }
        
        # Get the query
        query = text_prompt.strip() if text_prompt else context.get_user_input()
        
        # Handle image detection specially (for APE evaluation compatibility)
        if image_data:
            logger.info(f"Processing image with prompt: {query}")
            result = await self.agent.image_detector.detect(query, image_data)
            
            # For images, create task with history (APE evaluation format)
            task = context.current_task
            if not task:
                task = new_task(context.message)
            
            # Create the agent's response message
            agent_message = new_agent_text_message(
                result,
                task.context_id,
                task.id,
            )
            
            # Add to history and mark complete
            task.history.append(agent_message)
            task.status.state = TaskState.completed
            
            # Send the completed task
            await event_queue.enqueue_event(task)
            return
        
        # For non-image requests, use the clean task/artifact pattern
        logger.info(f"Processing query: {query}")
        
        # Create or get task
        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        # Process with the agent
        result = await self.agent.invoke(query)
        
        # Add result as artifact and complete
        await updater.add_artifact(
            [Part(root=TextPart(text=result))],
            name='result',
        )
        await updater.complete()
