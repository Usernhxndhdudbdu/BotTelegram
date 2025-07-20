# replit.md

## Overview

This is a complete Telegram roleplay bot for "The Krusty Krab • Neotecno" restaurant simulation. The bot implements a full restaurant management system with interactive menu browsing, order processing, staff management through dedicated groups with forum topics, sponsor requests, and a recruitment system. The entire system is designed for roleplay purposes and uses virtual credits rather than real money.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Python-based Telegram bot using aiogram v3
- **Architecture Pattern**: Modular handler-based system with router registration
- **State Management**: FSM (Finite State Machine) for multi-step user interactions using aiogram's built-in state system
- **Storage**: Memory storage for session data, JSON files for persistent data
- **Bot Structure**: Single bot instance with multiple routers for different functionalities

### Data Storage Solutions
- **Database**: JSON file-based storage system (no traditional database required)
- **Configuration Files**: 
  - `data/config.json` - Bot configuration, staff group info, orders, sponsors, applications, user carts, user states
  - `data/menu.json` - Restaurant menu items organized by categories with prices and descriptions
- **Data Models**: Dataclass-based models for Order, MenuItem, MenuCategory, OrderItem with serialization support
- **Data Persistence**: All data automatically saved to JSON files with proper error handling

### Authentication and Authorization
- **Admin System**: Environment variable-based admin user IDs (`ADMIN_IDS`)
- **Staff Group**: Private Telegram supergroup with forum topics enabled for staff management
- **Access Control**: Decorator-based admin checks for sensitive operations
- **Group Management**: Bot requires manual staff group setup with specific permissions

## Key Components

### 1. Enhanced Menu System (`handlers/menu.py`, `models/menu.py`)
- **Dynamic Categories**: Organized menu structure with admin-configurable categories
- **Interactive Navigation**: Inline keyboard navigation with "return to home" buttons throughout
- **Item Details**: Each menu item includes name, price, description, and availability status
- **Enhanced Admin Management**: 
  - Commands for adding/modifying menu items through bot interface
  - New "Add Category" button in admin panel for dynamic category creation
- **Cart Integration**: Shopping cart functionality with real-time item count display
- **Help System**: Comprehensive help section accessible from home menu

### 2. Enhanced Order Processing (`handlers/orders.py`, `models/order.py`)
- **Multi-Step Process**: Menu browsing → item selection → cart review → payment photo → order confirmation
- **Photo Verification**: Mandatory payment photo (roleplay) required before order confirmation
- **Sequential Order IDs**: Orders numbered sequentially (1, 2, 3...) instead of timestamps
- **Staff Integration**: Orders and payment photos sent as separate messages to staff topic
- **Order States**: Comprehensive order lifecycle (pending, preparing, ready, completed, rejected)
- **Cart Management**: Persistent shopping cart with add/remove/modify capabilities

### 3. Enhanced Staff Group Integration (`handlers/admin.py`)
- **Multi-Level Admin System**: Environment admins + database-stored admins via `/add_admin` command
- **Forum Topics**: Three dedicated topics for different operations:
  - 📦 Orders - All customer orders with management options + payment photos
  - 📜 Sponsor Requests - Sponsor applications with proposals + payment photos
  - 📝 Applications - Job applications with approval/rejection workflow
- **Enhanced Admin Commands**: 
  - `/setup_staff`, `/create_topics` for initial configuration
  - `/add_admin` to add new admins by Telegram ID
  - `/add_category` to add new menu categories
  - `/setup_sponsor_channel` to configure auto-publishing channel
- **Organized Messaging**: Text and photos sent as separate messages for better organization

### 4. Recruitment System (`handlers/recruitment.py`)
- **Multi-Step FSM Process**: Name input → Age input → Role selection using state machine
- **Available Positions**: Cook, waiter, manager, cleaner, delivery driver
- **Application Workflow**: User submits → Staff reviews in dedicated topic → Response sent to user
- **Data Collection**: Stores roleplay character information for staff evaluation

### 5. Enhanced Sponsor System (`handlers/sponsor.py`)
- **Multi-Step Process**: Users must first send/forward a message with their proposal, then provide payment photo
- **Photo Verification**: Mandatory payment photo (roleplay) required before request submission
- **Staff Integration**: Requests and photos sent as separate messages to staff topic for better organization
- **Auto-Publishing**: Approved sponsors automatically published to configured sponsor channel
- **Channel Setup**: Admin command `/setup_sponsor_channel` to configure publication channel

## Data Flow

### Order Flow
1. User browses menu via inline keyboards
2. Items added to persistent shopping cart
3. Checkout process shows order summary
4. Order confirmation creates database entry
5. Order forwarded to staff group topic with management buttons
6. Staff updates order status (preparing/ready/completed)
7. Status updates sent to customer automatically

### Application Flow
1. User starts recruitment process with `/curriculum`
2. FSM guides through multi-step form (name, age, role)
3. Complete application saved to database
4. Application appears in staff topic with approve/reject buttons
5. Staff decision triggers response message to applicant

### Admin Management Flow
1. Admin configures staff group using `/setup_staff` in target group
2. Topics created with `/create_topics` command
3. Menu modifications available through admin-only commands
4. All staff actions logged and responses automated

## External Dependencies

### Required Python Packages
- **aiogram v3**: Modern Telegram Bot API framework
- **asyncio**: Asynchronous programming support
- **json**: Data serialization for persistent storage
- **datetime**: Timestamp management for orders and applications
- **logging**: Comprehensive logging system
- **os**: Environment variable management

### Telegram API Requirements
- **Bot Token**: Required in `BOT_TOKEN` environment variable
- **Admin IDs**: Comma-separated admin user IDs in `ADMIN_IDS` environment variable
- **Group Permissions**: Bot needs admin rights in staff group with topic management permissions

## Deployment Strategy

### Environment Setup
- **Python 3.8+**: Required for aiogram v3 compatibility
- **Environment Variables**: `BOT_TOKEN` and `ADMIN_IDS` must be configured
- **Data Directory**: `data/` folder automatically created for JSON storage
- **File Permissions**: Write access needed for configuration file updates

### Manual Configuration Steps
1. Create Telegram bot via BotFather
2. Create private supergroup for staff
3. Add bot as admin with all permissions
4. Enable Topics in group settings
5. Run bot and use admin commands to link group
6. Configure menu items through admin interface

### Operational Considerations
- **File-based Storage**: JSON files provide simple deployment without database setup
- **Memory Storage**: Bot state resets on restart (acceptable for roleplay bot)
- **Error Handling**: Comprehensive try-catch blocks for Telegram API failures
- **Logging**: Detailed logging for debugging and monitoring
- **Scalability**: Suitable for small to medium roleplay communities