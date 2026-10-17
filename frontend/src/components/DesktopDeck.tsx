'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { ChevronUp, ChevronDown, Layers, Sparkles, Compass } from 'lucide-react';
import { ArticleCard, GenreFilter, GENRE_FILTERS } from '@/lib/types';
import { MusicCard } from './MusicCard';

interface DesktopDeckProps {
  initialCards: ArticleCard[];
}

export const DesktopDeck: React.FC<DesktopDeckProps> = ({ initialCards }) => {
  const [selectedGenre, setSelectedGenre] = useState<GenreFilter>('All');
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [isTransitioning, setIsTransitioning] = useState<boolean>(false);
  const wheelLockRef = useRef<boolean>(false);
  const lockTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Filter cards by genre
  const filteredCards = React.useMemo(() => {
    if (selectedGenre === 'All') return initialCards;
    return initialCards.filter((card) => card.genre === selectedGenre);
  }, [initialCards, selectedGenre]);

  // Reset index when genre changes or cards update
  useEffect(() => {
    setCurrentIndex(0);
  }, [selectedGenre]);

  const totalCards = filteredCards.length;

  const goToNext = useCallback(() => {
    if (wheelLockRef.current) return;
    setCurrentIndex((prev) => {
      if (prev < totalCards - 1) {
        setIsTransitioning(true);
        wheelLockRef.current = true;
        if (lockTimerRef.current) clearTimeout(lockTimerRef.current);
        lockTimerRef.current = setTimeout(() => {
          wheelLockRef.current = false;
          setIsTransitioning(false);
        }, 380);
        return prev + 1;
      }
      return prev;
    });
  }, [totalCards]);

  const goToPrev = useCallback(() => {
    if (wheelLockRef.current) return;
    setCurrentIndex((prev) => {
      if (prev > 0) {
        setIsTransitioning(true);
        wheelLockRef.current = true;
        if (lockTimerRef.current) clearTimeout(lockTimerRef.current);
        lockTimerRef.current = setTimeout(() => {
          wheelLockRef.current = false;
          setIsTransitioning(false);
        }, 380);
        return prev - 1;
      }
      return prev;
    });
  }, []);

  // Keyboard navigation listener (ArrowDown, ArrowUp, Spacebar, j, k)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if user is interacting with form controls
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }

      if (e.key === 'ArrowDown' || e.key === ' ' || e.key.toLowerCase() === 'j') {
        e.preventDefault();
        goToNext();
      } else if (e.key === 'ArrowUp' || e.key.toLowerCase() === 'k') {
        e.preventDefault();
        goToPrev();
      } else if (e.key === 'Home') {
        e.preventDefault();
        setCurrentIndex(0);
      } else if (e.key === 'End') {
        e.preventDefault();
        setCurrentIndex(totalCards - 1);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [goToNext, goToPrev, totalCards]);

  // Debounced mouse wheel vertical swipe listener
  useEffect(() => {
    const handleWheel = (e: WheelEvent) => {
      if (wheelLockRef.current) return;

      const deltaThreshold = 25;
      if (e.deltaY > deltaThreshold) {
        goToNext();
      } else if (e.deltaY < -deltaThreshold) {
        goToPrev();
      }
    };

    window.addEventListener('wheel', handleWheel, { passive: true });
    return () => window.removeEventListener('wheel', handleWheel);
  }, [goToNext, goToPrev]);

  // Clean up timers on unmount
  useEffect(() => {
    return () => {
      if (lockTimerRef.current) clearTimeout(lockTimerRef.current);
    };
  }, []);

  const activeCard = filteredCards[currentIndex] || filteredCards[0];
  const progressPercent = totalCards > 0 ? ((currentIndex + 1) / totalCards) * 100 : 0;

  return (
    <div className="w-screen h-screen overflow-hidden bg-neutral-950 flex flex-col justify-between relative select-none">
      {/* ------------------------------------------------------------------ */}
      {/* 1. TOP HEADER NAVIGATION BAR                                       */}
      {/* ------------------------------------------------------------------ */}
      <header className="w-full h-16 border-b border-neutral-900 bg-neutral-950/90 backdrop-blur-md px-8 flex items-center justify-between z-30 flex-shrink-0">
        {/* Brand identity */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-xl font-black tracking-widest text-white">DENIRA</span>
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse" />
          </div>
          <span className="text-[11px] font-mono tracking-wide uppercase px-2 py-0.5 rounded bg-neutral-900 border border-neutral-800 text-neutral-400">
            Desktop Deck
          </span>
        </div>

        {/* Genre Pill Filter Selector */}
        <nav className="flex items-center gap-1.5 overflow-x-auto no-scrollbar">
          {GENRE_FILTERS.map((genre) => {
            const isSelected = selectedGenre === genre;
            return (
              <button
                key={genre}
                onClick={() => setSelectedGenre(genre)}
                className={`text-xs font-medium px-3 py-1.5 rounded-lg transition-all duration-200 ${
                  isSelected
                    ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40 shadow-sm shadow-rose-950'
                    : 'text-neutral-400 hover:text-neutral-200 hover:bg-neutral-900 border border-transparent'
                }`}
              >
                {genre}
              </button>
            );
          })}
        </nav>

        {/* Live Story Progress Tracker */}
        <div className="flex items-center gap-3 text-xs font-mono text-neutral-400">
          <div className="flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5 text-rose-500" />
            <span>
              Story <strong className="text-white">{currentIndex + 1}</strong> of{' '}
              <strong className="text-neutral-400">{totalCards}</strong>
            </span>
          </div>
        </div>
      </header>

      {/* ------------------------------------------------------------------ */}
      {/* 2. CENTER CANVAS & VERTICAL DECK CARD STACK                        */}
      {/* ------------------------------------------------------------------ */}
      <main className="flex-1 w-full flex items-center justify-center relative overflow-hidden">
        {/* Subtle Ambient Radial Backlight */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-neutral-900/60 via-neutral-950 to-neutral-950 pointer-events-none" />

        {totalCards === 0 ? (
          <div className="text-center p-8 bg-neutral-900/60 rounded-2xl border border-neutral-800 max-w-md">
            <Layers className="w-10 h-10 text-neutral-600 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-neutral-200 mb-1">No stories in this genre</h3>
            <p className="text-xs text-neutral-400 mb-4">
              Switch to another genre or return to All to view the latest cycle.
            </p>
            <button
              onClick={() => setSelectedGenre('All')}
              className="text-xs font-semibold px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-white rounded-lg transition-colors"
            >
              Reset to All
            </button>
          </div>
        ) : (
          <div className="relative w-[900px] h-[520px] flex items-center justify-center">
            {/* The Active Split Card with Fluid Snapping Transition */}
            <div
              key={activeCard.url_hash}
              className={`transform transition-all duration-300 ease-out ${
                isTransitioning ? 'scale-[0.98] opacity-90' : 'scale-100 opacity-100'
              }`}
            >
              <MusicCard article={activeCard} isActive={true} />
            </div>
          </div>
        )}

        {/* ------------------------------------------------------------------ */}
        {/* 3. FLOATING DESKTOP VERTICAL NAVIGATION CONTROLS (RIGHT MARGIN)     */}
        {/* ------------------------------------------------------------------ */}
        <div className="absolute right-8 top-1/2 -translate-y-1/2 flex flex-col items-center gap-3 z-30">
          <button
            onClick={goToPrev}
            disabled={currentIndex === 0}
            aria-label="Previous story (Arrow Up)"
            className={`w-11 h-11 rounded-full flex items-center justify-center border transition-all duration-200 ${
              currentIndex === 0
                ? 'opacity-30 cursor-not-allowed border-neutral-800 bg-neutral-900/40 text-neutral-600'
                : 'border-neutral-700/80 bg-neutral-900/90 text-neutral-300 hover:text-white hover:border-rose-500/60 hover:bg-neutral-800 shadow-lg'
            }`}
          >
            <ChevronUp className="w-5 h-5" />
          </button>

          {/* Minimalist Vertical Indicator Rail */}
          <div className="w-1.5 h-36 bg-neutral-900 rounded-full relative overflow-hidden border border-neutral-800/80 my-1">
            <div
              className="w-full bg-rose-500 rounded-full transition-all duration-300"
              style={{
                height: `${Math.max(8, progressPercent)}%`,
                transform: `translateY(${
                  totalCards > 1 ? (currentIndex / (totalCards - 1)) * 100 : 0
                }%)`,
              }}
            />
          </div>

          <button
            onClick={goToNext}
            disabled={currentIndex >= totalCards - 1}
            aria-label="Next story (Arrow Down)"
            className={`w-11 h-11 rounded-full flex items-center justify-center border transition-all duration-200 ${
              currentIndex >= totalCards - 1
                ? 'opacity-30 cursor-not-allowed border-neutral-800 bg-neutral-900/40 text-neutral-600'
                : 'border-neutral-700/80 bg-neutral-900/90 text-neutral-300 hover:text-white hover:border-rose-500/60 hover:bg-neutral-800 shadow-lg'
            }`}
          >
            <ChevronDown className="w-5 h-5" />
          </button>
        </div>
      </main>

      {/* ------------------------------------------------------------------ */}
      {/* 4. BOTTOM STATUS BAR & PROGRESS TRACKER                            */}
      {/* ------------------------------------------------------------------ */}
      <footer className="w-full h-11 border-t border-neutral-900 bg-neutral-950 px-8 flex items-center justify-between text-xs text-neutral-500 z-30 flex-shrink-0">
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-rose-500" />
          <span>Curated Inshorts Music Deck • 6-Hour Automated Ingestion Cycle</span>
        </div>

        <div className="flex items-center gap-4 font-mono text-[11px]">
          <span>
            Progress: <strong className="text-neutral-300">{Math.round(progressPercent)}%</strong>
          </span>
          <span className="hidden md:inline">• Keyboard: [↓ / Space / J] Next • [↑ / K] Prev</span>
        </div>
      </footer>
    </div>
  );
};
