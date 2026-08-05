import { Metadata } from 'next';
import RedirectClient from './RedirectClient';

type Props = {
  params: Promise<{ id: string }> | { id: string };
};

// Open Graph metadata for social sharing
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const resolvedParams = await Promise.resolve(params);
  
  return {
    title: 'Post on Coyoote',
    description: 'Check out this post on the Coyoote app!',
    openGraph: {
      title: 'Post on Coyoote',
      description: 'Check out this post on the Coyoote app!',
      url: `https://mathos.cloud/post/${resolvedParams.id}`,
      siteName: 'Coyoote',
      type: 'article',
    },
  };
}

export default async function PostPage({ params }: Props) {
  const resolvedParams = await Promise.resolve(params);
  return <RedirectClient postId={resolvedParams.id} />;
}
