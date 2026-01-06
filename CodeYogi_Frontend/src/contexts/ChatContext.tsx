import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { Message } from "../types/chat";
import { useSelectedRepository } from "../hooks/useSelectedRepository";

interface ChatContextType {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  clearChat: () => void;
  addMessage: (message: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChatContext = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChatContext must be used within a ChatProvider");
  }
  return context;
};

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const { selectedRepo } = useSelectedRepository();
  const [messages, setMessages] = useState<Message[]>([]);

  // Initialize chat with welcome message
  useEffect(() => {
    const initialMessage: Message = {
      id: "welcome",
      type: "ai",
      content: selectedRepo
        ? `Hello! I'm CodeYogi AI. I see you have the repository "${selectedRepo.name}" selected. How can I assist you with it?`
        : "Hello! I'm CodeYogi AI. Select a repository or ask me a general question to get started.",
      timestamp: new Date(),
    };

    // Only set initial message if messages array is empty
    if (messages.length === 0) {
      setMessages([initialMessage]);
    } else {
      // Update the welcome message when selectedRepo changes
      setMessages((prev) => {
        const welcomeMessageIndex = prev.findIndex(
          (msg) => msg.id === "welcome"
        );
        if (welcomeMessageIndex !== -1) {
          const updatedMessages = [...prev];
          updatedMessages[welcomeMessageIndex] = initialMessage;
          return updatedMessages;
        }
        return prev;
      });
    }
  }, [selectedRepo]);

  // Save chat to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem("codeyogi-chat-messages", JSON.stringify(messages));
    }
  }, [messages]);

  // Load chat from localStorage on component mount
  useEffect(() => {
    const savedMessages = localStorage.getItem("codeyogi-chat-messages");
    if (savedMessages) {
      try {
        const parsedMessages = JSON.parse(savedMessages);
        // Convert timestamp strings back to Date objects
        const messagesWithDates = parsedMessages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
        setMessages(messagesWithDates);
      } catch (error) {
        console.error("Failed to load chat messages from localStorage:", error);
      }
    }
  }, []);

  const clearChat = () => {
    const initialMessage: Message = {
      id: "welcome",
      type: "ai",
      content: selectedRepo
        ? `Hello! I'm CodeYogi AI. I see you have the repository "${selectedRepo.name}" selected. How can I assist you with it?`
        : "Hello! I'm CodeYogi AI. Select a repository or ask me a general question to get started.",
      timestamp: new Date(),
    };
    setMessages([initialMessage]);
    localStorage.removeItem("codeyogi-chat-messages");
  };

  const addMessage = (message: Message) => {
    setMessages((prev) => [...prev, message]);
  };

  const updateMessage = (id: string, updates: Partial<Message>) => {
    setMessages((prev) =>
      prev.map((msg) => (msg.id === id ? { ...msg, ...updates } : msg))
    );
  };

  // Clear chat on page unload/close
  useEffect(() => {
    const handleBeforeUnload = () => {
      // You can choose to either clear the chat or keep it persistent
      // Comment out the next line if you want to keep chat persistent across browser sessions
      // localStorage.removeItem("codeyogi-chat-messages");
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);

  const value: ChatContextType = {
    messages,
    setMessages,
    clearChat,
    addMessage,
    updateMessage,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
