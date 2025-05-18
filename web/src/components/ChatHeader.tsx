import React, { useCallback, useState, useMemo } from 'react';
import { PlanetIcon } from '@/components/PlanetIcon';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useMediaQuery } from '@/hooks/use-media';
import { 
  Menu, 
  Plus, 
  ChevronDown, 
  X, 
  Command, 
  Settings,
  Download
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface ChatHeaderProps {
  title?: string;
  onNewChat?: () => void;
  onMenuToggle?: () => void;
  isMenuOpen?: boolean;
  mode?: 'light' | 'dark';
  onExportChat?: () => void;
  onSettings?: () => void;
  userName?: string;
}

export function ChatHeader({
  title = 'Agent Cosm',
  onNewChat,
  onMenuToggle,
  isMenuOpen = false,
  mode = 'dark',
  onExportChat,
  onSettings,
  userName
}: ChatHeaderProps) {
  // For performance, use a ref to track hover state instead of a state variable
  const hoverRef = React.useRef<HTMLButtonElement>(null);
  
  // Check if we're on mobile devices
  const isMobile = useMediaQuery('(max-width: 768px)');
  
  // Memoize colors to prevent rerenders
  const colors = useMemo(() => {
    return {
      bg: mode === 'dark' ? 'rgba(18, 18, 23, 0.8)' : 'rgba(255, 255, 255, 0.85)',
      text: mode === 'dark' ? 'white' : 'black',
      border: mode === 'dark' ? 'rgba(64, 64, 80, 0.5)' : 'rgba(230, 230, 235, 0.8)',
      buttonBg: mode === 'dark' ? 'rgba(45, 45, 60, 0.5)' : 'rgba(240, 240, 245, 0.8)',
      buttonHover: mode === 'dark' ? 'rgba(60, 60, 75, 0.7)' : 'rgba(230, 230, 235, 0.9)',
      menuButtonBg: isMenuOpen 
        ? (mode === 'dark' ? 'rgba(80, 80, 95, 0.7)' : 'rgba(220, 220, 225, 0.9)') 
        : 'transparent'
    };
  }, [mode, isMenuOpen]);
  
  // For better performance, use memoized event handlers
  const handleNewChat = useCallback(() => {
    if (onNewChat) onNewChat();
  }, [onNewChat]);

  const handleMenuToggle = useCallback(() => {
    if (onMenuToggle) onMenuToggle();
  }, [onMenuToggle]);
  
  const handleExportChat = useCallback(() => {
    if (onExportChat) onExportChat();
  }, [onExportChat]);
  
  const handleSettings = useCallback(() => {
    if (onSettings) onSettings();
  }, [onSettings]);

  // Memoized dropdown component to avoid unnecessary re-renders
  const UserDropdown = useMemo(() => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          className="p-1 h-8 gap-1.5 text-sm"
          style={{ 
            color: colors.text,
            background: 'transparent' 
          }}
        >
          <span className="max-w-[100px] truncate">{userName || 'User'}</span>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel>My Account</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleSettings}>
          <Settings className="mr-2 h-4 w-4" />
          <span>Settings</span>
        </DropdownMenuItem>
        <DropdownMenuItem onClick={handleExportChat}>
          <Download className="mr-2 h-4 w-4" />
          <span>Export Chat</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  ), [colors.text, userName, handleSettings, handleExportChat]);

  return (
    <header 
      className="sticky top-0 z-10 w-full"
      style={{ 
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        backgroundColor: colors.bg, 
        borderBottom: `1px solid ${colors.border}`,
        willChange: 'transform',
        transform: 'translateZ(0)',
      }}
    >
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          {/* Menu button (mobile only) */}
          {isMobile && (
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden h-8 w-8 mr-1"
              onClick={handleMenuToggle}
              style={{ 
                backgroundColor: colors.menuButtonBg,
                color: colors.text
              }}
              aria-label={isMenuOpen ? "Close menu" : "Open menu"}
            >
              {isMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>
          )}
        
          {/* Logo and title */}
          <Link href="/" className="flex items-center">
            <motion.div 
              whileHover={{ scale: 1.1, rotate: 10 }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              <PlanetIcon />
            </motion.div>
            <span 
              className="ml-2 text-lg font-medium hidden sm:block"
              style={{ color: colors.text }}
            >
              {title}
            </span>
          </Link>
        </div>

        <div className="flex items-center gap-2">
          {/* Keyboard shortcut indicator (desktop only) */}
          {!isMobile && (
            <div className="hidden md:flex items-center mr-1 text-xs text-muted-foreground border border-muted-foreground/30 rounded px-1.5 py-0.5">
              <Command className="h-3 w-3 mr-1" />
              <span>K</span>
            </div>
          )}
        
          {/* New chat button */}
          <Button
            ref={hoverRef}
            onClick={handleNewChat}
            className="flex items-center justify-center px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200"
            style={{ 
              background: hoverRef.current?.matches(':hover') 
                ? colors.buttonHover 
                : colors.buttonBg,
              color: colors.text
            }}
          >
            <Plus className="w-4 h-4 mr-1.5" />
            <span className="hidden sm:inline">New Chat</span>
          </Button>
          
          {/* User dropdown */}
          {!isMobile && UserDropdown}
          
          {/* Menu button (desktop only) */}
          {!isMobile && (
            <Button
              variant="ghost"
              size="icon"
              className="hidden md:flex h-8 w-8"
              onClick={handleMenuToggle}
              style={{ 
                backgroundColor: colors.menuButtonBg,
                color: colors.text
              }}
              aria-label={isMenuOpen ? "Close menu" : "Open menu"}
            >
              {isMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
            </Button>
          )}
        </div>
      </div>
    </header>
  );
}