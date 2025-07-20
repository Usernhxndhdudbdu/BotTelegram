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
            "carts": {},
            "user_states": {},
            "admins": [],
            "order_counter": 0,
            "sponsor_counter": 0
        })

        self.menu_data = self.load_json(self.menu_file, {
            "categories": {
                "🍔 Panini": {
                    "Hamburger Classico": {"price": 8, "description": "Hamburger con carne, lattuga e pomodoro"},
                    "Hamburger Deluxe": {"price": 12, "description": "Hamburger con doppia carne e formaggio"},
                    "Cheeseburger": {"price": 10, "description": "Hamburger con formaggio fuso"}
                },
                "🥤 Bevande": {
                    "Coca Cola": {"price": 3, "description": "Bibita fresca"},
                    "Acqua": {"price": 2, "description": "Acqua naturale"},
                    "Birra": {"price": 5, "description": "Birra fresca"}
                },
                "🍟 Extra": {
                    "Patatine Fritte": {"price": 4, "description": "Patatine croccanti"},
                    "Onion Rings": {"price": 4, "description": "Anelli di cipolla fritti"},
                    "Salse Varie": {"price": 1, "description": "Ketchup, maionese, senape"}
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

    def add_menu_item(self, category: str, name: str, price: int, description: str) -> bool:
        """Add new item to menu"""
        if "categories" not in self.menu_data:
            self.menu_data["categories"] = {}
        if category not in self.menu_data["categories"]:
            self.menu_data["categories"][category] = {}

        if name in self.menu_data["categories"][category]:
            return False  # Item already exists

        self.menu_data["categories"][category][name] = {
            "price": price,
            "description": description
        }
        self.save_menu()
        return True

    def remove_menu_item(self, category: str, item_name: str) -> bool:
        """Remove item from menu"""
        if "categories" not in self.menu_data or category not in self.menu_data["categories"]:
            return False

        if item_name in self.menu_data["categories"][category]:
            del self.menu_data["categories"][category][item_name]
            self.save_menu()
            return True
        return False

    def add_category(self, category_name: str) -> bool:
        """Add new category"""
        if "categories" not in self.menu_data:
            self.menu_data["categories"] = {}

        if category_name in self.menu_data["categories"]:
            return False  # Category already exists

        self.menu_data["categories"][category_name] = {}
        self.save_menu()
        return True

    def remove_category(self, category_name: str) -> bool:
        """Remove category"""
        if "categories" not in self.menu_data or category_name not in self.menu_data["categories"]:
            return False

        del self.menu_data["categories"][category_name]
        self.save_menu()
        return True

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

    def get_category_items(self, category: str) -> Dict:
        return self.menu_data.get("categories", {}).get(category, {})

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

        # Increment order counter for sequential numbering
        self.config["order_counter"] = self.config.get("order_counter", 0) + 1
        order_number = self.config["order_counter"]
        order_id = f"{order_number}"
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

        if "orders" not in self.config:
            self.config["orders"] = {}

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

        if "orders" not in self.config:
            self.config["orders"] = {}

        self.config["orders"][order_id] = order_data
        self.save_config()
        return order_id

    def add_admin(self, user_id: int) -> bool:
        """Add a new admin"""
        if 'admins' not in self.config:
            self.config['admins'] = []

        if user_id not in self.config['admins']:
            self.config['admins'].append(user_id)
            self.save_config()
            return True
        return False

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.config.get('admins', [])

    def set_sponsor_channel_id(self, channel_id: int):
        """Set sponsor channel ID"""
        self.config["sponsor_channel_id"] = channel_id
        self.save_config()

    def get_sponsor_channel_id(self) -> Optional[int]:
        """Get sponsor channel ID"""
        return self.config.get("sponsor_channel_id")

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
    def create_sponsor_request(self, user_id: int, username: str, message: str, original_message_id: int = None, original_chat_id: int = None) -> str:
        # Increment sponsor counter for sequential numbering
        self.config["sponsor_counter"] = self.config.get("sponsor_counter", 0) + 1
        sponsor_number = self.config["sponsor_counter"]
        sponsor_id = f"S{sponsor_number}"
        sponsor_data = {
            "id": sponsor_id,
            "user_id": user_id,
            "username": username,
            "message": message,
            "original_message_id": original_message_id,
            "original_chat_id": original_chat_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "staff_message_id": None
        }

        if "sponsors" not in self.config:
            self.config["sponsors"] = {}

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
    def create_application(self, user_id: int, username: str, full_name: str, minecraft_name: str, 
                         telegram: str, presentation: str, reason: str, experience: str, 
                         hours: str, advice: str, bad_employee: str, additional: str) -> str:
        app_id = f"app_{user_id}_{int(datetime.now().timestamp())}"
        app_data = {
            "id": app_id,
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "minecraft_name": minecraft_name,
            "telegram": telegram,
            "presentation": presentation,
            "reason": reason,
            "experience": experience,
            "hours": hours,
            "advice": advice,
            "bad_employee": bad_employee,
            "additional": additional,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "staff_message_id": None
        }

        if "applications" not in self.config:
            self.config["applications"] = {}

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

    # Admin management
    def add_admin(self, user_id: int) -> bool:
        """Add a new admin"""
        if "admins" not in self.config:
            self.config["admins"] = []

        if user_id not in self.config["admins"]:
            self.config["admins"].append(user_id)
            self.save_config()
            return True
        return False

    def remove_admin(self, user_id: int) -> bool:
        """Remove an admin"""
        if "admins" not in self.config:
            return False

        if user_id in self.config["admins"]:
            self.config["admins"].remove(user_id)
            self.save_config()
            return True
        return False

    def get_admins(self) -> list:
        """Get list of admin user IDs"""
        return self.config.get("admins", [])

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.config.get("admins", [])

    def get_current_time(self) -> datetime:
        """Get current datetime"""
        return datetime.now()
    
    def set_user_minecraft_name(self, user_id: int, minecraft_name: str, username: str = None):
        """Set user minecraft name"""
        if "minecraft_names" not in self.config:
            self.config["minecraft_names"] = {}
        if "users" not in self.config:
            self.config["users"] = {}
        
        self.config["minecraft_names"][str(user_id)] = minecraft_name
        self.config["users"][str(user_id)] = {
            "minecraft_name": minecraft_name,
            "username": username,
            "banned": False,
            "registered_at": self.get_current_time().isoformat()
        }
        self.save_config()
    
    def get_user_minecraft_name(self, user_id: int) -> str:
        """Get user minecraft name"""
        return self.config.get("minecraft_names", {}).get(str(user_id))
    
    def ban_user(self, user_id: int):
        """Ban user from bot"""
        if "users" not in self.config:
            self.config["users"] = {}
        if str(user_id) not in self.config["users"]:
            self.config["users"][str(user_id)] = {}
        
        self.config["users"][str(user_id)]["banned"] = True
        self.save_config()
    
    def unban_user(self, user_id: int):
        """Unban user from bot"""
        if "users" not in self.config:
            self.config["users"] = {}
        if str(user_id) not in self.config["users"]:
            self.config["users"][str(user_id)] = {}
        
        self.config["users"][str(user_id)]["banned"] = False
        self.save_config()
    
    def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        return self.config.get("users", {}).get(str(user_id), {}).get("banned", False)
    
    def get_all_users(self) -> dict:
        """Get all registered users"""
        return self.config.get("users", {})