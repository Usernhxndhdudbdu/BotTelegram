from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict

class MenuKeyboard:
    """Keyboards for menu navigation"""
    
    @staticmethod
    def home_menu() -> InlineKeyboardMarkup:
        """Home menu keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="🍔 Menu Ristorante", callback_data="main_menu")],
            [InlineKeyboardButton(text="📣 Richiedi Sponsor", callback_data="request_sponsor")],
            [InlineKeyboardButton(text="📝 Invia Candidatura", callback_data="start_application")],
            [InlineKeyboardButton(text="ℹ️ Aiuto", callback_data="help")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="🍔 Menù", callback_data="main_menu")],
            [InlineKeyboardButton(text="📣 Sponsor", callback_data="request_sponsor")],
            [InlineKeyboardButton(text="📝 Candidatura", callback_data="start_application")],
            [InlineKeyboardButton(text="🏠 Torna alla Home", callback_data="back_to_home")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """Help menu keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="🍔 Vai al Menù", callback_data="main_menu")],
            [InlineKeyboardButton(text="📣 Richiedi Sponsor", callback_data="request_sponsor")],
            [InlineKeyboardButton(text="📝 Invia Candidatura", callback_data="start_application")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def categories(categories: List[str], has_cart: bool = False) -> InlineKeyboardMarkup:
        """Categories selection keyboard"""
        keyboard = []
        
        for category in categories:
            keyboard.append([InlineKeyboardButton(
                text=category, 
                callback_data=f"category:{category}"
            )])
        
        if has_cart:
            keyboard.append([InlineKeyboardButton(
                text="🛒 Visualizza Carrello", 
                callback_data="view_cart"
            )])
        
        keyboard.append([InlineKeyboardButton(
            text="🏠 Torna alla Home", 
            callback_data="back_to_home"
        )])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def items(category: str, items: Dict, has_cart: bool = False) -> InlineKeyboardMarkup:
        """Items selection keyboard"""
        keyboard = []
        
        for item_name, item_data in items.items():
            price = item_data.get("price", 0)
            keyboard.append([InlineKeyboardButton(
                text=f"{item_name} - {price}€", 
                callback_data=f"item:{category}:{item_name}"
            )])
        
        # Navigation buttons
        nav_buttons = []
        if has_cart:
            nav_buttons.append(InlineKeyboardButton(
                text="🛒 Carrello", 
                callback_data="view_cart"
            ))
        nav_buttons.append(InlineKeyboardButton(
            text="🔙 Categorie", 
            callback_data="back_to_categories"
        ))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton(
            text="🏠 Torna alla Home", 
            callback_data="back_to_home"
        )])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def cart_actions() -> InlineKeyboardMarkup:
        """Cart actions keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="✅ Procedi all'Ordine", callback_data="checkout")],
            [InlineKeyboardButton(text="🗑️ Svuota Carrello", callback_data="clear_cart")],
            [InlineKeyboardButton(text="🔙 Continua Shopping", callback_data="back_to_categories")],
            [InlineKeyboardButton(text="🏠 Torna alla Home", callback_data="back_to_home")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

class OrderKeyboard:
    """Keyboards for order management"""
    
    @staticmethod
    def confirm_order() -> InlineKeyboardMarkup:
        """Order confirmation keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="✔️ Conferma Ordine", callback_data="confirm_order")],
            [InlineKeyboardButton(text="❌ Annulla", callback_data="cancel_order")],
            [InlineKeyboardButton(text="🏠 Torna alla Home", callback_data="back_to_home")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def staff_order_actions(order_id: str) -> InlineKeyboardMarkup:
        """Staff order management keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(text="🟢 Prendi in Carico", callback_data=f"order_action:accept:{order_id}"),
                InlineKeyboardButton(text="❌ Rifiuta", callback_data=f"order_action:reject:{order_id}")
            ],
            [
                InlineKeyboardButton(text="🔥 Pronto", callback_data=f"order_action:ready:{order_id}"),
                InlineKeyboardButton(text="✅ Completato", callback_data=f"order_action:complete:{order_id}")
            ],
            [
                InlineKeyboardButton(text="💬 Rispondi", callback_data=f"reply_to_user:{order_id}")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """Back to menu keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="🔙 Torna al Menù", callback_data="back_to_menu")],
            [InlineKeyboardButton(text="🏠 Torna alla Home", callback_data="back_to_home")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

class SponsorKeyboard:
    """Keyboards for sponsor requests"""
    
    @staticmethod
    def sponsor_request() -> InlineKeyboardMarkup:
        """Sponsor request keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="📣 Invia Richiesta", callback_data="request_sponsor")],
            [InlineKeyboardButton(text="❌ Annulla", callback_data="cancel_sponsor")],
            [InlineKeyboardButton(text="🏠 Torna alla Home", callback_data="back_to_home")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def staff_sponsor_actions(sponsor_id: str) -> InlineKeyboardMarkup:
        """Staff sponsor management keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Approva", callback_data=f"sponsor_action:approve:{sponsor_id}"),
                InlineKeyboardButton(text="❌ Rifiuta", callback_data=f"sponsor_action:reject:{sponsor_id}")
            ],
            [
                InlineKeyboardButton(text="💬 Rispondi", callback_data=f"reply_to_sponsor:{sponsor_id}")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """Back to menu keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="🔙 Torna al Menù", callback_data="back_to_menu")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

class RecruitmentKeyboard:
    """Keyboards for job applications"""
    
    @staticmethod
    def start_application() -> InlineKeyboardMarkup:
        """Start application keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="📝 Inizia Candidatura", callback_data="start_application")],
            [InlineKeyboardButton(text="❌ Annulla", callback_data="cancel_application")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def role_selection() -> InlineKeyboardMarkup:
        """Role selection keyboard"""
        roles = [
            ("👨‍🍳 Cuoco", "Cuoco"),
            ("🧑‍💼 Cameriere", "Cameriere"),
            ("👔 Manager", "Manager"),
            ("🧹 Addetto Pulizie", "Addetto Pulizie"),
            ("🚚 Delivery", "Delivery")
        ]
        
        keyboard = []
        for role_display, role_value in roles:
            keyboard.append([InlineKeyboardButton(
                text=role_display, 
                callback_data=f"role:{role_value}"
            )])
        
        keyboard.append([InlineKeyboardButton(
            text="❌ Annulla", 
            callback_data="cancel_application"
        )])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def cancel_application() -> InlineKeyboardMarkup:
        """Cancel application keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="❌ Annulla Candidatura", callback_data="cancel_application")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def additional_info() -> InlineKeyboardMarkup:
        """Additional info selection keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="✍️ Scrivi messaggio", callback_data="write_additional")],
            [InlineKeyboardButton(text="📝 Non ho nulla da dire", callback_data="no_additional_info")],
            [InlineKeyboardButton(text="❌ Annulla Candidatura", callback_data="cancel_application")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def staff_application_actions(app_id: str) -> InlineKeyboardMarkup:
        """Staff application management keyboard"""
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Approva", callback_data=f"app_action:approve:{app_id}"),
                InlineKeyboardButton(text="❌ Rifiuta", callback_data=f"app_action:reject:{app_id}")
            ],
            [
                InlineKeyboardButton(text="💬 Rispondi", callback_data=f"reply_to_applicant:{app_id}")
            ]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def user_management_actions(user_id: str, is_banned: bool = False) -> InlineKeyboardMarkup:
        """User management keyboard"""
        if is_banned:
            keyboard = [
                [InlineKeyboardButton(text="✅ Sbanna", callback_data=f"unban_user:{user_id}")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton(text="🚫 Banna", callback_data=f"ban_user:{user_id}")]
            ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def back_to_menu() -> InlineKeyboardMarkup:
        """Back to menu keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="🔙 Torna al Menù", callback_data="back_to_menu")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

class AdminKeyboard:
    """Keyboards for admin functions"""
    
    @staticmethod
    def menu_management(categories: List[str]) -> InlineKeyboardMarkup:
        """Menu management keyboard"""
        keyboard = []
        
        # View categories
        for category in categories:
            keyboard.append([InlineKeyboardButton(
                text=f"📋 Visualizza {category}", 
                callback_data=f"view_category:{category}"
            )])
        
        # Management options
        keyboard.append([
            InlineKeyboardButton(text="➕ Aggiungi Piatto", callback_data="add_new_item"),
            InlineKeyboardButton(text="📂 Gestisci Categorie", callback_data="manage_categories")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def category_selection(categories: List[str]) -> InlineKeyboardMarkup:
        """Category selection for adding items"""
        keyboard = []
        
        for category in categories:
            keyboard.append([InlineKeyboardButton(
                text=category, 
                callback_data=f"add_category:{category}"
            )])
        
        keyboard.append([InlineKeyboardButton(
            text="❌ Annulla", 
            callback_data="cancel_add_item"
        )])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def category_items_management(category: str, items: List[str]) -> InlineKeyboardMarkup:
        """Category items management keyboard"""
        keyboard = []
        
        # Show items with edit and remove options
        for item in items:
            keyboard.append([
                InlineKeyboardButton(
                    text=f"✏️ Modifica {item}", 
                    callback_data=f"edit_item:{category}:{item}"
                ),
                InlineKeyboardButton(
                    text=f"🗑️ Rimuovi {item}", 
                    callback_data=f"remove_item:{category}:{item}"
                )
            ])
        
        # Add new item to this category
        keyboard.append([InlineKeyboardButton(
            text=f"➕ Aggiungi Piatto a {category}", 
            callback_data=f"add_to_category:{category}"
        )])
        
        # Navigation
        keyboard.append([InlineKeyboardButton(
            text="🔙 Gestione Menù", 
            callback_data="back_to_menu_management"
        )])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def cancel_add_item() -> InlineKeyboardMarkup:
        """Cancel add item keyboard"""
        keyboard = [
            [InlineKeyboardButton(text="❌ Annulla", callback_data="cancel_add_item")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def category_management(categories: List[str]) -> InlineKeyboardMarkup:
        """Category management keyboard"""
        keyboard = []
        
        # Remove categories
        for category in categories:
            keyboard.append([InlineKeyboardButton(
                text=f"🗑️ Rimuovi {category}", 
                callback_data=f"remove_category:{category}"
            )])
        
        # Add new category
        keyboard.append([
            InlineKeyboardButton(text="➕ Aggiungi Categoria", callback_data="add_new_category")
        ])
        
        # Back button
        keyboard.append([
            InlineKeyboardButton(text="🔙 Gestione Menù", callback_data="back_to_menu_management")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
