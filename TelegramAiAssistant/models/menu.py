from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MenuItem:
    """Menu item model"""
    name: str
    price: int
    description: str
    category: str
    available: bool = True
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "category": self.category,
            "available": self.available
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MenuItem':
        return cls(
            name=data["name"],
            price=data["price"],
            description=data.get("description", ""),
            category=data["category"],
            available=data.get("available", True)
        )

@dataclass
class MenuCategory:
    """Menu category model"""
    name: str
    emoji: str
    items: List[MenuItem]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "emoji": self.emoji,
            "items": [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MenuCategory':
        items = [MenuItem.from_dict(item) for item in data.get("items", [])]
        return cls(
            name=data["name"],
            emoji=data.get("emoji", "🍽️"),
            items=items
        )

@dataclass
class Menu:
    """Complete menu model"""
    restaurant_name: str
    categories: List[MenuCategory]
    
    def get_category(self, name: str) -> Optional[MenuCategory]:
        """Get category by name"""
        for category in self.categories:
            if category.name == name:
                return category
        return None
    
    def get_item(self, category_name: str, item_name: str) -> Optional[MenuItem]:
        """Get menu item by category and name"""
        category = self.get_category(category_name)
        if not category:
            return None
        
        for item in category.items:
            if item.name == item_name:
                return item
        return None
    
    def to_dict(self) -> Dict:
        return {
            "restaurant_name": self.restaurant_name,
            "categories": [category.to_dict() for category in self.categories]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Menu':
        categories = [MenuCategory.from_dict(cat) for cat in data.get("categories", [])]
        return cls(
            restaurant_name=data.get("restaurant_name", "Ristorante"),
            categories=categories
        )
