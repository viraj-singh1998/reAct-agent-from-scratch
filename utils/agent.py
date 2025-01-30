'''
This is the common Agent class for the Act-only and ReAct agents. Their contrast lies in their system message.
'''
import re

class Agent():
    def __init__(self, system_message, llm_service_client, tools, model_id, vector_store):
        self.messages_history = []
        self.messages = []
        self.verbose = False
        self.available_tools = {tool_name:func_object for tool_name, func_object, func_doc in tools}
        self.client = llm_service_client
        self.model_id = model_id
        self.vector_store = vector_store
        self.answer_re = r"Answer:\s*(.*)"
        self.action_re = re.compile('^Action: (\w+): (.*)$')
        if system_message:
            self.messages.append({"role": "system", "content": system_message})

    def __call__(self, query):
        response = self.execute(query)
        self.messages_history.append(self.messages)
        self.messages = []
        return response

    def execute(self, query, role="user", max_turns=10):
        turns = 0
        self.messages.append({"role": "user", "content": query})
        while turns < max_turns:
            response_content = self.llm_call()
            self.messages.append({"role": "assistant", "content": response_content})
            if self.verbose:
                print(f">assistant ({turns}):\n{response_content}\n")
            actions = [self.action_re.match(a) for a in response_content.split('\n') if self.action_re.match(a)]
            if actions:
                # There is an action to run
                action, action_input = actions[0].groups()
                if action not in self.available_tools:
                    observation = "--Unknown tool: {}: {}\nRefer to available tools and choose again.".format(action, action_input)
                    self.messages.append({"role": "assistant", "content": observation})
                else:
                    if self.verbose:
                        print(">action {}:\ntool call\n\t tool: {}\n\t input: {}\n".format(turns, action, action_input))
                    # tool call

                    # observation = self.available_tools[action](action_input)
                    # self.messages.append({"role": "assistant", "content": str(observation)})
                    # turns += 1

                    try:
                        if action == "knowledge_base_lookup":
                            observation = self.available_tools[action](self.vector_store, action_input)
                        elif action == "get_webpage_info":
                            args = [arg.strip() for arg in action_input.split(',')]
                            if self.verbose:
                                print(f'visiting web page, args: {args}\n')
                            observation = self.available_tools[action](*args)
                        else:
                            observation = self.available_tools[action](action_input)
                        if self.verbose:
                            print(f">observation ({turns}):\n{observation}")
                        self.messages.append({"role": "assistant", "content": str(observation)})
                    except Exception as e:
                        if self.verbose:
                            print(f'>!!ERROR IN TOOL CALL!!\n\t details: {e}')
                        observation = "Error in tool call: {}: {}\nChange the search term or try another tool.".format(action, action_input)
                        if self.verbose:
                            print(f">observation ({turns}):\n{observation}")
                        self.messages.append({"role": "assistant", "content": observation})
            else:
                match = re.search(self.answer_re, response_content)
                if match:
                    result = match.group(1)
                    return result
            turns += 1
        correction_message = "It seems your response does not include the phrase: Answer: <final answer here>. Please ensure your next response explicitly includes 'Answer:' followed by the final answer."
        return self(correction_message)

    def llm_call(self):
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=self.messages
            )
        return response.choices[0].message.content

    def get_conversation(self, include_system_message=False):
        '''
        prints most recent query's execution flow
        '''
        while len(self.messages_history):
            if not self.messages_history[-1]:
                self.messages_history.pop()
            else:
                break
        
        converation = ""
        for message in self.messages_history[-1]:
            if message['role'] == 'system':
                if not include_system_message:
                    continue
            converation += f"\n{message['role'].upper()}:\n"
            converation += message['content']
            converation += "\n\n"
        return converation.strip('\n')