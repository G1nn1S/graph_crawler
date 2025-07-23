import aiohttp
import asyncio

# === Config ===
USERNAME = "PLACE YOU USERNAME HERE"
PASSWORD = "PLACE YOUR PASSWORD HERE"
CLIENT_ID = "YOUR CLIENT ID"
TENANT_ID = "YOUR TENANT ID"
TOKEN_URL = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
OUTPUT_FILE = "allowed-user-agents.txt"

# === Load User-Agents from File ===
def load_user_agents(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

# === Save allowed User-Agent ===
def save_allowed_user_agent(ua):
    with open(OUTPUT_FILE, "a") as f:
        f.write(ua + "\n")

# === Async Function to Test UA ===
async def test_user_agent(session, ua):
    headers = {
        "User-Agent": ua,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "client_id": CLIENT_ID,
        "scope": "openid profile",
        "grant_type": "password",
        "username": USERNAME,
        "password": PASSWORD
    }

    async with session.post(TOKEN_URL, headers=headers, data=data) as resp:
        status = resp.status
        try:
            json_resp = await resp.json()
        except Exception:
            json_resp = {"error": "Non-JSON response"}

        error_message = json_resp.get("error_description", "")
        is_blocked = "Access has been blocked by Conditional Access policies." in error_message

        print(f"\n[UA] {ua}\n[Status] {status}\n[Response] {json_resp}")

        if not is_blocked:
            save_allowed_user_agent(ua)

# === Main ===
async def main():
    user_agents = load_user_agents("use.txt")
    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [test_user_agent(session, ua) for ua in user_agents]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
