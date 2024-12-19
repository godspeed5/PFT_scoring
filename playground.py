# create 50 numerical score responses on the same prompt and the same system prompt (that directs the model to output a single numeric score) using the openrouter api and plot the mean and variance of the responses.

import requests
import numpy as np
import matplotlib.pyplot as plt

# Configuration for OpenRouter API
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Define the system and user prompts
system_prompt = "You are a financial analyst. Provide a cost estimate as a number only (without commas) and nothing else."
# user_prompt = "VERIFICATION RESPONSE ___ AI tools useful to the family office: 1. ChatGPT for idea generation and problem solving, 2. Github Copliot for faster coding, 3. AlphaSense for AI & NLP related to financial data and news, 4. Validea for AI providing copy trading signals, and 5. Qplum for portfolio and risk management."
user_prompt = "Develop a compelling pitch deck to attract potential investors for your real estate ventures, including market analysis, financial projections, and unique selling points of your properties. .. 270"

# Function to call the OpenRouter API
def get_score():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "x-ai/grok-2-1212",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0
        # "temperature": 0
        # "temperature": 0.1,
    }

    response = requests.post(API_URL, headers=headers, json=data)
    response_json = response.json()

    # Extract the numeric score from the response
    try:
        score = float(response_json['choices'][0]['message']['content'].lstrip('$'))
        return score
    except (KeyError, ValueError):
        print("Error extracting score from response:", response_json)
        return None

# Generate scores by calling the API 50 times
scores = []
for i in range(50):
    print(f"Fetching score {i + 1}/50...")
    score = get_score()
    if score is not None:
        scores.append(score)
        print(score)
    # else:
    #     print("Skipping invalid score...")

# Calculate mean and variance
mean_score = np.mean(scores)
variance_score = np.var(scores)

# Plot the histogram of scores
plt.figure(figsize=(10, 6))
plt.hist(scores, bins=10, alpha=0.7, color='blue', edgecolor='black')
plt.axvline(mean_score, color='red', linestyle='dashed', linewidth=2, label=f'Mean: {mean_score:.2f}')
plt.title('Distribution of API Scores')
plt.xlabel('Score')
plt.ylabel('Frequency')
plt.legend()
plt.show()

# Print mean and variance
print(f"Mean: {mean_score:.2f}")
print(f"Variance: {variance_score:.2f}")



