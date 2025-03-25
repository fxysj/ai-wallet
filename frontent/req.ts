import { TransactionResult } from "@/web3lib/core/KeyringController/types";
import { TransactionRequest } from "@ethersproject/abstract-provider";
import { tronTransferParams, solTransferParams, btcTransferParams } from "@/web3lib/core/wallet/types";
import { QuoteResponse, StatusResponse, SwapResponse } from "rango-sdk-basic";

type AccountWithChain = {
    id: string; // 唯一ID
    address: string;
    chainId: number;
  };


export enum PromptAction {

}

export type IntentType =
  | 'send'
  | 'receive'
  | 'swap'
  | 'buy'
  | 'deep research'
  | 'account analysis'
  | 'newsletter'
  | 'unclear';

// send card form data
export interface SendForm {
  chainId: string; // chain id, e.g. "60" for Ethereum, "56" for BSC, "195" for Tron, "501" for Solana
  fromAddress: string; // sender address, e.g. "0x1234567890123456789012345678901234567890"
  toAddress: string; // recipient address
  amount: string; // amount in string with decimals
  tokenAddress: string | null; // if null, it's a native token
  slippage: number; // slippage in number
  rawTx?: string; // if provided, it's a raw transaction
  signedTx?: string; // if provided, it's a signed transaction
}

// receive card form data
export interface ReceiveForm {
  myAddress: string;
  myChain: string;
}

// swap card form data
export interface SwapForm {
  fromTokenAddress: string; // from token address, e.g. "0x1234567890123456789012345678901234567890"
  fromChain: string; // from chain id, e.g. "60" for Ethereum, "56" for BSC, "195" for Tron, "501" for Solana
  fromAddress: string; // sender address, e.g. "0x1234567890123456789012345678901234567890"
  toTokenAddress: string; // to token address, e.g. "0x1234567890123456789012345678901234567890"
  toChain: string; // to chain id, e.g. "60" for Ethereum, "56" for BSC, "195" for Tron, "501" for Solana
  toAddress: string; // recipient address, e.g. "0x1234567890123456789012345678901234567890"
  amount: number; // amount in number
  slippage: number; // slippage in number
  disableEstimate: boolean;
  signedTx?: string;
}

// buy card form data
export interface BuyForm {
  chainId: string; // chain id, e.g. "60" for Ethereum, "56" for BSC, "195" for Tron, "501" for Solana
  cryptoToken: string; // crypto token, e.g. "BTC", "ETH", "USDT", "USDC"
  amount: number; // amount in number
  fiatCurrency: string; // fiat currency, e.g. "USD", "EUR", "CNY",
  paymentMethod:string
}

// research card form data
export interface ResearchForm {
  query: string; // topic, e.g. search keyword, which can be project/institution/bames, tokens, or related items
  depth: number; // depth, e.g. 1, 2, 3
  mode: string; // mode, e.g. "fast", "deep"
}

// analysis card form data
export interface AnalysisForm {
  account: AccountWithChain[] ; // wallet address, e.g. "0x1234567890123456789012345678901234567890"
}

// newsletter card form data
export interface NewsletterForm {
  timeframe: string; // timeframe, e.g. "daily", "weekly", "monthly"
  }

// task state
export enum TaskState {
  // Transaction actions
  SEND_TASK_NEED_MORE_INFO = 'SEND_TASK_NEED_MORE_INFO',
  SEND_TASK_READY_TO_SIGN = 'SEND_TASK_READY_TO_SIGN',
  SEND_TASK_SIGNED = 'SEND_TASK_SIGNED',
  SEND_TASK_BROADCASTED = 'SEND_TASK_BROADCASTED',
  SEND_TASK_FAILED = 'SEND_TASK_FAILED',
  SEND_TASK_CANCELLED = 'SEND_TASK_CANCELLED',

  // Receive actions
  RECEIVE_TASK_NEED_MORE_INFO = 'RECEIVE_TASK_NEED_MORE_INFO',
  RECEIVE_TASK_SHOULD_DISPLAY_QR_CODE = 'RECEIVE_TASK_SHOULD_DISPLAY_QR_CODE',

  // Swap actions
  SWAP_TASK_NEED_MORE_INFO = 'SWAP_TASK_NEED_MORE_INFO',
  SWAP_TASK_READY_TO_SIGN = 'SWAP_TASK_READY_TO_SIGN',
  SWAP_TASK_SIGNED = 'SWAP_TASK_SIGNED',
  SWAP_TASK_BROADCASTED = 'SWAP_TASK_BROADCASTED',
  SWAP_TASK_FAILED = 'SWAP_TASK_FAILED',
  SWAP_TASK_CANCELLED = 'SWAP_TASK_CANCELLED',

  // Buy actions
  BUY_TASK_NEED_MORE_INFO = 'BUY_TASK_NEED_MORE_INFO',
  BUY_TASK_EXECUTED = 'BUY_TASK_EXECUTED',
  BUY_TASK_FAILED = 'BUY_TASK_FAILED',
  BUY_TASK_CANCELLED = 'BUY_TASK_CANCELLED',

  // Research actions
  RESEARCH_TASK_NEED_MORE_INFO = 'RESEARCH_TASK_NEED_MORE_INFO',
  RESEARCH_TASK_DISPLAY_RESEARCH = 'RESEARCH_TASK_DISPLAY_RESEARCH',

  // Newsletter actions
  NEWSLETTER_TASK_NEED_MORE_INFO = 'NEWSLETTER_TASK_NEED_MORE_INFO',
  NEWSLETTER_TASK_DISPLAY_NEWSLETTER = 'NEWSLETTER_TASK_DISPLAY_NEWSLETTER',

  // Analysis actions
  ANALYSIS_TASK_NEED_MORE_INFO = 'ANALYSIS_TASK_NEED_MORE_INFO',
  ANALYSIS_TASK_DISPLAY_ANALYSIS = 'ANALYSIS_TASK_DISPLAY_ANALYSIS',

  // General actions
  GENERAL_TASK_DISPLAY_GENERAL_ASSISTANCE = 'GENERAL_TASK_DISPLAY_GENERAL_ASSISTANCE',

}

// Missing field definition for better type safety
export interface MissingField {
  name: string;
  type: string;
  description: string;
}


// Common properties shared by all tasks
export interface BaseTaskResult {
    success: boolean;
    message: string;
    promptedAction?: string[];
    confidence: number;
    alternatives?: string[];
  }

// Send transaction result - From preparation to broadcast
export interface SendTaskResult extends BaseTaskResult {
  data?: {
    intent: IntentType;
    state: TaskState;
    form: SendForm;
    missingFields?: MissingField[];
    transactionResult?: TransactionResult;
    timestamp?: string;
  };
}

// Receive task result
export interface ReceiveTaskResult extends BaseTaskResult {

  data?: {
    intent: IntentType;
    state: TaskState;
    form: ReceiveForm;
    missingFields?: MissingField[];
  };
}

// Swap task result
// check docs for more details: https://docs.rango.exchange/api-integration/basic-api-single-step/api-reference
export interface SwapTaskResult extends BaseTaskResult {
  data?: {
    intent: IntentType;
    state: TaskState;
    form: SwapForm;
    missingFields?: MissingField[];
    quoteResult?: QuoteResponse;
    swapResult?: SwapResponse;
    swapStatus?: StatusResponse
  };
}

// Buy task result
export interface BuyTaskResult extends BaseTaskResult {
  data?: {
    intent: IntentType;
    state: TaskState;
    form: BuyForm;
    missingFields?: MissingField[];
    quoteResult?: any;
  };
}

// Research task result - for deep research on crypto topics
export interface ResearchTaskResult extends BaseTaskResult {
  data?: {
    intent: IntentType;
    state: TaskState;
    form: ResearchForm;
    missingFields?: MissingField[];

    // project data from rootdata.com, paid api service
    project: Array<{
        introduce: string; // introduce of the project
        name: string; // name of the project
        logo: string; // logo of the project
        rootdataurl: string; // rootdata url of the project
        id: number; // id of the project
        type: number; // type of the project
      }>;

    overview: {
        logo: string;
        name: string;
        tldr: string;
        funFacts: string;
        sentimentIndicator: string;
        overallRating: string;
    };

    details: {
        rootDataResult: any; // data from rootdata.com, paid api service
        recentEvents:{
            unlock?: string;
            launch?: string;
            airdrop?: string;
            hackathon?: string;
            meetup?: string;
            conference?: string;
        },
        history: string;
        takeaways: string[];
        conclusions?: string[];
        ratings: {
            risk: string;
            volatility: string;
            marketCap: string;
            liquidity: string;
            age: string;
            community: string;
            developerActivity: string;
            twitterFollowers: string;
            telegramSubscribers: string;
            redditSubscribers: string;
            websiteTraffic: string;
        };
        overallRating: string;
        recommenededStrategy: string;
        references?: string[];
        relatedTopics?: string[];
    };
  };
}

export interface NewsItem {
  title: string;
  summary: string;
  content: string;
  url?: string;
  source?: string;
  published?: string;
}

// Newsletter task result - for daily crypto news updates
export interface NewsletterTaskResult extends BaseTaskResult {
  data?: {
    intent: IntentType;
    state: TaskState;
    form: NewsletterForm;
    missingFields?: MissingField[];
    newsletter: Array<NewsItem>;
  };
}

// Analysis task result - for wallet/account analysis
export interface AnalysisTaskResult extends BaseTaskResult {
  data?: {
    intent: IntentType;
    state: TaskState;
    form: AnalysisForm;
    missingFields?: MissingField[];
    overview?: {
        totalBalance: string;
        accountAge: string;
        activityLevel: string;
        riskProfile?: string;
        };
    details?:{
        tokenHoldings?: Array<{
            token: string;
            balance: string;
            value?: string;
            allocation?: string;
        }>;
        transactionHistory?: {
            count: number;
            averageValue?: string;
            frequency?: string;
            recentTransactions?: Array<any>;
        };
        investmentAdvice?: {
            riskAssessment?: string;
            diversificationSuggestions?: string[];
            opportunityAreas?: string[];
        };
    }

  };
}

// General Assistant task result - for general questions and unclear intents
export interface GeneralAssistantTaskResult extends BaseTaskResult {
    data?: {
        intent: IntentType;
        state: TaskState;
    };
}

// Union type for all possible results
export type TaskResult =
  | SendTaskResult
  | ReceiveTaskResult
  | SwapTaskResult
  | BuyTaskResult
  | ResearchTaskResult
  | NewsletterTaskResult
  | AnalysisTaskResult
  | GeneralAssistantTaskResult;