#测试deep_search_task.api_extra_asnyc
from app.agents.emun.LanguageEnum import LanguageEnum
from app.agents.tasks.deep_search_task import api_extra_asnyc
if __name__ == '__main__':
    selectedType =  {'id': 'type3_btc', 'title': 'Analysis report of the 比特币 BEP2（BTCB）', 'logo': 'https://www.binance.com/static/images/common/ogImage.jpg', 'type': 3, 'detail': '比特币 BEP2（BTCB）是由币安发行的与比特币1:1锚定的代币，运行在币安链（Binance Chain）上，旨在将比特币的流动性引入币安链生态系统。', 'chain_id': 56, 'contract_addresses': ['0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c'], 'symbol': 'BTCB'}
    print(api_extra_asnyc(selectedType,3,LanguageEnum.EN.value))
