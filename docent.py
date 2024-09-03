import os
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from dotenv import load_dotenv

class AiDocent:
    def __init__(self, coord):
        load_dotenv()
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.llm_model = ChatOpenAI(model_name='gpt-4o-mini', temperature=0.5)
        self.input = coord
        
    def prompt_engineering(self):
        proto_prompt = '''
            사용자가 위도와 경도를 물어보면 해당 좌표 근처에 있는 랜드마크에 대해서 
            설명해봐
        '''
        
        memory = ConversationBufferMemory()
        
        llm_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(f'{proto_prompt}'),
                HumanMessagePromptTemplate.from_template('{input}'),
                HumanMessagePromptTemplate.from_template('{history}')
            ]
        )
        
        return llm_prompt, memory
    
    def chaining(self):
        llm_prompt, memory = self.prompt_engineering()
        llm_chain = ConversationChain(
            llm = self.llm_model,
            prompt = llm_prompt,
            memory = memory
        )
        
        return llm_chain
    
    def run_llm(self):
        llm_chain = self.chaining()
        invoke = llm_chain.invoke(input=self.input)
        return invoke