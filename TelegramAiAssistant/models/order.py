from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class OrderItem:
    """Order item model"""
    item_name: str
    item_price: int
    quantity: int
    category: str
    
    @property
    def total_price(self) -> int:
        return self.item_price * self.quantity
    
    def to_dict(self) -> Dict:
        return {
            "item_name": self.item_name,
            "item_price": self.item_price,
            "quantity": self.quantity,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'OrderItem':
        return cls(
            item_name=data["item_name"],
            item_price=data["item_price"],
            quantity=data["quantity"],
            category=data.get("category", "")
        )

@dataclass
class Order:
    """Order model"""
    id: str
    user_id: int
    username: str
    items: List[OrderItem]
    status: str  # pending, preparing, ready, completed, rejected
    created_at: datetime
    staff_message_id: Optional[int] = None
    assigned_to: Optional[int] = None
    updated_at: Optional[datetime] = None
    
    @property
    def total_price(self) -> int:
        return sum(item.total_price for item in self.items)
    
    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "items": [item.to_dict() for item in self.items],
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "staff_message_id": self.staff_message_id,
            "assigned_to": self.assigned_to,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Order':
        items = [OrderItem.from_dict(item) for item in data.get("items", [])]
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            username=data["username"],
            items=items,
            status=data["status"],
            created_at=created_at,
            staff_message_id=data.get("staff_message_id"),
            assigned_to=data.get("assigned_to"),
            updated_at=updated_at
        )
