"""
LiveKit AI Agent for salon customer service.
"""
import asyncio
from livekit import agents, rtc
from livekit.agents import llm, WorkerOptions, cli
from src.agents.prompts import SALON_SYSTEM_PROMPT, get_escalation_message
from src.services.ai_service import ai_service
from src.services.knowledge_service import knowledge_service
from src.services.help_request_service import help_request_service
from src.models.help_request import HelpRequestCreate
from src.config.settings import settings
from src.utils.logger import logger


class SalonAgent:
    """
    AI agent for handling salon customer calls with human escalation.
    """
    
    def __init__(self):
        self.session_data = {}
    
    async def entrypoint(self, ctx: agents.JobContext):
        """
        Main entry point for LiveKit agent.
        
        This is called when a new call comes in.
        """
        logger.info(f"Agent started for room: {ctx.room.name}")
        
        # Initialize session data
        session_id = ctx.room.name
        self.session_data[session_id] = {
            'customer_phone': None,
            'customer_name': None,
            'conversation_history': []
        }
        
        # Connect to the room
        await ctx.connect()
        
        # Get participant (caller)
        participant = await ctx.wait_for_participant()
        logger.info(f"Participant joined: {participant.identity}")
        
        # Start the conversation
        await self._run_conversation(ctx, participant, session_id)
    
    async def _run_conversation(
        self, 
        ctx: agents.JobContext, 
        participant: rtc.Participant,
        session_id: str
    ):
        """
        Main conversation loop.
        """
        # Initial greeting
        greeting = "Hello! Welcome to Glamour Haven Salon. How can I help you today?"
        await ctx.room.local_participant.publish_data(
            greeting.encode(), 
            reliable=True
        )
        
        # Listen for customer messages
        async for event in rtc.RoomEvent.room_events(ctx.room):
            if isinstance(event, rtc.DataReceived):
                message = event.data.decode()
                logger.info(f"Customer: {message}")
                
                # Add to conversation history
                self.session_data[session_id]['conversation_history'].append({
                    'role': 'user',
                    'content': message
                })
                
                # Process the message
                response = await self._process_message(message, session_id)
                
                # Send response
                await ctx.room.local_participant.publish_data(
                    response.encode(),
                    reliable=True
                )
                
                logger.info(f"Agent: {response}")
    
    async def _process_message(self, message: str, session_id: str) -> str:
        """
        Process customer message and generate response.
        
        Returns:
            AI response or escalation message
        """
        # Search knowledge base
        relevant_knowledge = knowledge_service.search_knowledge(message)
        
        # Build context
        knowledge_list = [entry.to_dict() for entry in relevant_knowledge]
        
        # Check if AI can answer
        needs_help, answer = ai_service.check_if_needs_help(
            message, 
            knowledge_list
        )
        
        if needs_help:
            # Escalate to supervisor
            logger.info("Escalating to supervisor")
            return await self._escalate_to_supervisor(message, session_id)
        
        # AI can answer
        self.session_data[session_id]['conversation_history'].append({
            'role': 'assistant',
            'content': answer
        })
        
        return answer
    
    async def _escalate_to_supervisor(
        self, 
        question: str, 
        session_id: str
    ) -> str:
        """
        Create help request and notify supervisor.
        
        Returns:
            Message to customer about escalation
        """
        session = self.session_data.get(session_id, {})
        
        # Get customer phone (you'd collect this earlier in real implementation)
        customer_phone = session.get('customer_phone', 'unknown')
        
        # Create help request
        request_data = HelpRequestCreate(
            customer_phone=customer_phone,
            customer_name=session.get('customer_name'),
            question=question,
            context=str(session.get('conversation_history', []))
        )
        
        try:
            help_request = help_request_service.create_request(request_data)
            logger.info(f"Help request created: {help_request.request_id}")
        except Exception as e:
            logger.error(f"Failed to create help request: {str(e)}")
            return "I'm having trouble connecting to my supervisor. Please call us back shortly."
        
        return get_escalation_message()


def main():
    """
    Run the LiveKit agent.
    
    Usage:
        python -m src.agents.salon_agent
    """
    agent = SalonAgent()
    
    # Configure worker
    worker = WorkerOptions(
        entrypoint_fnc=agent.entrypoint,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
        ws_url=settings.livekit_url
    )
    
    # Run the agent
    cli.run_app(worker)


if __name__ == "__main__":
    main()