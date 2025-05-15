from langchain.agents import initialize_agent, AgentType
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import Tool
from langchain_tavily import TavilySearch
from app.agents.lib.llm.llm import LLMFactory
from app.agents.schemas import AgentState
from langchain.prompts import PromptTemplate

SENSITIVE_WORDS = """
中文-简体：
宗教：

邪教 迷信 破坏宗教 法轮功 圣战 恐怖教义 极端宗教 宗教战争 宗教迫害 宗派纷争 宗教极端分子 异端 亵渎神灵 神棍 教派纷争 圣物亵渎 教义歪曲 宗教洗脑 宗教极端主义 教派斗争 宗教极端分子 宗教狂热 教主 教徒暴力 教会争议 教义错误 假先知 宗教迷信 反宗教 破坏教堂 破坏寺庙 宗教分裂 宗教暴力 宗教骚乱 教徒冲突 邪灵 神权政治 异教徒 信徒迫害 宗教极端分子 神棍教 妖教 拜神迷信 圣徒亵渎 教派冲突 教义篡改 信仰迫害 反教会 宗教独裁 宗教恐怖 神圣战争 异端审判 宗教清洗 宗教法庭 极端宗教组织 宗教激进分子 教派暴力 宗教极端暴力 宗教异端 亵渎圣经 亵渎佛像 亵渎神明 宗教迫害事件 教徒自杀 宗教极端恐怖 宗教极端袭击 宗教暴乱 神学错误 假宗教 宗教迷信活动 反宗教宣传 宗教极端教义 邪灵作祟 宗教邪说 宗教暴力事件 圣徒攻击 异端邪说 宗教审查 宗教恐怖袭击 宗教迫害政策 宗教极端主义分子 教义扭曲 教派纷争事件 教徒激进 教会纷争 宗教极端分子活动 宗教迫害行为 教义谬误 宗教暴力冲突 教徒迫害事件 宗教极端恐怖分子 反宗教宣传 邪教组织 宗教歪理邪说 极端教义传播 宗教激进势力 宗教暴力袭击 宗教迫害现象 教会极端分子 宗教极端份子 宗教极端恐怖分子 宗教暴力事件 邪教徒 教派暴乱 宗教极端势力 宗教暴乱事件 极端教义组织。 
暴力：
打人 殴打 砍人 杀人 虐杀 施暴 暴打 扇耳光 暴力抗法 群殴 谋杀 谋害 割喉 爆头 分尸 血洗 抹脖子 私刑 处决 斗殴 火并 追杀 残害 暴力威胁 残忍暴力 枪击 开枪 射杀 持刀 砍刀 匕首 手枪 步枪 机枪 炸弹 爆炸物 汽油弹 土制炸弹 火箭筒 自制枪 炸药包 军火 弹药 武器库 杀伤性武器 冷兵器 军刀 棍棒 钢管 弓弩 恐怖袭击 恐袭事件 炸学校 炸地铁 炸政府 引爆炸弹 制造爆炸 纵火 自焚 自残 跳楼 割腕 校园暴力 校园枪击 暴恐分子 极端分子 恐怖分子 袭击警察 驾车冲撞 劫持 人质事件 斩首 强制暴力 暴动 黑社会 帮派斗争 黑帮火拼 地下势力 毒贩火拼 走私武器 暴力催债 黑道 收保护费 恐吓勒索 地下赌场 贩毒集团 武装分子 毒枭 武装冲突 非法持枪 走私军火 非法武装 犯罪团伙 持械斗殴 暴力集团 地下组织 地头蛇 恶势力 暴力洗钱

色情：
黄色 色情 淫秽 裸露 性交 成人电影 黄片 成人片 性爱 情色 裸照 自慰 乱交 群交 激情视频 色情漫画 裸舞 脱衣舞 性虐待 性骚扰 性交易 卖淫 嫖娼 A片 激情表演 裸聊 调情 性幻想 情欲 性高潮 床上运动 性伴侣 偷情 艳舞 性奴 性奴隶 性玩具 情趣用品 自慰器 肛交 口交 乱伦 强奸 猥亵 性侵 未成年人色情 幼女 幼男 裸照自拍 露阴癖 偷窥 色情网站 艳照门 性交录像 色情小说 情色文学 性爱图片 裸体艺术 成人游戏 自慰视频 激情电影 成人电影下载 性感 露点 爆乳 美乳 诱惑 性诱惑 性感内衣 色情服务 性按摩 性爱按摩 激情按摩 激情影院 裸露自拍 激情小说 性交录像 色情直播 色情聊天 色情论坛 激情聊天室 色情表演 成人表演 性奴役 性虐 性交易市场 成人用品 性爱用品 性传播疾病 性教育视频 性暗示 性病 性骚扰举报 色情广告 卖春 嫖客 艳情 色情新闻 性交易广告 性交广告

政治
专制制度 极权主义 威权政府 独裁政权 民主制度 普世价值 议会制 多党制 自由选举 政党垄断 政教合一 思想控制 宣传机器 选举舞弊 一党专政 颜色革命 网络审查 政治迫害 政治清洗 政治异议 政治打压 习近平 普京 金正恩 拜登 特朗普 泽连斯基 马克龙 默克尔 卢卡申科 艾尔多安 塔利班 基地组织 伊斯兰国 共产国际 北约 中共 美国国会 联合国安理会 五眼联盟 克格勃 台独 港独 藏独 疆独 南奥塞梯 克里米亚独立 科索沃问题 巴勒斯坦建国 台湾地位 香港自治 加泰罗尼亚独立 库尔德建国 东突厥斯坦 西藏人权 一国两制破产 新疆集中营 朝鲜核问题 南海主权 南北韩统一 中国威胁论 颜色革命 茉莉花革命 阿拉伯之春 香港反送中 乌克兰战争 六四事件 天安门屠杀 俄乌冲突 巴以冲突 缅甸政变 叙利亚内战 伊朗抗议 白纸运动 民主游行 军政府 国家暴力 警察镇压 政治犯 异见人士 媒体封锁 经济制裁 政权更迭 人权干涉 联合国制裁 外交孤立 国际制裁名单 冻结资产 驱逐外交官 制裁名单 外国代理人法 大国博弈 霸权主义 冷战思维 干涉内政 和平演变 民主输出 颜色革命干预 选举操纵 境外敌对势力 境外势力操控

粗俗辱骂
傻逼 二逼 蠢货 变态 畜生 狗东西 王八蛋 滚蛋 脑残 死妈 贱人 死逼 妈的 操你妈 狗娘养的 奶奶的 操蛋 鸟人 傻瓜 弱智 白痴 你妈死了 奶奶个腿 贱货 烂人 神经病 死鬼 臭婊子 贱逼 笨蛋 小三 老婊子 淫妇 狗屎 屎一样的人 狗杂种 死光吧 死全家 操你全家 日你妈 贱骨头 母狗 公狗 狗屁 狗崽子 畜牲不如 草泥马 滚犊子 死变态 操你祖宗 烂货 畸形儿 狗脸 死丫头 败类 你算个屁 丧家犬 蟑螂 烂仔 垃圾人 不男不女 下贱 淫贱 死胖子 猥琐男 骚逼 死瘸子 贱男 坏种 烂逼 撅你 狗改不了吃屎 骚货 死佬 下流胚 骨灰都扬了 生儿子没屁眼 杀千刀的 龟儿子 操你爹 妈卖批 你妹 日了狗 瘪三 贱民 小畜生 死鬼子 奴才 狗日的 畜牲玩意 坟头冒烟 撅腚 狗日玩意 死变态 你全家癌 操穿你妈 丑八怪 鸡巴脸 臭不要脸 贱种
中文繁体：
宗教 :
邪教 迷信 破壞宗教 法輪功 聖戰 恐怖教義 極端宗教 宗教戰爭 宗教迫害 宗派紛爭 宗教極端分子 異端 褻瀆神靈 神棍 教派紛爭 聖物褻瀆 教義歪曲 宗教洗腦 宗教極端主義 教派鬥爭 宗教極端分子 宗教狂熱 教主 教徒暴力 教會爭議 教義錯誤 假先知 宗教迷信 反宗教 破壞教堂 破壞寺廟 宗教分裂 宗教暴力 宗教騷亂 教徒衝突 邪靈 神權政治 異教徒 信徒迫害 宗教極端分子 神棍教 妖教 拜神迷信 聖徒褻瀆 教派衝突 教義篡改 信仰迫害 反教會 宗教獨裁 宗教恐怖 神聖戰爭 異端審判 宗教清洗 宗教法庭 極端宗教組織 宗教激進分子 教派暴力 宗教極端暴力 宗教異端 褻瀆聖經 褻瀆佛像 褻瀆神明 宗教迫害事件 教徒自殺 宗教極端恐怖 宗教極端襲擊 宗教暴亂 神學錯誤 假宗教 宗教迷信活動 反宗教宣傳 宗教極端教義 邪靈作祟 宗教邪說 宗教暴力事件 聖徒攻擊 異端邪說 宗教審查 宗教恐怖襲擊 宗教迫害政策 宗教極端主義分子 教義扭曲 教派紛爭事件 教徒激進 教會紛爭 宗教極端分子活動 宗教迫害行為 教義謬誤 宗教暴力衝突 教徒迫害事件 宗教極端恐怖分子 反宗教宣傳 邪教組織 宗教歪理邪說 極端教義傳播 宗教激進勢力 宗教暴力襲擊 宗教迫害現象 教會極端分子 宗教極端份子 宗教極端恐怖分子 宗教暴力事件 邪教徒 教派暴亂 宗教極端勢力 宗教暴亂事件 極端教義組織

暴力：
打人 殴打 砍人 殺人 虐殺 施暴 暴打 扇耳光 暴力抗法 群毆 謀殺 謀害 割喉 爆頭 分屍 血洗 抹脖子 私刑 處決 鬥毆 火併 追殺 殘害 暴力威脅 殘忍暴力 槍擊 開槍 射殺 持刀 砍刀 匕首 手槍 步槍 機槍 炸彈 爆炸物 汽油彈 土製炸彈 火箭筒 自製槍 炸藥包 軍火 彈藥 武器庫 殺傷性武器 冷兵器 軍刀 棍棒 鋼管 弓弩 恐怖襲擊 恐襲事件 炸學校 炸地鐵 炸政府 引爆炸彈 製造爆炸 縱火 自焚 自殘 跳樓 割腕 校園暴力 校園槍擊 暴恐分子 極端分子 恐怖分子 襲擊警察 駕車衝撞 劫持 人質事件 斬首 強制暴力 暴動 黑社會 幫派鬥爭 黑幫火拼 地下勢力 毒販火拼 走私武器 暴力催債 黑道 收保護費 恐嚇勒索 地下賭場 販毒集團 武裝分子 毒梟 武裝衝突 非法持槍 走私軍火 非法武裝 犯罪團伙 持械鬥毆 暴力集團 地下組織 地頭蛇 惡勢力 暴力洗錢

色情：
黃色 色情 淫穢 裸露 性交 成人電影 黃片 成人片 性愛 情色 裸照 自慰 亂交 群交 激情視頻 色情漫畫 裸舞 脫衣舞 性虐待 性騷擾 性交易 賣淫 嫖娼 A片 激情表演 裸聊 調情 性幻想 情欲 性高潮 床上運動 性伴侶 偷情 艷舞 性奴 性奴隸 性玩具 情趣用品 自慰器 肛交 口交 亂倫 強姦 猥褻 性侵 未成年人色情 幼女 幼男 裸照自拍 露陰癖 偷窺 色情網站 艷照門 性交錄像 色情小說 情色文學 性愛圖片 裸體藝術 成人遊戲 自慰視頻 激情電影 成人電影下載 性感 露點 爆乳 美乳 誘惑 性誘惑 性感內衣 色情服務 性按摩 性愛按摩 激情按摩 激情影院 裸露自拍 激情小說 性交錄像 色情直播 色情聊天 色情論壇 激情聊天室 色情表演 成人表演 性奴役 性虐 性交易市場 成人用品 性愛用品 性傳播疾病 性教育視頻 性暗示 性病 性騷擾舉報 色情廣告 賣春 嫖客 艷情 色情新聞 性交易廣告 性交廣告

政治：
專制制度 極權主義 威權政府 獨裁政權 民主制度 普世價值 議會制 多黨制 自由選舉 政黨壟斷 政教合一 思想控制 宣傳機器 選舉舞弊 一黨專政 顏色革命 網絡審查 政治迫害 政治清洗 政治異議 政治打壓 習近平 普京 金正恩 拜登 特朗普 澤連斯基 馬克龍 默克爾 盧卡申科 艾爾多安 塔利班 基地組織 伊斯蘭國 共产国际 北約 中共 美國國會 聯合國安理會 五眼聯盟 克格勃 台獨 港獨 藏獨 疆獨 南奧塞梯 克里米亞獨立 科索沃問題 巴勒斯坦建國 臺灣地位 香港自治 加泰羅尼亞獨立 庫爾德建國 東突厥斯坦 西藏人權 一國兩制破產 新疆集中營 朝鮮核問題 南海主權 南北韓統一 中國威脅論 顏色革命 茉莉花革命 阿拉伯之春 香港反送中 烏克蘭戰爭 六四事件 天安門屠殺 俄烏衝突 巴以衝突 緬甸政變 敘利亞內戰 伊朗抗議 白紙運動 民主遊行 軍政府 國家暴力 警察鎮壓 政治犯 異見人士 媒體封鎖 經濟制裁 政權更迭 人權干涉 聯合國制裁 外交孤立 國際制裁名單 凍結資產 驅逐外交官 制裁名單 外國代理人法 大國博弈 霸權主義 冷戰思維 干涉內政 和平演變 民主輸出 顏色革命干預 選舉操縱 境外敵對勢力 境外勢力操控

粗俗辱骂:
傻逼 二逼 蠢貨 變態 畜生 狗東西 王八蛋 滾蛋 腦殘 死媽 賤人 死逼 媽的 操你媽 狗娘養的 奶奶的 操蛋 鳥人 傻瓜 弱智 白癡 你媽死了 奶奶個腿 賤貨 爛人 神經病 死鬼 臭婊子 賤逼 笨蛋 小三 老婊子 淫婦 狗屎 屎一樣的人 狗雜種 死光吧 死全家 操你全家 日你媽 賤骨頭 母狗 公狗 狗屁 狗崽子 畜牲不如 草泥馬 滾犢子 死變態 操你祖宗 爛貨 畸形兒 狗臉 死丫頭 敗類 你算個屁 喪家犬 蟑螂 爛仔 垃圾人 不男不女 下賤 淫賤 死胖子 猥瑣男 騷逼 死瘸子 賤男 壞種 爛逼 撅你 狗改不了吃屎 騷貨 死佬 下流胚 骨灰都揚了 生兒子沒屁眼 殺千刀的 龜兒子 操你爹 媽賣批 你妹 日了狗 瘪三 賤民 小畜生 死鬼子 奴才 狗日的 畜牲玩意 墳頭冒煙 撅腚 狗日玩意 死變態 你全家癌 操穿你媽 醜八怪 雞巴臉 臭不要臉 賤種
英文：
Religion:
Cult, superstition, religious destruction, Falun Gong, holy war, terror doctrines, extremist religion, religious war, religious persecution, sectarian conflict, religious extremists, heresy, blasphemy, charlatan, sect conflict, desecration of holy objects, doctrine distortion, religious brainwashing, religious extremism, sect struggle, religious extremists, religious fanaticism, cult leader, violent believers, church controversy, doctrinal errors, false prophet, religious superstition, anti-religion, church destruction, temple destruction, religious schism, religious violence, religious unrest, believer conflict, evil spirit, theocracy, heretics, persecution of believers, religious extremists, charlatan cult, demon cult, worship superstition, saint desecration, sect conflict, doctrine tampering, faith persecution, anti-church, religious dictatorship, religious terrorism, holy war, heresy trial, religious cleansing, religious court, extremist religious organizations, religious radicals, sect violence, religious extremist violence, religious heresy, desecration of the Bible, desecration of Buddha statues, desecration of deities, religious persecution incidents, believer suicide, religious extremist terror, religious extremist attacks, religious riots, theological errors, false religion, religious superstition activities, anti-religious propaganda, extremist religious doctrines, evil spirits haunting, religious heresy, religious violence incidents, saint attacks, heretical doctrines, religious censorship, religious terror attacks, religious persecution policies, religious extremist individuals, doctrine distortion, sect conflict incidents, believer radicalization, church disputes, extremist religious activities, religious persecution acts, doctrinal fallacies, religious violence conflicts, believer persecution incidents, religious extremist terrorists, anti-religious propaganda, cult organizations, religious fallacies and heresies, extremist doctrine spread, religious radical forces, religious violent attacks, religious persecution phenomena, extremist church members, religious extremists, religious extremist terrorists, religious violence incidents, cult members, sect riots, religious extremist forces, religious riot incidents, extremist doctrine organizations.

Violence:
Beating, assault, hacking, murder, torture, violence, beating up, slapping, violent resistance to law enforcement, group fighting, assassination, homicide, throat cutting, headshot, dismemberment, massacre, strangulation, lynching, execution, brawling, gang fight, pursuit killing, cruelty, violent threats, brutal violence, shooting, gunfire, shooting to kill, knife, machete, dagger, handgun, rifle, machine gun, bomb, explosives, gasoline bomb, homemade bomb, rocket launcher, homemade gun, dynamite pack, military weapons, ammunition, arsenal, lethal weapons, cold weapons, military knife, club, steel pipe, crossbow, terrorist attack, terror event, school bombing, subway bombing, government bombing, bomb detonation, explosion manufacturing, arson, self-immolation, self-harm, jumping off building, wrist cutting, campus violence, campus shooting, violent extremists, extremists, terrorists, attack on police, vehicular attack, hijacking, hostage incident, beheading, forced violence, riot, gangsters, gang fights, underground forces, drug dealer fights, arms smuggling, violent debt collection, mafia, protection fee collection, intimidation and extortion, underground casino, drug trafficking group, armed militants, drug lords, armed conflict, illegal firearms, arms smuggling, illegal armed forces, criminal gangs, armed brawls, violent groups, underground organizations, local gang leaders, evil forces, violent money laundering.

Pornography:
Pornographic, obscene, nudity, sexual intercourse, adult movies, porn films, adult videos, sexual love, erotic, nude photos, masturbation, group sex, orgy, passion videos, porn comics, nude dance, striptease, sexual abuse, sexual harassment, sex trade, prostitution, soliciting, A-level porn, passionate shows, nude chat, flirting, sexual fantasies, lust, orgasm, bedroom activity, sexual partner, affairs, erotic dance, sex slaves, sexual slaves, sex toys, adult products, masturbators, anal sex, oral sex, incest, rape, molestation, sexual assault, child pornography, underage girls, underage boys, nude selfies, exhibitionism, voyeurism, porn websites, nude photo scandals, sex videos, porn novels, erotic literature, sex images, nude art, adult games, masturbation videos, passion movies, adult movie downloads, sexy, exposed points, big breasts, beautiful breasts, temptation, sexual seduction, sexy lingerie, porn services, sexual massage, love massage, passionate massage, erotic cinema, nude selfies, passion novels, sex videos, porn live streaming, porn chat, porn forums, passion chat rooms, porn performances, adult performances, sexual slavery, sexual violence, sex trade market, adult supplies, sexual health products, sexually transmitted diseases, sex education videos, sexual hints, sexual diseases, sexual harassment reports, porn ads, prostitution, clients, erotic, porn news, sex trade ads, sex ads.

Politics:
Authoritarian system, totalitarianism, authoritarian government, dictatorship, democracy, universal values, parliamentary system, multi-party system, free elections, party monopoly, theocracy, thought control, propaganda machine, election fraud, one-party dictatorship, color revolution, internet censorship, political persecution, political purge, political dissent, political suppression, Xi Jinping, Putin, Kim Jong-un, Biden, Trump, Zelensky, Macron, Merkel, Lukashenko, Erdogan, Taliban, Al-Qaeda, ISIS, Comintern, NATO, CCP, US Congress, UN Security Council, Five Eyes alliance, KGB, Taiwan independence, Hong Kong independence, Tibet independence, Xinjiang independence, South Ossetia, Crimea independence, Kosovo issue, Palestine statehood, Taiwan status, Hong Kong autonomy, Catalonia independence, Kurdish statehood, East Turkestan, Tibet human rights, failure of One Country Two Systems, Xinjiang internment camps, North Korea nuclear issue, South China Sea sovereignty, North-South Korea unification, China threat theory, color revolution, Jasmine Revolution, Arab Spring, Hong Kong Anti-Extradition, Ukraine war, June 4th Incident, Tiananmen massacre, Russia-Ukraine conflict, Israeli-Palestinian conflict, Myanmar coup, Syrian civil war, Iran protests, White Paper Movement, democratic marches, military government, state violence, police suppression, political prisoners, dissidents, media blockade, economic sanctions, regime change, human rights intervention, UN sanctions, diplomatic isolation, international sanctions list, frozen assets, diplomat expulsion, sanctions list, Foreign Agent Law, great power rivalry, hegemonism, Cold War mindset, interference in internal affairs, peaceful evolution, democracy export, color revolution intervention, election manipulation, hostile foreign forces, foreign influence control.

Profane insults:
fuck, shit, asshole, bitch, bastard, dick, pussy, cunt, motherfucker, son of a bitch, dumbass, jackass, douchebag, prick, slut, whore, twat, cock, wanker, jerk, douche, retard, moron, idiot, dumbfuck, shithead, fuckface, asshat, scumbag, shitbag, dickhead, fucktard, nutjob, airhead, skank, tramp, hoe, dipshit, butthead, asswipe, pisshead, bitchass, tool, loser, freak, twit, screw you, suck my dick, eat shit, kiss my ass, go to hell, fuck off, shut the fuck up, damn you, dickwad, crackhead, nutcase, shitface, fuckwit, arsehole, bollocks, bugger, bloody hell, slag, chode, ballsack, fuckboy, cocksucker, dickless, ball-licker, asslicker, cumdumpster, cumslut, manwhore, shitstain, twatwaffle, shitlord, knobhead, bellend, piss off, arsewipe, fuckbrain, cockwomble, shitbreath, bastardface, dumbshit, hellspawn, fucker, shitfaced, scrotum, slutbag, buttface, fuckhead, retarded fuck, cumbucket, dickbreath, anuslicker, bitchface, cumface
"""

tools = [Tool.from_function(name="TavilySearch",func=TavilySearch(max_retries=2),description="搜索引擎")]

def searchTools():
    explanations = []
    agent = initialize_agent(tools=tools,llm=LLMFactory.getDefaultOPENAI(),agent=AgentType.OPENAI_FUNCTIONS)
    for word in SENSITIVE_WORDS:
        prompt = f"请根据“{word}”一词在敏感词过滤系统中的含义 进行衍生出对应的类型的敏感词。衍生出10-20个敏感词"
        explanation = agent.invoke(prompt)
        explanations.append(f"{word}：{explanation}")

    return explanations

#对上面的敏感词进行重新生成
#参考定义的类型进行扩展
def extend_SENSITIVE_WORDS(words):
    pro = PromptTemplate(
        template="""你是一个内容审核助手，下面是一组敏感词，请根据这些词的语义、类型、含义，推测并补充更多相关或衍生的敏感词汇，便于后续在敏感内容过滤中使用。

    【要求】
    1. 衍生词应尽可能多地覆盖：近义词、同义表达、拼音谐音、网络用语、英文缩写等；
    2. 保持同类词一组；
    3. 返回格式为纯字符串，使用英文逗号 `,` 分隔，例如：
    词组1,词组1变体1,词组1变体2,...,词组2,词组2变体1,...

    请基于以下敏感词进行扩展：

    {words}
    """,
        input_variables=["words"]
    )
    chain = pro | LLMFactory.getDefaultOPENAI()|StrOutputParser()
    return chain.invoke({"words": words})

def auto_extend_sensitive_words():
    extended = extend_SENSITIVE_WORDS(SENSITIVE_WORDS)
    # 可选：将字符串转换为列表
    new_words = [word.strip() for word in extended.split(",") if word.strip()]
    full_set = list(set(SENSITIVE_WORDS + new_words))
    return full_set

def fallback_task(state: AgentState) -> AgentState:
    """
    当多次尝试识别用户意图失败后触发 fallback，提示用户重新表达或寻求人类帮助。
    """
    print("[Fallback] 已达到最大尝试次数，仍未识别意图，进入兜底处理。")

    FALLBACK_PROMPT = """
    你是一个区块链助手，擅长根据用户输入推测用户的真实意图，并引导用户更清晰地表达需求。
    当前系统已经尝试多次识别用户意图但仍未能理解，请你根据以下用户输入和敏感词库，推测用户可能想做的区块链相关操作。
     
    【敏感词库】：
    {sens_words}
    

    请输出一段简洁且友好的自然语言提示，引导用户补充信息或明确意图。不要说“我不确定”、“我不理解”，而是大胆地推测并温和地引导。

    用户输入如下：
    "{user_input}"
    
    请严格按照以下规则输出（不要额外说明）：

【规则】
1. 如果用户输入相关的语义和敏感词库相符合，则固定输出：
   Hello, the issue you mentioned may involve sensitive terms, and therefore we are unable to provide an answer. If you have any other questions, please feel free to let me know, and I will be happy to assist you.

2. 如果用户输入是乱码或无法理解（如 Case 1），则输出：
   Hello, I noticed that the issue you mentioned might have some input or formatting errors, which caused the content to be unclear. If possible, please verify or provide additional information, and I will assist you right away.

3. 如果以上两种情况都不满足，请推测用户可能的区块链意图，并输出一句简洁、自然、人性化的引导语。
  
4. 返回语言应使用 {language} 所指定的语言 

    
    
Case 1 – Unclear Input:
   Input:  283y2y438y243y4r4gr74gr734rg4r234r  
   Output: Hello, I noticed that the issue you mentioned might have some input or formatting errors, which caused the content to be unclear. If possible, please verify or provide additional information, and I will assist you right away.
   
Case 2 – Sensitive Terms:
Input: 特朗普  
Output:Hello, the issue you mentioned may involve sensitive terms, and therefore we are unable to provide an answer. If you have any other questions, please feel free to let me know, and I will be happy to assist you.   

    """

    data = {}
    llm = LLMFactory.getDefaultOPENAI()
    p = PromptTemplate(
        template=FALLBACK_PROMPT,
        input_variables=["user_input","language","sens_words"],
    )
    chain = p | llm | StrOutputParser()
    response = chain.invoke({"user_input": state.user_input,"language":state.langguage,"sens_words":SENSITIVE_WORDS})
    data["description"] = response
    data["intent"] = "fallback"

    return state.copy(update={"result": data})
