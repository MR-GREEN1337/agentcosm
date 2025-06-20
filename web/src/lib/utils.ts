import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const RENDERER_SERVICE_URL =
  process.env.NEXT_PUBLIC_RENDERER_SERVICE_URL ||
  'https://agentcosm-renderer-527185366316.us-central1.run.app';
