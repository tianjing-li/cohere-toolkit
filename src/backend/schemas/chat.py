from enum import StrEnum
from typing import Any, ClassVar, Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field

from backend.chat.enums import StreamEvent
from backend.schemas.citation import Citation
from backend.schemas.document import Document
from backend.schemas.search_query import SearchQuery
from backend.schemas.tool import ToolCall


class ChatRole(StrEnum):
    """One of CHATBOT|USER to identify who the message is coming from."""

    CHATBOT = "CHATBOT"
    USER = "USER"


class ChatCitationQuality(StrEnum):
    """Dictates the approach taken to generating citations by allowing the user to specify whether they want "accurate" results or "fast" results. Defaults to "accurate"."""

    FAST = "FAST"
    ACCURATE = "ACCURATE"


class ToolInputType(StrEnum):
    """Type of input passed to the tool"""

    QUERY = "QUERY"
    CODE = "CODE"


class ChatMessage(BaseModel):
    """A list of previous messages between the user and the model, meant to give the model conversational context for responding to the user's message."""

    role: ChatRole = Field(
        title="One of CHATBOT|USER to identify who the message is coming from.",
    )
    message: str = Field(
        title="Contents of the chat message.",
    )

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "message": self.message}


# TODO: fix titles of these types
class ChatResponse(BaseModel):
    event_type: ClassVar[StreamEvent] = Field()
    is_finished: bool = Field(
        title="Denotes whether or not the chat stream has finished.",
    )


class StreamStart(ChatResponse):
    """Stream start event."""

    event_type: ClassVar[StreamEvent] = StreamEvent.STREAM_START
    generation_id: str = Field()
    conversation_id: Optional[str] = Field(default=None)


class StreamTextGeneration(ChatResponse):
    """Stream text generation event."""

    event_type: ClassVar[StreamEvent] = StreamEvent.TEXT_GENERATION

    text: str = Field(
        title="Contents of the chat message.",
    )


class StreamCitationGeneration(ChatResponse):
    """Stream citation generation event."""

    event_type: ClassVar[StreamEvent] = StreamEvent.CITATION_GENERATION

    citations: List[Citation] = Field(
        title="Citations for the chat message.", default=[]
    )


class StreamQueryGeneration(ChatResponse):
    """Stream query generation event."""

    event_type: ClassVar[StreamEvent] = StreamEvent.SEARCH_QUERIES_GENERATION

    query: str = Field(
        title="Search query used to generate grounded response with citations.",
    )


class StreamSearchResults(ChatResponse):
    event_type: ClassVar[StreamEvent] = StreamEvent.SEARCH_RESULTS

    search_results: List[Dict[str, Any]] = Field(
        title="Search results used to generate grounded response with citations.",
        default=[],
    )
    documents: List[Document] = Field(
        title="Documents used to generate grounded response with citations.",
        default=[],
    )


class StreamToolInput(ChatResponse):
    event_type: ClassVar[StreamEvent] = StreamEvent.TOOL_INPUT
    input_type: ToolInputType
    tool_name: str
    input: str
    text: str


class StreamToolResult(ChatResponse):
    event_type: ClassVar[StreamEvent] = StreamEvent.TOOL_RESULT
    result: Union[str, None]

    documents: List[Document] = Field(
        title="Documents used to generate grounded response with citations.",
        default=[],
    )


class StreamSearchQueriesGeneration(ChatResponse):
    """Stream queries generation event."""

    event_type: ClassVar[StreamEvent] = StreamEvent.SEARCH_QUERIES_GENERATION

    search_queries: List[SearchQuery] = Field(
        title="Search query used to generate grounded response with citations.",
        default=[],
    )


class StreamEnd(ChatResponse):
    response_id: str
    event_type: ClassVar[StreamEvent] = StreamEvent.STREAM_END
    is_finished: ClassVar[bool] = True
    generation_id: str = Field()
    conversation_id: Optional[str] = Field()
    text: str = Field(
        title="Contents of the chat message.",
    )
    citations: List[Citation] = Field(
        title="Citations for the chat message.", default=[]
    )
    documents: List[Document] = Field(
        title="Documents used to generate grounded response with citations.",
        default=[],
    )
    search_results: List[Dict[str, Any]] = Field(
        title="Search results used to generate grounded response with citations.",
        default=[],
    )
    search_queries: List[SearchQuery] = Field(
        title="List of generated search queries.",
        default=[],
    )
    finish_reason: str = Field()


class NonStreamedChatResponse(ChatResponse):
    response_id: str | None = Field(
        title="Unique identifier for the response.",
    )
    generation_id: str | None = Field(
        title="Unique identifier for the generation.",
    )
    chat_history: List[ChatMessage] | None = Field(
        title="A list of previous messages between the user and the model, meant to give the model conversational context for responding to the user's message.",
    )
    finish_reason: str = Field(
        title="Reason the chat stream ended.",
    )
    text: str = Field(
        title="Contents of the chat message.",
    )
    citations: List[Citation] | None = Field(
        title="Citations for the chat message.",
        default=[],
    )
    documents: List[Document] | None = Field(
        title="Documents used to generate grounded response with citations.",
        default=[],
    )
    search_results: List[Dict[str, Any]] | None = Field(
        title="Search results used to generate grounded response with citations.",
        default=[],
    )
    search_queries: List[SearchQuery] | None = Field(
        title="List of generated search queries.",
        default=[],
    )
    conversation_id: str | None = Field(
        title="To store a conversation then create a conversation id and use it for every related request.",
    )
    tool_calls: List[ToolCall] | None = Field(
        title="List of tool calls generated for custom tools",
        default=[],
    )


class ChatResponseEvent(BaseModel):
    event: StreamEvent = Field(
        title="type of stream event",
    )

    data: Union[
        StreamStart,
        StreamTextGeneration,
        StreamCitationGeneration,
        StreamQueryGeneration,
        StreamSearchResults,
        StreamEnd,
        StreamToolInput,
        StreamToolResult,
        StreamSearchQueriesGeneration,
        NonStreamedChatResponse,
    ] = Field(
        title="Data returned from chat response of a given event type",
    )


class BaseChatRequest(BaseModel):

    # user_id: str = Field(
    #     title="A user id to store to store the conversation under.", exclude=True
    # )
    message: str = Field(
        title="The message to send to the chatbot.",
    )
    chat_history: List[ChatMessage] | None = Field(
        default=None,
        title="A list of entries used to construct the conversation. If provided, these messages will be used to build the prompt and the conversation_id will be ignored so no data will be stored to maintain state.",
    )
    conversation_id: str = Field(
        default_factory=lambda: str(uuid4()),
        title="To store a conversation then create a conversation id and use it for every related request",
    )
