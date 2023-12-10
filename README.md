# [Media Search bot](https://github.com/Mahesh0253/Media-Search-bot)

* Index channel or group files for inline search.
* When you post file on telegram channel or group this bot will save that file in database, so you can search easily in inline mode.
* Supports document, video and audio file formats with caption support.

## Installation

### Watch this video to create bot - https://youtu.be/dsuTn4qV2GA

```markdown

This project is a Telegram bot built with the Pyrogram library that provides various functionalities related to media, translation, and more. The bot is based on the original code from [Mahesh0253/Media-Search-bot](https://github.com/Mahesh0253/Media-Search-bot) and has been extended and modified.

## Features

- **Graph Plotting**: The bot can generate and send graphs for quadratic equations using the Baskara formula.
- **Currency Information**: Retrieve information about the current exchange rate of USD to BRL.
- **Translation**: Translate messages to different languages using the Google Translate API.
- **YouTube URL Handling**: Extract YouTube video URLs from messages.
- **Encryption and Decryption**: Encrypt and decrypt messages using a custom algorithm.
- **Advice Service**: Get random advice using an external advice API.
- **Google News**: Retrieve top headlines from Google News.
- **Channel Information**: Get information about indexed channels/groups.

## Usage

1. Start the bot by running the script.
2. Use various commands to perform actions such as graph plotting, currency information retrieval, translation, and more.

## Installation

1. Install the required libraries: `pyrogram`, `matplotlib`, and `requests`.
   ```bash
   pip install pyrogram matplotlib requests
   ```

2. Configure the bot using the information in the `info.py` file.

3. Run the bot script:
   ```bash
   python your_bot_script.py
   ```

## Commands

- `/start`: Start the bot and access various functionalities.
- `/dolar`: Retrieve information about the USD to BRL exchange rate.
- `/translate`: Translate messages to different languages.
- `/ytDown`: Extract YouTube video URLs from messages.
- `/encrypt` and `/decrypt`: Encrypt and decrypt messages using a custom algorithm.
- `/advice`: Get random advice.
- `/gnews`: Retrieve top headlines from Google News.
- `/bhask`: Solve quadratic equations using the Baskara formula.
- `/channel`: Get basic information about indexed channels/groups (admin only).
- `/total`: Show the total number of saved files in the database (admin only).
- `/logger`: Send the log file (admin only).
- `/delete`: Delete a file from the database (admin only).

## Acknowledgments

- [Mahesh0253](https://github.com/Mahesh0253) for the original code.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
```

Make sure to replace `your_bot_script.py` and `LICENSE.md` with the actual names of your bot script and license file, if applicable. You can also include additional sections or information based on your project's requirements.
