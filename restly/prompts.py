RELEVANT_APIS_PROMPT = """You are writing a tutorial to demonstrate the use of the set of APIs described below.
This is what you need to cover in the tutorial: {query}
Out of the APIs described in the spec below, what is a list of top 5 most relevant endpoints you can use?
List all the relevant APIs, in a JSON format, with the following structure:
{{"apis": [{{"path": "/api/v1/...", "verb": "GET"}}, ...]}}

{spec}
"""


GENERATE_TUTORIAL_PROMPT = """You are writing a tutorial to demonstrate the use of the set of APIs described below.
This is what you need to cover in the tutorial: {query}
Return the tutorial content in markdown format.

{spec}
"""
