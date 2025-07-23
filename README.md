# graph_crawler

Microsoft Graph Crawler

---

## Problem

During my training for [CloudBreach Breaching Azure course](https://cloudbreach.io/breachingazure/) course, I noticed that although I could connect to portal.azure.com, access was blocked due to Conditional Access Policies so I had to find a way to go around this and connect. I won’t reveal much to avoid spoiling the solution, but from the initial flag you’ll understand why this tool is useful and designed the way it is. Since I was bored of manually enumerating all the endpoints, I decided to build a tool to automate the process—making enumeration easier and saving time.

---

## Overview

`graph_crawler` is an asynchronous Python program designed to recursively enumerate Microsoft Graph API endpoints. Given a valid Microsoft Graph access token, it systematically queries a wide range of known endpoints — including users, groups, applications, service principals, devices, teams, policies, reports, and more — and saves all retrieved data as JSON files organized by resource type.

This tool is intended for enterprise-level discovery and inventory of Microsoft Graph resources, helping admins and security professionals gain deep insight into their Azure AD and Microsoft 365 environments.

---

## Features

- **Recursive crawling:** Automatically explores resource sub-endpoints (e.g., members, owners, calendar, events).
- **Wide endpoint coverage:** Supports hundreds of Microsoft Graph API endpoints across many resource types.
- **Organized storage:** Saves responses neatly into folders by resource type and ID to avoid clutter.
- **Async and efficient:** Uses `asyncio` and `aiohttp` for fast concurrent requests.
- **Extensible:** Easily add more endpoints or customize crawling behavior.

---

## Requirements

- Python 3.8+
- `aiohttp` library (`pip install aiohttp`)

---

## Usage

1. Obtain an Azure AD access token with appropriate Microsoft Graph permissions.
2. Run the crawler with your access token.

```bash

This set up came becase I was initially testing each endpoint manual so I left it like this. You can just paste you token without this if you want.
export GRAPH_TOKEN='<YOUR_ACCESS_TOKEN>'

python graph_crawler.py $GRAPH_TOKEN


⚠️ Disclaimer
This tool is developed strictly for educational, ethical hacking, and authorized security testing purposes. You must obtain proper permission before using it on any JIRA instance that you do not own or have explicit authorization to assess.

Unauthorized use of this tool against systems you do not own is illegal and unethical. The authors take no responsibility for any misuse or damage caused by this tool.

Use responsibly — always hack with permission. 🛡️

License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
