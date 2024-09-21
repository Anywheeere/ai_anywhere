import os
import re
import random
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from dotenv import load_dotenv
from datetime import datetime

class AiDocent:
    def __init__(self, coord, rdbms_path, data_path):
        load_dotenv()
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        self.llm_model = ChatOpenAI(model_name='gpt-4o-mini', temperature=0.8)
        self.input = coord
        self.rdbms_path = rdbms_path
        self.data_path = data_path
        self.retriver = None
        self.vectordb_path = 'docentDB'
    
    def connect_database(self):
        df = pd.read_csv(f'{self.rdbms_path}', encoding='utf-8')
        
        data_loader = TextLoader(self.data_path, encoding='utf-8')
        data_document = data_loader.load()

        first_splitter = RecursiveCharacterTextSplitter(separators='<', chunk_size=1000, chunk_overlap=0)
        second_splitter = RecursiveCharacterTextSplitter(separators='[', chunk_size=100, chunk_overlap=10)
        
        first_docs = first_splitter.create_documents([data_document[0].page_content])
        
        for i in range(len(first_docs)):
            data_info = second_splitter.create_documents([first_docs[i].page_content])
            df.loc[df['best 랜드마크'] == re.search(r'<(.*?)>',data_info[i][0].page_content).group(1), '랜드마크설명'] = df.loc[df['best 랜드마크'] == re.search(r'<(.*?)>',data_info[i][0].page_content).group(1)].apply(
                lambda row : data_info[random.randint(1,len(data_info)-1)], axis=1
            )
        
        update_path = 'update.csv'
        df.to_csv('update.csv',index=False, encoding='utf-8-sig')
        
        embeddings, documents = self.make_embedding(update_path)
        self.make_vectordb(embeddings, documents)
        
    def make_embedding(self, update_path):
        csv_loader = CSVLoader(file_path=update_path, encoding='utf-8-sig')
        documents = csv_loader.load()
        page_contents = [doc.page_content for doc in documents]
        
        embeddings = OpenAIEmbeddings()
        embeddings.embed_documents(page_contents)
        
        return embeddings, documents
        
    def make_vectordb(self, embeddings, documents):
        persist_directory = self.vectordb_path
        
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_directory
        )
        
        vectordb.persist()
           
    def connect_vectordb(self):
        if os.path.exists(self.vectordb_path):
            vectordb = Chroma(persist_directory='docentDB')
            self.retriver = vectordb.as_retriever()
        else:
            None
            
    def prompt_engineering(self):
        self.connect_vectordb()
        
        prompt = f'''
            너는 {self.retriver}에 있는 지식을 모두 가지고 있어 이걸 바탕으로 추론해서 이야기하는 아주 유명한 베테랑 관광가이드야. 
            너는 도슨트처럼 설명을해. 사용자와 상호작용을 할 수는 없어. 설명 길이는 95 텍스트 이내야.
            {self.input} 대해서 물어본게 1번째이면 추가 설명을 해줄 듯이 간략히 설명해.
            {self.input} 대해서 물어본게 2번째이면 1번째 대답이랑 똑같은 내용은 말하지마.
            {self.input} 대해서 물어본게 2번째이면 {datetime.now()}를 이야기하고 계절, 시간에 맞는 {self.input}에 대한 설명을 해.
            {self.input} 대해서 물어본게 3번째이면 1,2번째 대답이랑 똑같은 내용은 말하지마.  
            {self.input} 대해서 물어본게 3번째이면 사용자가 이전에 물어보았던 도시, 랜드마크와 연결시켜서 '이전에 방문하셨던'으로 시작하면서 설명을 해.
            {self.input} 대해서 물어본게 4번째이면 1,2,3번째 대답이랑 똑같은 내용은 말하지마.
            {self.input} 대해서 물어본게 4번째이면 {self.input}의 과거에 대해서 설명해.
            {self.input} 대해서 물어본게 5번째이면 1,2,3,4번째 대답이랑 똑같은 내용은 말하지마.
            {self.input} 대해서 물어본게 5번째이면 {self.input}의 현재에 대해서 설명해.
            {self.input} 대해서 물어본게 6번째이면 1,2,3,4,5번째 대답이랑 똑같은 내용은 말하지마.
            {self.input} 대해서 물어본게 6번째이면 {self.input}의 과거와 현재를 통해 미래에 어떤 모습일지 외형적, 내형적으로 추론해서 종합적으로 설명해.              
            {self.input} 대해서 물어본게 7번째이면 {self.input} 대해서 위의 내용들을 모두 종합하고 추론하고 요약해서 설명해.
            마지막까지 했으면 처음으로 돌아가서 계속 반복해.
        '''
        
        memory = ConversationBufferMemory()
        
        llm_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(f'{prompt}'),
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