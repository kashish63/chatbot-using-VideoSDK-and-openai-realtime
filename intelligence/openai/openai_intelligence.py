import base64
import traceback
from typing import Dict, List, Union, Callable, Optional
from utils.struct.openai import (
    AudioFormats,
    ClientToServerMessage,
    EventType,
    InputAudioBufferAppend,
    InputAudioTranscription,
    ItemCreate,
    FunctionCallOutputItemParam,
    ResponseFunctionCallArgumentsDone,
    ServerVADUpdateParams,
    SessionUpdate,
    SessionUpdateParams,
    Voices,
    generate_event_id,
    to_json,
)
import json

from asyncio.log import logger
from asyncio import AbstractEventLoop
import aiohttp
import asyncio
from agent.audio_stream_track import CustomAudioStreamTrack

class OpenAIIntelligence:
    def __init__(
        self, 
        loop: AbstractEventLoop, 
        api_key,
        model: str = "gpt-4o-mini-realtime-preview-2024-12-17",
        instructions="""\
            Actively listen to the user's questions and provide concise, relevant responses. 
            You can check the weather for users by calling the get_weather function.
            Acknowledge the user's intent before answering. Keep responses under 2 sentences.\
        """,
        base_url: str = "api.openai.com",
        voice: Voices = Voices.Alloy,
        temperature: float = 0.8,
        tools: List[Dict[str, Union[str, any]]] = [],
        input_audio_transcription: InputAudioTranscription = InputAudioTranscription(
            model="whisper-1"
        ),
        clear_audio_queue: Callable[[], None] = lambda: None,
        handle_function_call: Callable[[ResponseFunctionCallArgumentsDone], None] = lambda x: None,
        modalities=["text", "audio"],
        max_response_output_tokens=512,
        turn_detection: ServerVADUpdateParams = ServerVADUpdateParams(
            type="server_vad",
            threshold=0.5,
            prefix_padding_ms=300,
            silence_duration_ms=200,
        ),
        audio_track: CustomAudioStreamTrack = None,
        weather_api_key: str = None,
    
        ):
        self.model = model
        self.loop = loop
        self.api_key = api_key
        self.instructions = instructions
        self.base_url = base_url
        self.temperature = temperature
        self.voice = voice
        self.weather_api_key = weather_api_key
        
        # Define the weather function tool
        weather_tool = {
            "type": "function",
            "name": "get_weather",
            "description": "Get the current weather in a given location",             
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA or Paris, France"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Defaults to fahrenheit."
                    }
                },
                "required": ["location"]
            
        }
        }
        
        # Add weather tool to tools list if weather_api_key is provided
        self.tools = tools.copy() if tools else []
        
        self.tools.append(weather_tool)
        
        self.modalities = modalities
        self.max_response_output_tokens = max_response_output_tokens
        self.input_audio_transcription = input_audio_transcription
        self.clear_audio_queue = clear_audio_queue
        self.handle_function_call = handle_function_call
        self.turn_detection = turn_detection
        self.ws = None
        self.audio_track = audio_track
        
        self._http_session = aiohttp.ClientSession(loop=self.loop)
        self.session_update_params = SessionUpdateParams(
            model=self.model,
            instructions=self.instructions,
            input_audio_format=AudioFormats.PCM16,
            output_audio_format=AudioFormats.PCM16,
            temperature=self.temperature,
            voice=self.voice,
            tool_choice="auto",
            tools=self.tools,
            turn_detection=self.turn_detection,
            modalities=self.modalities,
            max_response_output_tokens=self.max_response_output_tokens,
            input_audio_transcription=self.input_audio_transcription,
        )
        # self.connected_event = asyncio.Event()   # used to notify when ws is ready
        self.pending_instructions: Optional[str] = None

    async def connect(self):
        # url = f"wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
        url = f"wss://api.openai.com/v1/realtime?model=gpt-4o-mini-realtime-preview-2024-12-17"
        print("Establishing OpenAI WS connection... ")
        self.ws = await self._http_session.ws_connect(
            url=url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1",
            },
        )
        
        if self.pending_instructions is not None:
            await self.update_session_instructions(self.pending_instructions)


        # self.connected_event = asyncio.Event()   # used to notify when ws is ready
        print("OpenAI WS connection established")
        self.receive_message_task = self.loop.create_task(
            self.receive_message_handler()
        )

        print("List of tools", self.tools)

        await self.update_session(self.session_update_params)

        await self.receive_message_task
        
    async def update_session_instructions(self, new_instructions: str):
        """
        Dynamically update the system instructions (the system prompt) 
        for translation into the target language.
        """
        if self.ws is None:
            self.pending_instructions = new_instructions
            return
        
        self.session_update_params.instructions = new_instructions
        await self.update_session(self.session_update_params)

    async def update_session(self, session: SessionUpdateParams):
        print("Updating session", session.tools)
        await self.send_request(
            SessionUpdate(
                event_id=generate_event_id(),
                session=session,
            )
        )
        
    
    async def send_request(self, request: ClientToServerMessage):
        request_json = to_json(request)
        await self.ws.send_str(request_json)
        
    async def send_audio_data(self, audio_data: bytes):
        """audio_data is assumed to be pcm16 24kHz mono little-endian"""
        print("sending audio")
        base64_audio_data = base64.b64encode(audio_data).decode("utf-8")
        message = InputAudioBufferAppend(audio=base64_audio_data)
        await self.send_request(message)

    async def get_weather(self, location, unit="fahrenheit"):
        """
        Get weather data for a specific location using the weather API
        """
        return {"weather":"good"}

    async def receive_message_handler(self):
        while True:
            async for response in self.ws:
                try:
                    await asyncio.sleep(0.01)
                    if response.type == aiohttp.WSMsgType.TEXT:
                        # print("Received message", response)
                        self.handle_response(response.data)
                    elif response.type == aiohttp.WSMsgType.ERROR:
                        logger.error("Error while receiving data from openai", response)
                except Exception as e:
                    traceback.print_exc()
                    print("Error in receiving message:", e)

    def clear_audio_queue(self):
        pass
                
    def on_audio_response(self, audio_bytes: bytes):
        self.loop.create_task(
            self.audio_track.add_new_bytes(iter([audio_bytes]))
        )
        
    def handle_response(self, message: str):
        message = json.loads(message)
        
        match message["type"]:
            
            case EventType.SESSION_CREATED:
                logger.info(f"Server Message: {message["type"]}")
                print("Session Created", message["session"])
                
            case EventType.SESSION_UPDATE:
                logger.info(f"Server Message: {message["type"]}")
                print("Session Updated", message["session"])

            case EventType.RESPONSE_AUDIO_DELTA:
                logger.info(f"Server Message: {message["type"]}")
                self.on_audio_response(base64.b64decode(message["delta"]))
                
            case EventType.RESPONSE_AUDIO_TRANSCRIPT_DONE:
                logger.info(f"Server Message: {message["type"]}")
                print(f"Response Transcription: {message["transcript"]}")
            
            case EventType.ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED:
                logger.info(f"Server Message: {message["type"]}")
                print(f"Client Transcription: {message["transcript"]}")
                print("Clearing audio queue in ITEM_INPUT_AUDIO_TRANSCRIPTION_COMPLETED")
                self.clear_audio_queue()
            
            case EventType.INPUT_AUDIO_BUFFER_SPEECH_STARTED:
                logger.info(f"Server Message: {message["type"]}")
                logger.info("Clearing audio queue")
                self.clear_audio_queue()
                
            case EventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE:
                logger.info(f"Server Message: {message["type"]}")
                print(f"Function call: {message["name"]}")
                print(f"Arguments: {message["arguments"]}")
                print(f"message is {message}")
                # Handle the function call based on the name
                if message["name"] == "get_weather":
                    try:
                        args = json.loads(message["arguments"])
                        location = args.get("location")
                        unit = args.get("unit", "fahrenheit")
                        
                        # Create a task to get the weather data
                        self.loop.create_task(self._handle_weather_function(location, unit, message["call_id"]))
                    except Exception as e:
                        logger.error(f"Error processing weather function call: {e}")
                        # Send a failed function call response
                        self.loop.create_task(self._send_function_response(
                            message["id"], 
                            {"error": f"Failed to process weather request: {str(e)}"}
                        ))
                else:
                    # Forward to the general function call handler
                    self.handle_function_call(message)
        
            case EventType.ERROR:
                logger.error(f"Server Error Message: ", message["error"], message)
                
    async def _handle_weather_function(self, location, unit, function_call_id):
        """
        Handle the weather function call and send the response back
        """
        try:
            # Get the weather data
            weather_data = await self.get_weather(location, unit)
            
            # Send the function response
            await self._send_function_response(function_call_id, weather_data)
        except Exception as e:
            logger.error(f"Error in weather function: {e}")
            await self._send_function_response(
                function_call_id, 
                {"error": f"Weather service error: {str(e)}"}
            )
    
    async def _send_function_response(self, function_call_id, response_data):
        """
        Send a function response back to the OpenAI API
        """
        function_response = json.dumps(response_data)
        function_output = FunctionCallOutputItemParam(
                call_id=function_call_id,
                output=function_response,
                type="function_call_output"
            )
        await self.send_request(
            ItemCreate(
                item=function_output,
                type=EventType.ITEM_CREATE
            )
            
        )