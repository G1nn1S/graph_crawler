import asyncio
import aiohttp
import os
import json
import re

BASE_URL = "https://graph.microsoft.com/v1.0"
OUTPUT_DIR = "graph_crawler_outputs"

RESOURCE_TO_ENDPOINTS = {
    'user': [
        "/users/{id}/manager",
        "/users/{id}/memberOf",
        "/users/{id}/transitiveMemberOf",
        "/users/{id}/ownedObjects",
        "/users/{id}/createdObjects",
        "/users/{id}/calendar",
        "/users/{id}/events",
        "/users/{id}/messages",
        "/users/{id}/contacts",
        "/users/{id}/joinedTeams",
        "/users/{id}/ownedDevices",
        "/users/{id}/registeredDevices",
        "/users/{id}/authentication",
        "/users/{id}/mailFolders",
        "/users/{id}/people",
        "/users/{id}/planner",
        "/users/{id}/calendarView",
        "/users/{id}/inferenceClassification",
        "/users/{id}/settings",
        "/users/{id}/drive",
        "/users/{id}/extensions",
        "/users/{id}/calendarGroups",
        "/users/{id}/outlook",
    ],
    'group': [
        "/groups/{id}/members",
        "/groups/{id}/owners",
        "/groups/{id}/calendar",
        "/groups/{id}/events",
        "/groups/{id}/transitiveMembers",
        "/groups/{id}/team",
        "/groups/{id}/settings",
        "/groups/{id}/conversations",
        "/groups/{id}/threads",
        "/groups/{id}/photos",
        "/groups/{id}/calendarView",
        "/groups/{id}/drive",
        "/groups/{id}/extensions",
        "/groups/{id}/sites",
    ],
    'application': [
        "/applications/{id}/owners",
        "/applications/{id}/tokenIssuancePolicies",
        "/applications/{id}/tokenLifetimePolicies",
        "/applications/{id}/appRoleAssignedTo",
        "/applications/{id}/appRoleAssignments",
        "/applications/{id}/synchronization",
        "/applications/{id}/addKey",
        "/applications/{id}/addPassword",
        "/applications/{id}/removeKey",
        "/applications/{id}/removePassword",
    ],
    'servicePrincipal': [
        "/servicePrincipals/{id}/owners",
        "/servicePrincipals/{id}/appRoleAssignedTo",
        "/servicePrincipals/{id}/appRoleAssignments",
        "/servicePrincipals/{id}/oauth2PermissionGrants",
        "/servicePrincipals/{id}/claimsMappingPolicies",
        "/servicePrincipals/{id}/tokenIssuancePolicies",
        "/servicePrincipals/{id}/tokenLifetimePolicies",
        "/servicePrincipals/{id}/federatedIdentityCredentials",
        "/servicePrincipals/{id}/transitiveMemberOf",
        "/servicePrincipals/{id}/memberOf",
        "/servicePrincipals/{id}/synchronization",
        "/servicePrincipals/{id}/addKey",
        "/servicePrincipals/{id}/addPassword",
        "/servicePrincipals/{id}/removeKey",
        "/servicePrincipals/{id}/removePassword",
    ],
    'device': [
        "/devices/{id}/registeredOwners",
        "/devices/{id}/registeredUsers",
        "/devices/{id}/transitiveMemberOf",
        "/devices/{id}/extensions",
        "/devices/{id}/commands",
        "/devices/{id}/deviceConfigurationStates",
    ],
    'team': [
        "/teams/{id}/channels",
        "/teams/{id}/members",
        "/teams/{id}/tags",
        "/teams/{id}/tags/{tagId}/members",
        "/teams/{id}/installedApps",
        "/teams/{id}/schedule",
        "/teams/{id}/primaryChannel",
    ],
    'directoryRole': [
        "/directoryRoles/{id}/members",
        "/directoryRoles/{id}/owners",
    ],
    'organization': [
        "/organization/{id}/branding",
        "/organization/{id}/settings",
    ],
    'securityAlert': [
        "/security/alerts/{id}/comments",
        "/security/alerts/{id}/feedback",
        "/security/alerts/{id}/redirect",
        "/security/alerts/{id}/alerts",
    ],
    'report': [
        "/reports/getTeamsUserActivityUserDetail(period='{period}')",
        "/reports/getOffice365ActiveUserDetail(period='{period}')",
        "/reports/getEmailActivityUserDetail(period='{period}')",
        "/reports/getSharePointSiteUsageDetail(period='{period}')",
    ],
    'policy': [
        "/policies/authorizationPolicy",
        "/policies/claimsMappingPolicies",
        "/policies/conditionalAccessPolicies",
        "/policies/tokenIssuancePolicies",
        "/policies/tokenLifetimePolicies",
        "/policies/activityBasedTimeoutPolicies",
        "/policies/appManagementPolicies",
    ],
}

BASE_ENDPOINTS = [
    "/users",
    "/groups",
    "/applications",
    "/servicePrincipals",
    "/me",
    "/devices",
    "/organization",
    "/reports",
    "/security/alerts",
    "/directoryRoles",
    "/teams",
    "/policies/authorizationPolicy",
    "/policies/claimsMappingPolicies",
    "/policies/conditionalAccessPolicies",
    "/policies/tokenIssuancePolicies",
    "/policies/tokenLifetimePolicies",
    "/policies/activityBasedTimeoutPolicies",
    "/policies/appManagementPolicies",
    "/identity/conditionalAccess/policies",
    "/identity/b2xUserFlows",
    "/identity/b2cUserFlows",
    "/identityGovernance/entitlementManagement",
    "/identityGovernance/accessReviews",
    "/identityGovernance/lifecycleWorkflows",
    "/identityGovernance/termsOfUse",
    "/me/joinedTeams",
    "/me/mailFolders",
    "/me/onenote",
    "/me/drive",
]

GUID_REGEX = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}")

def sanitize_filename(s: str) -> str:
    return s.replace("/", "_").replace("{", "").replace("}", "").strip()

def find_ids_in_json(data):
    found_ids = set()
    def recurse(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() == 'id' and isinstance(v, str) and GUID_REGEX.fullmatch(v):
                    found_ids.add(v)
                else:
                    recurse(v)
        elif isinstance(obj, list):
            for item in obj:
                recurse(item)
    recurse(data)
    return found_ids

async def fetch(session, url, headers):
    try:
        async with session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                print(f"[-] HTTP {resp.status} for {url}")
                return None
    except Exception as e:
        print(f"[!] Exception fetching {url}: {e}")
        return None

async def save_response(resource_type, resource_id, data):
    if resource_id:
        folder = os.path.join(OUTPUT_DIR, resource_type, resource_id)
    else:
        folder = os.path.join(OUTPUT_DIR, resource_type)
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, "response.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    if resource_id:
        print(f"[+] Saved {resource_type}/{resource_id}/response.json")
    else:
        print(f"[+] Saved {resource_type}/response.json")

def get_resource_type_from_endpoint(endpoint):
    parts = endpoint.strip("/").split("/")
    if not parts:
        return None
    first = parts[0].lower()
    if first.endswith('s'):
        return first[:-1]
    return first

def generate_child_endpoints(resource_id, resource_type):
    patterns = RESOURCE_TO_ENDPOINTS.get(resource_type, [])
    return [p.replace("{id}", resource_id) for p in patterns]

async def crawl_graph(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    visited = set()
    to_visit = set(BASE_ENDPOINTS)

    async with aiohttp.ClientSession() as session:
        while to_visit:
            batch = list(to_visit)
            to_visit.clear()
            tasks = []

            for ep in batch:
                if ep in visited:
                    continue
                visited.add(ep)
                url = BASE_URL + ep
                print(f"[*] Fetching {url}")
                tasks.append(fetch(session, url, headers))

            results = await asyncio.gather(*tasks)

            for i, data in enumerate(results):
                if data is None:
                    continue
                endpoint = batch[i]
                rtype = get_resource_type_from_endpoint(endpoint)
                if not rtype:
                    continue

                if '{id}' in endpoint:
                    parts = endpoint.strip("/").split("/")
                    try:
                        id_index = parts.index(rtype + 's') + 1
                        resource_id = parts[id_index]
                    except (ValueError, IndexError):
                        resource_id = None
                else:
                    resource_id = None

                await save_response(rtype, resource_id, data)

                ids_found = find_ids_in_json(data)
                if not ids_found:
                    continue

                for id_ in ids_found:
                    child_eps = generate_child_endpoints(id_, rtype)
                    for c_ep in child_eps:
                        if c_ep not in visited:
                            to_visit.add(c_ep)

    print("[*] Crawl finished.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python graph_crawler.py <ACCESS_TOKEN>")
        sys.exit(1)
    token = sys.argv[1]
    asyncio.run(crawl_graph(token))
