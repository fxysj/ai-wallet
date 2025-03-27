from app.utuls.prompt import ClientMessage


class Request(BaseModel):
    messages: List[ClientMessage]