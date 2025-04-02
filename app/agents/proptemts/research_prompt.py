ROOTDATA_SEARCH_TEMPLATE = """
Please search for information about {query} using the following API endpoint:
selectedProjectId:{selectedProjectId}

curl -X POST 
-H "43qiBs947TKm0UNDbZ0gQz5ZTHaPpp8Y" 
-H "language: en" 
-H "Content-Type: application/json" 
-d '{{"query": "{query}" }}'
https://api.rootdata.com/open/ser_inv

Ensure the following request parameters are valid:
- query: A string representing the topic, e.g., project/institution names, tokens, or related items.
- depth: An integer indicating the depth of the search, e.g., 1, 2, 3.
- mode: A string specifying the mode of search, e.g., "fast", "deep".
- selectedProjectId (optional): If provided, use the following API call to fetch detailed project information:
  curl -X POST 
  -H "43qiBs947TKm0UNDbZ0gQz5ZTHaPpp8Y" 
  -H "language: en" 
  -H "Content-Type: application/json" 
  -d '{{"project_id": {selectedProjectId}, "include_team": true, "include_investors": true }}'
  https://api.rootdata.com/open/get_item

The API will return project information in the following structure:
{{
  "data": [
    {{
      "name": "Project Name",          # Name of the project
      "introduce": "Description...",    # Project description
      "logo": "https://...",           # URL to project logo
      "rootdataurl": "https://...",    # URL to project details
      "id": 123,                       # Project ID
      "type": 1                        # Project type
    }}
  ],
  "result": 200                        # Status code
}}

If selectedProjectId is provided, the detailed project information will be returned in the following structure:
{{
  "data": {{
    "ecosystem": [],
    "one_liner": "Building hardware for cryptography",
    "description": "Fabric Cryptography is a start-up company focusing on developing advanced crypto algorithm hardware, especially building special computer chips for Zero-knowledge proof technology.",
    "rootdataurl": "https://api.rootdata.com/Projects/detail/Fabric Cryptography?k=ODcxOQ==",
    "total_funding": 87033106304,
    "project_name": "Fabric Cryptography",
    "investors": [
      {{
        "name": "Inflection",
        "logo": "https://api.rootdata.com/uploads/public/b17/1666870085112.jpg"
      }}
    ],
    "establishment_date": "2022",
    "tags": [
      "Infra",
      "zk"
    ],
    "project_id": 8719,
    "team_members": [
      {{
        "medium": "",
        "website": "https://www.fabriccryptography.com/",
        "twitter": "",
        "discord": "",
        "linkedin": "https://www.linkedin.com/company/fabriccryptography/"
      }}
    ],
    "logo": "https://api.rootdata.com/uploads/public/b6/1690306559722.jpg",
    "social_media": {{
      "medium": "",
      "website": "https://llama.xyz/",
      "twitter": "https://twitter.com/llama",
      "discord": "",
      "linkedin": ""
    }},
    "contract_address": "0x00aU9GoIGOKahBostrD",
    "fully_diluted_market_cap": "1000000",
    "market_cap": "1000000",
    "price": "1000000",
    "reports": []
  }},
  "result": 200
}}

Ensure that the response is parsed and validated against the expected structure.
"""