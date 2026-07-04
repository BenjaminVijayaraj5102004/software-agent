from ..schema.conversation_schema import ConversationCreate
from ..schema.message_schema import MessageCreate 


from strawberry.experimental import pydantic as pydantic_types


@pydantic_types.type(model=ConversationCreate, all_fields=True)
class ConversationCreateType:
    pass    


@pydantic_types.type(model=MessageCreate, all_fields=True)
class MessageCreateType:
    pass