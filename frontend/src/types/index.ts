export interface Document {
    id: string;
    name: string;
    contentType: string;
    size: number;
    embeddingStatus: string;
}

export interface Message {
    role: 'user' | 'assistant';
    content: string;
}