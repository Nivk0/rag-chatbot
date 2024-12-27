"use client";

import React, { useState, useRef, useEffect } from 'react';
import { Upload, Trash2 } from 'lucide-react';

interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
}

interface Document {
    id: string;
    name: string;
    file_path: string;
    content_type: string;
    size: number;
}

interface ChatState {
    [documentId: string]: Message[];
}

const DocumentChat: React.FC = () => {
    const [chatState, setChatState] = useState<ChatState>({});
    const [documents, setDocuments] = useState<Document[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [activeDocumentId, setActiveDocumentId] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const [query, setQuery] = useState('');
    const chatContainerRef = useRef<HTMLDivElement>(null);

    const loadDocuments = async () => {
        try {
            const response = await fetch('http://localhost:8000/documents');
            const docs = await response.json();
            setDocuments(docs);

            // Load saved chats for existing documents
            const savedChats = localStorage.getItem('documentChats');
            if (savedChats) {
                const parsedChats = JSON.parse(savedChats);
                // Only keep chats for documents that still exist
                const filteredChats: ChatState = {};
                docs.forEach((doc: { id: string | number; }) => {
                    if (parsedChats[doc.id]) {
                        filteredChats[doc.id] = parsedChats[doc.id];
                    }
                });
                setChatState(filteredChats);
                localStorage.setItem('documentChats', JSON.stringify(filteredChats));
            }
            return docs;
        } catch (error) {
            console.error('Failed to load documents:', error);
            return [];
        }
    };


    useEffect(() => {
        const loadSavedState = async () => {
            setIsLoading(true);
            try {
                const docs = await loadDocuments();

                // Load chat state from localStorage
                const savedChats = localStorage.getItem('documentChats');
                if (savedChats) {
                    setChatState(JSON.parse(savedChats));
                }

                // Set active document
                const savedActiveId = localStorage.getItem('activeDocumentId');
                if (savedActiveId && docs.some((doc: { id: string; }) => doc.id === savedActiveId)) {
                    setActiveDocumentId(savedActiveId);
                } else if (docs.length > 0) {
                    setActiveDocumentId(docs[0].id);
                }
            } catch (error) {
                console.error('Failed to load saved state:', error);
            } finally {
                setIsLoading(false);
            }
        };

        loadSavedState();
    }, []);

    useEffect(() => {
        if (Object.keys(chatState).length > 0) {
            localStorage.setItem('documentChats', JSON.stringify(chatState));
        }
    }, [chatState]);

    useEffect(() => {
        if (activeDocumentId) {
            localStorage.setItem('activeDocumentId', activeDocumentId);
        }
    }, [activeDocumentId]);

    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [chatState, activeDocumentId]);

    // Update chat state in localStorage whenever it changes
    useEffect(() => {
        if (Object.keys(chatState).length > 0) {
            localStorage.setItem('documentChats', JSON.stringify(chatState));
        }
    }, [chatState]);

    const handleDeleteDocument = async (docId: string) => {
        try {
            await fetch(`http://localhost:8000/documents/${docId}`, {
                method: 'DELETE',
            });

            // Update documents state
            setDocuments(prev => prev.filter(doc => doc.id !== docId));

            // Update chat state and remove deleted document's chat history
            const newChatState = { ...chatState };
            delete newChatState[docId];
            setChatState(newChatState);
            localStorage.setItem('documentChats', JSON.stringify(newChatState));

            // Update active document if needed
            if (activeDocumentId === docId) {
                const remainingDocs = documents.filter(doc => doc.id !== docId);
                const newActiveId = remainingDocs.length > 0 ? remainingDocs[0].id : null;
                setActiveDocumentId(newActiveId);
                if (newActiveId) {
                    localStorage.setItem('activeDocumentId', newActiveId);
                } else {
                    localStorage.removeItem('activeDocumentId');
                }
            }
        } catch (error) {
            console.error('Delete failed:', error);
        }
    };

    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (!files) return;
        setIsLoading(true);

        try {
            const formData = new FormData();
            Array.from(files).forEach(file => formData.append('files', file));

            const response = await fetch('http://localhost:8000/documents/upload', {
                method: 'POST',
                body: formData,
            });

            const newDocs = await response.json();
            setDocuments(prev => [...prev, ...newDocs]);

            // Initialize chat history for new documents
            const newChatState = { ...chatState };
            newDocs.forEach((doc: { id: string | number; }) => {
                if (!newChatState[doc.id]) {
                    newChatState[doc.id] = [];
                }
            });
            setChatState(newChatState);

            if (!activeDocumentId && newDocs.length > 0) {
                setActiveDocumentId(newDocs[0].id);
            }
        } catch (error) {
            console.error('Upload failed:', error);
        } finally {
            setIsLoading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    // Update the handleSubmit function:

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim() || !activeDocumentId) return;

        const newMessage: Message = {
            role: 'user',
            content: query,
            timestamp: Date.now()
        };

        const updatedMessages = [...(chatState[activeDocumentId] || []), newMessage];
        setChatState(prev => ({
            ...prev,
            [activeDocumentId]: updatedMessages
        }));

        setIsLoading(true);

        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: query,
                    document_ids: [activeDocumentId]  // Changed from document_id to document_ids array
                }),
            });

            if (!response.ok) {
                throw new Error(`Chat failed with status: ${response.status}`);
            }

            const data = await response.json();

            const assistantMessage: Message = {
                role: 'assistant',
                content: data.response,
                timestamp: Date.now()
            };

            setChatState(prev => ({
                ...prev,
                [activeDocumentId]: [...updatedMessages, assistantMessage]
            }));
        } catch (error) {
            console.error('Chat failed:', error);
            // Add error message to chat
            const errorMessage: Message = {
                role: 'assistant',
                content: 'Sorry, there was an error processing your request.',
                timestamp: Date.now()
            };
            setChatState(prev => ({
                ...prev,
                [activeDocumentId]: [...updatedMessages, errorMessage]
            }));
        } finally {
            setIsLoading(false);
            setQuery('');
        }
    };

    return (
        <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
            <div className="flex items-center justify-between mb-4">
                <h1 className="text-2xl font-bold text-white-900">Document Chat</h1>
                <button
                    onClick={() => fileInputRef.current?.click()}
                    className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                    <Upload size={20} />
                    Upload Documents
                </button>
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileUpload}
                    className="hidden"
                    multiple
                    accept=".pdf,.doc,.docx,.txt"
                />
            </div>

            {documents.length > 0 && (
                <div className="mb-4">
                    <h2 className="text-lg font-semibold mb-2 text-white-900">Documents</h2>
                    <div className="flex flex-wrap gap-2">
                        {documents.map((doc) => (
                            <div key={doc.id} className="flex items-center gap-2">
                                <button
                                    onClick={() => setActiveDocumentId(doc.id)}
                                    className={`p-2 rounded flex items-center gap-2 ${activeDocumentId === doc.id
                                        ? 'bg-blue-500 text-white'
                                        : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
                                        }`}
                                >
                                    <span>{doc.name}</span>
                                </button>
                                <button
                                    onClick={() => handleDeleteDocument(doc.id)}
                                    className="p-2 rounded bg-red-100 hover:bg-red-200 text-red-600"
                                >
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div ref={chatContainerRef} className="flex-1 bg-gray-50 rounded-lg p-4 mb-4 overflow-auto">
                {activeDocumentId ? (
                    chatState[activeDocumentId]?.map((message, index) => (
                        <div
                            key={index}
                            className={`mb-4 ${message.role === 'user' ? 'text-right' : 'text-left'}`}
                        >
                            <div
                                className={`inline-block p-3 rounded-lg ${message.role === 'user'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-200 text-gray-900'
                                    }`}
                            >
                                {message.content}
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="text-center text-gray-900">
                        Select a document to start chatting
                    </div>
                )}
                {isLoading && (
                    <div className="text-center text-gray-900">
                        Processing...
                    </div>
                )}
            </div>

            <form onSubmit={handleSubmit} className="flex gap-2">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={activeDocumentId ? "Ask a question about this document..." : "Select a document first"}
                    className="flex-1 p-2 border rounded text-gray-900 placeholder-gray-500"
                    disabled={!activeDocumentId}
                />
                <button
                    type="submit"
                    disabled={isLoading || !activeDocumentId}
                    className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
                >
                    Send
                </button>
            </form>
        </div>
    );
};

export default DocumentChat;