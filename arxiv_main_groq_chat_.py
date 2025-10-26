from groq import Groq
import os
from dotenv import load_dotenv
import json
from typing import List
import arxiv

load_dotenv()

model_name=os.getenv("model_name")

client = Groq()


def fetch_data(topic:str, max_results:int = 10) -> List[str]:

    arch_client = arxiv.Client()
    arch_search = arxiv.Search(
            query=topic,
            #max_results=max_results,
            max_results=2,
            sort_by=arxiv.SortCriterion.Relevance
        )
    papers = arch_client.results(search=arch_search)

    paper_ids = []
    for paper in papers:
        paper_ids.append(paper.get_short_id())
    return paper_ids


def extract_info(paper_ids: List) -> str:
    """
    Search for information about a specific paper by the given paper_id.
    
    Args:
        paper_id: The ID of the paper to look for
        
    Returns:
        JSON string with paper information if found, error message if not found
    """

    arch_client = arxiv.Client()
    arch_search = arxiv.Search(id_list=paper_ids)
        
    papers = arch_client.results(search=arch_search)

    papers_info = []

    for paper in papers:
        papers_info.append(
            {
                'title': paper.title,
                'authors' : [author.name for author in paper.authors],
                'summary' : paper.summary,
                'pdf_url' : paper.pdf_url,
                'published' : paper.published.strftime("%Y-%m-%d %H:%M:%S")
            }
        )

    if papers_info:
        return json.dumps(papers_info, indent=2)
    else:
        return f"There's no saved information related to paper {paper_ids}."

def execute_tool(tool_name, tool_args):

    mapping_tool_function = {
        "fetch_data": fetch_data,
        "extract_info": extract_info
    }
    result = mapping_tool_function[tool_name](**tool_args)

    if result is None:
        result = "The operation completed but didn't return any results."
        
    elif isinstance(result, list):
        result = ', '.join(result)
        
    elif isinstance(result, dict):
        # Convert dictionaries to formatted JSON strings
        result = json.dumps(result, indent=2)
    
    else:
        # For any other type, convert using str()
        result = str(result)
    return result




tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_data",
            "description": "Use this function to search the internal documents related to the paper.  Each document is identified by unique id called 'paper id'.  Based on the search the function returns the list of paper ids as a string of comma separted values",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to search for"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to retrieve",
                            "default": 5
                        }
                    },
                    "required": ["topic"]
                }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_info",
            "description": "Use this function to get the information related to list of paper ids.  The function accepts paper ids as JSON array.  It fetches the paper information from the documents based on the list of ids provided",
            "parameters": {
                    "type": "object",
                    "properties": {
                        "paper_ids": {
                            "type": "array",
                            "description": "The list of IDs for a paper to look for",
                            "items": {
                                "type": "string"
                            }
                        }
                    },
                    "required": ["paper_ids"]
            }
        }
    }
]


def process_query(messages:List) -> str:
    
    response = client.chat.completions.create(
        model=model_name, messages=messages, tools=tools, tool_choice="auto", max_completion_tokens=4096, temperature=0.5
    )

    response_message = response.choices[0].message    
    tool_calls = response_message.tool_calls
    messages.append(response_message)

    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            tool_result = execute_tool(tool_name=function_name,
                                tool_args=function_args)
            messages.append(
                {
                    "role": "tool",
                    "content": f"Tool call with the id : {tool_call.id} is completed with the function {function_name} and the result is : {json.dumps(tool_result)}.  Use this result for futher decision making",
                    "tool_call_id": tool_call.id
                }
            )
        return process_query(messages=messages)
    else:
        return response.choices[0].message.content



messages = [
    {"role": "system", "content": " You are a helpful assistance. Use tool to retrive relevant information.  The response should listed or summarized based on the query"},
    {"role": "user", "content": "Find related to the topics Physics, Mathematics"},
]

result = process_query(messages=messages)

print(result)