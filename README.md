

### Chart Question Answering (CQA) Webapp

The CQA tool can be found here at [▶ CQA webapp](https://cqa.shrestha.club/). If the tool is not working, please follow the instructions below to run the project locally. You will need to have the openai api key to run the project locally.

# Instruction to run the project locally
    - Fork the repository 
    - Navigate to the project directory
    - Run the following command to create a virtual environment
        **In Linux/Unix:**
        - python3 -m venv cqa-venv
        - source cqa-venv/bin/activate
        - pip install -r requirements.txt
        - rename .env.example to .env and update the openai api key and SAVE
        - streamlit run webapp_demo.py
        
        **In Windows:**
        - python -m venv cqa-venv
        - cqa-venv\Scripts\activate
        - pip install -r requirements.txt
        - rename .env.example to .env and update the openai api key and SAVE
        - streamlit run webapp_demo.py
    
