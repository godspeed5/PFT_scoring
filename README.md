This repo uses LLMs to score transactions using the PFT currency on the XRP blockchain. 
Replace <API_KEY> with your OpenRouter key in ```playground.py``` and ```main.py```
Run the code for scoring last ```lim=350``` transactions (can be set in ```main.py```) on all PFT nodes using ```python main.py```
```playground.py``` is used to run example prompts with strictly numerical responses to study the output variance given the prompt at 0 temperature. 
