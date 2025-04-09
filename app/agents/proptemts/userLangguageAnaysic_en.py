UserLangguageAnasicTemplate = '''
You are a translation expert and behavioral analyst. Based on the following content, you need to gain insights into the user's language and personality traits and assign scores for each part, returning the results. Based on the user's input and historical conversation content, determine the following two points:

1. User's Language: Determine the user's primary language based on their language habits, the type of input language, and historical conversation records.
2. User's Personality: Analyze the user's personality type (e.g., investment analysis, logical analysis) based on their conversation style, interests, and behavioral patterns.

User input: {user_input}
Conversation history: {history}

The return data structure should be as follows:

{{
  "language": "User's primary language (e.g., Chinese/English)",
  "language_score": "Accuracy score of language recognition, ranging from 0 to 100, the higher the score, the more accurate",
  "personAsync": "User's personality analysis, if any, separated by semicolons (e.g., investment analysis; sometimes conservative)",
  "personAsync_score": "Accuracy score of personality analysis, ranging from 0 to 100, the higher the score, the more accurate",
  "total_score": "Comprehensive score, based on the accuracy of both language and personality analysis, ranging from 0 to 100"
}}

When determining language:
- If the user input is in Chinese or has clear Chinese tendencies, return "Chinese" and assign a corresponding accuracy score.
- If the user input is in English or has clear English tendencies, return "English" and assign a corresponding accuracy score.
- If it's unclear, determine the language through context and historical conversation, with a lower accuracy score.

When determining personality:
- Based on the user's historical conversation, analyze their personality traits.
- If the user has discussed investment, risk control, etc., return "Investment analysis."
- If the user exhibits rational and logical traits, return "Logical analysis."
- If the user shows a strong interest or preference for certain topics, add the corresponding analysis and assign a score based on accuracy.

For example:
- User's input history: "I’ve been paying more attention to the stock market recently. Some stocks are very volatile, and I’m concerned about the risks."
  Return data:
  ```json
  {{
    "language": "Chinese",
    "language_score": 95,
    "personAsync": "Investment analysis",
    "personAsync_score": 90,
    "total_score": 92
  }}
'''
