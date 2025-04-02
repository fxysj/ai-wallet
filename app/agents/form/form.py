from typing import List, Optional, Dict, Union, Any


class AccountWithChain:
    def __init__(self, id: str, address: str, chainId: int):
        self.id = id
        self.address = address
        self.chainId = chainId


class IntentType:
    SEND = 'send'
    RECEIVE = 'receive'
    SWAP = 'swap'
    BUY = 'buy'
    DEEP_RESEARCH = 'deep research'
    ACCOUNT_ANALYSIS = 'account analysis'
    NEWSLETTER = 'newsletter'
    UNCLEAR = 'unclear'


class SendForm:
    def __init__(self, chainId: str, fromAddress: str, toAddress: str, amount: str, tokenAddress: Optional[str],
                 slippage: float, rawTx: Optional[str] = None, signedTx: Optional[str] = None):
        self.chainId = chainId
        self.fromAddress = fromAddress
        self.toAddress = toAddress
        self.amount = amount
        self.tokenAddress = tokenAddress
        self.slippage = slippage
        self.rawTx = rawTx
        self.signedTx = signedTx


class ReceiveForm:
    pass


class SwapForm:
    def __init__(self, fromTokenAddress: str, fromChain: str, fromAddress: str, toTokenAddress: str,
                 toChain: str, toAddress: str, amount: float, slippage: float, disableEstimate: bool,
                 signedTx: Optional[str] = None):
        self.fromTokenAddress = fromTokenAddress
        self.fromChain = fromChain
        self.fromAddress = fromAddress
        self.toTokenAddress = toTokenAddress
        self.toChain = toChain
        self.toAddress = toAddress
        self.amount = amount
        self.slippage = slippage
        self.disableEstimate = disableEstimate
        self.signedTx = signedTx


class BuyForm:
    def __init__(self, chainId: str, cryptoToken: str, amount: float, fiatCurrency: str, paymentMethod: str):
        self.chainId = chainId
        self.cryptoToken = cryptoToken
        self.amount = amount
        self.fiatCurrency = fiatCurrency
        self.paymentMethod = paymentMethod


class ResearchForm:
    def __init__(self, query: str, depth: int, mode: str, selectedProject: dict):
        self.query = query
        self.depth = depth
        self.mode = mode
        self.selectedProject = selectedProject


class AnalysisForm:
    def __init__(self, account: List[AccountWithChain]):
        self.account = account


class NewsletterForm:
    def __init__(self, timeframe: str):
        self.timeframe = timeframe


class TaskState:
    SEND_TASK_NEED_MORE_INFO = 'SEND_TASK_NEED_MORE_INFO'
    SEND_TASK_READY_TO_SIGN = 'SEND_TASK_READY_TO_SIGN'
    SEND_TASK_SIGNED = 'SEND_TASK_SIGNED'
    SEND_TASK_BROADCASTED = 'SEND_TASK_BROADCASTED'
    SEND_TASK_READY_TO_BROADCAST='SEND_TASK_READY_TO_BROADCAST'
    SEND_TASK_FAILED = 'SEND_TASK_FAILED'
    SEND_TASK_CANCELLED = 'SEND_TASK_CANCELLED'

    RECEIVE_TASK_NEED_MORE_INFO = 'RECEIVE_TASK_NEED_MORE_INFO'
    RECEIVE_TASK_SHOULD_DISPLAY_QR_CODE = 'RECEIVE_TASK_SHOULD_DISPLAY_QR_CODE'

    SWAP_TASK_NEED_MORE_INFO = 'SWAP_TASK_NEED_MORE_INFO'
    SWAP_TASK_READY_TO_SIGN = 'SWAP_TASK_READY_TO_SIGN'
    SWAP_TASK_SIGNED = 'SWAP_TASK_SIGNED'
    SWAP_TASK_BROADCASTED = 'SWAP_TASK_BROADCASTED'
    SWAP_TASK_READY_TO_BROADCAST = 'SWAP_TASK_READY_TO_BROADCAST'
    SWAP_TASK_FAILED = 'SWAP_TASK_FAILED'
    SWAP_TASK_CANCELLED = 'SWAP_TASK_CANCELLED'

    BUY_TASK_NEED_MORE_INFO = 'BUY_TASK_NEED_MORE_INFO'
    BUY_TASK_EXECUTED = 'BUY_TASK_EXECUTED'
    BUY_TASK_FAILED = 'BUY_TASK_FAILED'
    BUY_TASK_CANCELLED = 'BUY_TASK_CANCELLED'

    RESEARCH_TASK_NEED_MORE_INFO = 'RESEARCH_TASK_NEED_MORE_INFO'
    RESEARCH_TASK_DISPLAY_PROMPTED_PROJECT = 'RESEARCH_TASK_DISPLAY_PROMPTED_PROJECT'
    RESEARCH_TASK_DISPLAY_RESEARCH = 'RESEARCH_TASK_DISPLAY_RESEARCH'

    NEWSLETTER_TASK_NEED_MORE_INFO = 'NEWSLETTER_TASK_NEED_MORE_INFO'
    NEWSLETTER_TASK_DISPLAY_NEWSLETTER = 'NEWSLETTER_TASK_DISPLAY_NEWSLETTER'

    ANALYSIS_TASK_NEED_MORE_INFO = 'ANALYSIS_TASK_NEED_MORE_INFO'
    ANALYSIS_TASK_DISPLAY_ANALYSIS = 'ANALYSIS_TASK_DISPLAY_ANALYSIS'

    GENERAL_TASK_DISPLAY_GENERAL_ASSISTANCE = 'GENERAL_TASK_DISPLAY_GENERAL_ASSISTANCE'


class MissingField:
    def __init__(self, name: str, type_: str, description: str):
        self.name = name
        self.type = type_
        self.description = description


class BaseTaskResult:
    def __init__(self, success: bool, message: str, promptedAction: Optional[List[str]] = None,
                 confidence: float = 0.0, alternatives: Optional[List[str]] = None):
        self.success = success
        self.message = message
        self.promptedAction = promptedAction
        self.confidence = confidence
        self.alternatives = alternatives


class TransactionResult:
    def __init__(self, status: str, txHash: Optional[str] = None, errorMessage: Optional[str] = None):
        self.status = status
        self.txHash = txHash
        self.errorMessage = errorMessage


class SendTaskData:
    def __init__(
            self,
            intent: str,
            state: str,
            form: SendForm,
            missingFields: Optional[List[MissingField]] = None,
            transactionResult: Optional[TransactionResult] = None,
            timestamp: Optional[str] = None
    ):
        self.intent = intent
        self.state = state
        self.form = form
        self.missingFields = missingFields or []
        self.transactionResult = transactionResult
        self.timestamp = timestamp


class SendTaskResult(BaseTaskResult):
    def __init__(self, success: bool, message: str, data: SendTaskData):
        super().__init__(success, message)
        self.data = data


class ReceiveTaskData:
    def __init__(
            self,
            intent: str,
            state: str,
            form: ReceiveForm,
            missingFields: Optional[List[MissingField]] = None
    ):
        self.intent = intent
        self.state = state
        self.form = form
        self.missingFields = missingFields or []


class ReceiveTaskResult(BaseTaskResult):
    def __init__(self, success: bool, message: str, data: ReceiveTaskData):
        super().__init__(success, message)
        self.data = data


class SwapResponse:
    def __init__(self, status: str, txHash: Optional[str] = None):
        self.status = status
        self.txHash = txHash


class StatusResponse:
    def __init__(self, status: str, message: str):
        self.status = status
        self.message = message


class QuoteResponse:
    def __init__(self, price: float, source: str):
        self.price = price
        self.source = source


class SwapTaskData:
    def __init__(
            self,
            intent: str,
            state: str,
            form: SwapForm,
            missingFields: Optional[List[MissingField]] = None,
            quoteResult: Optional[QuoteResponse] = None,
            swapResult: Optional[SwapResponse] = None,
            swapStatus: Optional[StatusResponse] = None
    ):
        self.intent = intent
        self.state = state
        self.form = form
        self.missingFields = missingFields or []
        self.quoteResult = quoteResult
        self.swapResult = swapResult
        self.swapStatus = swapStatus


class SwapTaskResult(BaseTaskResult):
    def __init__(self, success: bool, message: str, data: SwapTaskData):
        super().__init__(success, message)
        self.data = data


class BuyTaskData:
    def __init__(self, intent: str, state: str, form: BuyForm,
                 missingFields: Optional[List[MissingField]] = None, quoteResult: Optional[Any] = None):
        self.intent = intent
        self.state = state
        self.form = form
        self.missingFields = missingFields if missingFields is not None else []
        self.quoteResult = quoteResult


class BuyTaskResult(BaseTaskResult):
    def __init__(self, success: bool, message: str, data: BuyTaskData):
        super().__init__(success, message)
        self.data = data


class Project:
    def __init__(self, introduce: str, name: str, logo: str, rootdataurl: str, id: int, type_: int):
        self.introduce = introduce
        self.name = name
        self.logo = logo
        self.rootdataurl = rootdataurl
        self.id = id
        self.type = type_


class Overview:
    def __init__(self, logo: str, name: str, tldr: str, funFacts: str, sentimentIndicator: str, overallRating: str):
        self.logo = logo #项目 logo 的 URL
        self.name = name
        self.tldr = tldr
        self.funFacts = funFacts
        self.sentimentIndicator = sentimentIndicator
        self.overallRating = overallRating


class Ratings:
    def __init__(self, risk: str, volatility: str, marketCap: str, liquidity: str, age: str, community: str,
                 developerActivity: str, twitterFollowers: str, telegramSubscribers: str, redditSubscribers: str,
                 websiteTraffic: str):
        self.risk = risk
        self.volatility = volatility
        self.marketCap = marketCap
        self.liquidity = liquidity
        self.age = age
        self.community = community
        self.developerActivity = developerActivity
        self.twitterFollowers = twitterFollowers
        self.telegramSubscribers = telegramSubscribers
        self.redditSubscribers = redditSubscribers
        self.websiteTraffic = websiteTraffic


class RecentEvents:
    def __init__(self, unlock: Optional[str] = None, launch: Optional[str] = None,
                 airdrop: Optional[str] = None, hackathon: Optional[str] = None,
                 meetup: Optional[str] = None, conference: Optional[str] = None):
        self.unlock = unlock
        self.launch = launch
        self.airdrop = airdrop
        self.hackathon = hackathon
        self.meetup = meetup
        self.conference = conference


class ResearchTaskDetails:
    def __init__(self, rootDataResult: Any, history: str, takeaways: List[str], ratings: Ratings, overallRating: str,
                 recommendedStrategy: str, recentEvents: RecentEvents, conclusions: Optional[List[str]] = None,
                 references: Optional[List[str]] = None, relatedTopics: Optional[List[str]] = None):
        self.rootDataResult = rootDataResult
        self.recentEvents = recentEvents if recentEvents else {}
        self.history = history
        self.takeaways = takeaways
        self.conclusions = conclusions if conclusions else []
        self.ratings = ratings
        self.overallRating = overallRating
        self.recommendedStrategy = recommendedStrategy
        self.references = references if references else []
        self.relatedTopics = relatedTopics if relatedTopics else []


class ResearchTaskData:
    def __init__(self, intent: IntentType, state: TaskState, form: ResearchForm,
                 missingFields: Optional[List[MissingField]] = None, promptedProject: List[Project] = None,
                 overview: Overview = None, details: ResearchTaskDetails = None):
        self.intent = intent
        self.state = state
        self.form = form
        self.missingFields = missingFields if missingFields is not None else []
        self.promptedProject = promptedProject if promptedProject is not None else []
        self.overview = overview
        self.details = details


class ResearchTaskResult(BaseTaskResult):
    def __init__(self, success: bool, message: str, data: ResearchTaskData):
        super().__init__(success, message)
        self.data = data


class NewsItem:
    def __init__(self, title: str, summary: str, url: Optional[str] = None,
                 source: Optional[str] = None, published: Optional[str] = None):
        self.title = title
        self.summary = summary
        self.url = url
        self.source = source
        self.published = published


class NewsletterTaskData:
    def __init__(self, intent: str, state: str, form: NewsletterForm,
                 missingFields: Optional[List[MissingField]] = None, newsletter: List[NewsItem] = None):
        self.intent = intent
        self.state = state
        self.form = form
        self.missingFields = missingFields if missingFields is not None else []
        self.newsletter = newsletter if newsletter is not None else []


class NewsletterTaskResult(BaseTaskResult):
    def __init__(self, success: bool, message: str, data: NewsletterTaskData):
        super().__init__(success, message)
        self.data = data


class TotalBalance:
    def __init__(self, value: str, trend: float, comparisonPercentile: float):
        self.value = value
        self.trend = trend
        self.comparisonPercentile = comparisonPercentile


class AccountHealth:
    def __init__(self, score: int, grade: str, riskProfile: str, diversificationScore: int):
        self.score = score
        self.grade = grade
        self.riskProfile = riskProfile
        self.diversificationScore = diversificationScore


class ActivitySnapshot:
    def __init__(self, level: str, accountAgeDays: int, accountAgePercentile: int,
                 weeklyTransactions: int, blockchainsUsed: List[str]):
        self.level = level
        self.accountAge = {'days': accountAgeDays, 'percentile': accountAgePercentile}
        self.weeklyTransactions = weeklyTransactions
        self.blockchainsUsed = blockchainsUsed



class EnhancedAnalysisTaskOverview:
    def __init__(self, totalBalance: TotalBalance, accountHealth: AccountHealth,
                 activitySnapshot: ActivitySnapshot):
        self.totalBalance = totalBalance
        self.accountHealth = accountHealth
        self.activitySnapshot = activitySnapshot


class Achievement:
    def __init__(self, id: str, title: str, description: str, unlockedAt: str, rarity: str,
                 icon: str, socialShareImage: Optional[str] = None):
        self.id = id
        self.title = title
        self.description = description
        self.unlockedAt = unlockedAt
        self.rarity = rarity
        self.icon = icon
        self.socialShareImage = socialShareImage


class Performance:
    def __init__(self, percentChange24h: float, percentChange7d: float, entryPosition: str):
        self.percentChange24h = percentChange24h
        self.percentChange7d = percentChange7d
        self.entryPosition = entryPosition


class TokenHolding:
    def __init__(self, token: str, symbol: str, logo: str, balance: str, value: str, allocation: str,
                 performance: Performance, riskLevel: str, tooltip: Optional[str] = None):
        self.token = token
        self.symbol = symbol
        self.logo = logo
        self.balance = balance
        self.value = value
        self.allocation = allocation
        self.performance = performance
        self.riskLevel = riskLevel
        self.tooltip = tooltip


class DAppUsage:
    def __init__(self, name: str, logo: str, usageCount: int, category: str):
        self.name = name
        self.logo = logo
        self.usageCount = usageCount
        self.category = category


class RecentTransaction:
    def __init__(self, hash: str, type_: str, description: str, value: str, timestamp: str, gasUsed: str):
        self.hash = hash
        self.type = type_
        self.description = description
        self.value = value
        self.timestamp = timestamp
        self.gasUsed = gasUsed


class TransactionHistory:
    def __init__(self, count: int, frequency: str, gasSavings: str, mostUsedDApps: List[DAppUsage],
                 recentTransactions: List[RecentTransaction]):
        self.count = count
        self.frequency = frequency
        self.gasSavings = gasSavings
        self.mostUsedDApps = mostUsedDApps
        self.recentTransactions = recentTransactions


class NextLevelGoalStep:
    def __init__(self, label: str, completed: bool, tooltip: Optional[str] = None):
        self.label = label
        self.completed = completed
        self.tooltip = tooltip


class NextLevelGoal:
    def __init__(self, id: str, title: str, description: str, difficulty: str, progress: int, reward: str,
                 steps: List[NextLevelGoalStep]):
        self.id = id
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.progress = progress
        self.reward = reward
        self.steps = steps


class Insight:
    def __init__(self, title: str, description: str, iconType: str, actionable: bool,
                 actionText: Optional[str] = None,
                 actionUrl: Optional[str] = None, relatedMetric: Optional[str] = None):
        self.title = title
        self.description = description
        self.iconType = iconType
        self.actionable = actionable
        self.actionText = actionText
        self.actionUrl = actionUrl
        self.relatedMetric = relatedMetric


class SocialShareOptions:
    def __init__(self, portfolioCard: str, achievementCards: List[str], accountAgeCard: str, customText: str):
        self.portfolioCard = portfolioCard
        self.achievementCards = achievementCards
        self.accountAgeCard = accountAgeCard
        self.customText = customText



# class EnhancedAnalysisTaskDetail:
#     def __init__(self,tokenHoldings:TokenHolding,performance:Performance,):

class EnhancedAnalysisTaskData:
    def __init__(self, intent: str, state: str, form: AnalysisForm,
                 missingFields: Optional[List[MissingField]] = None, overview: EnhancedAnalysisTaskOverview = None,
                 achievements: List[Achievement] = None, details: Optional[dict] = None,
                 socialShareOptions: SocialShareOptions = None):
        self.intent = intent
        self.state = state
        self.form = form
        self.missingFields = missingFields if missingFields is not None else []
        self.overview = overview
        self.achievements = achievements if achievements is not None else []
        self.details = details if details is not None else {}
        self.socialShareOptions = socialShareOptions


class EnhancedAnalysisTaskResult(BaseTaskResult):
    def __init__(self, success: bool, message: str, data: EnhancedAnalysisTaskData):
        super().__init__(success, message)
        self.data = data


class AnalysisTaskOverview:
    def __init__(self, totalBalance: str, accountAge: str, activityLevel: str, riskProfile: Optional[str] = None):
        self.totalBalance = totalBalance
        self.accountAge = accountAge
        self.activityLevel = activityLevel
        self.riskProfile = riskProfile


class AnalysisTaskTokenHolding:
    def __init__(self, token: str, balance: str, value: Optional[str] = None, allocation: Optional[str] = None):
        self.token = token
        self.balance = balance
        self.value = value
        self.allocation = allocation


class AnalysisTaskTransactionHistory:
    def __init__(self, count: int, averageValue: Optional[str] = None, frequency: Optional[str] = None,
                 recentTransactions: Optional[List[Any]] = None):
        self.count = count
        self.averageValue = averageValue
        self.frequency = frequency
        self.recentTransactions = recentTransactions if recentTransactions is not None else []


class AnalysisTaskInvestmentAdvice:
    def __init__(self, riskAssessment: Optional[str] = None, diversificationSuggestions: Optional[List[str]] = None,
                 opportunityAreas: Optional[List[str]] = None):
        self.riskAssessment = riskAssessment
        self.diversificationSuggestions = diversificationSuggestions if diversificationSuggestions is not None else []
        self.opportunityAreas = opportunityAreas if opportunityAreas is not None else []


class AnalysisTaskDetails:
    def __init__(self,
                 tokenHoldings: Optional[List[AnalysisTaskTokenHolding]] = [],
                 transactionHistory: Optional[AnalysisTaskTransactionHistory] = {},
                 investmentAdvice: Optional[AnalysisTaskInvestmentAdvice] = {},
                 ):
        self.tokenHoldings = tokenHoldings if tokenHoldings is not None else []
        self.transactionHistory = transactionHistory
        self.investmentAdvice = investmentAdvice


class AnalysisTaskData:
    def __init__(self, intent: str, state: str, form: AnalysisForm,
                 missingFields: Optional[List[MissingField]] = None, overview: Optional[AnalysisTaskOverview] = None,
                 details: Optional[AnalysisTaskDetails] = {}):
        self.intent = intent
        self.state = state
        self.form = form
        self.missingFields = missingFields if missingFields is not None else []
        self.overview = overview
        self.details = details if details is not None else {}


class AnalysisTaskResult(BaseTaskResult):
    def __init__(self, success: bool, message: str, data: AnalysisTaskData):
        super().__init__(success, message)
        self.data = data


class GeneralAssistantTaskData:
    def __init__(self, intent: str, state: str):
        self.intent = intent
        self.state = state


class GeneralAssistantTaskResult(BaseTaskResult):
    def __init__(self, success: bool, message: str, data: GeneralAssistantTaskData):
        super().__init__(success, message)
        self.data = data


TaskResult = Union[
    SendTaskResult,
    ReceiveTaskResult,
    SwapTaskResult,
    BuyTaskResult,
    ResearchTaskResult,
    NewsletterTaskResult,
    EnhancedAnalysisTaskResult,
    AnalysisTaskResult,
    GeneralAssistantTaskResult
]

if __name__ == '__main__':
    sendTaskData = SendTaskData()
    sendTaskData.intent = "send"
    print(sendTaskData)
    # sendTaskData = SendTaskData(
    #     intent=IntentType.SEND,
    #     state=TaskState.SEND_TASK_READY_TO_SIGN,
    #     form=SendForm(
    #         chainId="60",
    #         fromAddress="0x1234567890123456789012345678901234567890",
    #         toAddress="0x9876543210987654321098765432109876543210",
    #         amount="100",
    #         tokenAddress=None,
    #         slippage=0.5
    #     ),
    #     missingFields=[],
    #     transactionResult=TransactionResult(status="pending"),
    #     timestamp="2025-04-01T12:00:00Z"
    # )
    #
    # sendResult = SendTaskResult(
    #     success=True,
    #     message="Transaction ready to sign",
    #     data=sendTaskData
    # )
    #
    # print(sendResult.data.intent)
    # print(sendResult.data.form.amount)
    # print(TaskState.SEND_TASK_FAILED)
