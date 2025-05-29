import { NextRequest, NextResponse } from 'next/server';
import { TextToSpeechClient } from '@google-cloud/text-to-speech';

const client = new TextToSpeechClient({
  credentials: {
    client_email: process.env.GCP_CLIENT_EMAIL,
    private_key: process.env.GCP_PRIVATE_KEY?.replace(/\\n/g, '\n'),
  },
  projectId: process.env.GCP_PROJECT_ID,
});

const audioCache = new Map<string, { buffer: Buffer; timestamp: number }>();
const CACHE_TTL = 1000 * 60 * 60;
const MAX_CACHE_SIZE = 100;

function cleanCache() {
  const now = Date.now();
  for (const [key, value] of audioCache.entries()) {
    if (now - value.timestamp > CACHE_TTL) {
      audioCache.delete(key);
    }
  }

  if (audioCache.size > MAX_CACHE_SIZE) {
    const entries = Array.from(audioCache.entries());
    entries.sort((a, b) => a[1].timestamp - b[1].timestamp);
    const toDelete = entries.slice(0, audioCache.size - MAX_CACHE_SIZE);
    toDelete.forEach(([key]) => audioCache.delete(key));
  }
}

function generateCacheKey(text: string, voiceConfig: any): string {
  const configString = JSON.stringify(voiceConfig);
  const textHash = Buffer.from(text).toString('base64').slice(0, 50);
  const configHash = Buffer.from(configString).toString('base64').slice(0, 20);
  return `${textHash}-${configHash}`;
}

// Preprocessing for better TTS quality
function preprocessText(text: string): string {
  // Remove markdown formatting characters that would be pronounced
  let processed = text
    .replace(/\*\*(.*?)\*\*/g, '$1') // Bold
    .replace(/\*(.*?)\*/g, '$1') // Italic
    .replace(/`(.*?)`/g, '$1') // Code
    .replace(/_{2,}(.*?)_{2,}/g, '$1') // Underline
    .replace(/~{2}(.*?)~{2}/g, '$1') // Strikethrough
    .replace(/\[(.*?)\]\(.*?\)/g, '$1') // Links - keep link text only
    .replace(/#{1,6}\s*/g, '') // Remove header markers
    .replace(/^\s*[-*+]\s+/gm, '') // Remove bullet points
    .replace(/^\s*\d+\.\s+/gm, ''); // Remove numbered list markers

  // Handle abbreviations and technical terms
  processed = processed
    .replace(/\bAPI\b/g, 'A P I')
    .replace(/\bURL\b/g, 'U R L')
    .replace(/\bHTTP\b/g, 'H T T P')
    .replace(/\bJSON\b/g, 'Jason')
    .replace(/\bSQL\b/g, 'S Q L')
    .replace(/\bHTML\b/g, 'H T M L')
    .replace(/\bCSS\b/g, 'C S S')
    .replace(/\bJS\b/g, 'JavaScript');

  // Escape XML special characters for SSML
  processed = processed
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '')
    .replace(/'/g, '&apos;');

  // Add pauses for better pacing using proper SSML break tags
  processed = processed
    .replace(/\. /g, '. <break time="300ms"/>')
    .replace(/\? /g, '? <break time="400ms"/>')
    .replace(/! /g, '! <break time="400ms"/>')
    .replace(/: /g, ': <break time="200ms"/>')
    .replace(/; /g, '; <break time="200ms"/>');

  // Limit length for reasonable audio duration (adjust as needed)
  if (processed.length > 1000) {
    processed = processed.substring(0, 997) + '...';
  }

  return processed.trim();
}

// Validate SSML before sending to GCP
function validateSSML(ssml: string): boolean {
  try {
    // Basic SSML validation
    const xmlParser = new DOMParser();
    const doc = xmlParser.parseFromString(ssml, 'application/xml');

    // Check for parsing errors
    const parserError = doc.querySelector('parsererror');
    if (parserError) {
      console.error('SSML parsing error:', parserError.textContent);
      return false;
    }

    return true;
  } catch (error) {
    console.error('SSML validation error:', error);
    return false;
  }
}

export async function POST(request: NextRequest) {
  try {
    const startTime = Date.now();

    // Parse request body with error handling
    let body;
    try {
      const rawBody = await request.text();
      if (!rawBody.trim()) {
        return NextResponse.json(
          { error: 'Empty request body' },
          { status: 400 },
        );
      }
      body = JSON.parse(rawBody);
    } catch (parseError) {
      console.error('JSON parsing error:', parseError);
      return NextResponse.json(
        { error: 'Invalid JSON in request body' },
        { status: 400 },
      );
    }

    const { input, voice, audioConfig } = body;

    if (!input?.text) {
      return NextResponse.json(
        { error: 'Text input is required' },
        { status: 400 },
      );
    }

    // Preprocess text for better TTS quality
    const processedText = preprocessText(input.text);

    // Generate cache key
    const cacheKey = generateCacheKey(processedText, { voice, audioConfig });

    // Check cache first
    cleanCache();
    const cached = audioCache.get(cacheKey);
    if (cached) {
      console.log(
        `TTS cache hit for text: "${processedText.substring(0, 50)}..."`,
      );

      return new NextResponse(cached.buffer, {
        status: 200,
        headers: {
          'Content-Type': 'audio/wav',
          'Content-Length': cached.buffer.length.toString(),
          'Cache-Control': 'public, max-age=3600',
          'X-Cache': 'HIT',
          'X-Response-Time': `${Date.now() - startTime}ms`,
        },
      });
    }

    // Default voice configuration optimized for conversational AI
    const defaultVoice = {
      languageCode: 'en-US',
      name: 'en-US-Neural2-F', // High-quality neural voice
      ssmlGender: 'FEMALE',
      ...voice,
    };

    // Default audio configuration optimized for low latency
    const defaultAudioConfig = {
      audioEncoding: 'LINEAR16',
      sampleRateHertz: 24000,
      speakingRate: 1.2, // Slightly faster for conversation
      pitch: 0,
      volumeGainDb: 0,
      effectsProfileId: ['telephony-class-application'], // Optimized for voice apps
      ...audioConfig,
    };

    // Wrap text in SSML for better control
    const ssmlText = `<speak>${processedText}</speak>`;

    // Validate SSML before sending
    if (typeof window !== 'undefined' && !validateSSML(ssmlText)) {
      console.warn('Invalid SSML detected, falling back to plain text');
      // Fallback to plain text if SSML is invalid
      const ttsRequest = {
        input: { text: input.text },
        voice: defaultVoice,
        audioConfig: defaultAudioConfig,
      };
    }

    // Prepare the TTS request
    const ttsRequest = {
      input: { ssml: ssmlText },
      voice: defaultVoice,
      audioConfig: defaultAudioConfig,
    };

    console.log(`Generating TTS for: "${processedText.substring(0, 100)}..."`);
    console.log(`SSML: ${ssmlText.substring(0, 200)}...`);

    // Call Google Cloud TTS API
    const [response] = await client.synthesizeSpeech(ttsRequest);

    if (!response.audioContent) {
      throw new Error('No audio content received from GCP TTS');
    }

    // Convert to Buffer
    const audioBuffer = Buffer.from(response.audioContent as Uint8Array);

    // Cache the result
    audioCache.set(cacheKey, {
      buffer: audioBuffer,
      timestamp: Date.now(),
    });

    const processingTime = Date.now() - startTime;
    console.log(
      `TTS generated in ${processingTime}ms, audio size: ${audioBuffer.length} bytes`,
    );

    // Return audio with appropriate headers
    return new NextResponse(audioBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'audio/wav',
        'Content-Length': audioBuffer.length.toString(),
        'Cache-Control': 'public, max-age=3600',
        'X-Cache': 'MISS',
        'X-Response-Time': `${processingTime}ms`,
        'X-Audio-Duration': `${Math.round(audioBuffer.length / (24000 * 2))}s`, // Rough estimate
      },
    });
  } catch (error) {
    console.error('GCP TTS API Error:', error);

    // If it's an SSML error, try with plain text as fallback
    if (error instanceof Error && error.message.includes('Invalid SSML')) {
      try {
        console.log('Retrying with plain text fallback...');
        const body = await request.json();

        const ttsRequest = {
          input: { text: body.input.text },
          voice: {
            languageCode: 'en-US',
            name: 'en-US-Neural2-D',
            ssmlGender: 'MALE',
            ...body.voice,
          },
          audioConfig: {
            audioEncoding: 'LINEAR16',
            sampleRateHertz: 24000,
            speakingRate: 1.2,
            pitch: -4.0,
            volumeGainDb: 2.0,
            effectsProfileId: ['telephony-class-application'],
            ...body.audioConfig,
          },
        };

        const [response] = await client.synthesizeSpeech(ttsRequest);
        const audioBuffer = Buffer.from(response.audioContent as Uint8Array);

        return new NextResponse(audioBuffer, {
          status: 200,
          headers: {
            'Content-Type': 'audio/wav',
            'Content-Length': audioBuffer.length.toString(),
            'X-Fallback': 'plain-text',
          },
        });
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
      }
    }

    return NextResponse.json(
      {
        error: 'Failed to generate speech',
        details: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 },
    );
  }
}

// Optional: Health check endpoint
export async function GET() {
  try {
    // Test a simple TTS request to verify the service is working
    const testRequest = {
      input: { text: 'Test' },
      voice: {
        languageCode: 'en-US',
        name: 'en-US-Standard-A',
        ssmlGender: 'FEMALE',
      },
      audioConfig: {
        audioEncoding: 'LINEAR16',
        sampleRateHertz: 16000,
      },
    };

    await client.synthesizeSpeech(testRequest as any);

    return NextResponse.json({
      status: 'healthy',
      service: 'gcp-tts',
      cacheSize: audioCache.size,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        status: 'unhealthy',
        error: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 503 },
    );
  }
}
