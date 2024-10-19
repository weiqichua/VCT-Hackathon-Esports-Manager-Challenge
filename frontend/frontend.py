import logging
import os
import streamlit as st
import boto3
import json

boto3.set_stream_logger('', logging.DEBUG)

## Note : Create a .streamlit folder in the main directory, then create a secrets.toml file inside.
    # Add the following lines to the secrets.toml file (keep quotation marks):
    # AWS_ACCESS_KEY_ID="<insert id here>"
    # AWS_SECRET_ACCESS_KEY="<insert key here>""
    # AWS_REGION="ap-northeast-1" 



def get_bedrock_response(user_input):

    try:
        client = boto3.client(
            'bedrock-runtime',
            region_name=st.secrets["AWS_REGION"],
            aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"]
        )

        # Specify the model ID for Claude Haiku 3.0
        model_id = 'anthropic.claude-3-haiku-20240307-v1:0' 

        formatted_prompt = f'Human: {user_input}\nAssistant:'

        # Prepare the request body with the prompt and parameters
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",  # Adjust as needed
            "max_tokens": 512,  # Adjust as needed
            "messages": [
                {"role": "user", "content": formatted_prompt}
            ]
        }).encode('utf-8')

        # Invoke the model
        response = client.invoke_model(
            modelId=model_id,
            contentType='application/json',
            accept='application/json',
            body=body
        )
# logging.debug(f"Raw response: {response}")

        # Read and decode the response
        response_body = response['body'].read().decode('utf-8')
# logging.debug(f"Decoded response body: {response_body}")

        result = json.loads(response_body)
# logging.debug(f"Parsed result: {result}")

        assistant_reply = ''.join([item.get('text', '') for item in result.get('content', [])]).strip()
# logging.debug(f"Extracted reply: {assistant_reply}")
        
        return assistant_reply

    except client.exceptions.ModelErrorException as e:
        st.error(f"Model error: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# Streamlit UI
st.title('VALORANT eSports Manager Chatbot')
st.write('Enter a prompt to receive a response from the chatbot.')

# Input field for user prompt
prompt = st.text_area('Your Prompt', height=200)

# Button to submit the prompt
if st.button('Submit'):
    if prompt.strip():
        with st.spinner('Processing...'):
            response = get_bedrock_response(prompt)
# st.write(f"Debug - Raw response: {response}")
            if response:
                st.subheader('Model Response:')
                st.markdown(response, unsafe_allow_html=True)
            else:
                st.error("Failed to receive a response. Please try again.")
    else:
        st.warning('Please enter a prompt before submitting.')