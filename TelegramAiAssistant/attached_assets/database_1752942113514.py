import json
import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.config_file = "data/config.json"
        self.menu_file = "data/menu.json"
        self.ensure_data_directory()
        self.load_data()

    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)

    def load_data(self):
        """Load data from files"""
        self.config = self.load_json(self.config_file, {
            "staff_group_id": None,
            "topics": {},
            "orders": {},
            "sponsors": {},
            "applications": {},
            "user_carts": {},
            "user_states": {}
        })
        
        self.menu_data = self.load_json(self.menu_file, {
            "categories": {
                "🍽️ Menù Completo": {
                    "Hamburger Classico": {"price": 8},
                    "Hamburger Deluxe": {"price": 12},
                    "Cheeseburger": {"price": 10},
                    "Coca Cola": {"price": 3},
                    "Acqua": {"price": 2},
                    "Birra": {"price": 5},
                    "Patatine Fritte": {"price": 4},
                    "Onion Rings": {"price": 4},
                    "Salse Varie": {"price": 1}
                }
            }
        })

    def load_json(self, filename: str, default: Dict) -> Dict:
        """Load JSON file with default fallback"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def save_menu(self):
        """Save menu to file"""
        with open(self.menu_file, 'w', encoding='utf-8') as f:
            json.dump(self.menu_data, f, indent=2, ensure_ascii=False)

    # Staff group management
    def get_staff_group_id(self) -> Optional[int]:
        return self.config.get("staff_group_id")

    def set_staff_group_id(self, group_id: int):
        self.config["staff_group_id"] = group_id
        self.save_config()

    def get_topic_id(self, topic_name: str) -> Optional[int]:
        return self.config.get("topics", {}).get(topic_name)

    def set_topic_id(self, topic_name: str, topic_id: int):
        if "topics" not in self.config:
            self.config["topics"] = {}
        self.config["topics"][topic_name] = topic_id
        self.save_config()

    # Menu management
    def get_menu(self) -> Dict:
        return self.menu_data

    def get_categories(self) -> List[str]:
        return list(self.menu_data.get("categories", {}).keys())
    
    def remove_menu_item(self, category: str, item_name: str):
        """Remove a menu item"""
        if category in self.menu_data.get("categories", {}):
            if item_name in self.menu_data["categories"][category]:
                del self.menu_data["categories"][category][item_name]
                self.save_menu(self.menu_data)
    
    def update_menu_item_price(self, category: str, item_name: str, new_price: int):
        """Update menu item price"""
        if category in self.menu_data.get("categories", {}) and item_name in self.menu_data["categories"][category]:
            self.menu_data["categories"][category][item_name]["price"] = new_price
            self.save_menu(self.menu_data)

    def get_category_items(self, category: str) -> Dict:
        return self.menu_data.get("categories", {}).get(category, {})

    def add_menu_item(self, category: str, name: str, price: int, description: str):
        if "categories" not in self.menu_data:
            self.menu_data["categories"] = {}
        if category not in self.menu_data["categories"]:
            self.menu_data["categories"][category] = {}
        
        self.menu_data["categories"][category][name] = {
            "price": price,
            "description": description
        }
        self.save_menu()

    def remove_menu_item(self, category: str, name: str):
        if category in self.menu_data.get("categories", {}):
            if name in self.menu_data["categories"][category]:
                del self.menu_data["categories"][category][name]
                self.save_menu()

    # Cart management
    def get_user_cart(self, user_id: int) -> List[Dict]:
        """Get user's cart items"""
        if "carts" not in self.config:
            self.config["carts"] = {}
        return self.config["carts"].get(str(user_id), [])

    def add_to_cart(self, user_id: int, item_name: str, item_price: int, category: str):
        """Add item to user's cart"""
        if "carts" not in self.config:
            self.config["carts"] = {}
        
        if str(user_id) not in self.config["carts"]:
            self.config["carts"][str(user_id)] = []
        
        cart_item = {
            "item_name": item_name,
            "item_price": item_price,
            "category": category,
            "quantity": 1,
            "added_at": datetime.now().isoformat()
        }
        
        # Check if item already exists in cart
        existing_item = None
        for item in self.config["carts"][str(user_id)]:
            if item["item_name"] == item_name:
                existing_item = item
                break
        
        if existing_item:
            existing_item["quantity"] += 1
        else:
            self.config["carts"][str(user_id)].append(cart_item)
        
        self.save_config()

    def remove_from_cart(self, user_id: int, item_name: str):
        """Remove item from user's cart"""
        if "carts" not in self.config:
            return
        
        cart = self.config["carts"].get(str(user_id), [])
        self.config["carts"][str(user_id)] = [item for item in cart if item["item_name"] != item_name]
        self.save_config()

    def clear_cart(self, user_id: int):
        """Clear user's cart"""
        if "carts" not in self.config:
            return
        
        if str(user_id) in self.config["carts"]:
            del self.config["carts"][str(user_id)]
            self.save_config()

    def get_cart_total(self, user_id: int) -> int:
        """Get total price of items in cart"""
        cart = self.get_user_cart(user_id)
        return sum(item["item_price"] * item["quantity"] for item in cart)

    def get_cart_count(self, user_id: int) -> int:
        """Get total number of items in cart"""
        cart = self.get_user_cart(user_id)
        return sum(item["quantity"] for item in cart)

    # Order management
    def create_order_from_cart(self, user_id: int, username: str) -> Optional[str]:
        """Create order from user's cart"""
        cart = self.get_user_cart(user_id)
        if not cart:
            return None
        
        order_id = f"order_{user_id}_{int(datetime.now().timestamp())}"
        total_price = self.get_cart_total(user_id)
        
        order_data = {
            "id": order_id,
            "user_id": user_id,
            "username": username,
            "items": cart.copy(),
            "total_price": total_price,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "staff_message_id": None,
            "assigned_to": None
        }
        
        self.config["orders"][order_id] = order_data
        self.clear_cart(user_id)  # Clear cart after creating order
        self.save_config()
        return order_id

    def create_order(self, user_id: int, username: str, item_name: str, item_price: int) -> str:
        """Legacy method for single item orders"""
        order_id = f"order_{user_id}_{int(datetime.now().timestamp())}"
        order_data = {
            "id": order_id,
            "user_id": user_id,
            "username": username,
            "items": [{
                "item_name": item_name,
                "item_price": item_price,
                "quantity": 1
            }],
            "total_price": item_price,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "staff_message_id": None,
            "assigned_to": None
        }
        
        self.config["orders"][order_id] = order_data
        self.save_config()
        return order_id

    def get_order(self, order_id: str) -> Optional[Dict]:
        return self.config.get("orders", {}).get(order_id)

    def update_order_status(self, order_id: str, status: str, staff_user_id: Optional[int] = None):
        if order_id in self.config.get("orders", {}):
            self.config["orders"][order_id]["status"] = status
            self.config["orders"][order_id]["updated_at"] = datetime.now().isoformat()
            if staff_user_id:
                self.config["orders"][order_id]["assigned_to"] = staff_user_id
            self.save_config()

    def set_order_staff_message(self, order_id: str, message_id: int):
        if order_id in self.config.get("orders", {}):
            self.config["orders"][order_id]["staff_message_id"] = message_id
            self.save_config()

    # Sponsor management
    def create_sponsor_request(self, user_id: int, username: str) -> str:
        sponsor_id = f"sponsor_{user_id}_{int(datetime.now().timestamp())}"
        sponsor_data = {
            "id": sponsor_id,
            "user_id": user_id,
            "username": username,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "staff_message_id": None
        }
        
        self.config["sponsors"][sponsor_id] = sponsor_data
        self.save_config()
        return sponsor_id

    def get_sponsor_request(self, sponsor_id: str) -> Optional[Dict]:
        return self.config.get("sponsors", {}).get(sponsor_id)

    def update_sponsor_status(self, sponsor_id: str, status: str):
        if sponsor_id in self.config.get("sponsors", {}):
            self.config["sponsors"][sponsor_id]["status"] = status
            self.config["sponsors"][sponsor_id]["updated_at"] = datetime.now().isoformat()
            self.save_config()

    def set_sponsor_staff_message(self, sponsor_id: str, message_id: int):
        if sponsor_id in self.config.get("sponsors", {}):
            self.config["sponsors"][sponsor_id]["staff_message_id"] = message_id
            self.save_config()

    # Application management
    def create_application(self, user_id: int, username: str, name: str, age: str, role: str) -> str:
        app_id = f"app_{user_id}_{int(datetime.now().timestamp())}"
        app_data = {
            "id": app_id,
            "user_id": user_id,
            "username": username,
            "name": name,
            "age": age,
            "role": role,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "staff_message_id": None
        }
        
        self.config["applications"][app_id] = app_data
        self.save_config()
        return app_id

    def get_application(self, app_id: str) -> Optional[Dict]:
        return self.config.get("applications", {}).get(app_id)

    def update_application_status(self, app_id: str, status: str):
        if app_id in self.config.get("applications", {}):
            self.config["applications"][app_id]["status"] = status
            self.config["applications"][app_id]["updated_at"] = datetime.now().isoformat()
            self.save_config()

    def set_application_staff_message(self, app_id: str, message_id: int):
        if app_id in self.config.get("applications", {}):
            self.config["applications"][app_id]["staff_message_id"] = message_id
            self.save_config()

    def create_comprehensive_application(self, user_id: int, username: str, minecraft_name: str, 
                                       telegram_handle: str, presentation: str, motivation: str,
                                       experience: str, hours: str, suggestions: str, 
                                       situation: str, additional: str) -> str:
        """Create comprehensive application with all fields"""
        app_id = f"app_{user_id}_{int(datetime.now().timestamp())}"
        app_data = {
            "id": app_id,
            "user_id": user_id,
            "username": username,
            "minecraft_name": minecraft_name,
            "telegram_handle": telegram_handle,
            "presentation": presentation,
            "motivation": motivation,
            "experience": experience,
            "hours": hours,
            "suggestions": suggestions,
            "situation": situation,
            "additional": additional,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "staff_message_id": None
        }
        
        self.config["applications"][app_id] = app_data
        self.save_config()
        return app_id

    # User state management
    def set_user_state(self, user_id: int, state: str, data: Dict = None):
        """Set user's current state for multi-step interactions"""
        if "user_states" not in self.config:
            self.config["user_states"] = {}
            
        user_state_key = str(user_id)
        self.config["user_states"][user_state_key] = {
            "state": state,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        
        self.save_config()
    
    def get_user_state(self, user_id: int) -> Optional[Dict]:
        """Get user's current state"""
        if "user_states" not in self.config:
            return None
            
        user_state_key = str(user_id)
        return self.config["user_states"].get(user_state_key)
    
    def clear_user_state(self, user_id: int):
        """Clear user's state"""
        if "user_states" not in self.config:
            return
            
        user_state_key = str(user_id)
        if user_state_key in self.config["user_states"]:
            del self.config["user_states"][user_state_key]
            self.save_config()

    # User states for multi-step processes
    def set_user_state(self, user_id: int, state: str, data: Optional[Dict] = None):
        if "user_states" not in self.config:
            self.config["user_states"] = {}
        
        self.config["user_states"][str(user_id)] = {
            "state": state,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        self.save_config()

    def get_user_state(self, user_id: int) -> Optional[Dict]:
        return self.config.get("user_states", {}).get(str(user_id))

    def clear_user_state(self, user_id: int):
        if "user_states" in self.config and str(user_id) in self.config["user_states"]:
            del self.config["user_states"][str(user_id)]
            self.save_config()
