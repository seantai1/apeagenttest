"""Image detection tool for classifying images."""

import base64
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage


class ImageDetector:
    """Tool for detecting and classifying objects in images using multimodal LLM."""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        """Initialize the image detector with an LLM instance."""
        self.llm = llm
        
    def is_image_request(self, message_parts: list) -> bool:
        """
        Check if the message contains an image.
        
        Args:
            message_parts: List of message parts from the A2A message
            
        Returns:
            True if the message contains an image file
        """
        if not message_parts:
            return False
            
        # Check if any part has a file with image mime type
        for part in message_parts:
            if isinstance(part, dict) and part.get('kind') == 'file':
                file_info = part.get('file', {})
                mime_type = file_info.get('mimeType', '')
                if mime_type.startswith('image/'):
                    return True
        return False
    
    async def detect(self, text_prompt: str, image_data: Dict[str, Any]) -> str:
        """
        Detect and classify objects in an image.
        
        Args:
            text_prompt: The text prompt asking about the image
            image_data: Dictionary containing image file information
            
        Returns:
            The classification result
        """
        try:
            # Extract image data
            mime_type = image_data.get('mimeType', 'image/jpeg')
            base64_data = image_data.get('data', '')
            
            # Create system prompt for consistent classification
            system_prompt = """You are an image classification assistant. 
            When asked to identify animals or objects in images:
            1. Provide only the general category or class
            2. Use simple, common terms (e.g., "dog" not "golden retriever", "cat" not "persian cat")
            3. Answer with just the word, no extra text or punctuation
            4. If asked to choose between options (like "cat or dog"), answer with only one of those options
            
            Examples:
            Q: What animal is in this image? Please answer with just 'cat' or 'dog'.
            A: dog
            
            Q: What is this?
            A: car
            
            Q: Is this a cat or a dog?
            A: cat
            """
            
            # Format the message with both text and image
            # For Gemini, we need to format the image properly
            message_content = [
                {"type": "text", "text": system_prompt},
                {"type": "text", "text": text_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_data}"
                    }
                }
            ]
            
            # Create message for the model
            message = HumanMessage(content=message_content)
            
            # Get response from multimodal LLM
            response = await self.llm.ainvoke([message])
            
            # Extract and clean the answer
            answer = response.content.strip().lower()
            
            # If the prompt asks for cat or dog specifically, ensure we return one of those
            if 'cat' in text_prompt.lower() and 'dog' in text_prompt.lower():
                if 'cat' in answer:
                    return 'cat'
                elif 'dog' in answer:
                    return 'dog'
                else:
                    # Default to the answer if it's already one of them
                    if answer in ['cat', 'dog']:
                        return answer
            
            return answer
            
        except Exception as e:
            return f"Error detecting image: {str(e)}"