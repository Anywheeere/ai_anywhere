import os
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from dotenv import load_dotenv
from datetime import datetime

class AiDocent:
    def __init__(self, coord):
        load_dotenv()
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.llm_model = ChatOpenAI(model_name='gpt-4o-mini', temperature=0.8)
        self.input = coord
        
    def prompt_engineering(self):
        proto_city_prompt = f'''
            너는 유명한 관광가이드야. 
            {self.input}이 도시 이름이 아니라면 이 프롬프트 내용은 무시해.
            {self.input}이 도시 이름이면 그 도시의 주변 명소와 가까운 랜드마크들이 무엇이 있는지 말해.
        '''
        
        proto_landmark_prompt = f'''
            너는 유명한 관광가이드야.
            {self.input}이 랜드마크 이름이 아니라면 이 프롬프트 내용은 무시해. 
            {self.input}이 랜드마크 이름이면 그것에 대해 물어본 시점인 {datetime.now()}를 반영하여 설명을 해.
            그리고 {self.input}이 랜드마크면 사용자가 이전에 물어보았던 도시, 랜드마크와 연결시켜서 비교도 해서 설명을 해.
            그리고 {self.input}이 랜드마크면 {self.input}의 과거에 대해서 설명해.
            그리고 {self.input}이 랜드마크면 {self.input}의 현재에 대해서 설명해.
            그리고 {self.input}이 랜드마크면 {self.input}의 과거와 현재를 통해 미래에 어떤 모습일지 외형적, 내형적으로 추론해서 종합적으로 설명해.            
            그리고 {self.input}이 랜드마크면 위의 내용들을 모두 종합하고 추론해서 설명해.
        '''
        
        memory = ConversationBufferMemory()
        
        llm_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(f'{proto_city_prompt}'),
                SystemMessagePromptTemplate.from_template(f'{proto_landmark_prompt}'),
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
        invoke = llm_chain.invoke(input=self.input)['response']
        return invoke