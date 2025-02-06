from typing import Dict, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import json
import logging

from ..database.models import UserProfile, LeadScore, QualificationStatus
from ..analytics import get_analytics_manager

logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self):
        self.users: Dict[str, Dict[str, UserProfile]] = {}  # client_id -> {user_id -> profile}
        self.data_file = Path("data/users.json")
        self.analytics = get_analytics_manager()
        self._load_users()
    
    def _load_users(self) -> None:
        """Load users from JSON file"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        if self.data_file.exists():
            try:
                with open(self.data_file, "r") as f:
                    data = json.load(f)
                    self.users = {
                        client_id: {
                            user_id: UserProfile(**profile)
                            for user_id, profile in users.items()
                        }
                        for client_id, users in data.items()
                    }
            except Exception as e:
                logger.error(f"Error loading users: {e}")
                self.users = {}
    
    def _save_users(self) -> None:
        """Save users to JSON file"""
        try:
            with open(self.data_file, "w") as f:
                json.dump(
                    {
                        client_id: {
                            user_id: profile.dict()
                            for user_id, profile in users.items()
                        }
                        for client_id, users in self.users.items()
                    },
                    f,
                    default=str,
                    indent=2
                )
        except Exception as e:
            logger.error(f"Error saving users: {e}")

    async def get_or_create_user(
        self,
        phone_number: str,
        client_id: str,
        name: Optional[str] = None
    ) -> UserProfile:
        """Get existing user or create new one"""
        if client_id not in self.users:
            self.users[client_id] = {}
            
        if phone_number not in self.users[client_id]:
            user = UserProfile(
                user_id=phone_number,
                client_id=client_id,
                name=name
            )
            self.users[client_id][phone_number] = user
            self._save_users()
            logger.info(f"Created new user profile for {phone_number}")
        
        return self.users[client_id][phone_number]

    async def update_user_interaction(
        self,
        phone_number: str,
        client_id: str,
        message: str,
        response: str,
        detected_interests: Optional[List[str]] = None
    ) -> UserProfile:
        """Update user interaction and analyze engagement"""
        user = await self.get_or_create_user(phone_number, client_id)
        
        # Update basic metrics
        user.last_interaction = datetime.now()
        user.interaction_count += 1
        
        # Update conversation history
        user.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "response": response
        })
        user.conversation_history = user.conversation_history[-10:]  # Keep last 10
        
        # Update product interests if detected
        if detected_interests:
            user.product_interests.extend(detected_interests)
            user.product_interests = list(set(user.product_interests))  # Remove duplicates
        
        # Update lead score based on interaction
        await self._update_lead_score(user, message)
        
        self._save_users()
        return user

    async def _update_lead_score(self, user: UserProfile, message: str) -> None:
        """Update user's lead score based on interaction"""
        score = user.lead_score.score
        reasons = []
        
        # Scoring based on interaction frequency
        if user.interaction_count > 10:
            score += 2
            reasons.append("High engagement")
        
        # Scoring based on buying signals in message
        buying_signals = ["price", "cost", "buy", "purchase", "interested", "demo"]
        if any(signal in message.lower() for signal in buying_signals):
            score += 5
            reasons.append("Showing buying intent")
        
        # Update lead score
        user.lead_score = LeadScore(
            score=min(100, score),  # Cap at 100
            reasons=reasons,
            confidence=0.8
        )
        
        # Update qualification status based on score
        if score >= 80:
            user.qualification_status = QualificationStatus.HIGHLY_QUALIFIED
        elif score >= 60:
            user.qualification_status = QualificationStatus.QUALIFIED
        elif score >= 30:
            user.qualification_status = QualificationStatus.INVESTIGATING

    async def get_client_analytics(self, client_id: str) -> Dict:
        """Get analytics for a client's users"""
        if client_id not in self.users:
            return {}
            
        users = list(self.users[client_id].values())
        return await self.analytics.get_client_analytics(users)

    async def get_user_segments(self, client_id: str) -> Dict:
        """Get user segments for a client"""
        if client_id not in self.users:
            return {}
            
        users = list(self.users[client_id].values())
        return await self.analytics.get_user_segments(users)

# Singleton instance
user_manager: UserManager = None

def get_user_manager() -> UserManager:
    """Get or create user manager instance"""
    global user_manager
    if user_manager is None:
        user_manager = UserManager()
    return user_manager
