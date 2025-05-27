from langchain_core.output_parsers import StrOutputParser

from app.agents.lib.llm.llm import LLMFactory
from langchain.prompts.prompt import PromptTemplate
from app.agents.proptemts.v1.intent_prompt_deep_up import INTENT_PROMPT_TEMPLATE
if __name__ == '__main__':
    llm = LLMFactory.getDefaultOPENAI()
    c = PromptTemplate(
        template=INTENT_PROMPT_TEMPLATE,
        input_variables=["message_history","latest_message","attached_data"]
    )
    chain = c | llm |StrOutputParser()
    response =  chain.invoke({"message_history":[],"latest_message":"Uniswap","attached_data":{}})
    print(response)
