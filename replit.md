# Overview

This project is an advanced Python-based Discord bot with integrated API server capabilities, designed to provide high-quality trading insights. It focuses on stock chart generation, stock analysis, image analysis, and AI-powered report generation. The system ensures user request limits and automated channel cleanup, and supports enhanced data storage for various TradingView signal types. It features a comprehensive database-driven report generation system that queries stored historical data and offers robust report channel monitoring for AI analysis. **Recent migration (Aug 27, 2025) moved Order Block configuration from database to reliable file-based system using `orderblock_routes.conf` with CLI management tools.** **Order Block Chart Integration completed (Aug 27, 2025)** - All Order Block webhook signals now automatically include corresponding OB charts with professional trading indicators. The system aims for fully autonomous operation with a comprehensive Docker deployment solution for VPS environments.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Architectural Decisions

- **Bot Architecture**: Advanced design using `discord.py` commands.Bot framework with an integrated API server for TradingView webhook integration, operating in a hybrid mode.
- **Configuration Management**: Hybrid system using environment variables for secrets and file-based configuration for Order Block routing (`orderblock_routes.conf`).
- **Message Processing Pipeline**: Listens for `@mention` events and stock commands, processing CT (chart), OB (alternative chart layout), RP (report), image analysis, and prediction requests.
- **Error Handling Strategy**: Multi-layered with retry mechanisms, comprehensive logging, and graceful degradation.
- **UI/UX Decisions**: Responses are delivered via private messages with in-channel notifications, using clear error messages and gold-colored embeds for admin commands.
- **Independent Parsing Module System**: Features an independent parsing engine for real-time, configurable field parsing with advanced condition types and variable substitution.
- **AI Template Integration Engine**: Integrates parsed results into AI prompt templates, supporting multi-format output and dynamic variable replacement.
- **Order Block Configuration System (Aug 27, 2025)**: File-based configuration approach using `orderblock_routes.conf` for ticker-to-channel routing, managed by `OrderBlockConfigManager` and CLI tools, ensuring reliability and eliminating web interface caching issues.

## Technical Implementations & Feature Specifications

- **Discord Bot Functionality**: Monitors specified channels, handles various command formats, and differentiates channel behavior for AI report processing.
- **Stock Chart Generation & Analysis**: Generates stock charts using a Layout Chart Storage API with support for multiple chart layouts (CT command uses layout Gc320R2h, OB command uses layout IoT1qwuk), integrates AI for image analysis, provides stock trend prediction, and implements intelligent stock exchange detection. **OB Command fully implemented and tested (Aug 26, 2025)** - Alternative chart layout for Order Block analysis with specialized TradingView indicators. **Order Block Data Integration completed (Aug 26, 2025)** - Full `obData` field support throughout the system for comprehensive Order Block analysis. **Enhanced Trading Signal UI completed (Aug 26, 2025)** - OB information displays below supply/demand fields in Discord trading signals with interactive Order Block button for specialized OB chart generation.
- **TradingView Webhook Integration**: Receives, parses, and stores enhanced TradingView webhook data, supports 23+ technical indicator parsing (including `obData` for Order Block analysis), multi-timeframe trend analysis, and a dual AI report generation system:
  - **Trading Analysis Reports**: Interactive button-triggered reports using current webhook transaction data for immediate trade analysis.
  - **Trend Analysis Reports**: Channel command-triggered reports using database-stored larger timeframe data (1h, 4h) for comprehensive trend analysis.
  - Hourly data from larger timeframes is stored for trend analysis command usage.
  Features an enhanced 5-field rating system with automated direction determination and a 6-level trend strength classification. Includes intelligent report caching with automatic invalidation and a multi-AI failover system.
- **User & Admin Management**: Implements daily request limits, an admin exemption system, and a VIP management system.
- **Channel Management**: Automatic daily channel cleanup for monitored channels.
- **Deployment & Logging**: Provides a comprehensive Docker deployment solution with automated updates and self-recovery. Features a real-time JSON logging system.
- **Personal Webhook System**: Allows each Discord user to generate unique webhook URLs for direct TradingView alerts via DM. Includes API endpoints and Discord commands for webhook management, robust security with secret tokens, and automatic parsing and forwarding of alerts. Features interactive buttons for chart retrieval, AI analysis, and automated trade execution via TradersPost. Enhanced with supply/demand zone fields (nearest_supply, nearest_demand, reference_price), Order Block data (`obData`) for institutional level analysis, and accurate US Eastern time display for trading alerts.
- **Order Block Dedicated Webhook System (Aug 27, 2025)**: Specialized webhook endpoint `/webhook/orderblock` for TradingView Order Block signals with automatic ticker-to-channel routing. Supports 4 event types (New Bullish/Bearish OB Formed, Price Entering Bullish/Bearish OB) with color-coded Discord embeds. **Fully migrated to file-based configuration system** using `orderblock_routes.conf` for reliable ticker-channel mappings, replacing the problematic database approach. Includes comprehensive CLI management tools (`manage_routes.py`) and validation system. **Chart Integration completed (Aug 27, 2025)** - All OB signals now automatically include corresponding chart images using Chart-img API with Order Block layout, displaying institutional-level analysis with timeframe-specific indicators.
- **Visual Configuration Interface**: Provides web-based interfaces for configuration management, signal mapping, AI template editing, and independent parsing module configuration with real-time testing.
- **Signal Translation Engine**: Automatic translation of TradingView webhook signals to Chinese descriptions with configurable mappings and dynamic loading.
- **AI Prompt Template System**: Command-specific templates for charts, reports, image analysis, and forecasting with variable substitution and multi-language support.

## Design Patterns

- **Dependency Injection**: Configuration and webhook handler instances.
- **Single Responsibility Principle**: Modules focused on specific tasks.
- **Observer Pattern**: Bot observes Discord message events.

# External Dependencies

## Core Libraries
- **discord.py**: Discord API wrapper.
- **aiohttp**: Asynchronous HTTP client.
- **python-dotenv**: Environment variable management.
- **SQLAlchemy**: ORM for database interactions.
- **psycopg2**: PostgreSQL adapter.

## Discord Integration
- **Discord Bot Token**: Authentication.
- **Discord Gateway**: Real-time connection.

## APIs & Services
- **Layout Chart Storage API (TradingView)**: For custom stock charts.
- **Chart-img API**: For testing symbol availability.
- **AI Trend Band Signal Recognition Service**: For chart analysis.
- **Stock Trend Prediction Service**: For market predictions.
- **Google Gemini 2.5 Pro/Flash (Dual Account)**: Primary AI models with automatic failover between two Google accounts.
- **Claude Sonnet 4 Direct**: Backup AI model for report generation.
- **Clearbit Logo API**: Primary source for company logos.
- **UI-Avatars API**: Fallback logo service.
- **TradersPost**: For automated trade execution.

## Database
- **PostgreSQL**: For user tracking, request limits, VIP/exemption management, enhanced TradingView data storage, and personal webhook management.