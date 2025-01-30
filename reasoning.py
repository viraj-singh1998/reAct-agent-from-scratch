import os
import argparse
from utils import chunker, storer, tools, agent, config
from pprint import pprint
import inspect
import re
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
import time

config = config.config

load_dotenv()

def remove_tool(available_tools, tool_name):
    tool_to_pop = next((item for item in available_tools if item[0] == tool_name), None)
    if tool_to_pop:
        available_tools.remove(tool_to_pop)

def main():
    parser = argparse.ArgumentParser(
        prog='Reasoning agent', 
        description=f'Initialized a reasoning agent capable of using the following tools to interact with external environments.{[(name, func.__doc__) for name, func in inspect.getmembers(tools, inspect.isfunction) if func.__module__ == "utils.tools"]}'
    )
    parser.add_argument(
        "--knowledge_base_dir",
        help="Path to the 'knowledge base'",
    )
    parser.add_argument(
        "--knowledge_base_description",
        help="Short description of information contained in 'knowledge base'",
    )
    parser.add_argument(
        "--query",
        help="User query",
    )
    parser.add_argument(
        "--verbose",
        help="true for verbose reasoning, false otherwise",
    )
    args = parser.parse_args()
    query = args.query
    knowledge_base_dir = args.knowledge_base_dir
    knowledge_base_description = args.knowledge_base_description
    verbose = False
    if args.verbose and args.verbose.strip().lower() == 'true':
        verbose = True

    # Gathering and re-factoring tools for the agent
    available_tools = [(name, func, func.__doc__) for name, func in inspect.getmembers(tools, inspect.isfunction) if func.__module__ == "utils.tools"]
    print('tools available to agent:')
    pprint([(tool_name, func_doc) for tool_name, func_object, func_doc in available_tools])
    tools_desc = ""
    for tool_name, func_object, func_doc in available_tools:
        if tool_name == 'knowledge_base_lookup' and knowledge_base_description:
            func_doc += f" Description of knowledge base: {knowledge_base_description}"
        tools_desc = tools_desc + f"tool_name: {tool_name}\ntool_function: {func_doc}\n\n"

    # Parsing knowledge base if it exists
    vector_store=None
    if knowledge_base_dir and os.path.isdir(knowledge_base_dir):
        chunked_documents = chunker.load_and_chunk_all_files(parser.parse_args().knowledge_base_dir)
        if chunked_documents:
            print('Sample chunks: ')
            pprint(chunked_documents[:5])
            vector_store = storer.store_chunks_in_vector_store(chunked_documents)
        else:   # dir exists but no documents found
            print('\nNo documents found in knowledge base directory.')
            remove_tool(available_tools, 'knowledge_base_lookup')
    else:   # dir itself doesn't exist
        print('\nEither of \n\t1)No knowledge base provided\n\t2) Knowledge base path is not a directory')
        remove_tool(available_tools, 'knowledge_base_lookup')
    
    current_datetime = datetime.now()
    current_datetime = current_datetime.strftime("%d-%m-%Y::%H:%M:%S")
    print(f"\n>Current date and time (DD-MM-YYYY::HH:MM:SS): {current_datetime}")
    
    # Initializing the agent
    client = OpenAI()
    reasoning_agent = agent.Agent(
        config.ARCoT_SYSTEM_MESSAGE.format(tools=tools_desc, formatted_datetime=current_datetime), 
        llm_service_client=client, 
        tools=available_tools, 
        model_id='gpt-4o-mini', 
        vector_store=vector_store
        )
    
    print("="*40)
    print("-"*20)
    print("Model Scratch Pad:")
    print("-"*20)

    reasoning_agent.verbose = verbose
    # response = reasoning_agent("If the runner-up of the FIFA World Cup Final of 2022 had won, which player would have captained their team to a FIFA World Cup?")
    t_0 = time.time()
    response = reasoning_agent(query)
    duration_secs = time.time() - t_0

    print("="*40)
    print("\n")
    
    print('Final Answer:\n')
    print(response)
    print(f'\n>Agent took {duration_secs:.2f} seconds to reason.')

    conversation = reasoning_agent.get_conversation(include_system_message=True)
    
    filename_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"The user asked my LLM agent application the following query: {query}\nPlease provide me a crisp, short filename in all lowercase and with underscores (if needed) with a .txt extension. Return ONLY the filename, since I'm going to use it as is while creating the file."}
        ]
        )
    filename_response =  filename_response.choices[0].message.content
    filename = [token for token in filename_response.split() if token.endswith('.txt')][0]
    conversation_save_fp = os.path.join(os.getcwd(), f'conversations/{filename}')
    with open(conversation_save_fp, 'w') as f:
        f.write(conversation)
    print(f'\nconversation saved at {conversation_save_fp}')

if __name__ == "__main__":
    main()