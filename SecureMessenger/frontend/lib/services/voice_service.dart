// lib/services/voice_service.dart
import 'dart:io';
import 'dart:math';
import 'package:path_provider/path_provider.dart';
import 'package:record/record.dart';
import 'package:ffmpeg_kit_flutter_full_gpl/ffmpeg_kit.dart' show FFmpegKit, ReturnCode;

import 'encryption_service.dart';
import 'api_service.dart';

class VoiceService {
  VoiceService._();
  static final Record _recorder = Record();
  static String? _rawWavPath;

  // Inicia grabación PCM 48k WAV en un archivo temporal
  static Future<void> startRecording() async {
    final hasPerm = await _recorder.hasPermission();
    if (!hasPerm) {
      throw Exception('Mic permission denied');
    }
    final dir = await getTemporaryDirectory();
    _rawWavPath = '${dir.path}/voice_raw_${DateTime.now().millisecondsSinceEpoch}.wav';
    // WAV 48 kHz mono
    await _recorder.start(
      const RecordConfig(encoder: AudioEncoder.wav, sampleRate: 48000, numChannels: 1),
      path: _rawWavPath!,
    );
  }

  static Future<bool> isRecording() => _recorder.isRecording();

  // Detiene, distorsiona, cifra, sube y manda mensaje
  static Future<void> stopEncryptUploadAndSend({
    required String token,
    required int chatId,
    String filenameHint = 'voice.opus.sm1',
    String expiresAt = "",
  }) async {
    final recPath = await _recorder.stop();
    if (recPath == null) {
      throw Exception('Recorder returned null path');
    }
    final raw = File(recPath);
    if (!await raw.exists()) throw Exception('Raw recording not found');

    final tmpDir = await getTemporaryDirectory();
    final opusPath = '${tmpDir.path}/voice_${_rand()}.opus';
    final encPath  = '${tmpDir.path}/voice_${_rand()}.opus.sm1';

    try {
      // Distorsión + codificación a Opus (desktop usa ffmpeg CLI; móvil usa ffmpeg_kit)
      await _distortToOpus(inPath: raw.path, outPath: opusPath);

      // Cifrar a .sm1
      final enc = await EncryptionService.encryptFile(
        input: File(opusPath),
        chatId: chatId,
        outputPath: encPath,
      );

      // Subir a /voice/upload
      final voiceId = await ApiService.uploadVoiceEncrypted(
        token: token,
        chatId: chatId,
        voiceFile: enc,
        filename: filenameHint,
        expiresAt: expiresAt,
      );

      // Publicar mensaje type='voice'
      await ApiService.sendMessage(
        token,
        Message(
          id: 0,
          chatId: chatId,
          senderId: 0,
          content: voiceId, // el backend guarda el id; el cliente descargará y descifrará
          createdAt: DateTime.now().toIso8601String(),
          expiresAt: expiresAt.isEmpty ? null : expiresAt,
          type: 'voice',
          filename: filenameHint,
          mimetype: 'audio/opus+sm1',
        ),
      );
    } finally {
      // Limpieza best-effort
      try { await EncryptionService.secureDelete(raw); } catch (_) {}
      try { await EncryptionService.secureDelete(File(opusPath)); } catch (_) {}
      try { await EncryptionService.secureDelete(File(encPath)); } catch (_) {}
    }
  }

  // Distorsión de voz (pitch + filtro banda + bitcrusher) y codificación Opus 24 kbps
  static Future<void> _distortToOpus({required String inPath, required String outPath}) async {
    final args = [
      '-y',
      '-i', inPath,
      '-af',
      // pitch +15%, compensación de tempo, banda 300–3200 Hz, crusher 8-bit
      'asetrate=48000*1.15,aresample=48000,atempo=0.87,highpass=f=300,lowpass=f=3200,acrusher=bits=8:mode=log:aa=1',
      '-c:a', 'libopus',
      '-b:a', '24k',
      outPath,
    ];

    if (_isMobileOrMacOS()) {
      final cmd = args.join(' ');
      final session = await FFmpegKit.execute(cmd);
      final rc = await session.getReturnCode();
      if (!ReturnCode.isSuccess(rc)) {
        final logs = await session.getLogsAsString();
        throw Exception('ffmpeg_kit failed: rc=$rc logs=$logs');
      }
    } else {
      // Desktop: usa ffmpeg del sistema
      final proc = await Process.start('ffmpeg', args);
      final code = await proc.exitCode;
      if (code != 0) {
        final err = await proc.stderr.transform(const SystemEncoding().decoder).join();
        throw Exception('ffmpeg failed ($code): $err');
      }
    }
    if (!await File(outPath).exists()) {
      throw Exception('Distorted Opus not created');
    }
  }

  static bool _isMobileOrMacOS() {
    try {
      return Platform.isAndroid || Platform.isIOS || Platform.isMacOS;
    } catch (_) {
      return false;
    }
  }

  static String _rand() => Random.secure().nextInt(1<<32).toRadixString(16);
}

// Modelo Message usado por ApiService.sendMessage
class Message {
  final int id;
  final int chatId;
  final int senderId;
  final String content;
  final String createdAt;
  final String? expiresAt;
  final String type;
  final String? filename;
  final String? mimetype;

  Message({
    required this.id,
    required this.chatId,
    required this.senderId,
    required this.content,
    required this.createdAt,
    this.expiresAt,
    required this.type,
    this.filename,
    this.mimetype,
  });

  Map<String, dynamic> toJson() => {
    'chat_id': chatId,
    'content': content,
    'expires_at': expiresAt,
    'type': type,
    'filename': filename,
    'mimetype': mimetype,
  };
}
