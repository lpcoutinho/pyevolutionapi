# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2025-01-09

### Fixed
- **Critical**: Fixed ValidationError when API returns "connecting" status for instances
  - Updated `InstanceStatus` enum to properly include "connecting" status
  - Updated `ConnectionState` enum to properly include "connecting" state
  - Fixed issue where users would get ValidationError with status "connecting"
- **Export**: Added missing `InstanceStatus` enum to models package exports
  - Users can now import `InstanceStatus` from `pyevolutionapi.models`
- **Validation**: Improved QR code field parsing to accept mixed data types
  - Fixed issue where `count` field in QR code responses could be integer or string

### Technical Changes
- Enhanced Pydantic model validation to be more flexible with API response formats
- Added comprehensive tests for "connecting" status validation scenarios
- Improved model exports in `pyevolutionapi.models.__init__.py`

## [0.1.0] - 2025-01-08

### Added
- Initial release of PyEvolution API client
- Complete Evolution API v2.2.2 integration
- Support for WhatsApp instance management
- Message sending capabilities (text, media, audio, etc.)
- Group management features
- Chat operations and contact management
- Webhook configuration
- Profile management
- Comprehensive async/await support
- Type-safe models with Pydantic validation
- Retry mechanism with exponential backoff
- Rate limiting support
- Complete test suite with unit and integration tests

### Features
- **Instance Management**: Create, connect, restart, delete WhatsApp instances
- **Messaging**: Send text, media, audio, location, contact, sticker, poll, and status messages
- **Groups**: Create and manage WhatsApp groups, handle participants
- **Chats**: Search messages, mark as read, manage contacts
- **Webhooks**: Configure webhooks, WebSocket, RabbitMQ, and SQS integrations
- **Authentication**: Global API key and per-instance token support
