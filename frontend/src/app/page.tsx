// pages/index.tsx
import DocumentChat from '@/components/documentChat';
import type { NextPage } from 'next';
import Head from 'next/head';


const Home: NextPage = () => {
  return (
    <div>
      <Head>
        <title>Document Chat</title>
        <meta name="description" content="Chat with your documents using AI" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <DocumentChat />
      </main>
    </div>
  );
};

export default Home;  