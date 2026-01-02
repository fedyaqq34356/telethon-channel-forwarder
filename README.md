# Telethon Channel Forwarder

Telegram bot for automated message forwarding between channels using Telethon and Aiogram.

## Features

- Multiple Telegram account management
- Source and target channel configuration
- Flexible channel linking system
- Real-time message forwarding with media
- Web preview preservation
- Two-factor authentication support
- Persistent JSON storage
- Comprehensive logging

## Requirements

```
telethon
python-dotenv
aiogram
```

## Installation

```bash
git clone https://github.com/fedyaqq34356/telethon-channel-forwarder.git
cd telethon-channel-forwarder
pip install -r requirements.txt
```

Create `.env` file:

```
BOT_TOKEN=your_bot_token_here
ADMIN_IDS=123456789,987654321
```

## Getting Credentials

### Bot Token

1. Open Telegram and find @BotFather
2. Send `/newbot` command
3. Follow instructions to create bot
4. Copy token to `.env` file

### API Credentials

1. Visit https://my.telegram.org
2. Login with phone number
3. Navigate to API development tools
4. Create new application
5. Copy API ID and API Hash

### Admin IDs

1. Find @userinfobot in Telegram
2. Send `/start` command
3. Copy your user ID
4. Add to `ADMIN_IDS` in `.env`

## Usage

```bash
python main.py
```

Bot starts in polling mode and displays main keyboard.

### Account Management

**Add Account:**

1. Press "Dodaty akkaunt"
2. Enter session name (unique identifier)
3. Provide API ID from my.telegram.org
4. Provide API Hash
5. Enter phone number with country code (+380XXXXXXXXX)
6. Wait for verification code
7. Enter code separated by spaces (6 2 3 7 8)
8. If 2FA enabled, enter password

Example:

```
Session name: my_account
API ID: 12345678
API Hash: abcdef1234567890abcdef1234567890
Phone: +380991234567
Code: 6 2 3 7 8
```

**List Accounts:**

Press "Spysok akkauntiv" to view all added accounts with phone numbers.

**Delete Account:**

1. Press "Vydalyty akkaunt"
2. Enter account number from list
3. Confirm deletion

### Channel Management

**Add Source Channel:**

1. Press "Dodaty dzherelo"
2. Enter channel identifier:
   - Username: @channelname
   - ID: -1001234567890

**Add Target Channel:**

1. Press "Dodaty otrymuvach"
2. Enter channel identifier (username or ID)

**List All Channels:**

Press "Vsi kanaly" to view sources and targets separately.

**Delete Channel:**

1. Press "Vydalyty kanal"
2. Choose channel type (source or target)
3. Enter channel number from list

### Link Management

**Create Link:**

1. Press "Zv'iazaty kanaly"
2. View source channel list
3. Enter source number
4. View target channel list
5. Enter target number

Example:

```
Sources:
1. @news_channel
2. -1001234567890

Enter source: 1

Targets:
1. @my_channel
2. -1009876543210

Enter target: 1

Link created: @news_channel → @my_channel
```

**List Links:**

Press "Spysok zv'iazkiv" to view all active forwarding routes.

**Delete Link:**

1. Press "Vydalyty zv'iazok"
2. Enter link number from list

### Forwarding Control

**Start Forwarding:**

Press "Zapustyty" to begin message forwarding.

Requirements:
- At least one account added
- At least one link created
- Account must be authorized

**Stop Forwarding:**

Press "Zupynyty" to stop all forwarding operations.

## Message Types

The forwarder handles:

- Plain text messages
- Formatted text (bold, italic, code)
- Photos and images
- Videos and animations
- Documents and files
- Audio messages
- Voice messages
- Stickers
- Messages with link previews

Preserved attributes:
- Original formatting entities
- Media quality
- Captions
- Link previews
- Message metadata

## Output Structure

```
telethon-channel-forwarder/
├── sessions/
│   ├── my_account.session
│   └── backup_account.session
├── logs/
│   ├── 2026-01-02.log
│   └── 2026-01-03.log
├── data.json
├── .env
├── main.py
├── config.py
├── storage.py
├── auth.py
├── forwarder.py
├── states.py
├── keyboards.py
├── logger.py
├── handlers/
│   ├── accounts.py
│   ├── channels.py
│   ├── links.py
│   └── forwarding.py
├── requirements.txt
└── README.md
```

## File Contents

**data.json** - Application state

```json
{
  "accounts": {
    "my_account": {
      "api_id": 12345678,
      "api_hash": "hash_string",
      "phone": "+380991234567"
    }
  },
  "source_channels": [
    "@news_channel",
    "-1001234567890"
  ],
  "target_channels": [
    "@my_channel",
    "-1009876543210"
  ],
  "links": [
    {
      "source": "@news_channel",
      "target": "@my_channel"
    }
  ]
}
```

**Session Files** - Telethon authentication

Binary files containing authorization data. Do not edit manually.

**Log Files** - Daily operation logs

```
22:30:15 | INFO | Zapusk bota
22:30:20 | INFO | Dodano akkaunt: my_account
22:31:05 | INFO | Dodano dzherelo: @news_channel
22:31:10 | INFO | Dodano otrymuvach: @my_channel
22:31:15 | INFO | Dodano zv'iazok: @news_channel → @my_channel
22:32:00 | INFO | Zapushcheno peresylannia dlia my_account
22:32:05 | INFO | Pereslano: @news_channel → @my_channel
```

## Project Structure

**main.py** - Application entry point

Initializes bot, dispatcher, routers. Starts polling.

**config.py** - Configuration loader

Loads environment variables. Provides BOT_TOKEN and ADMIN_IDS.

**storage.py** - Data persistence

Manages accounts, channels, links. JSON serialization. File I/O operations.

**auth.py** - Authentication logic

Handles Telegram authorization flow. Code verification. 2FA support. Session management.

**forwarder.py** - Message forwarding

Event handlers. Media type detection. Message sending. Error recovery.

**states.py** - FSM definitions

State groups for multi-step operations. Account, Channel, Link states.

**keyboards.py** - UI elements

Reply keyboards. Button layouts. Cancel options.

**logger.py** - Logging setup

File and console handlers. Daily log rotation. Structured formatting.

**handlers/accounts.py** - Account operations

Add, list, delete accounts. Code verification. Password handling.

**handlers/channels.py** - Channel operations

Add, list, delete channels. Source and target management.

**handlers/links.py** - Link operations

Create, list, delete links. Link validation.

**handlers/forwarding.py** - Forwarding control

Start and stop operations. Client management. Active forwarder tracking.

## Configuration

**Environment Variables:**

```
BOT_TOKEN         Bot authentication token
ADMIN_IDS         Comma-separated admin user IDs
```

**Channel Identifiers:**

Username format: @channelname
ID format: -1001234567890

Bot must be admin in target channels with post permissions.

**Session Storage:**

Sessions stored in `sessions/` directory.
Each account has separate `.session` file.
Files are SQLite databases managed by Telethon.

## Logging

**Log Format:**

```
HH:MM:SS | LEVEL | MESSAGE
```

**Log Levels:**

- INFO - Normal operations, state changes
- ERROR - Failures, exceptions, critical issues

**Log Rotation:**

New file created daily: `logs/YYYY-MM-DD.log`

**Logged Events:**

- Application startup and shutdown
- Account additions and removals
- Channel additions and removals
- Link creations and deletions
- Forwarding start and stop
- Message forwarding success
- Error details with context

## Error Handling

**Authentication Errors:**

- Invalid API credentials - Check API ID and hash
- Phone code expired - Request new code
- 2FA password wrong - Verify password
- Account restricted - Check Telegram restrictions

**Channel Errors:**

- Channel not found - Verify channel exists
- Access denied - Ensure bot is channel admin
- Invalid identifier - Check username or ID format

**Forwarding Errors:**

- No permissions - Add bot as channel admin
- Media too large - Telegram file size limits
- Flood wait - Automatic retry with delay

All errors logged with full context. User receives error notification in chat.

## State Management

**FSM States:**

Account flow:
```
session_name → api_id → api_hash → phone → code → [password] → complete
```

Channel flow:
```
source/target → input → complete
delete_type → delete_choice → complete
```

Link flow:
```
source → target → complete
delete_choice → complete
```

**State Cancellation:**

Press "Skasuvaty" at any step to abort operation and return to main menu.

## API Rate Limits

Telegram API limits:
- Message sending: 30 messages per second per account
- Channel operations: 20 operations per minute

Bot includes automatic delays to prevent rate limiting.

For high-volume forwarding:
- Use multiple accounts
- Distribute links across accounts
- Monitor logs for flood wait errors

## Security Considerations

**Credential Storage:**

- API credentials in `.env` file
- Session files contain auth tokens
- Never commit `.env` or `sessions/` to git
- Use restrictive file permissions (chmod 600)

**Access Control:**

- Only admin IDs can use bot
- Each user has isolated active forwarders
- Session files are user-specific

**Privacy:**

- No data sent to external services
- All processing happens locally
- Logs contain only operation details
- No message content logged

## Troubleshooting

**Bot not responding:**

- Check BOT_TOKEN is valid
- Verify bot is not blocked
- Check internet connection
- Review logs for errors

**Cannot add account:**

- Verify API ID and hash are correct
- Check phone number format includes country code
- Ensure phone can receive SMS
- Try requesting new verification code

**Forwarding not working:**

- Verify account is authorized
- Check bot is admin in target channels
- Ensure links are created correctly
- Review logs for specific errors

**Session expired:**

- Delete account and re-add
- Verify account not logged out on phone
- Check for Telegram security notifications

## Performance

**Operation Times:**

- Account authorization: 5-10 seconds
- Channel resolution: < 1 second
- Link creation: < 1 second
- Message forwarding: < 1 second per message

**Resource Usage:**

- Memory: 50-100 MB per active account
- CPU: Minimal during idle
- Network: Depends on message volume

**Scaling:**

- Supports multiple accounts
- Each account can forward independently
- Recommended: 1-3 accounts per bot instance

## Data Source

All operations use official Telegram API via Telethon library.

Bot framework provided by Aiogram library.

## Privacy

- No user data collected
- No analytics or tracking
- All data stored locally
- No external API calls except Telegram

## Known Limitations

- One account per forwarding session
- Sequential message processing
- No message history forwarding
- No message editing/deletion sync
- Requires bot admin permissions

## Future Enhancements

Potential features:

- Multi-account forwarding
- Message filtering by keywords
- Scheduled forwarding
- Message templates
- Forward statistics
- Web dashboard
- Docker deployment

## Support

**Telegram API:** https://core.telegram.org/api

**Telethon Documentation:** https://docs.telethon.dev

**Aiogram Documentation:** https://docs.aiogram.dev

**Issues:** https://github.com/fedyaqq34356/telethon-channel-forwarder/issues

## License

GNU General Public License v3.0

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/gpl-3.0.html

## Contributing

Contributions welcome. Please ensure:

- Code follows existing architecture
- Functions are single-purpose
- All operations logged
- Errors handled gracefully
- Documentation updated

Submit pull requests to main branch.

## Author
Built with Python, Telethon, and Aiogram.
Repository: https://github.com/fedyaqq34356/telethon-channel-forwarder