"""
Seed initial knowledge base with salon information.
"""
import sys
sys.path.append('.')

from src.services.knowledge_service import knowledge_service
from src.models.knowledge_base import KnowledgeCreate
from src.config.firebase_config import firebase_config
from src.utils.logger import logger


def seed_initial_knowledge():
    """Populate knowledge base with initial salon information."""
    
    logger.info("Seeding knowledge base...")
    
    # Initialize Firebase
    firebase_config.initialize()
    
    initial_knowledge = [
        {
            "question": "What are your business hours?",
            "answer": "We're open Monday-Friday 9 AM-8 PM, Saturday 9 AM-6 PM, and Sunday 10 AM-5 PM.",
            "category": "hours",
            "keywords": ["hours", "open", "timing", "schedule"]
        },
        {
            "question": "How much does a women's haircut cost?",
            "answer": "Women's haircuts range from $45 to $75 depending on the stylist and hair length.",
            "category": "pricing",
            "keywords": ["haircut", "women", "price", "cost"]
        },
        {
            "question": "Do you do hair coloring?",
            "answer": "Yes! We offer hair coloring ($80-$150), highlights ($100-$180), and balayage ($150-$250).",
            "category": "services",
            "keywords": ["coloring", "highlights", "balayage", "dye"]
        },
        {
            "question": "Where are you located?",
            "answer": "We're at 123 Beauty Street, Downtown, near the central metro station with easy parking.",
            "category": "location",
            "keywords": ["location", "address", "where", "parking"]
        },
        {
            "question": "How do I book an appointment?",
            "answer": "You can call us at (555) 123-4567, book online at www.glamourhaven.com, or walk in!",
            "category": "booking",
            "keywords": ["book", "appointment", "schedule", "reserve"]
        },
        {
            "question": "Do you accept walk-ins?",
            "answer": "Yes, walk-ins are welcome! However, appointments are recommended for guaranteed availability.",
            "category": "booking",
            "keywords": ["walk-in", "appointment", "waiting"]
        },
        {
            "question": "What's your cancellation policy?",
            "answer": "We require 24-hour notice for cancellations. Late arrivals may need to reschedule.",
            "category": "policies",
            "keywords": ["cancellation", "policy", "reschedule", "late"]
        },
        {
            "question": "Do you offer manicures and pedicures?",
            "answer": "Yes! Manicures are $25-$35, pedicures are $35-$50, and gel nails are $45-$60.",
            "category": "services",
            "keywords": ["manicure", "pedicure", "nails", "gel"]
        },
        {
            "question": "What facial treatments do you offer?",
            "answer": "We offer various facial treatments ranging from $60 to $100. Book a consultation for personalized recommendations!",
            "category": "services",
            "keywords": ["facial", "skincare", "treatment"]
        },
        {
            "question": "How much does a men's haircut cost?",
            "answer": "Men's haircuts range from $30 to $45 depending on the stylist.",
            "category": "pricing",
            "keywords": ["haircut", "men", "price", "cost"]
        }
    ]
    
    count = 0
    for item in initial_knowledge:
        try:
            entry = KnowledgeCreate(**item)
            knowledge_service.add_entry(entry)
            count += 1
            logger.info(f"Added: {item['question']}")
        except Exception as e:
            logger.error(f"Failed to add entry: {str(e)}")
    
    logger.info(f"✅ Seeded {count} knowledge entries successfully!")


if __name__ == "__main__":
    seed_initial_knowledge()