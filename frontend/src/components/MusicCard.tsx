'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { ExternalLink, Clock, Radio } from 'lucide-react';
import { ArticleCard } from '@/lib/types';

interface MusicCardProps {
  article: ArticleCard;
  isActive?: boolean;
}

const GENRE_FALLBACK_IMAGES: Record<string, string> = {
  'Rock & Indie':
    'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=80',
  'Hip-Hop':
    'https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=1200&q=80',
  'Electronic':
    'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?auto=format&fit=crop&w=1200&q=80',
  'Metal':
    'https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=1200&q=80',
  'Pop':
    'https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&w=1200&q=80',
  'Audio & Gear':
    'https://images.unsplash.com/photo-1598653222000-6b7b7a552625?auto=format&fit=crop&w=1200&q=80',
  'Discovery':
    'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=1200&q=80',
};

const DEFAULT_IMAGE =
  'https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80';

function formatRelativeTime(dateString: string): string {
  try {
    const published = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - published.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 5) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    return `${diffDays}d ago`;
  } catch {
    return 'Recent';
  }
}

export const MusicCard: React.FC<MusicCardProps> = ({ article, isActive = false }) => {
  const fallbackUrl = GENRE_FALLBACK_IMAGES[article.genre] || DEFAULT_IMAGE;
  const initialImage = article.image_url?.trim() || fallbackUrl;
  const [imgSrc, setImgSrc] = useState<string>(initialImage);

  return (
    <article
      className="w-[900px] h-[520px] rounded-2xl bg-neutral-900 border border-neutral-800/90 shadow-2xl flex overflow-hidden select-none transition-all duration-300 relative group"
      aria-current={isActive ? 'true' : undefined}
    >
      {/* ------------------------------------------------------------------ */}
      {/* LEFT HALF (50% Width, Full Height): Rich Media Cover Visual        */}
      {/* ------------------------------------------------------------------ */}
      <div className="w-1/2 h-full relative overflow-hidden bg-neutral-950 flex-shrink-0">
        <Image
          src={imgSrc}
          alt={article.headline}
          fill
          priority={isActive}
          className="object-cover w-full h-full transform transition-transform duration-700 group-hover:scale-105"
          sizes="450px"
          onError={() => setImgSrc(fallbackUrl)}
        />
        {/* Cinematic Atmospheric Gradients */}
        <div className="absolute inset-0 bg-gradient-to-t from-neutral-950/85 via-neutral-950/20 to-transparent pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-neutral-900/60 pointer-events-none" />

        {/* Source Outlet Overlay Badge on Media Bottom */}
        <div className="absolute bottom-4 left-4 flex items-center gap-2 bg-neutral-950/80 backdrop-blur-md px-3 py-1.5 rounded-lg border border-neutral-800/80 text-xs font-medium text-neutral-300">
          <Radio className="w-3.5 h-3.5 text-rose-500 animate-pulse" />
          <span>{article.source}</span>
        </div>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* RIGHT HALF (50% Width, Full Height): Editorial Core               */}
      {/* ------------------------------------------------------------------ */}
      <div className="w-1/2 h-full p-8 flex flex-col justify-between bg-neutral-900 relative">
        {/* Top Header Row: Genre & Relative Time */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="bg-rose-500/15 text-rose-400 border border-rose-500/30 text-xs font-semibold px-3 py-1 rounded-full uppercase tracking-wider">
              {article.genre}
            </span>
          </div>

          <div className="flex items-center gap-1.5 text-neutral-500 text-xs font-mono">
            <Clock className="w-3.5 h-3.5 text-neutral-500" />
            <span>{formatRelativeTime(article.published_at)}</span>
          </div>
        </div>

        {/* Center Editorial Core */}
        <div className="my-auto py-2">
          <h2 className="text-2xl font-bold text-neutral-100 leading-snug tracking-tight mb-4 group-hover:text-white transition-colors">
            {article.headline}
          </h2>
          <p className="text-neutral-300 text-base leading-relaxed font-normal antialiased line-clamp-6">
            {article.summary}
          </p>
        </div>

        {/* Bottom Footer Action Row */}
        <div className="pt-4 border-t border-neutral-800/80 flex items-center justify-between gap-4">
          {/* Outbound Link Button */}
          <a
            href={article.link}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-xs font-semibold text-neutral-200 hover:text-white bg-neutral-800 hover:bg-rose-600 px-4 py-2.5 rounded-xl border border-neutral-700/60 hover:border-rose-500 transition-all duration-200 group/btn"
          >
            <span>Read full story at {article.source}</span>
            <ExternalLink className="w-3.5 h-3.5 text-neutral-400 group-hover/btn:text-white group-hover/btn:translate-x-0.5 group-hover/btn:-translate-y-0.5 transition-transform" />
          </a>

          {/* Keyboard Flipping Hint */}
          <div className="hidden sm:flex items-center gap-1 text-[11px] font-mono text-neutral-500 bg-neutral-950/60 px-2.5 py-1 rounded-md border border-neutral-800/60">
            <span>Flip</span>
            <kbd className="px-1 py-0.5 bg-neutral-800 rounded text-neutral-400 text-[10px]">↓</kbd>
            <kbd className="px-1 py-0.5 bg-neutral-800 rounded text-neutral-400 text-[10px]">↑</kbd>
          </div>
        </div>
      </div>
    </article>
  );
};
