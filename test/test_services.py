from unittest.mock import MagicMock
from app.services.Agent import chat, get_agent


def test_agent_chat_invocation(monkeypatch):
    """Test chat function correctly converts message history and invokes engineering agent."""
    mock_agent = MagicMock()
    mock_agent.invoke.return_value = {
        "final_answer": "AI Response generated from Engineering Stack"
    }
    
    monkeypatch.setattr("app.services.Agent.get_agent", lambda: mock_agent)
    
    mock_msg1 = MagicMock()
    mock_msg1.role = "user"
    mock_msg1.content = "What is the architecture?"
    
    mock_msg2 = MagicMock()
    mock_msg2.role = "assistant"
    mock_msg2.content = "It is a multi-agent engineering stack."
    
    res = chat(
        conversation_history=[mock_msg1, mock_msg2],
        conversation_id="conv_123"
    )
    
    assert res == "AI Response generated from Engineering Stack"
    assert mock_agent.invoke.called
