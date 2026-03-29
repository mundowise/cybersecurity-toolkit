// lib/widgets/voice_send_button.dart
import 'package:flutter/material.dart';
import '../services/voice_service.dart';

class VoiceSendButton extends StatefulWidget {
  final String token;
  final int chatId;
  final String expiresAt; // "" si no expira

  const VoiceSendButton({
    super.key,
    required this.token,
    required this.chatId,
    this.expiresAt = "",
  });

  @override
  State<VoiceSendButton> createState() => _VoiceSendButtonState();
}

class _VoiceSendButtonState extends State<VoiceSendButton> {
  bool _rec = false;
  bool _busy = false;

  @override
  Widget build(BuildContext context) {
    return IconButton(
      tooltip: _rec ? 'Detener y enviar' : 'Grabar mensaje de voz',
      icon: _busy
          ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2))
          : Icon(_rec ? Icons.stop_circle : Icons.mic, size: 26),
      onPressed: _busy ? null : () async {
        try {
          if (!_rec) {
            await VoiceService.startRecording();
            setState(() => _rec = true);
          } else {
            setState(() { _rec = false; _busy = true; });
            await VoiceService.stopEncryptUploadAndSend(
              token: widget.token,
              chatId: widget.chatId,
              filenameHint: 'voice.opus.sm1',
              expiresAt: widget.expiresAt,
            );
          }
        } catch (e) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Voz: $e')),
          );
        } finally {
          if (mounted) setState(() => _busy = false);
        }
      },
    );
  }
}
