import { fetchArticles } from '@/lib/supabase';
import { DesktopDeck } from '@/components/DesktopDeck';

// Next.js Incremental Static Regeneration (ISR): revalidate every 6 hours (21600 seconds)
export const revalidate = 21600;

export default async function HomePage() {
  const articles = await fetchArticles(150);

  return <DesktopDeck initialCards={articles} />;
}
