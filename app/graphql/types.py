from ..schema.conversation_schema import ConversationResponse , ConversationListItem
from ..schema.message_schema import MessageResponse

from strawberry.experimental import pydantic as pydantic_types

@pydantic_types.type(model=ConversationResponse, all_fields=True)
class ConversationResponseType:
    pass


@pydantic_types.type(model=ConversationListItem, all_fields=True)
class ConversationListItemType:
    pass


@pydantic_types.type(model=MessageResponse, all_fields=True)
class MessageResponseType:
    pass
