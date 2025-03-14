Version 0.3
-----------

Date
  2025-03-14

Added
 * Tests and linters
 * Update `pyupgw` to version 0.13
 * Use EUID as unique_id for devices that don't have serial number available

Version 0.2
-----------

Date
  2024-03-01

Changed
 * Update `pyupgw` to version 0.12
 * Rethrow exceptions as `HomeAssistantError` when a client operation fails
 * Do not try to add climate entities if serial number cannot be retrieved
 * Improve documentation

Version 0.1
-----------

Initial release
