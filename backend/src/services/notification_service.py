"""
Notification Service - Simulates sending messages to supervisor and customers.
"""
from typing import Optional
from src.models.help_request import HelpRequest
from src.utils.logger import logger


class NotificationService:
    """
    Handles notifications to supervisors and customers.
    
    Phase 1: Console logging simulation
    Phase 2: Can integrate Twilio, webhooks, etc.
    """
    
    def notify_supervisor(self, help_request: HelpRequest) -> bool:
        """
        Notify supervisor about a new help request.
        
        Currently simulated via console log.
        """
        try:
            message = self._format_supervisor_notification(help_request)
            
            logger.info("=" * 60)
            logger.info("📞 SUPERVISOR NOTIFICATION")
            logger.info("=" * 60)
            logger.info(message)
            logger.info("=" * 60)
            
            # TODO: Integrate webhook or SMS in production
            # Example: self._send_webhook(supervisor_webhook_url, message)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to notify supervisor: {str(e)}")
            return False
    
    def notify_customer(
        self, 
        phone: str, 
        question: str, 
        answer: str
    ) -> bool:
        """
        Send follow-up answer to customer.
        
        Currently simulated via console log.
        """
        try:
            message = self._format_customer_notification(question, answer)
            
            logger.info("=" * 60)
            logger.info(f"📱 CUSTOMER NOTIFICATION TO {phone}")
            logger.info("=" * 60)
            logger.info(message)
            logger.info("=" * 60)
            
            # TODO: Integrate Twilio SMS in production
            # Example: self._send_sms(phone, message)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to notify customer: {str(e)}")
            return False
    
    def _format_supervisor_notification(self, help_request: HelpRequest) -> str:
        """Format the supervisor notification message."""
        return f"""Hey! I need help answering a customer question.

Customer: {help_request.customer_name or help_request.customer_phone}
Phone: {help_request.customer_phone}

Question: {help_request.question}

Context: {help_request.context or 'No additional context'}

Request ID: {help_request.request_id}

Please respond through the admin panel to help this customer!
"""
    
    def _format_customer_notification(self, question: str, answer: str) -> str:
        """Format the customer follow-up message."""
        return f"""Hi! Thanks for your patience. Here's the answer to your question:

Your question: {question}

Answer: {answer}

Feel free to call us again if you have more questions!
"""
    
    def _send_webhook(self, url: str, payload: dict) -> bool:
        """
        Send webhook notification (for future integration).
        """
        # TODO: Implement webhook integration
        # import requests
        # response = requests.post(url, json=payload)
        # return response.status_code == 200
        pass
    
    def _send_sms(self, phone: str, message: str) -> bool:
        """
        Send SMS via Twilio (for future integration).
        """
        # TODO: Implement Twilio integration
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=message,
        #     from_=twilio_phone,
        #     to=phone
        # )
        # return message.sid is not None
        pass


# Global service instance
notification_service = NotificationService()