from videosdk import MeetingConfig, VideoSDK, Participant, Stream
from rtc.videosdk.meeting_handler import MeetingHandler
from rtc.videosdk.participant_handler import ParticipantHandler
from agent.audio_stream_track import CustomAudioStreamTrack
from intelligence.openai.openai_intelligence import OpenAIIntelligence
from utils.struct.openai import InputAudioTranscription

import soundfile as sf
import numpy as np
import librosa
import asyncio
import os

import dotenv
dotenv.load_dotenv()
api_key=os.getenv("OPENAI_API_KEY")


class AIAgent:
    def __init__(self, meeting_id: str, authToken: str, name: str):
        self.loop = asyncio.get_event_loop()
        self.audio_track = CustomAudioStreamTrack(
            loop=self.loop,
            handle_interruption=True
        )
        self.last_openai_send_time = 0  # Track when we last sent audio to OpenAI
        self.rate_limit_interval = 0.5  # Minimum seconds between API calls
        self.enable_audio_processing = False  # Control flag for audio processing
        self.audio_processing_lock = asyncio.Lock()  # Lock for thread-safe audio processing
        self.meeting_config = MeetingConfig(
            name=name,
            meeting_id=meeting_id,
            token=authToken,
            mic_enabled=True,
            webcam_enabled=False,
            custom_microphone_audio_track=self.audio_track
        )
        self.current_participant = None
        self.audio_listener_tasks = {}
        self.agent = VideoSDK.init_meeting(**self.meeting_config)
        self.agent.add_event_listener(
            MeetingHandler(
                on_meeting_joined=self.on_meeting_joined,
                on_meeting_left=self.on_meeting_left,
                on_participant_joined=self.on_participant_joined,
                on_participant_left=self.on_participant_left,
            ))
        
        # Initialize OpenAI connection parameters
        self.intelligence = OpenAIIntelligence(
            loop=self.loop,
            api_key=api_key,
            base_url="api.openai.com",  # Verify correct API endpoint
            input_audio_transcription=InputAudioTranscription(model="whisper-1"),
            audio_track=self.audio_track
        )
        
        self.participants_data = {}
        self.is_chatting = False
        self.ai_is_speaking = False  # Track if AI is currently speaking
        self.human_is_speaking = False
    
    async def add_audio_listener(self, stream: Stream):
        # Audio activity detection parameters
        silence_threshold = 0.01  # Adjust based on your need
        min_speech_frames = 5  # Minimum consecutive frames with activity
        speech_counter = 0
        is_speaking = False
        buffer = []
        max_buffer_size = 50  # Maximum frames to buffer (adjust based on your needs)
        
        while True:
            try:
                await asyncio.sleep(0.01)
                if not self.intelligence.ws:
                    continue

                frame = await stream.track.recv()      
                audio_data = frame.to_ndarray()[0]
                audio_data_float = (
                    audio_data.astype(np.float32) / np.iinfo(np.int16).max
                )
                audio_mono = librosa.to_mono(audio_data_float.T)
                
                # Check for voice activity
                energy = np.mean(np.abs(audio_mono))
                
                # Detect speech start
                if energy > silence_threshold:
                    speech_counter += 1
                    if speech_counter >= min_speech_frames and not is_speaking:
                        is_speaking = True
                        print("Speech detected")

                        self.human_is_speaking = True
                        
                        # Check if AI is speaking and interrupt if needed
                        if self.ai_is_speaking:
                            print("Human interrupted AI - sending stop signal")
                            await self.interrupt_ai_speech()
                else:
                    speech_counter = max(0, speech_counter - 1)
                    
                # If no longer speaking, send buffered audio and reset
                if is_speaking and speech_counter == 0:
                    is_speaking = False
                    self.human_is_speaking = False
                    if buffer:
                        print(f"Sending {len(buffer)} audio frames to OpenAI")
                        combined_audio = np.concatenate(buffer)
                        audio_resampled = librosa.resample(
                            combined_audio, orig_sr=48000, target_sr=16000
                        )
                        pcm_frame = (
                            (audio_resampled * np.iinfo(np.int16).max)
                            .astype(np.int16)
                            .tobytes()
                        )
                        await self.intelligence.send_audio_data(pcm_frame)
                        buffer = []
                
                # Buffer audio when speaking
                if is_speaking or speech_counter > 0:
                    buffer.append(audio_mono)
                    # Send in chunks if buffer gets too large
                    if len(buffer) >= max_buffer_size:
                        print(f"Buffer full, sending {len(buffer)} audio frames")
                        combined_audio = np.concatenate(buffer)
                        audio_resampled = librosa.resample(
                            combined_audio, orig_sr=48000, target_sr=16000
                        )
                        pcm_frame = (
                            (audio_resampled * np.iinfo(np.int16).max)
                            .astype(np.int16)
                            .tobytes()
                        )
                        await self.intelligence.send_audio_data(pcm_frame)
                        buffer = []

            except Exception as e:
                print("Audio processing error:", e)
                break

    async def interrupt_ai_speech(self):
        """Send interrupt signal to OpenAI to stop AI from speaking"""
        try:
            # Send interruption signal to OpenAI
            if hasattr(self.intelligence, 'interrupt_speech') and callable(self.intelligence.interrupt_speech):
                await self.intelligence.interrupt_speech()
            else:
                # If direct method doesn't exist, use track's interruption mechanism
                self.audio_track.trigger_interruption()
                
            # Set AI speaking flag to False
            self.ai_is_speaking = False
            print("AI speech interrupted successfully")
            
        except Exception as e:
            print(f"Error interrupting AI speech: {e}")
    
    # Add method to track when AI starts speaking
    def on_ai_speech_start(self):
        """Called when AI starts speaking"""
        self.ai_is_speaking = True
        print("AI started speaking")
    
    # Add method to track when AI stops speaking
    def on_ai_speech_end(self):
        """Called when AI finishes speaking"""
        self.ai_is_speaking = False
        print("AI stopped speaking")
    
    # Add hooks to the intelligence class if available
    def setup_speech_tracking(self):
        """Set up hooks to track AI speech status"""
        if hasattr(self.intelligence, 'set_speech_start_callback'):
            self.intelligence.set_speech_start_callback(self.on_ai_speech_start)
        
        if hasattr(self.intelligence, 'set_speech_end_callback'):
            self.intelligence.set_speech_end_callback(self.on_ai_speech_end)
                
    async def start_conversation(self):
        """Start a conversation with OpenAI by sending an initial greeting."""
        try:
            # Wait for OpenAI connection to be established
            await asyncio.sleep(2)
            
            self.setup_speech_tracking()
            # Set initial conversation instructions
            initial_instructions = """
            You are an AI assistant in a video call. You should:
            1. Introduce yourself briefly
            2. Ask how you can help the participants today
            3. Be conversational and friendly
            4. Listen carefully to questions and provide helpful responses
            5. When responding, be concise but complete
            6. Pause appropriately between phrases to sound natural
            7. If interrupted, stop speaking immediately and listen to the user
            8. make call to a function named get_weather for weather information
            """
            
            await self.intelligence.update_session_instructions(initial_instructions)
            
            # Send initial greeting through audio
            print("Starting conversation with participants")
            self.is_chatting = True
            
            # Enable agent's microphone if not already enabled
            if not self.audio_track.enabled:
                self.audio_track.enabled = True
                
            # Set audio processing parameters
            self.enable_audio_processing = True
                
        except Exception as e:
            print(f"Error starting conversation: {e}")
    
    def on_meeting_joined(self, data):
        print("Meeting Joined - Starting OpenAI connection")
        # Connect to OpenAI and start conversation immediately
        async def setup_and_start():
            await self.intelligence.connect()
            # Start conversation after connection is established
            await self.start_conversation()
            
        asyncio.create_task(setup_and_start())
        print("participant length", len(self.participants_data))
        
    def on_meeting_left(self, data):
        print(f"Meeting Left")
        # Clean up OpenAI connection
        if self.intelligence.ws:
            asyncio.create_task(self.intelligence.disconnect())
        self.is_chatting = False
        
    def on_participant_joined(self, participant: Participant):
        peer_name = participant.display_name
        
        # Check if metadata exists and has preferred language
        if hasattr(participant, 'meta_data') and participant.meta_data and "preferredLanguage" in participant.meta_data:
            native_lang = participant.meta_data["preferredLanguage"]
        else:
            native_lang = "English"  # Default language
            
        self.participants_data[participant.id] = {
            "name": peer_name,
            "lang": native_lang
        }
        print("Participant joined:", peer_name)
        print("Native language:", native_lang)
        
        print("participant length", len(self.participants_data))
        
        # Update conversation mode based on participants
        if len(self.participants_data) == 2:
            # Extract the info for each participant
            participant_ids = list(self.participants_data.keys())
            p1 = self.participants_data[participant_ids[0]]
            p2 = self.participants_data[participant_ids[1]]

            # Build translator-specific instructions when two participants
            translator_instructions = f"""
                
                Your job is to translate, from one language to another, don't engage in any conversation
            """

            # Dynamically tell OpenAI to use these instructions
            asyncio.create_task(self.intelligence.update_session_instructions(translator_instructions))
        elif len(self.participants_data) == 1 and self.is_chatting:  
            # If only one participant (plus the agent), switch to assistant mode
            assistant_instructions = f"""
                You are an AI assistant speaking with {peer_name} who speaks {native_lang}.
                Communicate in {native_lang}.
                Be helpful, conversational, and engaging.
                Ask how you can assist them today.
            """
            
            asyncio.create_task(self.intelligence.update_session_instructions(assistant_instructions))

        def on_stream_enabled(stream: Stream):
            print("Participant stream enabled")
            self.current_participant = participant
            print("Participant stream enabled for", self.current_participant.display_name)
            if stream.kind == "audio":
                self.audio_listener_tasks[stream.id] = self.loop.create_task(
                    self.add_audio_listener(stream)
                )

        def on_stream_disabled(stream: Stream):
            print("Participant stream disabled")
            if stream.kind == "audio":
                if stream.id in self.audio_listener_tasks:
                    audio_task = self.audio_listener_tasks[stream.id]
                    if audio_task is not None:
                        audio_task.cancel()

        participant.add_event_listener(
            ParticipantHandler(
                participant_id=participant.id,
                on_stream_enabled=on_stream_enabled,
                on_stream_disabled=on_stream_disabled
            )
        )

    def on_participant_left(self, participant: Participant):
        print("Participant left:", participant.display_name)
        
        # Remove participant from data
        if participant.id in self.participants_data:
            del self.participants_data[participant.id]
            
        # If there's still one participant left, update conversation mode
        if len(self.participants_data) == 1:
            remaining_id = list(self.participants_data.keys())[0]
            remaining_participant = self.participants_data[remaining_id]
            
            assistant_instructions = f"""
                You are an AI assistant speaking with {remaining_participant['name']} who speaks {remaining_participant['lang']}.
                Communicate in {remaining_participant['lang']}.
                Be helpful, conversational, and engaging.
                Ask how you can assist them today.
            """
            
            asyncio.create_task(self.intelligence.update_session_instructions(assistant_instructions))
          
    async def join(self):
        await self.agent.async_join()
    
    async def leave(self):
        # Properly disconnect from OpenAI before leaving
        if self.intelligence.ws:
            await self.intelligence.disconnect()
        self.agent.leave()

