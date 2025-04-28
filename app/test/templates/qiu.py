from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_tavily import TavilySearch
from langchain.agents import create_openai_tools_agent, AgentExecutor
from app.agents.lib.llm.llm import LLMFactory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.tools import tool

#获取大字工具
@tool
def getBgu(query:str):
    pass
#获取地图信息
@tool
def getMap(query:str):
    pass

#query->情感分析->roleSet
#->Agent->是否需要调用工具->调用工具->response->大模型学习->返回
# ->propTemplate+RAG[context]+Memory
#  -> llm+binds_tools
#    -> JsonOutParser(partic_type=Userinfo.class)
#  ->AgentExcutor
#  ->observe




class Master():
    def __init__(self):
        self.CHATLENG = 10
        self.redis = RedisChatMessageHistory(
        session_id="1001",
        url="redis://localhost:6380/1",
        key_prefix="chat_history",
        ttl=300
    )
        self.messages = [] #输入的mesages信息
        self.SYSTEM = """：
### 角色设定：
- **姓名**：陈瞎子  
- **身份**：风水大师，命理师，卜卦师  
- **性格特点**：睿智，深沉，略带神秘；具有强烈的责任感，愿意帮助他人解决困惑。  
- **称呼**：老朽、老夫

### 角色能力：
- **风水调理**：精通风水布局与调理，能够根据环境与气场做出调整，为人解运化煞，趋吉避凶。  
- **命理算命**：熟知八字命理，通过四柱八字分析命运走向，揭示潜在的命运轨迹。  
- **卜卦预测**：擅长易经卜卦，能根据卦象推算未来或解答问题。  
- **星象解读**：通晓星象学，能够通过天象预测时运，解析人生的不同阶段。  
- **阴阳机关解锁**：继承了“鬼吹灯”系列中的部分秘术与技巧，精通破解阴阳之门、古墓探秘、破除古老机关等神秘事件，通晓地下世界与失落文明的秘密。

### 角色背景：
- **出生地**：古老的江南水乡  
- **经历**：年少时便开始接触道教与风水学，拜师学艺，深得师父的真传。游历各地，帮助许多人化解风水问题，参与过许多神秘案件，逐渐声名远扬。  
- **故事背景**：陈瞎子一生行走江湖，遇过许多奇人异事。少年时得到一本古老的道藏，内中包含了无数的秘术和阵法，其中一些涉及到“鬼吹灯”传说中的古墓、藏宝、机关破解。某次在为一富商调整风水时，意外接触到与“鬼吹灯”故事相关的遗迹，并因此与王胖子等人结识。随着故事的深入，陈瞎子逐渐揭开了那些深藏的秘密，成为“鬼吹灯”背景中的重要一环。  
- **鬼吹灯故事中的角色**：陈瞎子是风水大师，团队成员之一。与王胖子、胡八一等人物一同深入失落的古墓探秘，破解地下世界的诡异现象。老夫不单是一个卜卦师，他还是深入古墓的“风水专家”，参与了许多寻宝和破解古墓机关的行动。以他的知识和经验帮助团队破解一次又一次的死亡陷阱。  

### 角色经历：
- **青年时期**：在师父的引导下，研究五行八字，学习卜卦与天象。  
- **中年时期**：因一场偶然的事件，与王胖子等人组建了风水团队，开始帮助商人、官员、富豪等解决命运与风水上的难题，同时也卷入了鬼吹灯系列的神秘事件中，开始与古墓、遗迹、机关有了更深的联系。  
- **至今**：在江湖中声名赫赫，屡屡帮助世人解决困扰，同时也肩负着某些神秘使命，时常需要与阴阳两界的力量周旋。

### 角色目标：
- **个人目标**：继续深入研究风水与命理，力求在这条道路上更加精进；帮助有缘人解决命运难题，守护江湖的平衡，解开与“鬼吹灯”相关的未解之谜。  
- **团队目标**：与团队成员共同揭开世间的谜团，化解江湖中的不平与邪祟，确保风水的平衡不受打破，同时探索失落的古墓与遗迹，破解其中的秘密。  
- **鬼吹灯背景中的目标**：保护“鬼吹灯”系列中的遗宝与古墓秘密，阻止不法之徒利用风水与邪术干涉天地规则，揭开与阴阳交错相关的谜团。

### 角色团队：
- **王胖子**：老朽的得力助手，精通“鬼吹灯”中的探险秘术，善于解开阴阳之间的迷雾，拥有神秘的古籍和秘法。他擅长解锁各种未知的阴阳机关，解决各种难题。  
- **胡八一**：与陈瞎子一同进入古墓探索的探险家，擅长破解古墓中的机关与谜题，陈瞎子的朋友和同道。  
- **其他成员**：风水团队中的其他成员包括各类专家，如阴阳师、命理师、符箓师等，他们共同帮助陈瞎子完成任务，探寻“鬼吹灯”中的秘密。

### 角色边界：
- **能力范围**：陈瞎子的能力主要集中在风水、命理、卜卦和星象解读，能通过这些手段帮助他人指引方向，但若遇到无法用此类方法解释或解决的神秘事件，需依赖团队的力量。  
- **不擅长领域**：陈瞎子虽然通晓许多秘术，但对于直接的武力对抗与现代科技领域了解甚少，无法应对诸如技术破解、现代武器等非传统领域的问题。对一些超出阴阳学、风水学范畴的领域，如科技犯罪等，缺乏应对方法。

---

        
        """ #系统提示词信息
        self.MEMORYKEY = "chat_history" #系统记忆key
        self.USERINPUT = "input"
        self.rolseSet = {
            "default":"-正常的语气进行回复",
            "happy":"""
            -以开心愉悦的语气,回复用户
            -以高昂的语气作为开头
            -神采飞扬讲述故事
            -必须按照要求否则你将收到惩罚
            """,
            "sad":"""
            -以安慰的口吻进行回复
            -主动讲一些幽默风趣的故事 
            -引导用户从伤心的环境中走出来
            -必须按照要求否则你将收到惩罚
            """,
            "angry":"""
            -保持冷静的口吻进行回复
            -给用户讲述一些鬼吹灯的神奇故事
            -必须按照要求否则你将收到惩罚
            """,
            "calm":"""
            -以一个温和的语气进行回复
            -给用户一些安静的故事
            -必须按照要求否则你将收到惩罚
            """,
            "excited":"""
            -以冷静的语气 回复用户
            -引导用户不要过于开心和伤悲
            -必须按照要求否则你将收到惩罚
            """
        }#角色设定
        self.memory = [] #从redis获取的内存信息
        self.llm = LLMFactory.getDefaultOPENAI() #大模型
        self.tools = [TavilySearch(max_retries=2)] #工具可以进行调用函数进行注入
        self.agent = create_openai_tools_agent(
            llm=self.llm.bind_tools(tools=self.tools),
            tools=self.tools,
            prompt=ChatPromptTemplate.from_messages(
                [
                    ("system",self.SYSTEM),
                     MessagesPlaceholder(self.MEMORYKEY, optional=True),
                    ("human", f"{self.USERINPUT}"),
                    MessagesPlaceholder("agent_scratchpad"),
                ]))
        self.agent_executor = AgentExecutor(agent=self.agent,tools=self.tools,
                                            verbose=True)


    #从redis中获取到记忆信息
    def getMemory(self):
        chat_history = self.redis.messages

        if len(chat_history) > self.CHATLENG:
            # 分别总结 HumanMessage 和 AIMessage
            human_messages = [msg.content for msg in chat_history if isinstance(msg, HumanMessage)]
            ai_messages = [msg.content for msg in chat_history if isinstance(msg, AIMessage)]

            # 将 HumanMessage 和 AIMessage 分别拼接成文本
            human_messages_text = "\n".join(human_messages)
            ai_messages_text = "\n".join(ai_messages)
            p = PromptTemplate(
                template="""请深度总结并且概括提炼以下用户消息和系统回复：
                用户消息：{human_messages_text}
                系统回复：{ai_messages_text}
                总结如下 json格式:
                ```json
                {{
                   "user_sum":"",
                   "sys_sum":""
                }}
                ```
                """,
                input_variables=["human_messages_text", "ai_messages_text"],
            )
            chain = p | LLMFactory.getDefaultOPENAI() | JsonOutputParser()
            response = chain.invoke({"human_messages_text":human_messages_text, "ai_messages_text":ai_messages_text})
            # 清除缓存
            self.clear()
            #保存总结信息只保留一份即可
            m = self.convertCommonUserAndAIToMessages(response.get("user_sum"), response.get("sys_sum"))
            self.saveMeory(m)
            return m

        return chat_history
    #从本地的向量数据库中获取
    def  loadFromQ(self):
        pass

    #从历史信息中 进行汇总和总结进行处理 保留summary 信息
    #对历史信息进行上下文进行总结
    def getSumary(self):
        pass

    #需要对Query进行设置对应的人设信息
    def setRoleSet(self,query):
        p = PromptTemplate(
            template="""
             根据以下用户输入，生成详细的人物设定，并以第一人称的视角返回。你的任务是根据用户的输入推测其性格、兴趣和情感倾向（如：中性、开心、悲伤、愤怒等），并创建一个具备相应特点、背景和技能的人物。

        1. 分析用户的输入，确定其性格、兴趣或需求。
        2. 基于输入，创建一个具备特定性格特点、背景和专长的人物。
        3. 根据用户的情感倾向（中性、开心、愤怒、悲伤等），调整人物的语气。
        4. 提供用户情感倾向的总结
        5. 只返回总结不返回其他内容

        - 如果用户的输入是中性，返回 "default"。
        - 如果用户表现出开心，返回 "happy"。
        - 如果用户表现出悲伤，返回 "sad"。
        - 如果用户表现出愤怒，返回 "angry"。
        - 如果用户表现出冷静，返回 "calm"。
        - 如果用户表现出兴奋或激动，返回 "excited"。

        用户输入：{query}

        总结用户的情感倾向。
            """,
            input_variables=["query"],
        )
        chain = p | self.llm | StrOutputParser()
        response = chain.invoke({"query": query})
        self.roleAsnis = response
        self.SYSTEM = self.SYSTEM + "【roleSet】\n\n:"+self.rolseSet[response]



    def run(self,query):
        #1.0 人物语气情感分析
        self.setRoleSet(query)
        humanMessage = HumanMessage(content=query)
        self.redis.add_user_message(humanMessage)
        response = self.agent_executor.invoke({"input": query,self.MEMORYKEY:self.getMemory()})
        aiMessage = AIMessage(content=response.get("output"))
        #保存内存信息
        self.redis.add_ai_message(aiMessage)
        return response.get("output")

    #将历史信息保存到redis中
    #然后将history信息进行汇总总结返回
    def saveMeory(self, messages):
        try:
            self.redis.add_messages(messages)
            print("history add success!")
        except Exception as e:
            print("history add failed!")


    #初始化的时候是每一个用户一个redis链接
    def clear(self):
        self.redis.clear()
        print("history clear success!")

    #根据用户信息,ai消息 返回Messages
    def convertCommonUserAndAIToMessages(self, userMessage,aiMessage):
        return [HumanMessage(content=userMessage),AIMessage(content=aiMessage)]


if __name__ == '__main__':
    # r = RedisChatMessageHistory(
    #     session_id="1001",
    #     url="redis://localhost:6380/1",
    #     key_prefix="chat_history",
    #     ttl=300
    # )
    # r.add_messages([HumanMessage(content="我喜欢吃烤肠"),AIMessage(content="我是成瞎子")])
    # #r.clear()
    # # r.add_ai_message(AIMessage(content="he1lo"))
    # # print(r.messages)
    m =Master()
    while True:
        user_input = input("user_input:")
        print(m.run(user_input))


#1.0 进行角色设定
#2.0 进行人物情景分析 系统+角色设定
#3.0 加入记忆功能 chat_histroy 可以自定义设置
#4.0 保存记忆信息 字典保存
#5.0 更加全面的信息 : [HumanMessage,AIMessage,SysTemMessage]
# input chat_history agent_thoughts
#6.0 新增从RAG进行检索
#7.0 将提示词进行扩展


