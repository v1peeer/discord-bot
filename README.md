# discord bot
simple discord bot for tickets, economy etc.

# features
- member counting channels
- auto-creation of welcome and rules channels
- economy function (balance/work/send/daily/casino)
- giveaway function
- ticket system

# how to use
1. install python3
2. install requirements: `pip install -r requirements.txt`
3. edit the config
4. start the bot: `python3 bot.py`

# example config
```json
{
    "github_token": "your_github_token_here",
    "repo_name": "your_repo_name_here",
    "github_username": "your_github_username_here",
    "prefix": "+",
    "token": "your_bot_token_here"
}
```
- github token, username and repo name are required for the ticket transcripts to work
