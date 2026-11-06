# Femdom Cage — Discord Bot

> **⚠️ Content notice: 18+ only.**
> This bot provides adult, kink-oriented (BDSM / femdom) roleplay tools for consenting adults in age-verified Discord communities. Most commands are registered as **NSFW** and only work in age-restricted channels. Please don't deploy it in servers that include minors or people who haven't opted in.

A [nextcord](https://github.com/nextcord/nextcord) bot backed by MongoDB that lets dommes and subs play out consensual dynamics on Discord — gags, prisons, tasks, ownership, blindfolds — alongside everyday community features like an economy, levels, auctions, and SFW roleplay actions.

---
## Mental Health issues

During my time making Empress I was going through a lot, and it discouraged my effort on the project, I'm sorry in advance and I would prefer if people didn't leave hateful comments on my work as my workflow has since improved. Empress was my first shot at a public bot and I am so happy that I was able to share this with you all. I made an effort to fix everything but I just had no motivation to fix it so instead I left it. Empress did have a donation page that didn't actually work and I later disabled. When Empress was made I was a solo dev making things for the love of it and I was new into my journey of public bots. I loved it so much and the people who liked my work, however when I started doing timers I ran into problems. Empress will always be in my heart and I hope someone can pull request and improve on it. Thank you for taking time to read this.

Stay kinky and I love you all
~Lina

## 🤍 Consent & safety first

Play only works when everyone involved wants to be there. The bot is built with that in mind, and anyone running it should keep it that way:

- **`/safeword` is always available, to everyone.** It immediately lifts every restriction on the caller — gags, prison locks, badwords, tie-ups, blindfold channels — and posts a clear message telling others to stop. It should never be disabled, gated behind a paywall, or ignored.
- **Ownership requires consent.** `/own` sends the sub an accept/decline prompt; nothing happens unless they accept, and ignoring it counts as declining.
- **Moderators have a way out, too.** `force_ungag`, `force_untie`, `force_unlock`, `force_badword`, and `force_remove_blindfold` let staff clear anything stuck or unwanted.
- **Restrictions are time-bound.** Gags, prisons, and tasks run on timers and expire on their own.
- **Server owners decide what's on.** Modules (including the adult content search) can be enabled or disabled per server with `/settings`.

If you're running this bot in a community, consider pinning a short guide to your safeword and consent norms where members will see it.

---

## ✨ Features

| Area | Commands | What it does |
|---|---|---|
| **Dynamics** (`cogs/bdsm.py`) | `/own`, `/disown`, `/create`, `/edit`, `/profile` | Consent-based ownership and personal kink profiles |
| | `/gag`, `/gagged`, `/say` | Webhook-based gags that rewrite a sub's messages; speak as a sub |
| | `/prison lock` · `unlock`, `/locked` | Lock a sub into a channel until they write their lines |
| | `/task give` · `list` · `completed` | Timed tasks with optional punishments |
| | `/tie bind` · `untie` · `list` | Restrict a sub to a single channel |
| | `/badword add` · `remove` · `clear` · `list` | Forbidden words for a sub |
| | `/blindfold add/remove member · spectator` | Private punishment channels with optional spectators |
| | `/status` | See everything currently applied to a user |
| **Safety** (`cogs/admin.py`, `cogs/moderation.py`) | `/safeword`, `/restore`, `force_*` | Remove restrictions instantly |
| **Economy** (`cogs/economy.py`) | `/balance`, `/daily`, `/give`, `/bet`, `/shop`, `/buy` | Server currency and buyable roles |
| **Auctions** (`cogs/auction.py`) | `/auction sell` · `bid` | Playful, opt-in auctions using server currency |
| **Levels** (`cogs/levels.py`) | `/level`, `/level_ reward`, `/delete reward` | XP and level-up role rewards |
| **Roleplay** (`cogs/roleplay.py`) | `/roleplay hug · kiss · pet · boop …`, `/nsfw_rp …` | SFW and NSFW action GIFs |
| **Admin** (`cogs/admin.py`) | `/config bdsm`, `/customize`, `/permissions`, `/currency`, `/update_buyable_role` | Role mapping, embed colors/images, prison permissions |
| **Moderation** (`cogs/moderation.py`) | `/set max_subs · level · channel`, `/reset`, `/delete_from_db` | Server-level limits and cleanup |
| **Server settings** (`cogs/settings.py`) | `/settings enable` · `disable` | Turn modules on or off |
| **Misc** | `/help`, `/commands`, `/feedback`, `/donate`, `/activate`, `/invite` | Help, bug reports, Patreon perks |

Background loops in `main.py` handle gag/prison/task expiry, snipe cleanup, and the bot's presence status.

---

## 📁 Project layout

```
.
├── main.py            # Bot entry point: loads cogs, starts timer loops
├── cogs/              # One file per feature module (auto-loaded)
├── CONF/
│   ├── owners.json    # Bot owner user IDs
│   ├── webhooks.json  # Webhook URLs for whitelist/blacklist logs
│   └── lines.json     # Line sets used by /prison
├── static/            # Images and the font used for generated cards
└── scripts/m.py       # Small one-off dev script
```

---

## 🚀 Getting started

### Requirements

- Python 3.10+ (3.11 / 3.13 also used)
- A MongoDB instance (the bot uses the `femdom_cage` database)
- A Discord application with the **Message Content** intent enabled

### Install

```bash
pip install nextcord pymongo motor python-dotenv aiohttp aiofiles requests pillow humanfriendly pytz uwuipy patreon pyaes pbkdf2
```

### Configure

Create a `.env` file with the following keys:

```env
TOKEN=            # Discord bot token
MONGODB=          # MongoDB connection string
OWNER=            # Your Discord user ID
TEST_TOKEN=       # Optional: token for a test bot
PATREON_TOKEN=    # Optional: Patreon integration for /activate
PATREON_SECRET=
PATREON_ID=
PATREON_CALLBACK=
ENCRYPT_PASS=
ELASTIC_URL=      # Optional
ELASTIC_TOKEN=
```

> **Note:** `main.py` currently loads its env from the hard-coded path `/root/as.env`, while the cogs call `load_dotenv()` from the working directory. Point both at the same file (or change `main.py` to `load_dotenv()`) before running locally.

Then edit `CONF/owners.json` with your user ID and `CONF/webhooks.json` with your own logging webhooks.

### Run

```bash
python main.py
```

Once it's online, set things up in your server:

1. `/config bdsm` — map your Domme / Switch / Sub / Punishment roles.
2. `/settings enable` — choose which modules your community wants.
3. `/customize` — optionally set your embed color and images.
4. Mark the channels you want to use for play as **age-restricted** in Discord.

---

## 🔐 Keeping secrets safe

This folder contains `.env` and `scripts/.env` with live credentials. Before sharing or putting it under version control:

- Add a `.gitignore` covering `.env`, `scripts/.env`, `__pycache__/`, and `*.save`.
- If these files have ever been shared or committed, **rotate the Discord token, MongoDB password, and Patreon secrets.**
- `CONF/webhooks.json` contains webhook URLs, which anyone can post to — treat them as secrets too.

---

## 🐞 Known issues

Small things noticed while writing this README — worth fixing when you have a moment:

- **`/safeword` blindfold cleanup** (`cogs/admin.py`, around line 73) uses an undefined `user` instead of `ctx.user`, so the safeword can error partway through for someone who is blindfolded. Since this is the safety command, it's the most important one to fix.
- `main.py` `snipe_loop` prints an undefined `_id` (line 65), and `timers_loop` calls `safe_fetch_channel`, which is never defined, so gag punishments from tasks won't apply.
- `cogs/tord.py` is an empty stub, and `cogs/listeners.py.save` is a leftover backup.

---

## 💬 Feedback

Found a bug or have an idea? Use `/feedback` in Discord. Thanks for helping keep the space fun, safe, and consensual. 🖤
