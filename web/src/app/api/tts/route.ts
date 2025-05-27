// Backend API endpoint (e.g., /api/tts)
// This goes on your server, not in the frontend

import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

// Initialize ElevenLabs client with your API key (server-side only)
const elevenlabs = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY // Store in environment variables
});

export async function POST(request: any) {
  try {
    const { text, voiceId = "JBFqnCBsd6RMkjVDRZzb" } = await request.json();

    if (!text) {
      return new Response("Text is required", { status: 400 });
    }

    // Generate speech using ElevenLabs
    const audioStream = await elevenlabs.textToSpeech.convert(voiceId, {
      text: text,
      modelId: "eleven_multilingual_v2",
      outputFormat: "mp3_44100_128",
    });

    // Convert ReadableStream to buffer
    const reader = audioStream.getReader();
    const chunks = [];

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
    }

    const audioBuffer = Buffer.concat(chunks);

    // Return the audio as a response
    return new Response(audioBuffer, {
      status: 200,
      headers: {
        "Content-Type": "audio/mpeg",
        "Content-Length": audioBuffer.length.toString(),
      },
    });

  } catch (error) {
    console.error("TTS generation error:", error);
    return new Response("TTS generation failed", { status: 500 });
  }
}

// Alternative Express.js implementation:
/*
import express from 'express';
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const app = express();
app.use(express.json());

const elevenlabs = new ElevenLabsClient({
  apiKey: process.env.ELEVENLABS_API_KEY
});

app.post('/api/tts', async (req, res) => {
  try {
    const { text, voiceId = "JBFqnCBsd6RMkjVDRZzb" } = req.body;

    if (!text) {
      return res.status(400).json({ error: "Text is required" });
    }

    const audioStream = await elevenlabs.textToSpeech.convert(voiceId, {
      text: text,
      modelId: "eleven_multilingual_v2",
      outputFormat: "mp3_44100_128",
    });

    // Convert ReadableStream to buffer
    const reader = audioStream.getReader();
    const chunks = [];

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
    }

    const audioBuffer = Buffer.concat(chunks);

    res.set({
      'Content-Type': 'audio/mpeg',
      'Content-Length': audioBuffer.length
    });

    res.send(audioBuffer);

  } catch (error) {
    console.error("TTS generation error:", error);
    res.status(500).json({ error: "TTS generation failed" });
  }
});
*/

// Even simpler approach - stream directly to response:
/*
export async function POST(request: any) {
  try {
    const { text, voiceId = "JBFqnCBsd6RMkjVDRZzb" } = await request.json();

    if (!text) {
      return new Response("Text is required", { status: 400 });
    }

    const audioStream = await elevenlabs.textToSpeech.convert(voiceId, {
      text: text,
      modelId: "eleven_multilingual_v2",
      outputFormat: "mp3_44100_128",
    });

    // Stream directly to response (more memory efficient)
    return new Response(audioStream, {
      status: 200,
      headers: {
        "Content-Type": "audio/mpeg",
      },
    });

  } catch (error) {
    console.error("TTS generation error:", error);
    return new Response("TTS generation failed", { status: 500 });
  }
}
*/
