import requests
import base64
from mistralai.client import MistralClient
import os

# Retrieve the API key from environment variables
api_key = os.environ["MISTRAL_API_KEY"]

# Specify model
model = "pixtral-12b-2409"

# Initialize the Mistral client
client = MistralClient(api_key=api_key)

# base64_image = getimages()

def getimages():
    # Calling API for random image
    img_url = 'https://picsum.photos/200'
                                    # Very temp TODO: Remove and debug
    img_data = requests.get(img_url, verify=False).content

    # Getting the base64 string
    # img_data_encoded = base64.b64encode(img_data).decode('utf-8')
    img_data_encoded = base64.b64encode(img_data)

    return img_data_encoded

def encodeimage(img_data):

    """
    Helper function to base64 encode and decode for AI processing
    """

    img_data= base64.b64encode(img_data.read())
    # print("From encodeimage() - encoded img_data is: ", img_data)

    return img_data

def decodeimage(img_data):

    # print("From decodeimage() - decoded img_data is: ", img_data.decode('utf-8'))

    return img_data.decode('utf-8')



def getproductdescription(image_data, prompt=None):

    # We'll send our own custom message prompt or default to this one
    message_data = prompt
    
    if not prompt:
        message_data = "Give me a short product description for this picture that is a title of 5-12 words."

    """Function that takes base64 utf-8 image data and returns an image description from Mistral's AI"""

    # Define the messages for the chat
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": message_data
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{image_data}" 
                }
            ]
        }
    ]

    # Get the chat response
    chat_response = client.chat.complete(
        model=model,
        messages=messages
    )

    # Print the content of the response and return as output
    print(chat_response.choices[0].message.content)

    output = chat_response.choices[0].message.content

    return output