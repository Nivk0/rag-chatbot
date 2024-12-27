export interface Document {
    id: string;
    name: string;
    contentType: string;
    size: number;
}

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const uploadDocuments = async (files: FileList): Promise<Document[]> => {
    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('files', file);
    });

    const response = await fetch(`${API_URL}/documents/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error('Upload failed');
    }

    return response.json();
};

export const sendChatMessage = async (
    text: string,
    documentIds: string[]
): Promise<{ response: string }> => {
    const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text,
            document_ids: documentIds, // Make sure this matches the backend expectation
        }),
    });

    if (!response.ok) {
        const error = await response.text();
        throw new Error(`Chat request failed: ${error}`);
    }

    return response.json();
};