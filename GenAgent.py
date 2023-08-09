import os
import json
import openai
from utils import *
import random
import langchain
from langchain import PromptTemplate
from langchain.llms import OpenAI, OpenAIChat
from langchain import LLMChain
from re import compile
from datetime import datetime
from typing import NamedTuple
from openai import Embedding


#set env variables
os.environ["OPENAI_API_KEY"] = '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'

def embedding(text: str):
    MODEL = "text-embedding-ada-002"
    return Embedding.create(model=MODEL, input=text).data[0].embedding

class Memory:

    def __init__(self, description: str):
        now = datetime.now()

        self.description = description
        self.creation_timestamp = now
        self.most_recent_access_timestamp = now

        self.importance = self.get_importance()
        self.embedding = embedding(description)
        
    def get_importance(self):
        prompt_text = """On the scale of 1 to 10, where 1 is purely mundane
                        (e.g., brushing teeth, making bed, casual talk) and 10 is
                        extremely poignant (e.g., a break up, college
                        acceptance, sex), rate the likely poignancy of the
                        following piece of memory.
                        Memory:" {Memory} "
                        Rating: <fill in integer>"""  
                        
        prompt_template = PromptTemplate(template=prompt_text, input_variables=['Memory'])
        llm = OpenAIChat(model_name="gpt-4",temperature = 0.0, max_tokens = 1)
        importance_chain = LLMChain(llm=llm, prompt=prompt_template)
        response = importance_chain.run(self.description)
        print("imp",response)
        return int(response)
     
    def __repr__(self):
        return self.description

    def access(self):
        self.most_recent_access_timestamp = datetime.now()

class Score(NamedTuple):
    score: float
    memory: Memory
    
class MemoryStream:

    def __init__(self,user_id):
        self.stream: list[Memory] = []
        self.user_id = user_id
        self.DECAY_FACTOR = 0.99
        self.ALPHA_RECENCY = 1
        self.APLHA_IMPORTANCE = 0
        self.ALPHA_RELEVANCE = 1
        
    def add_memory(self,memory:Memory):
        self.stream.append(memory)
        return
    
    
    def retrieve_memories(self, agents_current_situation: str):
        def sort(memory: Memory):
            hours_since_last_retrieval = (
                datetime.now() - memory.most_recent_access_timestamp
            ).total_seconds() / SECONDS_IN_HOUR

            recency = self.DECAY_FACTOR**hours_since_last_retrieval
            importance = min_max_scale(memory.importance, 0, 10)
            relevance = min_max_scale(
                cosine_similarity(
                    memory.embedding, embedding(agents_current_situation)
                ),
                -1,
                1,
            )
            score = (
                self.ALPHA_RECENCY * recency
                + self.APLHA_IMPORTANCE * importance
                + self.ALPHA_RELEVANCE * relevance
            )

            return Score(score, memory)

        return sorted(self.stream, key=sort, reverse=False)
    
    
class agent:
    def __init__(self,memory_stream,message):
        self.memory_stream = memory_stream
        self.message = message
        
        # time modules
        # add default msg to memstrm
        
    def reflect(self):
        # Determine whether to generate a reflection based on the sum of importance scores
        threshold = 10  # Adjust this threshold as needed based on experimentation
        n_memories = 20
        recent_memories = self.memory_stream.stream[-n_memories:]  # Get the 100 most recent memories
        sum_importance = sum(memory.importance for memory in recent_memories)
        if sum_importance >= threshold:
            # Generate reflection
            reflection_query = """Given only the information above, what are 3 most salient high-level
            questions we can answer about the subjects in the statements?{memories_description}
            answer in json format, example :{
                                                "questions": [
                                                "What is ...?",
                                                "What ...?",
                                                "What does ...?"]
                                            }
                                            """ # use openai functions
            
            reflection_template = PromptTemplate(reflection_query,["memories_description"])
            memories_description = ""
            for idx, memory in enumerate(recent_memories):
                memories_description += f"Statement {idx + 1}: {memory.description}\n"
  
            # Prompt the language model to generate high-level questions
            llm = OpenAIChat(model_name="gpt-3.5-turbo",temperature = 0.3, max_tokens = 60)  # Replace this with the appropriate model
            q_chain = LLMChain(llm=llm,prompt=reflection_template)
            response = q_chain.run(memories_description)

            response_data = json.loads(response)
            questions_list = response_data["questions"]
            
            # get all relevent mems to question
            gathered_memories = []
            for question in questions_list:
                retrieved_memory = self.memory_stream.retrieve_memories(question)[-5:]
                gathered_memories.extend(retrieved_memory)
            
            # generate insights
            insight_query = """statements about Zaina
                                {memories_description}
                                What 5 high-level insights can you infer from
                                the above statements? (example format: insight
                                (because of 1, 5, 3))
                                            """
            insight_template = PromptTemplate(insight_query,["memories_description"])
            memories_description = ""
            for idx, memory in enumerate(gathered_memories):
                memories_description += f"Statement {idx + 1}: {memory.description}\n"
            
            
            
        return
    
    def plan(self):
        
        return
    
    
    def run(self):
        
        # add msg to strm
        new_memory = Memory(self.message)
        self.memory_stream.add_memory(new_memory)
        
        # retreive mem from mem strm
        agents_current_situation = self.message
        retrieved_memory = self.memory_stream.retrieve_memories(agents_current_situation)
        
        # update reflection and add to strm
        self.reflect()
         
        # update plan and add to strm
        self.plan()
        
        # give mem subset to final llm for response
        top_mem = 5
        memory_subset = retrieved_memory[-top_mem:]
        
        # add response to mem strm
        response = self.final_llm(memory_subset)
        self.memory_stream.add_memory(Memory(response))
        return response
        
    def final_llm(self,memory_subset):
        return response



if __name__ == "__main__":
    # test
    a = MemoryStream(1)
    f=[4,8,9,8]
    for i in range(20,30,1):
        b = Memory(" i had a date with a {} yrs old girl i met at the bar yesterday".format(i))
        a.add_memory(b)
    print(f[-10:],a.retrieve_memories("give me the 2 yrs old"))