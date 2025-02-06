from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import Counter
from ..database.models import UserProfile, QualificationStatus

class UserAnalytics:
    def __init__(self):
        self.cache_duration = timedelta(minutes=15)
        self._cache = {}
    
    async def get_client_analytics(self, users: List[UserProfile]) -> Dict:
        """Generate comprehensive analytics for a client's users"""
        now = datetime.now()
        
        # Basic metrics
        total_users = len(users)
        active_24h = sum(1 for user in users 
                        if now - user.last_interaction < timedelta(days=1))
        
        # Engagement metrics
        total_interactions = sum(user.interaction_count for user in users)
        avg_interactions = total_interactions / total_users if total_users > 0 else 0
        
        # Lead qualification breakdown
        qualification_breakdown = Counter(user.qualification_status for user in users)
        
        # Conversion metrics
        converted = sum(1 for user in users 
                       if user.qualification_status == QualificationStatus.CUSTOMER)
        conversion_rate = (converted / total_users * 100) if total_users > 0 else 0
        
        return {
            "overview": {
                "total_users": total_users,
                "active_users_24h": active_24h,
                "total_interactions": total_interactions,
                "avg_interactions_per_user": round(avg_interactions, 2)
            },
            "lead_qualification": {
                status.value: qualification_breakdown[status]
                for status in QualificationStatus
            },
            "conversion": {
                "converted_users": converted,
                "conversion_rate": round(conversion_rate, 2)
            },
            "timestamp": now.isoformat()
        }
    
    async def get_user_segments(self, users: List[UserProfile]) -> Dict:
        """Segment users based on behavior and attributes"""
        segments = {
            "high_value": [],
            "need_nurturing": [],
            "at_risk": [],
            "new": []
        }
        
        for user in users:
            if user.interaction_count == 0:
                segments["new"].append(user.user_id)
            elif user.lead_score.score >= 70:
                segments["high_value"].append(user.user_id)
            elif now - user.last_interaction > timedelta(days=7):
                segments["at_risk"].append(user.user_id)
            else:
                segments["need_nurturing"].append(user.user_id)
        
        return segments

# Singleton instance
analytics_manager: UserAnalytics = None

def get_analytics_manager() -> UserAnalytics:
    """Get or create analytics manager instance"""
    global analytics_manager
    if analytics_manager is None:
        analytics_manager = UserAnalytics()
    return analytics_manager 